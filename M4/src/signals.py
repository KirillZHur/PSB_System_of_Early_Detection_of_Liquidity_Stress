import pandas as pd


def add_seasonal_factor(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["Seasonal_Factor"] = 1.0

    # налоговая неделя — основной сезонный фактор
    result.loc[result["Tax_Week_Flag"] == 1, "Seasonal_Factor"] += 0.20

    # конец месяца — дополнительное давление
    result.loc[result["End_of_Month_Flag"] == 1, "Seasonal_Factor"] += 0.10

    # конец квартала — усиленный сезонный эффект
    result.loc[result["End_of_Quarter_Flag"] == 1, "Seasonal_Factor"] += 0.10

    # ограничение из ТЗ: 1.0–1.4
    result["Seasonal_Factor"] = result["Seasonal_Factor"].clip(1.0, 1.4)

    result["M4_signal"] = result["Seasonal_Factor"]

    result["module"] = "M4_tax_seasonality"

    return result


def build_m4_signals(df: pd.DataFrame) -> pd.DataFrame:
    result = add_seasonal_factor(df)

    columns = [
        "date",
        "module",
        "Tax_Week_Flag",
        "End_of_Month_Flag",
        "End_of_Quarter_Flag",
        "Seasonal_Factor",
        "M4_signal",
    ]

    return result[columns]