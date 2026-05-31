from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

import pandas as pd
import requests


RAW_DIR = Path("M2/data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SEC_REPO_URL = "https://www.cbr.ru/secinfo/secinfo.asmx"
KEYRATE_URL = "https://www.cbr.ru/hd_base/keyrate/"


def _build_headers() -> dict[str, str]:
    return {"User-Agent": "Mozilla/5.0"}


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _element_to_record(element: ET.Element) -> dict[str, str]:
    record: dict[str, str] = {}

    for key, value in element.attrib.items():
        record[_strip_ns(key)] = value

    for child in element:
        tag = _strip_ns(child.tag)

        if list(child):
            nested_record = _element_to_record(child)
            for nested_key, nested_value in nested_record.items():
                record[f"{tag}_{nested_key}"] = nested_value
            continue

        record[tag] = (child.text or "").strip()

    return record


def _extract_repeating_record_elements(root: ET.Element) -> list[ET.Element]:
    grouped: dict[str, list[ET.Element]] = {}

    for element in root.iter():
        children = [child for child in element if isinstance(child.tag, str)]
        if len(children) < 3:
            continue

        leaf_children = [child for child in children if not list(child)]
        if len(leaf_children) < max(3, len(children) // 2):
            continue

        grouped.setdefault(_strip_ns(element.tag), []).append(element)

    if not grouped:
        raise ValueError("Не удалось выделить строки с результатами аукционов из XML")

    _, elements = max(grouped.items(), key=lambda item: len(item[1]))
    return elements


def parse_repo_xml(xml_text: str) -> pd.DataFrame:
    root = ET.fromstring(xml_text)
    row_elements = _extract_repeating_record_elements(root)
    records = [_element_to_record(element) for element in row_elements]

    if not records:
        raise ValueError("XML репо не содержит записей")

    return pd.DataFrame(records)


def build_repo_soap_envelope(from_date: str, to_date: str) -> str:
    from_dt = datetime.strptime(from_date, "%d.%m.%Y").strftime("%Y-%m-%dT00:00:00")
    to_dt = datetime.strptime(to_date, "%d.%m.%Y").strftime("%Y-%m-%dT00:00:00")

    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <REPOXML xmlns="http://web.cbr.ru/">
      <DateFrom>{from_dt}</DateFrom>
      <DateTo>{to_dt}</DateTo>
    </REPOXML>
  </soap:Body>
</soap:Envelope>"""


def load_repo_from_sec(
    from_date: str = "01.01.2010",
    to_date: str | None = None,
) -> pd.DataFrame:
    if to_date is None:
        to_date = datetime.today().strftime("%d.%m.%Y")

    payload = build_repo_soap_envelope(from_date, to_date)
    headers = _build_headers()
    headers["Content-Type"] = "text/xml; charset=utf-8"
    headers["SOAPAction"] = '"http://web.cbr.ru/REPOXML"'

    response = requests.post(
        SEC_REPO_URL,
        data=payload.encode("utf-8"),
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()

    output_path = RAW_DIR / "repo_sec.xml"
    output_path.write_text(response.text, encoding="utf-8")

    return parse_repo_xml(response.text)


def load_repo_from_local() -> pd.DataFrame:
    file_path = RAW_DIR / "repo_sec.xml"

    if not file_path.exists():
        raise FileNotFoundError("Не найден локальный файл M2/data/raw/repo_sec.xml")

    return parse_repo_xml(file_path.read_text(encoding="utf-8"))


def load_repo(update: bool = True) -> pd.DataFrame:
    if update:
        try:
            return load_repo_from_sec()
        except Exception as error:
            print(f"Не удалось загрузить репо с SEC ЦБ: {error}")
            print("Пробую использовать локальный файл M2/data/raw/repo_sec.xml")

    return load_repo_from_local()


def build_keyrate_url(
    from_date: str = "17.09.2013",
    to_date: str | None = None,
) -> str:
    if to_date is None:
        to_date = datetime.today().strftime("%d.%m.%Y")

    params = {
        "UniDbQuery.Posted": "True",
        "UniDbQuery.From": from_date,
        "UniDbQuery.To": to_date,
    }

    return f"{KEYRATE_URL}?{urlencode(params)}"


def load_keyrate_from_site(
    from_date: str = "17.09.2013",
    to_date: str | None = None,
) -> pd.DataFrame:
    url = build_keyrate_url(from_date, to_date)

    print(f"Загрузка ключевой ставки: {url}")

    tables = pd.read_html(url)
    if not tables:
        raise ValueError("На странице ключевой ставки не найдены таблицы")

    df = max(tables, key=len)

    output_path = RAW_DIR / "keyrate_history.xlsx"
    df.to_excel(output_path, index=False)

    return df


def load_keyrate_from_local() -> pd.DataFrame:
    file_path = RAW_DIR / "keyrate_history.xlsx"

    if not file_path.exists():
        raise FileNotFoundError("Не найден локальный файл M2/data/raw/keyrate_history.xlsx")

    return pd.read_excel(file_path)


def load_keyrate(update: bool = True) -> pd.DataFrame:
    if update:
        try:
            return load_keyrate_from_site()
        except Exception as error:
            print(f"Не удалось загрузить ключевую ставку с сайта ЦБ: {error}")
            print("Пробую использовать локальный файл M2/data/raw/keyrate_history.xlsx")

    return load_keyrate_from_local()
