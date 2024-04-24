import pandas as pd
from flask import Blueprint, render_template

from backend.models import Tag
from backend.scripts.add_simulation_data import Scenario, MS3, BO3
from backend.utils.utils import create_line_chart

page_bp = Blueprint('page', __name__, template_folder='templates')


@page_bp.route('/')
def index():
    return render_template('index.html')


@page_bp.route('/ms3', methods=['GET'])
def ms3():
    scenario = Scenario(method_name=MS3)
    df = Tag.get_data_by_names(scenario.tags)
    df.columns = df.columns.str.replace('_' + MS3, '')
    df_sum = df.sum()

    chart_tags = [t.replace('_' + MS3, '') for t in scenario.chart_tags]
    plot = create_line_chart(df[chart_tags], title='3 Hour Rolling Sum', x_axis_title='Timestamp',
                             y_axis_title='Kilowatts')
    df_sum = df_sum.apply(lambda x: f"{x:,.0f}")
    arguments = df_sum.to_dict()

    return render_template('kpi_dashboard.html', plot_div=plot, method=scenario.model_name, **arguments)


@page_bp.route('/bo3', methods=['GET'])
def bo3():
    scenario = Scenario(method_name=BO3)
    df = Tag.get_data_by_names(scenario.tags)
    df.columns = df.columns.str.replace('_' + BO3, '')
    df_sum = df.sum()
    chart_tags = [t.replace('_' + BO3, '') for t in scenario.chart_tags]
    plot = create_line_chart(df[chart_tags], title='Best of 3 hours method', x_axis_title='Timestamp',
                             y_axis_title='Kilowatts')
    df_sum = df_sum.apply(lambda x: f"{x:,.0f}")
    arguments = df_sum.to_dict()
    return render_template('kpi_dashboard.html', plot_div=plot, method=scenario.model_name, **arguments)

