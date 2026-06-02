from pathlib import Path

from src.loader import load_all_module_signals
from src.preprocess import build_aggregation_dataset
from src.aggregator import build_lsi
from src.plot import build_aggregation_plots


PROCESSED_DIR = Path("aggregation/data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    module_data = load_all_module_signals()

    dataset = build_aggregation_dataset(module_data)

    lsi = build_lsi(dataset)

    output_path = PROCESSED_DIR / "lsi_signals.csv"
    lsi.to_csv(output_path, index=False, encoding="utf-8-sig")

    plot_paths = build_aggregation_plots(lsi)

    print("\nLSI:")
    print(lsi.tail())

    print(f"\nCSV сохранён: {output_path}")

    print("\nГрафики сохранены:")
    for path in plot_paths:
        print(path)


if __name__ == "__main__":
    main()