import time

import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin

import warnings
warnings.filterwarnings('ignore')


BASE_URL = (
    "https://roskazna.gov.ru/"
    "finansovye-operacii/"
    "razmeshchenie-sredstv-edinogo-kaznachejskogo-scheta/"
    "razmeshchenie-sredstv-edinogo-kaznachejskogo-scheta-na-bankovskih-depozitah"
)

DOWNLOAD_FOLDER = Path(
    "data/roskazna_xml"
)

DOWNLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

headers = {
    'Host': 'roskazna.gov.ru',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:151.0) Gecko/20100101 Firefox/151.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://www.google.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'TE': 'trailers'
}

def get_xml_links():
    links = []

    for page in range(1, 113):
        print(f"page {page}")

        url = (BASE_URL + f"?page={page}")

        r = requests.get(url, timeout=60,headers=headers, verify=False)
        soup = BeautifulSoup(r.text,"html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if ((("/storage/operation-day-files/" in href) or ("/storage/migrate/roskaznagovru/opd/" in href))
                    and (href.lower().endswith(".xml"))):
                links.append(urljoin("https://roskazna.gov.ru", href))
        print(f"found {len(links)} xml files")
        time.sleep(10)

    return list(set(links))


def download_xmls():
    links = get_xml_links()

    print(f"found {len(links)} xml files")

    with open("./save.txt", "w") as f:
        f.write(json.dumps(links))

    for url in links:
        filename = (url.split("/")[-1])

        filepath = (DOWNLOAD_FOLDER / filename)

        if filepath.exists():
            continue

        try:
            print(f"download {filename}")

            r = requests.get(url, headers=headers, verify=False, timeout=60)

            with open(filepath, "wb") as f:
                f.write(r.content)

            time.sleep(2)
        except Exception as e:
            print(filename, e)


if __name__ == "__main__":
    download_xmls()