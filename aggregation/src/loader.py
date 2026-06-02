from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


MODULE_PATHS = {
    "M1": PROJECT_ROOT / "M1/data/processed/m1_reserves_signals.csv",
    "M2": PROJECT_ROOT / "M2/data/processed/m2_repo_signals_demo.csv",
    "M3": PROJECT_ROOT / "M3/src/output/auctions_enriched.csv",
    "M4": PROJECT_ROOT / "M4/data/processed/m4_tax_seasonality_signals.csv",
    "M5": PROJECT_ROOT / "M5/output/treasury_stress.csv",
}


def _load_csv_if_exists(path: Path, module_name: str) -> pd.DataFrame | None:
    if not path.exists():
        print(f"[WARN] Файл для {module_name} не найден: {path}")
        return None

    df = pd.read_csv(path)

    if "date" not in df.columns:
        if "Дата" in df.columns:
            df = df.rename(columns={"Дата": "date"})
        elif "auction_date" in df.columns:
            df = df.rename(columns={"auction_date": "date"})
        elif "month" in df.columns:
            df = df.rename(columns={"month": "date"})
        else:
            print(f"[WARN] В файле {module_name} не найдена колонка date")
            return None

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    return df


def load_m1() -> pd.DataFrame | None:
    df = _load_csv_if_exists(MODULE_PATHS["M1"], "M1")
    if df is None:
        return None

    return df[["date", "M1_signal"]].copy()


def load_m2() -> pd.DataFrame | None:
    df = _load_csv_if_exists(MODULE_PATHS["M2"], "M2")
    if df is None:
        return None

    if "M2_signal" not in df.columns:
        print("[WARN] В M2 нет колонки M2_signal")
        return None

    return df[["date", "M2_signal"]].copy()


def load_m3() -> pd.DataFrame | None:
    df = _load_csv_if_exists(MODULE_PATHS["M3"], "M3")
    if df is None:
        return None

    if "M3_signal" in df.columns:
        signal_col = "M3_signal"
    elif "stress_signal" in df.columns:
        signal_col = "stress_signal"
    elif "MAD_score_cover" in df.columns:
        signal_col = "MAD_score_cover"
    else:
        print("[WARN] В M3 не найдена колонка сигнала")
        return None

    result = df[["date", signal_col]].copy()
    result = result.rename(columns={signal_col: "M3_signal"})

    return result


def load_m4() -> pd.DataFrame | None:
    df = _load_csv_if_exists(MODULE_PATHS["M4"], "M4")
    if df is None:
        return None

    needed = ["date", "Seasonal_Factor", "Tax_Week_Flag"]
    existing = [col for col in needed if col in df.columns]

    return df[existing].copy()


def load_m5() -> pd.DataFrame | None:
    df = _load_csv_if_exists(MODULE_PATHS["M5"], "M5")

    if df is None:
        return None

    if "M5_signal" in df.columns:
        signal_col = "M5_signal"
    elif "MAD_score_Roskazna" in df.columns:
        signal_col = "MAD_score_Roskazna"
    elif "MAD_score_CBR" in df.columns:
        signal_col = "MAD_score_CBR"
    else:
        print(f"[WARN] В M5 не найдена колонка сигнала. Колонки: {list(df.columns)}")
        return None

    result = df[["date", signal_col]].copy()
    result = result.rename(columns={signal_col: "M5_signal"})
    result["M5_signal"] = result["M5_signal"].fillna(0.0)

    return result


def load_all_module_signals() -> dict[str, pd.DataFrame]:
    loaders = {
        "M1": load_m1,
        "M2": load_m2,
        "M3": load_m3,
        "M4": load_m4,
        "M5": load_m5,
    }

    result = {}

    for name, loader in loaders.items():
        df = loader()
        if df is not None:
            result[name] = df
            print(f"[OK] {name}: {df.shape}")

    return result