import numpy as np
import pandas as pd
import re

def parse_reserve_period_dates(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["reserve_period_start"] = pd.NaT
    result["reserve_period_end"] = pd.NaT

    pattern = r"(\d{2}\.\d{2}\.\d{4})\s*[—-]\s*(\d{2}\.\d{2}\.\d{4})"

    extracted = result["reserve_period"].astype(str).str.extract(pattern)

    result["reserve_period_start"] = pd.to_datetime(
        extracted[0],
        format="%d.%m.%Y",
        errors="coerce"
    )

    result["reserve_period_end"] = pd.to_datetime(
        extracted[1],
        format="%d.%m.%Y",
        errors="coerce"
    )

    return result

def prepare_reserves(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()

    # В Excel первые строки служебные, данные начинаются с 3-й строки
    df = df.iloc[2:].reset_index(drop=True)

    df = df.rename(columns={
        df.columns[0]: "date",
        df.columns[1]: "actual_avg_balances",
        df.columns[2]: "required_reserves",
        df.columns[3]: "required_reserves_accounts",
        df.columns[9]: "reserve_period",
    })

    df = df[[
        "date",
        "actual_avg_balances",
        "required_reserves",
        "required_reserves_accounts",
        "reserve_period",
    ]]

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["actual_avg_balances", "required_reserves", "required_reserves_accounts"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(" ", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    df["spread"] = df["actual_avg_balances"] - df["required_reserves"]
    df = parse_reserve_period_dates(df)

    return df


def prepare_ruonia(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()

    # Нормализуем названия колонок
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )

    column_map = {}

    for col in df.columns:
        if "Дата ставки" in col:
            column_map[col] = "date"
        elif "Ставка RUONIA" in col:
            column_map[col] = "ruonia"
        elif "Объем сделок RUONIA" in col:
            column_map[col] = "ruonia_volume"

    df = df.rename(columns=column_map)

    if "date" not in df.columns:
        raise ValueError(f"Не найдена колонка даты. Колонки: {list(df.columns)}")

    if "ruonia" not in df.columns:
        raise ValueError(f"Не найдена колонка RUONIA. Колонки: {list(df.columns)}")

    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")

    df["ruonia"] = pd.to_numeric(df["ruonia"], errors="coerce")

    df["ruonia"] = np.where(df["ruonia"] > 100, df["ruonia"] / 100, df["ruonia"])

    if "ruonia_volume" in df.columns:
        df["ruonia_volume"] = pd.to_numeric(df["ruonia_volume"], errors="coerce")

        df["ruonia_volume"] = np.where(
            df["ruonia_volume"] > 10000,
            df["ruonia_volume"] / 100,
            df["ruonia_volume"]
        )
    else:
        df["ruonia_volume"] = np.nan

    df = df.dropna(subset=["date", "ruonia"])
    df = df.sort_values("date")

    return df[["date", "ruonia", "ruonia_volume"]]


def aggregate_ruonia_monthly(ruonia: pd.DataFrame) -> pd.DataFrame:
    df = ruonia.copy()

    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby("month", as_index=False)
        .agg(
            ruonia=("ruonia", "mean"),
            ruonia_volume=("ruonia_volume", "sum"),
        )
        .rename(columns={"month": "date"})
    )

    return monthly


def merge_reserves_with_ruonia(
    reserves: pd.DataFrame,
    ruonia_monthly: pd.DataFrame
) -> pd.DataFrame:
    df = reserves.copy()
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp()

    result = df.merge(
        ruonia_monthly,
        on="date",
        how="left"
    )

    return result