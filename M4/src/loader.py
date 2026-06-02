from pathlib import Path
import pandas as pd
import requests


RAW_DIR = Path("M4/data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

FNS_CALENDAR_URL = "https://www.nalog.gov.ru/rn77/calendar/"


def download_fns_calendar_page() -> Path:
    output_path = RAW_DIR / "fns_calendar_page.html"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(FNS_CALENDAR_URL, headers=headers, timeout=60)
    response.raise_for_status()

    output_path.write_text(response.text, encoding="utf-8")

    return output_path


def build_manual_tax_calendar(
    start_date: str = "2022-01-01",
    end_date: str = "2026-12-31"
) -> pd.DataFrame:

    months = pd.date_range(start_date, end_date, freq="MS")

    rows = []

    for month_start in months:
        year = month_start.year
        month = month_start.month

        tax_date = pd.Timestamp(year=year, month=month, day=28)

        rows.append({
            "tax_date": tax_date,
            "tax_type": "ЕНП / основные налоговые платежи",
            "source": "manual_calendar"
        })

        # конец квартала — усиленный налоговый период
        if month in [3, 6, 9, 12]:
            rows.append({
                "tax_date": tax_date,
                "tax_type": "Квартальные налоговые платежи",
                "source": "manual_calendar"
            })

    df = pd.DataFrame(rows)

    return df


def load_tax_calendar(update: bool = True) -> pd.DataFrame:

    if update:
        try:
            download_fns_calendar_page()
        except Exception as error:
            print(f"Не удалось скачать страницу ФНС: {error}")
            print("Продолжаю работу с ручным календарём налоговых дат")

    df = build_manual_tax_calendar()

    output_path = RAW_DIR / "tax_calendar.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    return df