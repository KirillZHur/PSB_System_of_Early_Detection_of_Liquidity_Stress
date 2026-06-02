import pandas as pd


def build_daily_calendar(
    start_date: str = "2022-01-01",
    end_date: str = "2026-12-31"
) -> pd.DataFrame:
    dates = pd.date_range(start_date, end_date, freq="D")

    df = pd.DataFrame({
        "date": dates
    })

    return df


def add_tax_week_flag(
    calendar_df: pd.DataFrame,
    tax_df: pd.DataFrame,
    days_before: int = 7,
    days_after: int = 7
) -> pd.DataFrame:
    result = calendar_df.copy()

    result["Tax_Week_Flag"] = 0

    for tax_date in tax_df["tax_date"].unique():
        start = tax_date - pd.Timedelta(days=days_before)
        end = tax_date + pd.Timedelta(days=days_after)

        mask = (
            (result["date"] >= start) &
            (result["date"] <= end)
        )

        result.loc[mask, "Tax_Week_Flag"] = 1

    return result


def add_end_of_month_flag(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["End_of_Month_Flag"] = (
        result["date"].dt.is_month_end
    ).astype(int)

    return result


def add_end_of_quarter_flag(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["End_of_Quarter_Flag"] = (
        result["date"].dt.is_quarter_end
    ).astype(int)

    return result


def build_preprocessed_calendar(
    tax_df: pd.DataFrame
) -> pd.DataFrame:
    calendar = build_daily_calendar()

    calendar = add_tax_week_flag(calendar, tax_df)
    calendar = add_end_of_month_flag(calendar)
    calendar = add_end_of_quarter_flag(calendar)

    return calendar