import os
from pathlib import Path

NEDOSPROS_THRESHOLD = 1.2
PERESPROS_THRESHOLD = 2.0
MAD_WINDOW_YEARS = 3

MINFIN_URL_TEMPLATE = "https://minfin.gov.ru/ru/document?id_4=315131-rezultaty_provedennykh_auktionsov_po_razmeshcheniyu_gosudarstvennykh_tsennykh_bumag_v_{year}_godu_na_{date}"

REQUEST_TIMEOUT = 30
REQUEST_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = DATA_DIR / "cache"

for d in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    d.mkdir(exist_ok=True, parents=True)

OUTPUT_CSV = OUTPUT_DIR / "auctions_enriched.csv"
COVER_RATIO_PLOT = OUTPUT_DIR / "cover_ratio.png"
MAD_SCORES_PLOT = OUTPUT_DIR / "mad_scores.png"
