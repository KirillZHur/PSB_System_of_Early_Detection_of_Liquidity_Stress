import time
import requests
from pathlib import Path
from config import MINFIN_URL_TEMPLATE, REQUEST_TIMEOUT, REQUEST_RETRIES, USER_AGENT, CACHE_DIR
from utils import logger, parse_date, format_date_for_url

def fetch_minfin_page(year: int, date_str: str, use_cache: bool = True) -> str:
    url = MINFIN_URL_TEMPLATE.format(year=year, date=date_str)
    cache_file = CACHE_DIR / f"minfin_{year}_{date_str.replace('.', '_')}.html"
    
    if use_cache and cache_file.exists():
        logger.info(f"Загрузка из кэша: {cache_file}")
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(REQUEST_RETRIES):
        try:
            logger.info(f"Загрузка {url}, попытка {attempt+1}")
            resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            html = resp.text
            if use_cache:
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(html)
            return html
        except Exception as e:
            logger.warning(f"Ошибка загрузки: {e}")
            time.sleep(2)
    raise Exception(f"Не удалось загрузить страницу после {REQUEST_RETRIES} попыток: {url}")

def fetch_cbr_confirmation(url: str) -> str:
    logger.info(f"Загрузка подтверждения с ЦБ: {url}")
    return ""
