from typing import Dict
import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd

def create_line_chart(df:pd.DataFrame, title: str, x_axis_title, y_axis_title: str) -> plot:
    """
    Create a Plotly line chart

    Args:
        title (str): Title of the chart.
        y_axis_title (str): Title for the Y-axis.

    Returns:
        str: HTML div element containing the Plotly chart.
    """
    df_reset = df.reset_index()
    df_long = df_reset.melt(id_vars=['index'], value_vars=df.columns, var_name='Series', value_name='Values')
    fig = px.line(df_long, x='index', y='Values', color='Series')
    fig.update_layout(
        title=title,
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title
    )
    return plot(fig, output_type='div', include_plotlyjs=False)

