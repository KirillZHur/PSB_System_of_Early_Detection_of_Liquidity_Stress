from __future__ import annotations

import re

import numpy as np
import pandas as pd


def _normalize_column_name(name: str) -> str:
    value = str(name).lower().replace("\xa0", " ").strip()
    value = value.replace("%", " pct ").replace("№", " no ")
    value = re.sub(r"[^a-zа-я0-9]+", "_", value)
    return value.strip("_")


def _find_column(columns: list[str], patterns: list[str]) -> str | None:
    normalized = {_normalize_column_name(column): column for column in columns}

    for pattern in patterns:
        for normalized_name, original_name in normalized.items():
            if pattern in normalized_name:
                return original_name

    return None


def _to_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("\xa0", "", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def prepare_repo(raw_df: pd.DataFrame, target_term_days: int = 7) -> pd.DataFrame:
    df = raw_df.copy()
    df.columns = [str(column).replace("\xa0", " ").strip() for column in df.columns]

    date_col = _find_column(df.columns.tolist(), [
        "auction_date",
        "date_auction",
        "date",
        "дата",
    ])
    term_col = _find_column(df.columns.tolist(), [
        "term_days",
        "term",
        "days",
        "срок",
    ])
    demand_col = _find_column(df.columns.tolist(), [
        "total_bids_received",
        "bids_received",
        "demand",
        "bid",
        "спрос",
    ])
    allotted_col = _find_column(df.columns.tolist(), [
        "total_amount_allotted",
        "amount_allotted",
        "allotted",
        "заключенных_сделок",
        "размещ",
        "предостав",
    ])
    cutoff_col = _find_column(df.columns.tolist(), [
        "cut_off_rate",
        "cutoff_rate",
        "cutoff",
        "ставка_отсечения",
    ])
    weighted_col = _find_column(df.columns.tolist(), [
        "weighted_repo_rate",
        "weighted_rate",
        "средневзвеш",
    ])

    required_columns = {
        "date": date_col,
        "term_days": term_col,
        "demand_volume": demand_col,
        "allotted_volume": allotted_col,
        "cutoff_rate": cutoff_col,
        "weighted_rate": weighted_col,
    }

    missing = [key for key, value in required_columns.items() if value is None]
    if missing:
        raise ValueError(
            "Не удалось сопоставить колонки репо: "
            f"{missing}. Доступные колонки: {list(df.columns)}"
        )

    df = df.rename(columns={value: key for key, value in required_columns.items()})
    df = df[list(required_columns.keys())].copy()

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    for column in [
        "term_days",
        "demand_volume",
        "allotted_volume",
        "cutoff_rate",
        "weighted_rate",
    ]:
        df[column] = _to_numeric(df[column])

    df = df.dropna(subset=["date", "term_days"])
    df = df.sort_values(["date", "term_days"]).reset_index(drop=True)
    df["term_days"] = df["term_days"].astype(int)

    df = df[df["term_days"] == target_term_days].copy()

    df["cover_ratio"] = np.where(
        df["allotted_volume"] > 0,
        df["demand_volume"] / df["allotted_volume"],
        np.nan,
    )

    return df


def prepare_keyrate(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df.columns = [str(column).replace("\xa0", " ").strip() for column in df.columns]

    date_col = _find_column(df.columns.tolist(), ["date", "дата"])
    keyrate_col = _find_column(df.columns.tolist(), ["rate", "ставка"])

    if date_col is None or keyrate_col is None:
        raise ValueError(
            "Не удалось сопоставить колонки ключевой ставки. "
            f"Доступные колонки: {list(df.columns)}"
        )

    df = df.rename(columns={date_col: "date", keyrate_col: "key_rate"})
    df = df[["date", "key_rate"]].copy()

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df["key_rate"] = _to_numeric(df["key_rate"])

    df = df.dropna(subset=["date", "key_rate"])
    df = df.sort_values("date").reset_index(drop=True)

    return df


def merge_repo_with_keyrate(repo: pd.DataFrame, keyrate: pd.DataFrame) -> pd.DataFrame:
    repo_df = repo.sort_values("date").copy()
    keyrate_df = keyrate.sort_values("date").copy()

    result = pd.merge_asof(
        repo_df,
        keyrate_df,
        on="date",
        direction="backward",
    )

    result["rate_spread"] = result["cutoff_rate"] - result["key_rate"]
    result["weighted_rate_spread"] = result["weighted_rate"] - result["key_rate"]

    return result
