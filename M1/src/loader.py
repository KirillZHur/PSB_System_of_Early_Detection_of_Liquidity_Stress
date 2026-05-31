from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests


RAW_DIR = Path("M1/data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

RESERVES_URL = "https://www.cbr.ru/vfs/hd_base/RReserves/required_reserves_table.xlsx"
RUONIA_DYNAMICS_URL = "https://www.cbr.ru/hd_base/ruonia/dynamics/"


def download_file(url: str, output_path: Path) -> Path:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)

    return output_path


def download_reserves_excel() -> Path:
    output_path = RAW_DIR / "required_reserves_table.xlsx"
    return download_file(RESERVES_URL, output_path)


def load_reserves(update: bool = True) -> pd.DataFrame:
    file_path = RAW_DIR / "required_reserves_table.xlsx"

    if update or not file_path.exists():
        file_path = download_reserves_excel()

    return pd.read_excel(file_path)


def build_ruonia_dynamics_url(
    from_date: str = "11.01.2010",
    to_date: str | None = None
) -> str:
    if to_date is None:
        to_date = datetime.today().strftime("%d.%m.%Y")

    params = {
        "UniDbQuery.Posted": "True",
        "UniDbQuery.From": from_date,
        "UniDbQuery.To": to_date,
    }

    return f"{RUONIA_DYNAMICS_URL}?{urlencode(params)}"


def load_ruonia_from_site(
    from_date: str = "11.01.2010",
    to_date: str | None = None
) -> pd.DataFrame:
    url = build_ruonia_dynamics_url(from_date, to_date)

    print(f"Загрузка RUONIA: {url}")

    tables = pd.read_html(url)

    if not tables:
        raise ValueError("На странице RUONIA не найдены таблицы")

    # Берём самую большую таблицу, обычно это основная таблица RUONIA
    df = max(tables, key=len)

    output_path = RAW_DIR / "ruonia_history_from_site.xlsx"
    df.to_excel(output_path, index=False)

    return df


def load_ruonia_from_local() -> pd.DataFrame:
    file_path = RAW_DIR / "ruonia_history.xlsx"

    if not file_path.exists():
        raise FileNotFoundError(
            "Не найден локальный файл M1/data/raw/ruonia_history.xlsx"
        )

    return pd.read_excel(file_path)


def load_ruonia(update: bool = True) -> pd.DataFrame:
    if update:
        try:
            return load_ruonia_from_site()
        except Exception as error:
            print(f"Не удалось загрузить RUONIA с сайта ЦБ: {error}")
            print("Пробую использовать локальный файл M1/data/raw/ruonia_history.xlsx")

    return load_ruonia_from_local()