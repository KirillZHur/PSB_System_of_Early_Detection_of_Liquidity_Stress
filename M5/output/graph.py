import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

def main():
    output_dir = "treasury_charts"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv('treasury_stress.csv')

    # Преобразуем месяц в datetime
    df['month'] = pd.to_datetime(df['month'])

    # Очищаем числовые колонки от пробелов и запятых
    df['budget_balance'] = df['budget_balance'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float)
    df['liquidity_balance'] = df['liquidity_balance'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float)
    df['budget_delta'] = df['budget_delta'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float)

    # ГРАФИК 1: Приток/Отток средств бюджета
    print("Создание графика 1: Приток/Отток средств бюджета...")

    fig, ax = plt.subplots(figsize=(16, 8))

    colors = df['budget_delta'].apply(lambda x: '#2ecc71' if x > 0 else '#e74c3c' if x < 0 else '#95a5a6')

    bars = ax.bar(df['month'], df['budget_delta'], color=colors, width=20, alpha=0.8, edgecolor='black', linewidth=0.5)

    # Нулевая линия
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

    # Настройка графика
    ax.set_title('Приток/Отток средств бюджета (Δ бюджетных остатков)', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Дата', fontsize=14, fontweight='bold')
    ax.set_ylabel('Изменение (млн ₽)', fontsize=14, fontweight='bold')

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45, ha='right')

    # Добавляем подписи для крупных изменений
    for i, (date, delta) in enumerate(zip(df['month'], df['budget_delta'])):
        if abs(delta) > 15000:
            ax.text(date, delta, f'{delta/1000:.0f}млрд',
                    ha='center', va='bottom' if delta > 0 else 'top',
                    fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_budget_flows.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(os.path.join(output_dir, '01_budget_flows.jpg'), dpi=300, bbox_inches='tight')
    plt.show()

    # ГРАФИК 2: Ground Truth - Структурный баланс ликвидности ЦБ

    fig, ax = plt.subplots(figsize=(16, 8))

    # Линия структурного баланса ликвидности
    ax.plot(df['month'], df['liquidity_balance'], color='#3498db', linewidth=2.5,
            label='Структурный баланс ликвидности', marker='o', markersize=4, markeredgecolor='black', markeredgewidth=0.5)

    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

    # Пороговые линии стресса
    ax.axhline(y=500, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Порог стресса 1 (>500 млрд ₽)')
    ax.axhline(y=1000, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Порог стресса 2 (>1000 млрд ₽)')

    # Закрашиваем зоны стресса
    ax.fill_between(df['month'], 0, df['liquidity_balance'], where=(df['liquidity_balance'] > 500) & (df['liquidity_balance'] <= 1000), color='orange', alpha=0.2, label='Зона повышенного стресса')
    ax.fill_between(df['month'], 0, df['liquidity_balance'], where=(df['liquidity_balance'] > 1000), color='red', alpha=0.2, label='Зона критического стресса')

    ax.set_title('Ground Truth: Структурный баланс ликвидности (данные ЦБ РФ)', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Дата', fontsize=14, fontweight='bold')
    ax.set_ylabel('Дефицит ликвидности (млрд ₽)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_ground_truth_liquidity.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(os.path.join(output_dir, '02_ground_truth_liquidity.jpg'), dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()