from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PLOTS_DIR = Path("M4/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_seasonal_factor(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["date"], df["Seasonal_Factor"], label="Seasonal_Factor")

    ax.set_title("М4: Сезонный фактор налогового периода")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Seasonal_Factor")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    output_path = PLOTS_DIR / "m4_seasonal_factor.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def plot_flags(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["date"], df["Tax_Week_Flag"], label="Tax_Week_Flag")
    ax.plot(df["date"], df["End_of_Month_Flag"], label="End_of_Month_Flag")
    ax.plot(df["date"], df["End_of_Quarter_Flag"], label="End_of_Quarter_Flag")

    ax.set_title("М4: Календарные флаги")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Флаг")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    output_path = PLOTS_DIR / "m4_calendar_flags.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def plot_monthly_average_factor(df: pd.DataFrame) -> Path:
    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        monthly.groupby("month", as_index=False)
        .agg(Seasonal_Factor=("Seasonal_Factor", "mean"))
    )

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(monthly["month"], monthly["Seasonal_Factor"], label="Средний Seasonal_Factor за месяц")

    ax.set_title("М4: Средний сезонный фактор по месяцам")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Средний Seasonal_Factor")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    output_path = PLOTS_DIR / "m4_monthly_seasonal_factor.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def build_m4_plots(df: pd.DataFrame) -> list[Path]:
    paths = [
        plot_seasonal_factor(df),
        plot_flags(df),
        plot_monthly_average_factor(df),
    ]

    return paths