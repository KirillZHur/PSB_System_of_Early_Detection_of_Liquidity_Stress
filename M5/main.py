import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

from pathlib import Path


BUDGET_FILE = "src/data/budget.xlsx"
ROSKAZNA_FOLDER = "src/data/roskazna_xml"
LIQUIDITY_FILE = "src/data/bliquidity.csv"
OUTPUT_FILE = "output/treasury_stress.csv"

def load_budget_balance(path):
    raw = pd.read_excel(path, header=None)

    dates = raw.iloc[1, 1:]
    values = raw.iloc[2, 1:]

    df = pd.DataFrame({
        "month": pd.to_datetime(dates, format='%d.%m.%Y', errors='coerce'),
        "budget_balance": pd.to_numeric(values, errors="coerce")
    })

    df = df.dropna()
    return df

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    auc = root.find("Depoauc1")

    try:
        return {
            "date": pd.to_datetime(auc.findtext("aucdate"), dayfirst=True),
            "deposit_volume": float(auc.findtext("totalaccept")),
            "banks_count": int(auc.findtext("crbidders"))
        }
    except Exception as e:
        print(e)
        return {
            "date": pd.to_datetime(auc.findtext("aucdate"), dayfirst=True),
            "deposit_volume": float(0),
            "banks_count": int(0)
        }


def load_roskazna_folder(folder):
    rows = []

    for file in Path(folder).glob("*.XML"):
        try:
            rows.append(parse_xml(file))
        except Exception as e:
            print(f"ERROR {file}: {e}")

    return pd.DataFrame(rows)


def aggregate_roskazna_monthly(df):
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby("month")
          .agg(
              deposit_volume=("deposit_volume", "sum"),
              banks_count=("banks_count", "mean")
          )
          .reset_index()
    )

    return monthly

def load_liquidity(path):
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["month"])
    return df[["month", "liquidity_balance"]]

def rolling_mad_score(series, window=36):
    scores = []

    for i in range(len(series)):
        if i < window:
            scores.append(np.nan)
            continue

        history = series.iloc[i-window:i].dropna()
        median = history.median()
        mad = np.median(np.abs(history - median))

        if mad == 0:
            scores.append(0)
            continue

        score = (series.iloc[i] - median) / mad
        scores.append(score)

    return pd.Series(scores, index=series.index)

def build_flag(row):
    budget_delta = row["budget_delta"]
    ros_score = row["MAD_score_Roskazna"]

    if budget_delta <= -500_000 or ros_score <= -2:
        return 2
    if budget_delta <= -300_000 or ros_score <= -1.5:
        return 1
    return 0

def main():
    print("Loading CBR budget...")
    budget = load_budget_balance(BUDGET_FILE)

    print("Loading Roskazna XML...")
    roskazna_raw = load_roskazna_folder(ROSKAZNA_FOLDER)
    roskazna = aggregate_roskazna_monthly(roskazna_raw)

    print("Loading liquidity...")
    liquidity = load_liquidity(LIQUIDITY_FILE)

    print("Merging...")
    df = (
        budget.merge(roskazna, on="month", how="left")
              .merge(liquidity, on="month", how="left")
    )

    df = df.sort_values("month")

    # последние 5 лет
    cutoff = df["month"].max() - pd.DateOffset(years=5)
    df = df[df["month"] >= cutoff].copy()

    df["budget_delta"] = df["budget_balance"].diff()
    df["deposit_delta"] = df["deposit_volume"].diff()

    df["MAD_score_CBR"] = rolling_mad_score(df["budget_delta"])
    df["MAD_score_Roskazna"] = rolling_mad_score(df["deposit_delta"])

    df["Flag_Budget_Drain"] = df.apply(build_flag, axis=1)



    columns = [
        "month",
        "budget_balance",
        "deposit_volume",
        "banks_count",
        "budget_delta",
        "deposit_delta",
        "MAD_score_CBR",
        "MAD_score_Roskazna",
        "liquidity_balance",
        "Flag_Budget_Drain"
    ]

    df = df[columns]
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"Saved -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()