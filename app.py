import streamlit as st
import pandas as pd
import numpy as np

YANDEX_PHONE = "133133133133"


@st.cache_data
def load_data(file) -> pd.DataFrame:
    """Читает CSV в формате orderTable, приводит числа и даты."""
    # Читаем CSV как строки, чтобы не потерять научную нотацию в телефонах
    df = pd.read_csv(file, sep=";", encoding="utf-8-sig", dtype=str)

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


def normalize_phone(phone) -> str:
    """Нормализует телефон: обрабатывает научную нотацию и убирает все нецифровые символы."""
    phone_str = str(phone).strip()
    
    # Если это NaN или пустая строка
    if phone_str.lower() in ['nan', 'none', '']:
        return ""
    
    # Пытаемся обработать научную нотацию (например, "1.33133e+11" или "1,33133E+11")
    try:
        # Заменяем запятую на точку для десятичных разделителей
        phone_clean = phone_str.replace(",", ".")
        # Пытаемся преобразовать в float, затем в int
        phone_float = float(phone_clean)
        phone_int = int(phone_float)
        return str(phone_int)
    except (ValueError, OverflowError):
        # Если не получилось (не число), убираем все символы кроме цифр
        phone_str = ''.join(filter(str.isdigit, phone_str))
        return phone_str


def categorize_by_phone(phone: str) -> str:
    """Категоризирует по телефону: Яндекс (133133133133) или Лейка (всё остальное)."""
    phone_normalized = normalize_phone(phone)
    if phone_normalized == YANDEX_PHONE:
        return "Яндекс"
    return "Лейка"


def compare_washes(df1, df2, name1, name2):
    """Сравнивает уникальные мойки между двумя датафреймами."""
    washes1 = set(df1["wash_key"].dropna().unique())
    washes2 = set(df2["wash_key"].dropna().unique())
    
    only_in_1 = washes1 - washes2  # Мойки только в первом файле
    only_in_2 = washes2 - washes1  # Мойки только во втором файле
    common = washes1 & washes2      # Общие мойки
    
    return {
        "only_in_1": sorted(only_in_1),
        "only_in_2": sorted(only_in_2),
        "common": sorted(common),
        "count_1": len(washes1),
        "count_2": len(washes2),
        "count_common": len(common),
    }


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

    # Автоматическое сравнение файлов (если загружено больше одного)
    if len(uploaded_files) > 1:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Сравнение файлов")
        
        compare_file1 = st.sidebar.selectbox(
            "Первый файл (базовый период)",
            file_labels,
            index=0,
            key="compare_file1"
        )
        compare_file2 = st.sidebar.selectbox(
            "Второй файл (сравниваемый период)",
            file_labels,
            index=min(1, len(file_labels) - 1),
            key="compare_file2"
        )
        
        # Автоматическое сравнение при загрузке файлов
        if compare_file1 != compare_file2:
            df1_compare = load_data(next(f for f in uploaded_files if f.name == compare_file1))
            df2_compare = load_data(next(f for f in uploaded_files if f.name == compare_file2))
            
            comparison = compare_washes(df1_compare, df2_compare, compare_file1, compare_file2)
            
            st.sidebar.write(f"**{compare_file1}:** {comparison['count_1']} моек")
            st.sidebar.write(f"**{compare_file2}:** {comparison['count_2']} моек")
            st.sidebar.write(f"**Общих моек:** {comparison['count_common']}")
            
            if len(comparison['only_in_1']) > 0:
                st.sidebar.warning(f"⚠️ **Исчезло моек:** {len(comparison['only_in_1'])}")
            if len(comparison['only_in_2']) > 0:
                st.sidebar.info(f"ℹ️ **Появилось моек:** {len(comparison['only_in_2'])}")
            
            # Сохраняем результат сравнения в session state для отображения
            st.session_state['comparison'] = comparison
            st.session_state['compare_names'] = (compare_file1, compare_file2)

    df = load_data(selected_file)
    
    # Применяем категоризацию к исходным данным ДО фильтрации
    df = df.assign(
        partner_category=df["Телефон"].apply(categorize_by_phone)
    )
    
    # Отладочная информация (можно убрать после проверки)
    with st.sidebar.expander("🔍 Отладка категоризации", expanded=False):
        st.write(f"**Всего записей:** {len(df)}")
        st.write(f"**Лейка:** {len(df[df['partner_category'] == 'Лейка'])}")
        st.write(f"**Яндекс:** {len(df[df['partner_category'] == 'Яндекс'])}")
        
        # Показываем примеры нормализованных телефонов
        sample_phones = df["Телефон"].head(10).apply(normalize_phone).unique()
        st.write(f"**Примеры нормализованных телефонов (первые 10):**")
        for phone in sample_phones[:10]:
            st.write(f"- `{phone}`")
        
        # Проверяем, есть ли телефон 133133133133 в данных
        all_phones_normalized = df["Телефон"].apply(normalize_phone)
        yandex_count = (all_phones_normalized == YANDEX_PHONE).sum()
        st.write(f"**Записей с телефоном {YANDEX_PHONE}:** {yandex_count}")

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
        "Исключить Яндекс (133133133133)", value=False
    )

    filtered = df.copy()
    if exclude_yandex:
        filtered = filtered[filtered["partner_category"] != "Яндекс"]

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

    # Выручка по категориям (используем "Поступило на бокс" как в графике)
    leyka_total = filtered.loc[
        filtered["partner_category"] == "Лейка", "Поступило на бокс"
    ].sum()
    yandex_total = filtered.loc[
        filtered["partner_category"] == "Яндекс", "Поступило на бокс"
    ].sum()
    
    # Отладочная информация
    leyka_count = len(filtered[filtered["partner_category"] == "Лейка"])
    yandex_count = len(filtered[filtered["partner_category"] == "Яндекс"])
    
    col_partner1, col_partner2 = st.columns(2)
    col_partner1.metric(
        "Выручка Лейка (₽)",
        f"{leyka_total:,.0f}".replace(",", " "),
        help=f"Записей: {leyka_count}"
    )
    col_partner2.metric(
        "Выручка Яндекс (₽)",
        f"{yandex_total:,.0f}".replace(",", " "),
        help=f"Записей: {yandex_count}"
    )

    # --- Подписки (FranchisingGroup) ---
    # Фильтруем записи с партнёром FranchisingGroup (учитываем возможные варианты написания)
    subscription_mask = filtered["Партнёр"].astype(str).str.strip().str.lower().str.contains("franchisinggroup", case=False, na=False)
    subscription_data = filtered[subscription_mask]
    
    subscription_total = subscription_data["Поступило на бокс"].sum()
    subscription_unique_clients = subscription_data["Телефон"].astype(str).str.strip().nunique()
    subscription_count = len(subscription_data)
    
    st.markdown("---")
    st.subheader("📋 Подписки (FranchisingGroup)")
    col_sub1, col_sub2 = st.columns(2)
    col_sub1.metric(
        "Сумма оплаченных подписок (₽)",
        f"{subscription_total:,.0f}".replace(",", " "),
        help=f"Записей: {subscription_count}"
    )
    col_sub2.metric(
        "Уникальных клиентов с подпиской",
        f"{subscription_unique_clients:,}".replace(",", " "),
        help=f"Количество уникальных телефонов"
    )

    # --- Сравнение файлов (показываем сразу после KPI) ---
    if 'comparison' in st.session_state and 'compare_names' in st.session_state:
        comparison = st.session_state['comparison']
        name1, name2 = st.session_state['compare_names']
        
        # Показываем исчезнувшие мойки сразу, если они есть
        if comparison['only_in_1']:
            st.markdown("---")
            st.error(f"⚠️ **ВНИМАНИЕ: {len(comparison['only_in_1'])} мойка(и) не работают в {name2} по сравнению с {name1}**")
            
            st.subheader(f"❌ Мойки, которые исчезли в {name2}:")
            
            # Показываем в виде таблицы для лучшей читаемости
            missing_washes_df = pd.DataFrame({
                "Партнёр | Автомойка | Адрес": comparison['only_in_1']
            })
            st.dataframe(missing_washes_df, use_container_width=True, hide_index=True)
            
            # Дополнительная статистика
            col_comp1, col_comp2, col_comp3 = st.columns(3)
            col_comp1.metric(f"Моек в {name1}", comparison['count_1'])
            col_comp2.metric(f"Моек в {name2}", comparison['count_2'])
            col_comp3.metric("Общих моек", comparison['count_common'])
        
        # Показываем появившиеся мойки (менее критично)
        if comparison['only_in_2']:
            st.markdown("---")
            st.info(f"ℹ️ **Новые мойки в {name2} ({len(comparison['only_in_2'])}):**")
            new_washes_df = pd.DataFrame({
                "Партнёр | Автомойка | Адрес": comparison['only_in_2']
            })
            st.dataframe(new_washes_df, use_container_width=True, hide_index=True)

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

    st.markdown("---")
    st.subheader("Динамика выручки Лейка vs Яндекс")

    partner_daily = (
        filtered[filtered["partner_category"].isin(["Лейка", "Яндекс"])]
        .groupby(["date", "partner_category"])
        .agg(revenue=("Поступило на бокс", "sum"))
        .reset_index()
    )

    if partner_daily.empty:
        st.info("Нет данных по выбранным фильтрам для партнёров Лейка и Яндекс.")
    else:
        partner_pivot = (
            partner_daily.pivot(
                index="date", columns="partner_category", values="revenue"
            )
            .fillna(0)
            .sort_index()
        )
        st.line_chart(partner_pivot, use_container_width=True)
        st.caption(
            "Сравнение суммарной выручки (Поступило на бокс) по дням для партнёров Лейка и Яндекс."
        )

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