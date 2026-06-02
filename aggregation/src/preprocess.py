import pandas as pd


def to_monthly(df: pd.DataFrame, signal_columns: list[str]) -> pd.DataFrame:
    result = df.copy()

    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["date"])

    result["date"] = result["date"].dt.to_period("M").dt.to_timestamp()

    agg_dict = {}

    for col in signal_columns:
        if col in result.columns:
            agg_dict[col] = "mean"

    if not agg_dict:
        return result[["date"]].drop_duplicates()

    monthly = (
        result.groupby("date", as_index=False)
        .agg(agg_dict)
    )

    return monthly


def merge_module_signals(module_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    monthly_tables = []

    if "M1" in module_data:
        monthly_tables.append(
            to_monthly(module_data["M1"], ["M1_signal"])
        )

    if "M2" in module_data:
        monthly_tables.append(
            to_monthly(module_data["M2"], ["M2_signal"])
        )

    if "M3" in module_data:
        monthly_tables.append(
            to_monthly(module_data["M3"], ["M3_signal"])
        )

    if "M4" in module_data:
        monthly_tables.append(
            to_monthly(module_data["M4"], ["Seasonal_Factor", "Tax_Week_Flag"])
        )

    if "M5" in module_data:
        monthly_tables.append(
            to_monthly(module_data["M5"], ["M5_signal"])
        )

    if not monthly_tables:
        raise ValueError("Нет данных модулей для агрегации")

    result = monthly_tables[0]

    for table in monthly_tables[1:]:
        result = result.merge(table, on="date", how="outer")

    result = result.sort_values("date").reset_index(drop=True)

    return result


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    # Если какой-то модуль отсутствует, создаём нейтральную колонку
    for col in ["M1_signal", "M2_signal", "M3_signal", "M5_signal"]:
        if col not in result.columns:
            result[col] = 0.0

    # Пропуски в стресс-сигналах считаем отсутствием сигнала
    for col in ["M1_signal", "M2_signal", "M3_signal", "M5_signal"]:
        result[col] = result[col].fillna(0.0)

    # Для сезонного фактора нейтральное значение = 1.0
    if "Seasonal_Factor" not in result.columns:
        result["Seasonal_Factor"] = 1.0
    else:
        result["Seasonal_Factor"] = result["Seasonal_Factor"].fillna(1.0)

    # Для налогового флага нейтральное значение = 0
    if "Tax_Week_Flag" not in result.columns:
        result["Tax_Week_Flag"] = 0
    else:
        result["Tax_Week_Flag"] = result["Tax_Week_Flag"].fillna(0)

    return result


def clip_negative_signals(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    # Отрицательные значения не считаем стрессом
    for col in ["M1_signal", "M2_signal", "M3_signal", "M5_signal"]:
        result[col] = result[col].clip(lower=0)

    return result


def limit_date_range(df: pd.DataFrame) -> pd.DataFrame:

    result = df.copy()

    result = result[result["date"] >= "2022-01-01"]
    result = result[result["date"] <= "2026-12-31"]

    return result.reset_index(drop=True)


def build_aggregation_dataset(module_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    merged = merge_module_signals(module_data)
    merged = fill_missing_values(merged)
    merged = clip_negative_signals(merged)
    merged = limit_date_range(merged)

    columns = [
        "date",
        "M1_signal",
        "M2_signal",
        "M3_signal",
        "M5_signal",
        "Seasonal_Factor",
        "Tax_Week_Flag",
    ]

    return merged[columns]