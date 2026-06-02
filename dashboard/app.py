from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LSI_PATH = PROJECT_ROOT / "aggregation/data/processed/lsi_signals.csv"


st.set_page_config(
    page_title="RU Liquidity Sentinel",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_lsi_data() -> pd.DataFrame:
    df = pd.read_csv(LSI_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")
    return df


def get_status_color(status: str) -> str:
    if status == "ЗЕЛЁНЫЙ":
        return "🟢"
    if status == "ЖЁЛТЫЙ":
        return "🟡"
    return "🔴"


def main():
    st.title("RU Liquidity Sentinel")
    st.caption("Система раннего выявления стресса ликвидности")

    if not LSI_PATH.exists():
        st.error(
            "Файл aggregation/data/processed/lsi_signals.csv не найден. "
            "Сначала запусти: python aggregation/main.py"
        )
        return

    df = load_lsi_data()

    st.sidebar.header("Фильтры")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.sidebar.date_input(
        "Период",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered = df[
            (df["date"].dt.date >= start_date) &
            (df["date"].dt.date <= end_date)
        ]
    else:
        filtered = df.copy()

    latest = filtered.iloc[-1]

    status_icon = get_status_color(latest["LSI_status"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Текущий LSI", f"{latest['LSI']:.1f} / 100")
    col2.metric("Статус", f"{status_icon} {latest['LSI_status']}")
    col3.metric("Seasonal Factor", f"{latest['Seasonal_Factor']:.2f}")
    col4.metric("Tax Week", int(latest["Tax_Week_Flag"]))

    st.divider()

    st.subheader("Динамика Liquidity Stress Index")

    fig_lsi = go.Figure()

    fig_lsi.add_hrect(
        y0=0,
        y1=40,
        fillcolor="green",
        opacity=0.12,
        line_width=0,
        annotation_text="Норма",
        annotation_position="top left"
    )

    fig_lsi.add_hrect(
        y0=40,
        y1=70,
        fillcolor="yellow",
        opacity=0.18,
        line_width=0,
        annotation_text="Напряжение",
        annotation_position="top left"
    )

    fig_lsi.add_hrect(
        y0=70,
        y1=100,
        fillcolor="red",
        opacity=0.12,
        line_width=0,
        annotation_text="Стресс",
        annotation_position="top left"
    )

    fig_lsi.add_trace(
        go.Scatter(
            x=filtered["date"],
            y=filtered["LSI"],
            mode="lines",
            name="LSI"
        )
    )

    fig_lsi.update_layout(
        height=450,
        yaxis_title="LSI, 0–100",
        xaxis_title="Дата",
        yaxis=dict(range=[0, 100])
    )

    st.plotly_chart(fig_lsi, use_container_width=True)

    st.subheader("Вклад модулей в итоговый сигнал")

    contribution_cols = [
        "M1_contribution",
        "M2_contribution",
        "M3_contribution",
        "M5_contribution",
    ]

    contribution_df = filtered[["date"] + contribution_cols].copy()

    fig_contrib = px.area(
        contribution_df,
        x="date",
        y=contribution_cols,
        labels={
            "value": "Вклад",
            "date": "Дата",
            "variable": "Модуль"
        },
        title="Вклад модулей в LSI_raw"
    )

    fig_contrib.update_layout(height=420)
    st.plotly_chart(fig_contrib, use_container_width=True)

    st.subheader("Сигналы модулей")

    signal_cols = [
        "M1_signal",
        "M2_signal",
        "M3_signal",
        "M5_signal",
    ]

    fig_signals = px.line(
        filtered,
        x="date",
        y=signal_cols,
        labels={
            "value": "Сигнал",
            "date": "Дата",
            "variable": "Модуль"
        },
        title="Динамика сигналов M1–M5"
    )

    fig_signals.update_layout(height=420)
    st.plotly_chart(fig_signals, use_container_width=True)

    st.subheader("Сезонный фактор М4")

    fig_season = px.line(
        filtered,
        x="date",
        y="Seasonal_Factor",
        title="Seasonal_Factor во времени",
        labels={
            "date": "Дата",
            "Seasonal_Factor": "Seasonal Factor"
        }
    )

    fig_season.update_layout(height=350)
    st.plotly_chart(fig_season, use_container_width=True)

    st.subheader("Последние значения")

    table_cols = [
        "date",
        "LSI",
        "LSI_status",
        "M1_signal",
        "M2_signal",
        "M3_signal",
        "M5_signal",
        "Seasonal_Factor",
        "Tax_Week_Flag",
    ]

    st.dataframe(
        filtered[table_cols].tail(20),
        use_container_width=True
    )


if __name__ == "__main__":
    main()