import re
import logging
from datetime import datetime, timedelta
from typing import Union, Optional
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ofz_module")

def clean_number(value: Union[str, float, int, None]) -> Optional[float]:
    if value is None or value == "" or value == "-":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^\d,\-\.]", "", str(value).strip())
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        logger.warning(f"Не удалось преобразовать число: {value}")
        return None

def parse_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    logger.warning(f"Неизвестный формат даты: {date_str}")
    return None

def format_date_for_url(date_obj: datetime) -> str:
    return date_obj.strftime("%d.%m.%Y")

def safe_divide(a, b, default=None):
    try:
        if b is None or float(b) == 0:
            return default
        return a / b
    except (TypeError, ValueError):
        return default

def generate_fallback_data() -> pd.DataFrame:
    """Создаёт тестовые данные из примера задания, чтобы графики гарантированно строились."""
    data = {
        'date': [
            datetime(2026, 1, 14), datetime(2026, 1, 14),
            datetime(2026, 1, 21), datetime(2026, 1, 21),
            datetime(2026, 1, 28), datetime(2026, 1, 28)
        ],
        'format': ['Аукцион', 'Аукцион', 'Аукцион', 'Аукцион', 'Аукцион', 'Аукцион'],
        'code': ['26253RMFS', '26225RMFS', '26228RMFS', '26230RMFS', '26254RMFS', '26235RMFS'],
        'bond_type': ['ОФЗ-ПД'] * 6,
        'maturity_date': [datetime(2038,10,6), datetime(2034,5,10), datetime(2030,4,10),
                          datetime(2039,3,16), datetime(2040,10,3), datetime(2031,3,12)],
        'days_to_maturity': [4648, 3038, 1540, 4802, 5362, 1869],
        'offer_volume': [674231.1, 43860.6, 100000.0, 88953.9, 921781.0, 100000.0],
        'cut_price': [91.4983, 66.3191, 79.8112, 61.6841, 90.6718, 70.0000],
        'avg_price': [91.5200, 66.3382, 79.8785, 61.7155, 90.7655, 70.0004],
        'cut_yield': [14.99, 14.80, 14.66, 14.71, 15.07, 14.89],
        'avg_yield': [14.99, 14.80, 14.64, 14.71, 15.07, 14.89],
        'total_demand': [44396.3, 25897.1, 56940.6, 74557.8, 77644.7, 46170.6],
        'placement_volume': [13460.9, 13651.9, 14949.8, 50860.7, 59568.8, 18894.1],
        'revenue': [12726.9, 9211.0, 12251.9, 32601.5, 56168.3, 13635.2]
    }
    df = pd.DataFrame(data)
    return df
