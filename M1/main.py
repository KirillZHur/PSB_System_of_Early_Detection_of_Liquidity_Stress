from pathlib import Path

from src.loader import load_reserves, load_ruonia
from src.preprocess import (
    prepare_reserves,
    prepare_ruonia,
    aggregate_ruonia_monthly,
    merge_reserves_with_ruonia,
)
from src.signals import build_m1_signals
from src.plot import build_m1_plots


PROCESSED_DIR = Path("M1/data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    reserves_raw = load_reserves(update=True)
    ruonia_raw = load_ruonia(update=True)

    reserves = prepare_reserves(reserves_raw)
    ruonia = prepare_ruonia(ruonia_raw)
    ruonia_monthly = aggregate_ruonia_monthly(ruonia)

    merged = merge_reserves_with_ruonia(reserves, ruonia_monthly)

    signals = build_m1_signals(merged)

    output_path = PROCESSED_DIR / "m1_reserves_signals.csv"
    signals.to_csv(output_path, index=False, encoding="utf-8-sig")

    plot_paths = build_m1_plots(signals)

    print("M1 signals:")
    print(signals.tail())

    print(f"\nCSV сохранён: {output_path}")

    print("\nГрафики сохранены:")
    for path in plot_paths:
        print(path)


if __name__ == "__main__":
    main()