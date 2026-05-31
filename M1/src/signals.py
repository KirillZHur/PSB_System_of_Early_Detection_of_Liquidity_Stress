import numpy as np
import pandas as pd


def rolling_mad_score(
    series: pd.Series,
    window: int = 36,
    min_periods: int = 12
) -> pd.Series:
    rolling_median = series.rolling(
        window=window,
        min_periods=min_periods
    ).median()

    rolling_mad = series.rolling(
        window=window,
        min_periods=min_periods
    ).apply(
        lambda x: np.median(np.abs(x - np.median(x))),
        raw=True
    )

    rolling_mad = rolling_mad.replace(0, np.nan)

    return (series - rolling_median) / rolling_mad


def add_mad_scores(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["MAD_score_spread"] = rolling_mad_score(result["spread"])
    result["MAD_score_RUONIA"] = rolling_mad_score(result["ruonia"])

    return result


def add_end_of_period_flag(df: pd.DataFrame, days_before_end: int = 5) -> pd.DataFrame:
    result = df.copy()

    if "reserve_period_end" not in result.columns:
        result["Flag_EndOfPeriod"] = 1
        return result


    result["Flag_EndOfPeriod"] = result["reserve_period_end"].notna().astype(int)

    return result


def add_m1_signal(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    spread_score = result["MAD_score_spread"].clip(lower=0).fillna(0)
    ruonia_score = result["MAD_score_RUONIA"].clip(lower=0).fillna(0)

    result["M1_signal"] = (
        0.6 * spread_score +
        0.4 * ruonia_score
    )

    result["M1_signal"] = result["M1_signal"].clip(lower=0)

    return result


def build_m1_signals(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    # Убираем периоды, где еще нет фактических данных
    result = result.dropna(subset=["spread"])

    result = add_mad_scores(result)
    result = add_end_of_period_flag(result)
    result = add_m1_signal(result)

    result["module"] = "M1_reserves"

    columns = [
        "date",
        "module",
        "actual_avg_balances",
        "required_reserves",
        "required_reserves_accounts",
        "spread",
        "ruonia",
        "MAD_score_spread",
        "MAD_score_RUONIA",
        "Flag_EndOfPeriod",
        "M1_signal",
    ]

    return result[columns]