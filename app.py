import streamlit as st
import pandas as pd
import numpy as np

YANDEX_PHONE = "133133133133"


@st.cache_data
def load_data(file) -> pd.DataFrame:
    """Читает CSV в формате orderTable, приводит числа и даты."""
    df = pd.read_csv(file, sep=";", encoding="utf-8-sig")

    # Приводим числовые колонки
    num_cols = [
        "Поступило на бокс",
        "Оплачено деньгами",
        "Оплачено бонусами",
        "Начислено кешбека",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("\u00a0", " ", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Даты / время
    df["Дата оплаты"] = pd.to_datetime(df["Дата оплаты"], errors="coerce")
    df["date"] = df["Дата оплаты"].dt.date
    df["hour"] = df["Дата оплаты"].dt.hour
    df["weekday"] = df["Дата оплаты"].dt.weekday

    # Итоговый чек
    df["total"] = df.get("Оплачено деньгами", 0) + df.get("Оплачено бонусами", 0)

    # Ключ мойки (Партнёр | Автомойка | Адрес)
    df["Партнёр"] = df["Партнёр"].fillna("")
    df["Автомойка"] = df["Автомойка"].fillna("")
    df["Адрес"] = df["Адрес"].fillna("")
    df["wash_key"] = df["Партнёр"] + " | " + df["Автомойка"] + " | " + df["Адрес"]

    return df


def main():
    st.set_page_config(page_title="Carwash Dashboard", layout="wide")
    st.title("Дашборд по автомойкам (orderTable)")

    st.sidebar.header("Настройки данных")

    # Загрузка одного или нескольких CSV
    uploaded_files = st.sidebar.file_uploader(
        "Загрузите один или несколько CSV-файлов `orderTable`",
        type=["csv"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        st.info("Загрузите хотя бы один CSV-файл, чтобы увидеть дашборд.")
        st.stop()

    # Выбор текущего файла для анализа
    file_labels = [f.name for f in uploaded_files]
    selected_label = st.sidebar.selectbox("Выберите файл", file_labels)
    selected_file = next(f for f in uploaded_files if f.name == selected_label)

    df = load_data(selected_file)

    st.sidebar.markdown("---")
    st.sidebar.header("Фильтры")

    # Диапазон дат
    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range = st.sidebar.date_input(
        "Диапазон дат",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple):
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    # Исключить Яндекс
    exclude_yandex = st.sidebar.checkbox(
        "Исключить Яндекс (133133133133)", value=True
    )

    filtered = df.copy()
    if exclude_yandex:
        filtered = filtered[
            filtered["Телефон"].astype(str).str.strip() != YANDEX_PHONE
        ]

    # Фильтры по партнёру / автомойке / адресу
    partners = sorted(
        [p for p in filtered["Партнёр"].dropna().unique().tolist() if p]
    )
    partner_sel = st.sidebar.multiselect("Партнёр", partners)

    washes = sorted(
        [w for w in filtered["Автомойка"].dropna().unique().tolist() if w]
    )
    wash_sel = st.sidebar.multiselect("Автомойка", washes)

    addresses = sorted(
        [a for a in filtered["Адрес"].dropna().unique().tolist() if a]
    )
    addr_sel = st.sidebar.multiselect("Адрес", addresses)

    # Применяем фильтр по дате
    mask = (filtered["date"] >= start_date) & (filtered["date"] <= end_date)

    if partner_sel:
        mask &= filtered["Партнёр"].isin(partner_sel)
    if wash_sel:
        mask &= filtered["Автомойка"].isin(wash_sel)
    if addr_sel:
        mask &= filtered["Адрес"].isin(addr_sel)

    filtered = filtered[mask]

    st.caption(
        f"Текущий файл: **{selected_label}**, записей после фильтров: **{len(filtered)}**"
    )

    if filtered.empty:
        st.warning("По выбранным фильтрам нет данных.")
        st.stop()

    # --- KPI-блок ---
    st.subheader("Общие показатели")

    unique_clients = (
        filtered["Телефон"].astype(str).str.strip().nunique()
    )
    unique_washes_partner_addr = (
        filtered[["Партнёр", "Адрес"]]
        .dropna(subset=["Адрес"])
        .drop_duplicates()
        .shape[0]
    )

    total_cash = filtered["Оплачено деньгами"].sum()
    total_bonus = filtered["Оплачено бонусами"].sum()
    total_sum = filtered["total"].sum()
    cashback_sum = filtered["Начислено кешбека"].sum()

    avg_check = filtered["total"].mean()
    median_check = filtered["total"].median()
    bonus_share = total_bonus / total_sum * 100 if total_sum > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Уникальные клиенты",
        f"{unique_clients:,}".replace(",", " "),
    )
    col2.metric(
        "Уникальные мойки (Партнёр+Адрес)",
        f"{unique_washes_partner_addr}",
    )
    col3.metric(
        "Всего операций",
        f"{len(filtered):,}".replace(",", " "),
    )
    col4.metric(
        "Средний чек (₽)",
        f"{avg_check:,.2f}".replace(",", " "),
    )

    col5, col6, col7, col8 = st.columns(4)
    col5.metric(
        "Итоговая сумма (₽)",
        f"{total_sum:,.0f}".replace(",", " "),
    )
    col6.metric(
        "Оплачено деньгами (₽)",
        f"{total_cash:,.0f}".replace(",", " "),
    )
    col7.metric(
        "Оплачено бонусами (₽)",
        f"{total_bonus:,.0f}".replace(",", " "),
    )
    col8.metric("Доля бонусов (%)", f"{bonus_share:.2f}")

    st.markdown(
        f"**Медианный чек:** {median_check:.2f} ₽ &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"**Сумма кешбека:** {cashback_sum:,.0f} ₽".replace(",", " ")
    )

    # --- Динамика по дням ---
    st.markdown("---")
    st.subheader("Динамика по дням")

    daily = (
        filtered.groupby("date")
        .agg(
            orders=("№", "count"),
            revenue=("Поступило на бокс", "sum"),
        )
        .reset_index()
        .sort_values("date")
    )

    col_d1, col_d2 = st.columns(2)
    col_d1.line_chart(
        daily.set_index("date")["orders"], use_container_width=True
    )
    col_d1.caption("Количество заказов по дням")

    col_d2.line_chart(
        daily.set_index("date")["revenue"], use_container_width=True
    )
    col_d2.caption("Выручка по дням (Поступило на бокс)")

    # --- Топ мойки ---
    st.markdown("---")
    st.subheader("Топ‑мойки")

    top_wash = (
        filtered.groupby("wash_key")
        .agg(
            orders=("№", "count"),
            revenue=("Поступило на бокс", "sum"),
            avg_check=("Поступило на бокс", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    st.markdown("**Топ‑10 моек по выручке:**")
    st.dataframe(
        top_wash.head(10).rename(
            columns={
                "wash_key": "Партнёр | Автомойка | Адрес",
                "orders": "Заказов",
                "revenue": "Выручка",
                "avg_check": "Ср. чек",
            }
        ),
        use_container_width=True,
    )

    # --- Выбросы ---
    st.markdown("---")
    st.subheader("Выбросы по сумме чека")

    amounts = filtered["total"].values
    q1 = np.percentile(amounts, 25)
    q3 = np.percentile(amounts, 75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    outliers = filtered[filtered["total"] > upper]

    st.markdown(
        f"Q1 = {q1:.2f} ₽, Q3 = {q3:.2f} ₽, порог выброса = {upper:.2f} ₽, "
        f"количество выбросов = {len(outliers)}"
    )

    show_outliers = st.checkbox("Показать таблицу выбросов", value=False)
    if show_outliers and not outliers.empty:
        st.dataframe(
            outliers[
                [
                    "Дата оплаты",
                    "Телефон",
                    "Клиент",
                    "Партнёр",
                    "Автомойка",
                    "Адрес",
                    "total",
                    "Оплачено деньгами",
                    "Оплачено бонусами",
                ]
            ].sort_values("total", ascending=False),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()