from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PLOTS_DIR = Path("M2/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


STRESS_PERIODS = [
    ("2014-12-01", "2014-12-31", "декабрь 2014"),
    ("2022-02-01", "2022-03-31", "февраль–март 2022"),
    ("2023-08-01", "2023-08-31", "август 2023"),
]


def add_stress_periods(ax):
    for start, end, _label in STRESS_PERIODS:
        ax.axvspan(
            pd.to_datetime(start),
            pd.to_datetime(end),
            alpha=0.15,
        )


def plot_cover_and_rate(df: pd.DataFrame) -> Path:
    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.plot(df["date"], df["cover_ratio"], label="Cover ratio")
    ax1.set_xlabel("Дата")
    ax1.set_ylabel("Cover ratio")

    ax2 = ax1.twinx()
    ax2.plot(df["date"], df["cutoff_rate"], linestyle="--", label="Ставка отсечения")
    ax2.plot(df["date"], df["key_rate"], linestyle=":", label="Ключевая ставка")
    ax2.set_ylabel("Ставка, % годовых")

    add_stress_periods(ax1)

    ax1.set_title("М2: Cover ratio и ставка репо ЦБ")
    ax1.grid(True, alpha=0.3)

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

    output_path = PLOTS_DIR / "m2_cover_rate.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def plot_mad_scores(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["date"], df["MAD_score_cover"], label="MAD_score_cover")
    ax.plot(df["date"], df["MAD_score_rate_spread"], label="MAD_score_rate_spread")

    add_stress_periods(ax)

    ax.set_title("М2: MAD-нормализованные сигналы")
    ax.set_xlabel("Дата")
    ax.set_ylabel("MAD-score")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    output_path = PLOTS_DIR / "m2_mad_scores.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def plot_m2_signal(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["date"], df["M2_signal"], label="M2_signal")
    add_stress_periods(ax)

    ax.set_title("М2: Итоговый сигнал стресса")
    ax.set_xlabel("Дата")
    ax.set_ylabel("M2_signal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    output_path = PLOTS_DIR / "m2_signal.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path


def build_m2_plots(df: pd.DataFrame) -> list[Path]:
    paths = [
        plot_cover_and_rate(df),
        plot_mad_scores(df),
        plot_m2_signal(df),
    ]

    return paths
