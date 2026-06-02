import re
import logging
from datetime import datetime
from typing import Union, Optional

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
