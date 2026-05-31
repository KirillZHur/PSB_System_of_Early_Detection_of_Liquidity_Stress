import numpy as np
import pandas as pd


def rolling_mad_score(
    series: pd.Series,
    window: int = 756,
    min_periods: int = 252,
) -> pd.Series:
    rolling_median = series.rolling(
        window=window,
        min_periods=min_periods,
    ).median()

    rolling_mad = series.rolling(
        window=window,
        min_periods=min_periods,
    ).apply(
        lambda x: np.median(np.abs(x - np.median(x))),
        raw=True,
    )

    rolling_mad = rolling_mad.replace(0, np.nan)

    return (series - rolling_median) / rolling_mad


def add_mad_scores(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["MAD_score_cover"] = rolling_mad_score(result["cover_ratio"])
    result["MAD_score_rate_spread"] = rolling_mad_score(result["rate_spread"])
    return result


def add_flags(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["Flag_Demand"] = (result["cover_ratio"] > 2.0).astype(int)
    return result


def add_m2_signal(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    cover_score = result["MAD_score_cover"].clip(lower=0).fillna(0)
    rate_score = result["MAD_score_rate_spread"].clip(lower=0).fillna(0)
    demand_flag = result["Flag_Demand"].fillna(0)

    result["M2_signal"] = 0.5 * cover_score + 0.4 * rate_score + 0.1 * demand_flag
    result["M2_signal"] = result["M2_signal"].clip(lower=0)

    return result


def build_m2_signals(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result = result.dropna(subset=["cover_ratio", "rate_spread"])

    result = add_mad_scores(result)
    result = add_flags(result)
    result = add_m2_signal(result)

    result["module"] = "M2_repo"

    columns = [
        "date",
        "module",
        "term_days",
        "demand_volume",
        "allotted_volume",
        "cover_ratio",
        "cutoff_rate",
        "weighted_rate",
        "key_rate",
        "rate_spread",
        "weighted_rate_spread",
        "MAD_score_cover",
        "MAD_score_rate_spread",
        "Flag_Demand",
        "M2_signal",
    ]

    return result[columns]
