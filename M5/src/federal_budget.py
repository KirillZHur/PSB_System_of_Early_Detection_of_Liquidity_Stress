import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream,*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
}

link = 'https://www.cbr.ru/vfs/statistics/banksector/borrowings/02_29_Budget_all.xlsx'

if __name__ == "__main__":
    r = requests.get(link, headers=headers, timeout=60, verify=False)
    r.raise_for_status()  # Проверка на ошибки HTTP

    with open('data/budget.xlsx', "wb") as f:
        f.write(r.content)
