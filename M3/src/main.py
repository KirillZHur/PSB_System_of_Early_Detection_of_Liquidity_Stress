import pandas as pd
from datetime import datetime
from config import OUTPUT_CSV, COVER_RATIO_PLOT, MAD_SCORES_PLOT, USE_FALLBACK_DATA
from data_fetcher import fetch_minfin_page
from table_parser import parse_auctions_table
from metrics_calculator import calculate_cover_ratio, calculate_flags, calculate_spread_to_curve
from mad_normalizer import add_mad_scores
from signals_aggregator import get_latest_signals, export_history
from visualizer import plot_cover_ratio, plot_mad_scores
from utils import logger, format_date_for_url, generate_fallback_data

def main():
    year = 2026
    date_for_url = format_date_for_url(datetime(2026, 2, 26))
    
    try:
        logger.info("Попытка загрузить данные с сайта Минфина...")
        html = fetch_minfin_page(year, date_for_url)
        df = parse_auctions_table(html)
        if df.empty:
            raise ValueError("Парсер вернул пустой DataFrame")
        logger.info(f"Загружено строк аукционов: {len(df)}")
    except Exception as e:
        logger.error(f"Не удалось получить данные с сайта: {e}")
        if USE_FALLBACK_DATA:
            logger.info("Использую встроенные тестовые данные из примера задания")
            df = generate_fallback_data()
        else:
            raise
    
    if df.empty:
        logger.error("Нет данных для дальнейшей обработки")
        return
    
    df = calculate_cover_ratio(df)
    df = calculate_spread_to_curve(df)
    df = calculate_flags(df)
    df = add_mad_scores(df)
    
    export_history(df, OUTPUT_CSV)
    
    signals = get_latest_signals(df)
    logger.info(f"Текущие сигналы: {signals}")
    
    plot_cover_ratio(df, COVER_RATIO_PLOT)
    plot_mad_scores(df, MAD_SCORES_PLOT)
    
    logger.info(f"Графики сохранены в {OUTPUT_DIR}")
    logger.info("Обработка успешно завершена")

if __name__ == "__main__":
    main()
