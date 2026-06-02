import pandas as pd
from utils import logger

def get_latest_signals(df: pd.DataFrame) -> dict:
    if df.empty:
        logger.warning("DataFrame пуст, сигналы не вычислены")
        return {}
    latest = df.sort_values('date').iloc[-1]
    signals = {
        'MAD_score_cover': latest.get('MAD_score_cover', None),
        'MAD_score_yield_spread': latest.get('MAD_score_yield_spread', None),
        'Flag_Nedospros': bool(latest.get('Flag_Nedospros', False)),
        'Flag_Perespros': bool(latest.get('Flag_Perespros', False)),
        'cover_ratio': latest.get('cover_ratio', None),
        'yield_spread': latest.get('yield_spread', None),
        'date': latest.get('date', None)
    }
    return signals

def export_history(df: pd.DataFrame, path: str) -> None:
    if df.empty:
        return
    cols = ['date', 'cover_ratio', 'Flag_Nedospros', 'Flag_Perespros', 
            'MAD_score_cover', 'yield_spread', 'MAD_score_yield_spread']
    existing = [c for c in cols if c in df.columns]
    df[existing].to_csv(path, index=False)
    logger.info(f"История сигналов сохранена в {path}")
