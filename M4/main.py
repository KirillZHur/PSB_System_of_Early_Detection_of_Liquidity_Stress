from pathlib import Path

from src.loader import load_tax_calendar
from src.preprocess import build_preprocessed_calendar
from src.signals import build_m4_signals
from src.plot import build_m4_plots


PROCESSED_DIR = Path("M4/data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    tax_calendar = load_tax_calendar(update=True)

    calendar = build_preprocessed_calendar(tax_calendar)

    signals = build_m4_signals(calendar)

    output_path = PROCESSED_DIR / "m4_tax_seasonality_signals.csv"
    signals.to_csv(output_path, index=False, encoding="utf-8-sig")

    plot_paths = build_m4_plots(signals)

    print("M4 SIGNALS:")
    print(signals.tail())

    print("\nSeasonal factor distribution:")
    print(signals["Seasonal_Factor"].value_counts().sort_index())

    print(f"\nCSV сохранён: {output_path}")

    print("\nГрафики сохранены:")
    for path in plot_paths:
        print(path)


if __name__ == "__main__":
    main()