import pandas as pd
from bs4 import BeautifulSoup
from utils import logger, clean_number, parse_date, generate_fallback_data

def parse_auctions_table(html: str) -> pd.DataFrame:
    try:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        if not table:
            table = soup.find("table", text="ДАТА АУКЦИОНА")
        if not table:
            raise ValueError("Таблица не найдена в HTML")
        
        dfs = pd.read_html(str(table), header=0, decimal=',', thousands=' ')
        if not dfs:
            raise ValueError("pandas не смог прочитать таблицу")
        
        df = dfs[0]
        df.columns = [str(col).strip().lower().replace('\n', ' ').replace('  ', ' ') for col in df.columns]
        
        mapping = {
            'дата аукциона': 'date',
            'формат': 'format',
            'код выпуска': 'code',
            'тип бумаги': 'bond_type',
            'дата погашения': 'maturity_date',
            'дней до погашения': 'days_to_maturity',
            'объем предложения': 'offer_volume',
            'цена среднего отсечения': 'cut_price',
            'цена среднего взвешивания': 'avg_price',
            'доходность по цене отсечения': 'cut_yield',
            'доходность по средне-взвешенной цене': 'avg_yield',
            'совокупный объем спроса по номиналу': 'total_demand',
            'объем размещения по номиналу': 'placement_volume',
            'объем выручки': 'revenue'
        }
        df.columns = [col.replace('*', '') for col in df.columns]
        
        result = pd.DataFrame()
        for orig, new in mapping.items():
            if orig in df.columns:
                result[new] = df[orig]
            else:
                found = [c for c in df.columns if orig in c]
                if found:
                    result[new] = df[found[0]]
                else:
                    logger.warning(f"Колонка '{orig}' не найдена, пропускаем")
        
        if 'format' in result.columns:
            result = result[result['format'].astype(str).str.lower() == 'аукцион'].copy()
        
        numeric_cols = ['offer_volume', 'cut_price', 'avg_price', 'cut_yield', 'avg_yield',
                        'total_demand', 'placement_volume', 'revenue', 'days_to_maturity']
        for col in numeric_cols:
            if col in result.columns:
                result[col] = result[col].apply(clean_number)
        
        if 'date' in result.columns:
            result['date'] = result['date'].apply(parse_date)
        if 'maturity_date' in result.columns:
            result['maturity_date'] = result['maturity_date'].apply(parse_date)
        
        if result.empty:
            raise ValueError("После фильтрации не осталось строк")
        
        return result
    except Exception as e:
        logger.error(f"Ошибка парсинга таблицы: {e}. Использую тестовые данные.")
        return generate_fallback_data()
