import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from config import COVER_RATIO_PLOT, MAD_SCORES_PLOT, NEDOSPROS_THRESHOLD, PERESPROS_THRESHOLD
from utils import logger

def plot_cover_ratio(df: pd.DataFrame, save_path: str = None):
    if df.empty or 'cover_ratio' not in df.columns:
        logger.warning("Нет данных для графика cover_ratio")
        return
    df = df.sort_values('date')
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['cover_ratio'], marker='o', linestyle='-', linewidth=1.5, label='Cover Ratio')
    
    plt.axhline(y=NEDOSPROS_THRESHOLD, color='red', linestyle='--', label=f'Недоспрос ({NEDOSPROS_THRESHOLD})')
    plt.axhline(y=PERESPROS_THRESHOLD, color='green', linestyle='--', label=f'Переспрос ({PERESPROS_THRESHOLD})')
    
    y_min, y_max = plt.ylim()
    plt.fill_between(df['date'], NEDOSPROS_THRESHOLD, y_min, where=(df['cover_ratio'] <= NEDOSPROS_THRESHOLD),
                     color='red', alpha=0.2, label='Зона недоспроса')
    plt.fill_between(df['date'], PERESPROS_THRESHOLD, y_max, where=(df['cover_ratio'] >= PERESPROS_THRESHOLD),
                     color='green', alpha=0.2, label='Зона переспроса')
    
    plt.title('Cover Ratio ОФЗ во времени')
    plt.xlabel('Дата аукциона')
    plt.ylabel('Cover Ratio (спрос/предложение)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        logger.info(f"График cover_ratio сохранён в {save_path}")
    else:
        plt.show()
    plt.close()

def plot_mad_scores(df: pd.DataFrame, save_path: str = None):
    if df.empty:
        return
    df = df.sort_values('date')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    if 'MAD_score_cover' in df.columns:
        ax1.plot(df['date'], df['MAD_score_cover'], marker='o', color='blue')
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.axhline(y=2, color='red', linestyle='--', alpha=0.5)
        ax1.axhline(y=-2, color='red', linestyle='--', alpha=0.5)
        ax1.set_title('MAD-нормализация Cover Ratio')
        ax1.set_ylabel('MAD score')
        ax1.grid(True)
    
    if 'MAD_score_yield_spread' in df.columns:
        ax2.plot(df['date'], df['MAD_score_yield_spread'], marker='s', color='orange')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.axhline(y=2, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(y=-2, color='red', linestyle='--', alpha=0.5)
        ax2.set_title('MAD-нормализация спреда доходности')
        ax2.set_ylabel('MAD score')
        ax2.grid(True)
    
    plt.xlabel('Дата аукциона')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        logger.info(f"График MAD scores сохранён в {save_path}")
    else:
        plt.show()
    plt.close()
