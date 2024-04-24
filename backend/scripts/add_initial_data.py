import contextlib

import pandas as pd
from database import db
from backend.models import Tag, Data, TagTypeEnum, Configuration


def add_initial_data() -> None:
    from database import db
    meta = db.metadata
    with contextlib.closing(db.engine.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()

    df = pd.read_excel("backend/scripts/data/Tech Assessment - G7 Software Developer - Data.xlsx")
    df = df.drop(0)
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df = df.drop(['year', 'month', 'day', 'hour'], axis=1)
    df = df.set_index('datetime')
    df.index.name = 'datetime'
    tags = df.columns.values.tolist()
    df['ACTUAL'] = df['Actual']
    for name in tags:
        tag: Tag = Tag(name=name.upper())
        if name.lower() in ['actual']:
            tag.type = TagTypeEnum.actual
        if name.lower() in ['fsp1', 'fsp2']:
            tag.type = TagTypeEnum.prediction
        db.session.add(tag)

        for index, value in df[tag.name].items():
            if pd.isnull(value):
                continue
            data = Data(tag=tag, value=value, timestamp=index)
            db.session.add(data)

    config:Configuration = Configuration()

    config.sale_value = 1
    config.penalty = 0.2

    config.max_plant_output = 117000
    config.max_sale_output = 100000

    config.battery_capacity = 60000
    config.battery_charge_rate = 20000
    config.batter_discharge_rate = 20000
    db.session.add(config)
    db.session.commit()

