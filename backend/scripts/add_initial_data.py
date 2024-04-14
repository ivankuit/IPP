import pandas as pd


def add_initial_data() -> None:
    df = pd.read_excel("data/initial_data.xlsx")
    print(df.head())
