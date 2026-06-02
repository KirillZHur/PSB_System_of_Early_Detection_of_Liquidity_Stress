import pandas as pd
import numpy as np
from config import NEDOSPROS_THRESHOLD, PERESPROS_THRESHOLD
from utils import safe_divide, logger

def calculate_cover_ratio(df: pd.DataFrame) -> pd.DataFrame:
    if 'total_demand' not in df.columns or 'offer_volume' not in df.columns:
        raise ValueError("Не хватает колонок для расчета cover_ratio")
    df = df.copy()
    df['cover_ratio'] = df.apply(lambda row: safe_divide(row['total_demand'], row['offer_volume']), axis=1)
    return df

def calculate_flags(df: pd.DataFrame) -> pd.DataFrame:
    if 'cover_ratio' not in df.columns:
        raise ValueError("Сначала выполните calculate_cover_ratio")
    df = df.copy()
    df['Flag_Nedospros'] = df['cover_ratio'] < NEDOSPROS_THRESHOLD
    df['Flag_Perespros'] = df['cover_ratio'] > PERESPROS_THRESHOLD
    return df

def calculate_spread_to_curve(df: pd.DataFrame, benchmark_curve: pd.DataFrame = None) -> pd.DataFrame:
    if 'avg_yield' not in df.columns:
        raise ValueError("Не хватает колонки avg_yield")
    df = df.copy()
    if benchmark_curve is not None and not benchmark_curve.empty:
        merged = pd.merge(df, benchmark_curve, on='date', how='left')
        df['yield_spread'] = merged['avg_yield'] - merged['benchmark_yield']
    else:
        logger.warning("Бенчмарк-кривая не передана, используется медиана доходности всех аукционов")
        median_yield = df['avg_yield'].median()
        df['yield_spread'] = df['avg_yield'] - median_yield
    return df
