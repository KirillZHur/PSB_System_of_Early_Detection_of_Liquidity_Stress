# Модуль М2 — Аукционы репо ЦБ

Модуль М2 рассчитывает дневной сигнал стресса ликвидности на основе итогов аукционов репо Банка России.

Источники данных:

* SEC REPOXML: `https://www.cbr.ru/secinfo/secinfo.asmx?op=REPOXML`
* Ключевая ставка: `https://www.cbr.ru/hd_base/keyrate/`

Запуск:

```bash
python M2/main.py
```

Выходной файл:

```text
M2/data/processed/m2_repo_signals.csv
```
