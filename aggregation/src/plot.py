from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PLOTS_DIR = Path("aggregation/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_lsi(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))

    # зоны стресса
    ax.axhspan(0, 40, facecolor="green", alpha=0.12, label="Зелёная зона: 0–40")
    ax.axhspan(40, 70, facecolor="yellow", alpha=0.18, label="Жёлтая зона: 40–70")
    ax.axhspan(70, 100, facecolor="red", alpha=0.12, label="Красная зона: 70–100")

    # линии границ зон
    ax.axhline(40, linestyle="--", linewidth=1)
    ax.axhline(70, linestyle="--", linewidth=1)

    # сам индекс поверх зон
    ax.plot(df["date"], df["LSI"], label="LSI", linewidth=2)

    ax.set_title("Liquidity Stress Index (LSI)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("LSI, 0–100")
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    output_path = PLOTS_DIR / "lsi_dynamics.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path

def plot_module_contributions(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.stackplot(
        df["date"],
        df["M1_contribution"],
        df["M2_contribution"],
        df["M3_contribution"],
        df["M5_contribution"],
        labels=["M1", "M2", "M3", "M5"],
        alpha=0.8
    )

    ax.set_title("Вклад модулей в LSI_raw")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Вклад")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    output_path = PLOTS_DIR / "module_contributions.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def plot_lsi_and_seasonality(df: pd.DataFrame) -> Path:
    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.plot(df["date"], df["LSI"], label="LSI")
    ax1.set_xlabel("Дата")
    ax1.set_ylabel("LSI, 0–100")
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(df["date"], df["Seasonal_Factor"], linestyle="--", label="Seasonal_Factor")
    ax2.set_ylabel("Seasonal_Factor")

    ax1.set_title("LSI и сезонный фактор М4")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

    output_path = PLOTS_DIR / "lsi_seasonality.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def build_aggregation_plots(df: pd.DataFrame) -> list[Path]:
    return [
        plot_lsi(df),
        plot_module_contributions(df),
        plot_lsi_and_seasonality(df),
    ]