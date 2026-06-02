import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
from config import MAD_WINDOW_YEARS
from utils import logger

def rolling_mad_normalize(series: pd.Series, dates: pd.Series, window_years: int = MAD_WINDOW_YEARS) -> pd.Series:
    series = series.copy()
    dates = pd.to_datetime(dates)
    if len(series) != len(dates):
        raise ValueError("Длины series и dates должны совпадать")
    
    df = pd.DataFrame({'value': series, 'date': dates}).sort_values('date').reset_index(drop=True)
    mad_scores = pd.Series(index=df.index, dtype=float)
    
    for idx, current_date in df['date'].items():
        start_date = current_date - DateOffset(years=window_years)
        window = df[(df['date'] >= start_date) & (df['date'] < current_date)]
        if len(window) < 3:
            mad_scores[idx] = np.nan
            continue
        median = window['value'].median()
        mad = (window['value'] - median).abs().median()
        if mad == 0:
            mad = 1e-6
        current_val = df.loc[idx, 'value']
        mad_scores[idx] = (current_val - median) / mad
    
    return mad_scores

def add_mad_scores(df: pd.DataFrame) -> pd.DataFrame:
    if 'cover_ratio' not in df.columns or 'yield_spread' not in df.columns:
        raise ValueError("Не хватает колонок cover_ratio или yield_spread")
    df = df.copy()
    df = df.sort_values('date').reset_index(drop=True)
    df['MAD_score_cover'] = rolling_mad_normalize(df['cover_ratio'], df['date'])
    df['MAD_score_yield_spread'] = rolling_mad_normalize(df['yield_spread'], df['date'])
    return df
