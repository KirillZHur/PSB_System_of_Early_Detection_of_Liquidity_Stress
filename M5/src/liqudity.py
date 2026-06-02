import pandas as pd
import re
import os

URL = (
    "https://www.cbr.ru/hd_base/"
    "bliquidity/"
    "?UniDbQuery.Posted=True"
    "&UniDbQuery.From=01.01.2010"
    "&UniDbQuery.To=31.12.2030"
)


def clean_number(value):
    if pd.isna(value):
        return None

    value_str = str(value).strip()
    if isinstance(value, (int, float)):
        return value

    value_str = re.sub(r'\s+', '', value_str)
    value_str = value_str.replace(',', '.')

    try:
        return float(value_str)
    except ValueError:
        return None


def load_liquidity():
    """Загружает таблицу с сайта ЦБ РФ"""
    tables = pd.read_html(URL, thousands=' ', decimal=',')

    df = tables[0]
    print("Исходные данные (первые 5 строк):")
    print(df.head())

    return df


def liquidity_to_monthly(df):
    df.columns = [str(c).strip() for c in df.columns]

    date_col = df.columns[0]
    value_col = df.columns[1]

    df = df.rename(columns={date_col: "date", value_col: "liquidity_raw"})

    df["date"] = pd.to_datetime(df["date"], dayfirst=True)

    df["liquidity_balance"] = df["liquidity_raw"].apply(clean_number)

    # Месячная группировка
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.sort_values("date")
        .groupby("month")
        .tail(1)[["month", "liquidity_balance"]]
        .reset_index(drop=True)
    )

    return monthly

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    raw_df = load_liquidity()

    monthly_liquidity = liquidity_to_monthly(raw_df.copy())

    monthly_liquidity.to_csv("data/bliquidity.csv", index=False)
