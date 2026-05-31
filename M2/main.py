from pathlib import Path

from src.loader import load_keyrate, load_repo
from src.plot import build_m2_plots
from src.preprocess import (
    merge_repo_with_keyrate,
    prepare_keyrate,
    prepare_repo,
)
from src.signals import build_m2_signals


PROCESSED_DIR = Path("M2/data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    repo_raw = load_repo(update=True)
    keyrate_raw = load_keyrate(update=True)

    repo = prepare_repo(repo_raw)
    keyrate = prepare_keyrate(keyrate_raw)

    merged = merge_repo_with_keyrate(repo, keyrate)
    signals = build_m2_signals(merged)

    output_path = PROCESSED_DIR / "m2_repo_signals.csv"
    signals.to_csv(output_path, index=False, encoding="utf-8-sig")

    plot_paths = build_m2_plots(signals)

    print("M2 signals:")
    print(signals.tail())

    print(f"\nCSV сохранён: {output_path}")

    print("\nГрафики сохранены:")
    for path in plot_paths:
        print(path)


if __name__ == "__main__":
    main()
