from collections import deque, Counter
from typing import Deque

import numpy as np
import pandas as pd

from database import db
from backend.models import Data, Tag

MS3 = 'MS3'
BO3 = 'BO3'


class Scenario:
    def __init__(self, method_name, maximum_sale_value=100000):
        self.maximum_sale_value = maximum_sale_value
        self.model_name = method_name.upper()
        self.kpis = ['DECLARED', 'SHORTFALL',
                     'REVENUE', 'PENALTY', 'CURTAILED']
        self.chart_tags = [f'DECLARED_{method_name}', f'ACTUAL', f'BATTERY_CAPACITY_{method_name}']
        self.tags = [i + f'_{self.model_name}' for i in self.kpis] + ['ACTUAL', 'BATTERY_CAPACITY_' + method_name]

    def sold(self, value, timestamp):
        if value is None or pd.isnull(value):
            raise ValueError('Value cannot be None')
        tag_sold = Tag.get_by_name('SOLD' + f'_{self.model_name}')
        tag_revenue = Tag.get_by_name('REVENUE' + f'_{self.model_name}')
        if not pd.isnull(value):
            db.session.add(Data(tag=tag_sold, value=value, timestamp=timestamp))
            db.session.add(Data(tag=tag_revenue, value=value, timestamp=timestamp))

    def declared(self, value, timestamp):
        value = min(value, self.maximum_sale_value)
        tag_declared = Tag.get_by_name('DECLARED' + f'_{self.model_name}')
        db.session.add(Data(tag=tag_declared, value=value, timestamp=timestamp))

    def curtailed(self, value, timestamp):
        tag = Tag.get_by_name('CURTAILED' + f'_{self.model_name}')
        db.session.add(Data(tag=tag, value=value, timestamp=timestamp))

    def penatly(self, value, timestamp):
        tag = Tag.get_by_name('PENALTY' + f'_{self.model_name}')
        db.session.add(Data(tag=tag, value=value, timestamp=timestamp))

    def battery(self, value, timestamp):
        tag = Tag.get_by_name('BATTERY_CAPACITY' + f'_{self.model_name}')
        db.session.add(Data(tag=tag, value=value, timestamp=timestamp))

    def shortfall(self, value, timestamp):
        tag = Tag.get_by_name('SHORTFALL' + f'_{self.model_name}')
        db.session.add(Data(tag=tag, value=value, timestamp=timestamp))


class HistoricalData:
    def __init__(self, model_number, prediction_value, actual):
        self.model_number = model_number
        self.prediction_value = prediction_value
        self.actual = actual
        self.diff = self.prediction_value - self.actual

    def __hash__(self):
        return hash(self.model_number)

    def __repr__(self):
        return f'Model #: {self.model_number}, diff:{self.diff}'


def get_and_clean_raw_data():
    tags = db.session.query(Tag).filter(Tag.name.in_(['ACTUAL', 'FSP1', 'FSP2'])).all()
    data = []
    for tag in tags:
        df = tag.get_data()
        data.append(df)
    df = pd.concat(data, axis=1)
    return df


def add_method_ms3_data(df, scenario: Scenario):
    df['DIFF_FSP1'] = df['ACTUAL'] - df['FSP1']
    df['DIFF_FSP2'] = df['ACTUAL'] - df['FSP2']
    # rolling average vs rolling sum -> a sum is more appropriate for energy production,
    # and less information goes missing than in an average. In an average, high deviations
    # could be missed, but not in a sum

    df['FSP1_RS'] = df['DIFF_FSP1'].rolling(3).sum().abs()
    df['FSP2_RS'] = df['DIFF_FSP2'].rolling(3).sum().abs()
    df['MODEL_TO_USE_MS3'] = np.where(df['FSP1_RS'] < df['FSP2_RS'], 1, 2)
    df['MODEL_TO_USE_MS3'] = df['MODEL_TO_USE_MS3'].shift(freq='-1h')
    df['DECLARED_MS3'] = np.where(df['MODEL_TO_USE_MS3'] == 1,
                                  np.clip(df['FSP1'], 0, scenario.maximum_sale_value),
                                  np.clip(df['FSP2'], 0, scenario.maximum_sale_value))
    df['DIFF_MS3'] = df['ACTUAL'] - df['DECLARED_MS3']

    tag_declared = Tag.get_by_name('DECLARED_MS3')
    declared = [Data(value=value, timestamp=i, tag=tag_declared) for i, value in df['DECLARED_MS3'].items()]
    db.session.add_all(declared)
    db.session.commit()
    return df


def add_method_bo3_data(df, scenario: Scenario):
    predictions = deque()

    def get_model_for_declaration(predictions: [Deque[HistoricalData]]):
        model_count = Counter(i.model_number for i in predictions)
        model, count = model_count.most_common(1)[0]
        return model

    # constructing methods to use for predictions
    for (ia, act), (i1, v1), (i2, v2) in zip(df['ACTUAL'].items(), df['FSP1'].items(), df['FSP2'].items()):
        hs1 = HistoricalData(1, v1, act)
        hs2 = HistoricalData(2, v2, act)
        models = {hs1, hs2}
        # Penalising models for under predicting
        if hs1.diff < 0:
            models.remove(hs1)
        if hs2.diff < 0:
            models.remove(hs2)

        # use the model with the smallest difference.
        if len(models) == 2:
            best_in_scenario = hs1 if hs1.diff < hs2.diff else hs2
        elif len(models) == 1:
            best_in_scenario = models.pop()
        else:
            best_in_scenario = hs1 if abs(hs1.diff) < abs(hs2.diff) else hs2

        # keep track of the best model for the past 3 hours
        predictions.append(best_in_scenario)

        if len(predictions) > 3:
            predictions.popleft()

        # declare with model to use for the upcoming hour
        # B03 -> best of 3 for above criteria

        df.at[ia, 'MODEL_FOR_NEXT_HOUR_BO3'] = get_model_for_declaration(predictions)
    df['MODEL_TO_USE_BO3'] = df['MODEL_FOR_NEXT_HOUR_BO3'].shift(freq='-1h')
    df['DECLARED_BO3'] = np.where(df['MODEL_TO_USE_BO3'] == 1,
                                  np.clip(df['FSP1'], 0, scenario.maximum_sale_value),
                                  np.clip(df['FSP2'], 0, scenario.maximum_sale_value))

    df['DIFF_BO3'] = df['ACTUAL'] - df['DECLARED_BO3']
    tag_declared = Tag.get_by_name('DECLARED_BO3')
    declared = [Data(value=value, timestamp=i, tag=tag_declared) for i, value in df['DECLARED_BO3'].items() if
                not pd.isnull(value)]
    db.session.add_all(declared)
    db.session.commit()
    return df


def run_simulations(df, scenario):
    method = scenario.model_name

    # do actual calculations to sell
    for (i_d, diff), (i_act, actual) in zip(df[f'DIFF_{method}'].items(), df['ACTUAL'].items()):
        i, diff = (i_d, diff)
        i_act, actual = (i_act, actual)

        #  if diff > 0 == surplus power, if diff < 0 == shortfall of power
        # just recreating the value here without having to iterate through 3 series from the df
        declared = min(actual + diff, 100000)
        previous_index = i - pd.Timedelta(hours=1)
        if previous_index in df.index:
            battery_capacity = f'BATTERY_CAPACITY_{method}'
            df_to_ffill = df.loc[:i].copy()
            df_to_ffill[battery_capacity] = df_to_ffill[battery_capacity].ffill()
            df.update(df_to_ffill)
            previous_battery_capacity = df.at[previous_index, battery_capacity]
        else:
            df.loc[df.index.min(), f'BATTERY_CAPACITY_{method}'] = 0
            previous_battery_capacity = 0
        previous_battery_capacity = 0 if previous_battery_capacity != previous_battery_capacity else previous_battery_capacity
        max_battery_capacity = 60000
        if previous_battery_capacity > max_battery_capacity:
            raise ValueError(f'Battery capacity exceeds {max_battery_capacity}')
        if diff <= 0:
            if previous_battery_capacity >= abs(diff):
                battery_capacity = previous_battery_capacity - abs(diff)
                fsp1 = df.at[i, 'FSP1']
                fsp2 = df.at[i, 'FSP2']
                if fsp1 == 0 and fsp2 == 0:
                    if previous_battery_capacity > 10000:
                        declared = 10000
                        scenario.sold(value=declared, timestamp=i)
                        scenario.battery(value=previous_battery_capacity - declared, timestamp=i)
                        df.at[i, f'BATTERY_CAPACITY_{method}'] -= declared
                else:
                    scenario.sold(declared, i)
                    scenario.battery(battery_capacity, i)

            elif previous_battery_capacity < abs(diff):
                # will incur penalty
                extract_from_battery = min(previous_battery_capacity, 20000)
                sold = actual + extract_from_battery
                battery_capacity = previous_battery_capacity - extract_from_battery
                scenario.sold(sold, i)
                scenario.battery(battery_capacity, i)
                shortfall = declared - sold
                penalty = shortfall*0.2
                scenario.penatly(value=abs(penalty), timestamp=i)
                scenario.shortfall(value=shortfall, timestamp=i)

        elif diff > 0:
            scenario.sold(declared, i)
            if previous_battery_capacity >= max_battery_capacity:
                curtail = previous_battery_capacity - max_battery_capacity
                scenario.curtailed(curtail, i)
            elif previous_battery_capacity + diff >= max_battery_capacity:

                available_capacity = max_battery_capacity - previous_battery_capacity

                to_battery = min(diff, available_capacity)
                if to_battery >= 20000:
                    to_battery = 20000 - to_battery
                battery_capacity = f'BATTERY_CAPACITY_{method}'
                df.at[i, battery_capacity] += to_battery
                scenario.battery(df.at[i, battery_capacity], i)
                scenario.curtailed(value=diff - to_battery, timestamp=i)
            else:
                to_battery =  diff
                battery_capacity = f'BATTERY_CAPACITY_{method}'
                df_to_ffill = df.loc[:i].copy()
                df_to_ffill[battery_capacity] = df_to_ffill[battery_capacity].ffill()
                df.update(df_to_ffill)
                df.at[i, battery_capacity] += to_battery
                scenario.battery(df.at[i, battery_capacity], i)


def add_simulation_data():
    df = get_and_clean_raw_data()
    db.session.commit()

    bo3 = Scenario(method_name=BO3)
    db.session.commit()

    ms3 = Scenario(method_name=MS3)
    db.session.commit()

    df = add_method_ms3_data(df, ms3)
    db.session.commit()

    df = add_method_bo3_data(df, bo3)

    db.session.commit()

    for i in [bo3, ms3]:
        run_simulations(df, scenario=i)
    db.session.commit()
