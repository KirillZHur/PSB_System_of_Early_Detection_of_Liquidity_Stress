import numpy as np
import pandas as pd


WEIGHTS = {
    "M1_signal": 0.25,
    "M2_signal": 0.30,
    "M3_signal": 0.20,
    "M5_signal": 0.25,
}


def calculate_weighted_raw_score(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["M1_contribution"] = result["M1_signal"] * WEIGHTS["M1_signal"]
    result["M2_contribution"] = result["M2_signal"] * WEIGHTS["M2_signal"]
    result["M3_contribution"] = result["M3_signal"] * WEIGHTS["M3_signal"]
    result["M5_contribution"] = result["M5_signal"] * WEIGHTS["M5_signal"]

    result["LSI_raw"] = (
        result["M1_contribution"]
        + result["M2_contribution"]
        + result["M3_contribution"]
        + result["M5_contribution"]
    )

    return result


def apply_seasonal_factor(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["LSI_adjusted"] = result["LSI_raw"] * result["Seasonal_Factor"]

    return result


def sigmoid_scale(series: pd.Series) -> pd.Series:
    x = series.fillna(0)

    return 100 / (1 + np.exp(-x))


def calculate_lsi(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result = calculate_weighted_raw_score(result)
    result = apply_seasonal_factor(result)

    result["LSI"] = sigmoid_scale(result["LSI_adjusted"])

    return result


def add_lsi_status(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    def get_status(value: float) -> str:
        if value < 40:
            return "ЗЕЛЁНЫЙ"
        if value < 70:
            return "ЖЁЛТЫЙ"
        return "КРАСНЫЙ"

    result["LSI_status"] = result["LSI"].apply(get_status)

    return result


def calculate_module_contribution_share(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    contribution_cols = [
        "M1_contribution",
        "M2_contribution",
        "M3_contribution",
        "M5_contribution",
    ]

    total = result[contribution_cols].sum(axis=1)

    for col in contribution_cols:
        share_col = col.replace("_contribution", "_share")
        result[share_col] = np.where(total > 0, result[col] / total, 0)

    return result


def build_lsi(df: pd.DataFrame) -> pd.DataFrame:
    result = calculate_lsi(df)
    result = add_lsi_status(result)
    result = calculate_module_contribution_share(result)

    return result