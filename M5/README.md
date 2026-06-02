# Модуль М5 — Средства федерального казначейства

## Описание модуля

Модуль отслеживает бюджетный канал движения ликвидности: когда в бюджет поступают крупные платежи, деньги уходят с корсчетов банков на ЕКС — отток ликвидности. Когда казначейство размещает излишки обратно — ликвидность возвращается в систему.

Модуль автоматически собирает данные ЦБ РФ, рассчитывает спред между фактическими остатками и обязательными резервами, выполняет MAD-нормализацию сигналов и формирует итоговые сигналы MAD_score_ЦБ, MAD_score_Росказна, Flag_Budget_Drain.

# Источники данных

### ЦБ РФ — ежемесячные Excel, раздел «Привлечённые средства»

https://www.cbr.ru/vfs/statistics/banksector/borrowings/02_29_Budget_all.xlsx

### Росказна — размещения ЕКС на банковских депозитах (история 3–5 лет):

https://roskazna.gov.ru/finansovye-operacii/razmeshchenie-sredstv-edinogo-kaznachejskogo-scheta/razmeshchenie-sredstv-edinogo-kaznachejskogo-scheta-na-bankovskih-depozitah

### Ground truth для калибровки — таблица «Ликвидность банковского сектора» ЦБ РФ:

https://www.cbr.ru/hd_base/bliquidity/?UniDbQuery.Posted=True&UniDbQuery.From=01.02.2014&UniDbQuery.To=01.06.2026

---

# Структура проекта

```text
M5/
├── output/
│   ├── treasury_charts/
│   ├── treasury_stress.csv
│   └── graph.py
├── src/
│   ├── data/
│   ├── federal_budget.py
│   ├── liquidity.py
│   └── roskazna_downloader.py
├── main.py
└── README.md
```


# Запуск модуля

## Установка зависимостей

```bash
pip install pandas numpy requests matplotlib openpyxl lxml
```

## Запуск

```bash
python M5/main.py
```