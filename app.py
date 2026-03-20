import streamlit as st
import pandas as pd
import numpy as np

YANDEX_PHONE = "133133133133"
TBANK_PHONE = "71119999991"  # Партнёр Т-Банк, клиент "Т Банк"

CITY_COORDS = {
    "Абакан": (53.721152, 91.442387),
    "Адыгея": (44.61, 40.10),
    "Азнакаево": (54.859808, 53.074533),
    "Азов": (47.112442, 39.423581),
    "Аксай": (47.269804, 39.862615),
    "Алатырь": (54.839816, 46.572195),
    "Альметьевск": (54.901383, 52.297113),
    "Анапа": (44.8939, 37.3175),
    "Астрахань": (46.3497, 48.0408),
    "Бакал": (54.2253, 58.8155),
    "Балаково": (52.0278, 47.8007),
    "Балашиха": (55.8094, 37.9581),
    "Барнаул": (53.3606, 83.7636),
    "Беляевка": (51.82, 55.30),
    "Благодарный": (45.1033, 43.4369),
    "Брянск": (53.2521, 34.3717),
    "Бугульма": (54.5363, 52.7894),
    "Буденновск": (44.7844, 44.1658),
    "Винсады": (44.16, 43.10),
    "Владимир": (56.1296, 40.4066),
    "Волгоград": (48.7194, 44.5018),
    "Волжский": (48.7858, 44.7639),
    "Воронеж": (51.6720, 39.1843),
    "Ворсма": (55.9903, 43.2722),
    "Гуково": (48.0482, 39.9328),
    "Евпатория": (45.2000, 33.3583),
    "Заречный": (53.1961, 45.1692),
    "Зеленодольск": (55.8444, 48.5174),
    "Ижевск": (56.8498, 53.2045),
    "Иркутск": (52.2978, 104.2964),
    "Казань": (55.7887, 49.1221),
    "Калининград": (54.7104, 20.5109),
    "Канск": (56.2019, 95.7175),
    "Карагали": (46.39, 48.14),
    "Керчь": (45.3561, 36.4674),
    "Киржач": (56.1489, 38.8631),
    "Ковров": (56.3556, 41.3172),
    "Коломна": (55.0794, 38.7783),
    "Кольчугино": (56.3328, 39.3911),
    "Копейск": (55.1172, 61.6282),
    "Королёв": (55.9162, 37.8545),
    "Костерево": (55.93, 39.62),
    "Красногорск": (55.8315, 37.3305),
    "Краснодар": (45.0353, 38.9753),
    "Краснообск": (54.92, 82.99),
    "Красноярск": (56.0153, 92.8932),
    "Крымск": (44.9294, 37.9911),
    "Куровское": (55.5789, 38.9167),
    "Лакинск": (56.0183, 39.9497),
    "Ликино-Дулево": (55.7083, 38.9550),
    "Лосино-Петровский": (55.8714, 38.2006),
    "Луховицы": (54.9653, 39.0258),
    "Магнитогорск": (53.4186, 58.9794),
    "Майкоп": (44.6083, 40.1053),
    "Мамадыш": (55.7167, 51.4167),
    "Маркс": (51.7042, 46.7528),
    "Матвеев-курган": (47.5675, 38.8669),
    "Махачкала": (42.9849, 47.5047),
    "Меленки": (55.3342, 41.6342),
    "Минеральные Воды": (44.2108, 43.1353),
    "Михайловка": (50.0703, 43.2378),
    "Михайловск": (45.1283, 42.0289),
    "Мичуринск": (52.8928, 40.4936),
    "Моршанск": (53.4436, 41.8106),
    "Москва": (55.7558, 37.6173),
    "Муром": (55.5725, 42.0511),
    "Мыски": (53.7125, 87.8014),
    "Наро-Фоминск": (55.3878, 36.7325),
    "Невинномысск": (44.6333, 41.9444),
    "Нефтекамск": (56.0880, 54.2483),
    "Нижнекамск": (55.6366, 51.8244),
    "Нижний Новгород": (56.2965, 43.9361),
    "Новоалтайск": (53.3917, 83.9364),
    "Новокузнецк": (53.7557, 87.1098),
    "Новокуйбышевск": (53.0992, 49.9461),
    "Новороссийск": (44.7235, 37.7685),
    "Новосибирск": (55.0084, 82.9357),
    "Новочеркасск": (47.4116, 40.0938),
    "Обь": (54.99, 82.71),
    "Орел": (52.9651, 36.0705),
    "Оренбург": (51.7682, 55.0970),
    "Орехово-Зуево": (55.8039, 38.9619),
    "Орск": (51.2047, 58.5667),
    "Отрадный": (53.3667, 51.3500),
    "Пекша": (56.12, 40.55),
    "Пенза": (53.2001, 45.0000),
    "Петропавловск-Камчатский": (53.0377, 158.6550),
    "Петушки": (55.9297, 39.4656),
    "Пушкино": (56.0106, 37.8472),
    "Ростов-на-Дону": (47.2357, 39.7015),
    "Руза": (55.6986, 36.1953),
    "Рузаевка": (54.0614, 44.9489),
    "Самара": (53.1959, 50.1002),
    "Самара южное шоссе 3в": (53.1959, 50.1002),
    "Санкт-Петербург": (59.9343, 30.3351),
    "Саранск": (54.1875, 45.1749),
    "Саратов": (51.5924, 46.0342),
    "Сергиев Посад": (56.3000, 38.1333),
    "Симферополь": (44.9481, 34.1042),
    "Славянск-на-Кубани": (45.2558, 37.5797),
    "Смоленск": (54.7818, 32.0401),
    "Собинка": (55.9878, 40.0167),
    "Соль-Илецк": (51.1667, 54.9833),
    "Сочи": (43.5855, 39.7231),
    "Стерлитамак": (53.6246, 55.9502),
    "Судогда": (55.9522, 40.8625),
    "Сургут": (61.2500, 73.4167),
    "Таганрог": (47.2362, 38.8964),
    "Тверь": (56.8587, 35.9176),
    "Темрюк": (45.2706, 37.3872),
    "Тольятти": (53.5303, 49.3461),
    "Торжок": (57.0433, 34.9622),
    "Туапсе": (44.1056, 39.0800),
    "Тула": (54.1961, 37.6182),
    "Улан-Удэ": (51.8344, 107.5846),
    "Ульяновск": (54.3282, 48.3866),
    "Уссурийск": (43.8023, 131.9469),
    "Уфа": (54.7431, 55.9678),
    "Ухта": (63.5671, 53.6834),
    "Чегем": (43.5667, 43.5833),
    "Челябинск": (55.1644, 61.4368),
    "Череповец": (59.1333, 37.9000),
    "Шатура": (55.5728, 39.5364),
    "Шаховская": (56.0283, 35.5083),
    "Шахты": (47.7085, 40.2144),
    "Электросталь": (55.7896, 38.4467),
    "Элиста": (46.3077, 44.2558),
    "Юрьев-Польский": (56.5031, 39.6831),
    "Ярославль": (57.6299, 39.8737),
    "п. Бугры": (60.07, 30.37),
    "пгт. Краснобродский": (54.16, 86.39),
    "пос. Свердловский": (55.87, 38.05),
    "с. Юровка": (45.04, 37.30),
    "ст. Ивановская": (45.26, 38.98),
}


_CATEGORY_COLS = ["Партнёр", "Автомойка", "Адрес", "wash_key", "Город", "Тип оплаты"]


@st.cache_data
def load_data(file) -> pd.DataFrame:
    """Читает CSV в формате orderTable, приводит числа и даты."""
    if hasattr(file, "seek"):
        file.seek(0)
    df = pd.read_csv(file, sep=";", encoding="utf-8-sig", dtype=str)

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

    df["Дата оплаты"] = pd.to_datetime(df["Дата оплаты"], errors="coerce")
    df["date"] = df["Дата оплаты"].dt.date
    df["hour"] = df["Дата оплаты"].dt.hour
    df["weekday"] = df["Дата оплаты"].dt.weekday
    df["month"] = df["Дата оплаты"].dt.to_period("M").astype(str)

    df["total"] = df.get("Оплачено деньгами", 0) + df.get("Оплачено бонусами", 0)

    df["Партнёр"] = df["Партнёр"].fillna("")
    df["Автомойка"] = df["Автомойка"].fillna("")
    df["Адрес"] = df["Адрес"].fillna("")
    df["wash_key"] = df["Партнёр"] + " | " + df["Автомойка"] + " | " + df["Адрес"]

    for col in _CATEGORY_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


_DEDUP_COLS = ["Телефон", "Дата оплаты", "Автомойка", "Поступило на бокс"]


@st.cache_data
def merge_and_deduplicate(files) -> pd.DataFrame:
    """Объединяет несколько CSV в один DataFrame с дедупликацией."""
    frames = []
    for f in files:
        part = load_data(f)
        part["_source_file"] = f.name
        frames.append(part)
    merged = pd.concat(frames, ignore_index=True)

    before = len(merged)
    existing = [c for c in _DEDUP_COLS if c in merged.columns]
    if existing:
        merged = merged.drop_duplicates(subset=existing, keep="first")
    after = len(merged)
    merged.attrs["dedup_removed"] = before - after

    for col in _CATEGORY_COLS:
        if col in merged.columns:
            merged[col] = merged[col].astype("category")
    return merged


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
    """Категоризирует по телефону: Яндекс, Т-Банк или Лейка (всё остальное)."""
    phone_normalized = normalize_phone(phone)
    if phone_normalized == YANDEX_PHONE:
        return "Яндекс"
    if phone_normalized == TBANK_PHONE:
        return "Т-Банк"
    return "Лейка"


def get_period_label(df):
    """Определяет период анализа из данных и возвращает строку для отображения."""
    if df.empty or "date" not in df.columns:
        return None
    
    dates = df["date"].dropna()
    if dates.empty:
        return None
    
    # Преобразуем date в datetime для работы с периодами
    dates_dt = pd.to_datetime(dates)
    
    # Определяем основной месяц (самый частый месяц в данных)
    months = dates_dt.dt.to_period("M")
    main_month = months.mode()
    
    if len(main_month) > 0:
        month_period = main_month[0]
        # Форматируем: "ноябрь 2024"
        month_names = {
            1: "январь", 2: "февраль", 3: "март", 4: "апрель",
            5: "май", 6: "июнь", 7: "июль", 8: "август",
            9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"
        }
        month_name = month_names[month_period.month]
        year = month_period.year
        return f"{month_name} {year}"
    
    # Если не удалось определить основной месяц, показываем диапазон
    min_date = dates.min()
    max_date = dates.max()
    if min_date == max_date:
        return min_date.strftime("%d.%m.%Y")
    else:
        return f"{min_date.strftime('%d.%m.%Y')} - {max_date.strftime('%d.%m.%Y')}"


def group_transactions_to_visits(df, time_window_minutes=30):
    """
    Группирует транзакции одного клиента в визиты.
    Транзакции одного клиента в пределах time_window_minutes считаются одним визитом.
    Векторизованная реализация через groupby + diff (~100-500x быстрее iterrows).
    """
    empty_result = pd.DataFrame(columns=[
        "visit_id", "visit_total", "Оплачено деньгами",
        "Оплачено бонусами", "Поступило на бокс", "Телефон", "Дата оплаты",
    ])
    if df.empty or "Дата оплаты" not in df.columns or "Телефон" not in df.columns:
        return empty_result

    df_work = df.dropna(subset=["Дата оплаты", "Телефон"]).copy()
    if df_work.empty:
        return empty_result

    df_work = df_work.sort_values(["Телефон", "Дата оплаты"])

    prev_time = df_work.groupby("Телефон")["Дата оплаты"].shift(1)
    gap_minutes = (df_work["Дата оплаты"] - prev_time).dt.total_seconds() / 60
    df_work["visit_id"] = (gap_minutes.isna() | (gap_minutes > time_window_minutes)).cumsum()

    visits = (
        df_work.groupby("visit_id")
        .agg({
            "total": "sum",
            "Оплачено деньгами": "sum",
            "Оплачено бонусами": "sum",
            "Поступило на бокс": "sum",
            "Телефон": "first",
            "Дата оплаты": "first",
        })
        .reset_index()
        .rename(columns={"total": "visit_total"})
    )
    return visits


def calculate_ltv(df):
    """
    Рассчитывает LTV (Lifetime Value) для каждого клиента.
    LTV = сумма всех транзакций клиента за период.
    
    Returns:
        DataFrame с колонками: Телефон, LTV, количество_визитов, количество_транзакций
    """
    if df.empty or "Телефон" not in df.columns or "total" not in df.columns:
        return pd.DataFrame(columns=["Телефон", "LTV", "количество_визитов", "количество_транзакций"])
    
    # Группируем транзакции в визиты
    visits = group_transactions_to_visits(df, time_window_minutes=30)
    
    # Рассчитываем LTV по клиентам (сумма всех визитов клиента)
    ltv_by_client = (
        visits.groupby("Телефон")
        .agg({
            "visit_total": "sum",  # LTV = сумма всех визитов
            "visit_id": "count"    # количество визитов
        })
        .reset_index()
        .rename(columns={"visit_total": "LTV", "visit_id": "количество_визитов"})
    )
    
    # Добавляем количество транзакций для каждого клиента
    transaction_count = (
        df.groupby("Телефон")
        .size()
        .reset_index(name="количество_транзакций")
    )
    
    ltv_by_client = ltv_by_client.merge(transaction_count, on="Телефон", how="left")
    ltv_by_client = ltv_by_client.sort_values("LTV", ascending=False)
    
    return ltv_by_client


def find_bonus_only_phones(df):
    """
    Находит телефоны, которые за весь период оплачивали ТОЛЬКО бонусами
    (сумма «Оплачено деньгами» = 0). Это операторы, владельцы моек или
    разовые реферальные пользователи, искажающие статистику.
    """
    if df.empty or "Телефон" not in df.columns:
        return set()

    wash_only = df[df["Тип оплаты"].astype(str).str.strip() == "Мойка автомобиля"]
    if wash_only.empty:
        return set()

    phone_money = (
        wash_only.groupby("Телефон")["Оплачено деньгами"]
        .sum()
        .reset_index()
    )
    bonus_only = phone_money[phone_money["Оплачено деньгами"] == 0]["Телефон"]
    return set(bonus_only.tolist())


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

    file_labels = [f.name for f in uploaded_files]

    # Режим данных: один файл или объединение всех
    if len(uploaded_files) > 1:
        data_mode = st.sidebar.radio(
            "Режим данных",
            ["Один файл", "Все файлы вместе"],
            index=0,
            key="data_mode",
        )
    else:
        data_mode = "Один файл"

    if data_mode == "Один файл":
        selected_label = st.sidebar.selectbox("Выберите файл", file_labels)
        selected_file = next(f for f in uploaded_files if f.name == selected_label)
        df = load_data(selected_file)
    else:
        df = merge_and_deduplicate(uploaded_files)
        dedup_removed = df.attrs.get("dedup_removed", 0)
        selected_label = f"Объединено {len(uploaded_files)} файлов"
        if dedup_removed > 0:
            st.sidebar.success(f"Дедупликация: удалено {dedup_removed:,} дублей".replace(",", " "))

    # Фильтр по месяцам (доступен всегда, полезен при объединении)
    if "month" in df.columns:
        available_months = sorted(df["month"].dropna().unique())
        if len(available_months) > 1:
            month_sel = st.sidebar.multiselect(
                "Месяцы",
                available_months,
                default=available_months,
                key="month_filter",
            )
            if month_sel and len(month_sel) < len(available_months):
                df = df[df["month"].isin(month_sel)]

    # Сравнение файлов (если загружено больше одного и режим «Один файл»)
    if len(uploaded_files) > 1 and data_mode == "Один файл":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Сравнение файлов")

        compare_file1 = st.sidebar.selectbox(
            "Первый файл (базовый период)",
            file_labels,
            index=0,
            key="compare_file1",
        )
        compare_file2 = st.sidebar.selectbox(
            "Второй файл (сравниваемый период)",
            file_labels,
            index=min(1, len(file_labels) - 1),
            key="compare_file2",
        )

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

            st.session_state['comparison'] = comparison
            st.session_state['compare_names'] = (compare_file1, compare_file2)
    
    # Применяем категоризацию к исходным данным ДО фильтрации
    df = df.assign(
        partner_category=df["Телефон"].apply(categorize_by_phone)
    )
    
    # Отладочная информация (можно убрать после проверки)
    with st.sidebar.expander("🔍 Отладка категоризации", expanded=False):
        st.write(f"**Всего записей:** {len(df)}")
        st.write(f"**Лейка:** {len(df[df['partner_category'] == 'Лейка'])}")
        st.write(f"**Яндекс:** {len(df[df['partner_category'] == 'Яндекс'])}")
        st.write(f"**Т-Банк:** {len(df[df['partner_category'] == 'Т-Банк'])}")
        
        # Показываем примеры нормализованных телефонов
        sample_phones = df["Телефон"].head(10).apply(normalize_phone).unique()
        st.write(f"**Примеры нормализованных телефонов (первые 10):**")
        for phone in sample_phones[:10]:
            st.write(f"- `{phone}`")
        
        # Проверяем, есть ли телефоны партнёров в данных
        all_phones_normalized = df["Телефон"].apply(normalize_phone)
        yandex_count = (all_phones_normalized == YANDEX_PHONE).sum()
        tbank_count = (all_phones_normalized == TBANK_PHONE).sum()
        st.write(f"**Записей с телефоном {YANDEX_PHONE} (Яндекс):** {yandex_count}")
        st.write(f"**Записей с телефоном {TBANK_PHONE} (Т-Банк):** {tbank_count}")

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

    # Исключить Яндекс / Т-Банк
    exclude_yandex = st.sidebar.checkbox(
        "Исключить Яндекс (133133133133)", value=False
    )
    exclude_tbank = st.sidebar.checkbox(
        "Исключить Т-Банк (71119999991)", value=False
    )

    # Находим телефоны, платящие только бонусами (операторы / владельцы моек)
    bonus_only_phones = find_bonus_only_phones(df)
    exclude_bonus_only = st.sidebar.checkbox(
        f"Исключить оплату только бонусами ({len(bonus_only_phones)} тел.)",
        value=False,
        help=(
            "Исключает пользователей, у которых все транзакции оплачены "
            "только бонусами (0₽ деньгами). Обычно это операторы, владельцы "
            "моек или разовые реферальные пользователи."
        ),
    )

    filtered = df.copy()
    if exclude_yandex:
        filtered = filtered[filtered["partner_category"] != "Яндекс"]
    if exclude_tbank:
        filtered = filtered[filtered["partner_category"] != "Т-Банк"]
    if exclude_bonus_only and bonus_only_phones:
        filtered = filtered[~filtered["Телефон"].isin(bonus_only_phones)]

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

    # Определяем период анализа из данных
    period_label = get_period_label(filtered)
    
    # Показываем период анализа на витрине
    if period_label:
        st.info(f"📅 **Период анализа:** {period_label.capitalize()} | Файл: {selected_label} | Записей: **{len(filtered)}**")
    else:
        st.caption(
            f"Текущий файл: **{selected_label}**, записей после фильтров: **{len(filtered)}**"
        )

    if exclude_bonus_only and bonus_only_phones:
        excluded_txs = len(df[df["Телефон"].isin(bonus_only_phones)])
        st.warning(
            f"🔒 **Фильтр активен:** исключено {len(bonus_only_phones)} телефонов "
            f"({excluded_txs:,} транзакций), оплачивающих только бонусами".replace(",", " ")
        )

    if filtered.empty:
        st.warning("По выбранным фильтрам нет данных.")
        st.stop()

    # --- KPI-блок ---
    # Показываем период в заголовке KPI, если он определён
    if period_label:
        st.subheader(f"Общие показатели за {period_label}")
    else:
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

    # ВАЖНО: Средний чек ВСЕГДА считаем БЕЗ Яндекса и Т-Банка, так как для партнёров
    # все транзакции идут с одним телефоном, и визиты считаются неправильно
    filtered_for_avg_check = filtered[
        ~filtered["partner_category"].isin(["Яндекс", "Т-Банк"])
    ]
    
    # Группируем транзакции в визиты (транзакции одного клиента в пределах 30 минут = один визит)
    visits = group_transactions_to_visits(filtered_for_avg_check, time_window_minutes=30)
    
    # Средний чек считаем по визитам, а не по отдельным транзакциям
    avg_check = visits["visit_total"].mean() if len(visits) > 0 else 0.0
    median_check = visits["visit_total"].median() if len(visits) > 0 else 0.0
    
    # Для сравнения показываем также средний чек по транзакциям (старый способ)
    avg_check_by_transactions = filtered["total"].mean()
    
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
    # Показываем средний чек по визитам с информацией о количестве визитов
    num_visits = len(visits)
    num_transactions = len(filtered_for_avg_check)
    col4.metric(
        "Средний чек (₽)",
        f"{avg_check:,.2f}".replace(",", " "),
        help=f"По визитам БЕЗ Яндекс и Т-Банк (визитов: {num_visits:,}, транзакций: {num_transactions:,})"
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
    tbank_total = filtered.loc[
        filtered["partner_category"] == "Т-Банк", "Поступило на бокс"
    ].sum()
    
    # Отладочная информация
    leyka_count = len(filtered[filtered["partner_category"] == "Лейка"])
    yandex_count = len(filtered[filtered["partner_category"] == "Яндекс"])
    tbank_count = len(filtered[filtered["partner_category"] == "Т-Банк"])
    
    col_partner1, col_partner2, col_partner3 = st.columns(3)
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
    col_partner3.metric(
        "Выручка Т-Банк (₽)",
        f"{tbank_total:,.0f}".replace(",", " "),
        help=f"Записей: {tbank_count}"
    )

    # --- Операции по партнёрам (база для сервисного сбора) ---
    # Только «Мойка автомобиля» — исключаем подписки (покупка/продление кешбэка)
    is_wash = filtered["Тип оплаты"].astype(str).str.strip() == "Мойка автомобиля"

    ops_leyka = int((is_wash & (filtered["partner_category"] == "Лейка")).sum())
    ops_yandex = int((is_wash & (filtered["partner_category"] == "Яндекс")).sum())
    ops_tbank = int((is_wash & (filtered["partner_category"] == "Т-Банк")).sum())
    ops_subscriptions = int((~is_wash).sum())

    col_ops1, col_ops2, col_ops3 = st.columns(3)
    col_ops1.metric(
        "Операций Лейка",
        f"{ops_leyka:,}".replace(",", " "),
        help=(
            f"Только оплаты за мойку (без подписок). "
            f"Визитов: {num_visits:,} | Ср. транзакций за визит: {ops_leyka / num_visits:.1f}"
            if num_visits > 0 else "Нет визитов"
        ),
    )
    col_ops2.metric(
        "Операций Яндекс",
        f"{ops_yandex:,}".replace(",", " "),
    )
    col_ops3.metric(
        "Операций Т-Банк",
        f"{ops_tbank:,}".replace(",", " "),
    )
    if ops_subscriptions > 0:
        st.caption(
            f"Не учтено подписок (покупка/продление кешбэка): **{ops_subscriptions:,}**".replace(",", " ")
        )

    # --- DAU / WAU / MAU (только Лейка) ---
    st.markdown("---")
    st.subheader("📊 DAU / WAU / MAU (пользователи Лейки)")

    leyka_data = filtered[filtered["partner_category"] == "Лейка"].copy()
    leyka_data["phone_norm"] = leyka_data["Телефон"].apply(normalize_phone)

    if not leyka_data.empty and "date" in leyka_data.columns:
        all_dates = sorted(leyka_data["date"].dropna().unique())

        # DAU: уникальные телефоны в каждый день
        dau_series = (
            leyka_data.groupby("date")["phone_norm"]
            .nunique()
            .reindex(all_dates)
            .fillna(0)
            .astype(int)
        )

        # WAU: скользящее окно 7 дней (предагрегация — O(days) вместо O(days×rows))
        phone_dates = leyka_data[["phone_norm", "date"]].drop_duplicates()
        wau_values = []
        date_phones = phone_dates.groupby("date")["phone_norm"].apply(set).to_dict()
        for d in all_dates:
            d_pd = pd.Timestamp(d)
            window_start = (d_pd - pd.Timedelta(days=6)).date()
            phones_in_window = set()
            for wd in all_dates:
                if window_start <= wd <= d and wd in date_phones:
                    phones_in_window |= date_phones[wd]
            wau_values.append(len(phones_in_window))
        wau_series = pd.Series(wau_values, index=all_dates)

        # MAU: все уникальные за весь период
        mau = leyka_data["phone_norm"].nunique()

        # Средние значения за период
        avg_dau = dau_series.mean()
        avg_wau = wau_series.mean()

        col_au1, col_au2, col_au3 = st.columns(3)
        col_au1.metric(
            "Среднее DAU",
            f"{avg_dau:,.0f}".replace(",", " "),
            help="Среднее число уникальных платящих пользователей Лейки в день"
        )
        col_au2.metric(
            "Среднее WAU",
            f"{avg_wau:,.0f}".replace(",", " "),
            help="Среднее число уникальных пользователей за скользящие 7 дней"
        )
        col_au3.metric(
            "MAU",
            f"{mau:,}".replace(",", " "),
            help="Уникальные платящие пользователи Лейки за весь период"
        )

        # Stickiness: DAU/MAU, WAU/MAU
        stickiness_dau = avg_dau / mau * 100 if mau > 0 else 0
        stickiness_wau = avg_wau / mau * 100 if mau > 0 else 0
        st.markdown(
            f"**Stickiness:** DAU/MAU = {stickiness_dau:.1f}% &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"WAU/MAU = {stickiness_wau:.1f}%"
        )

        # График DAU + WAU по дням
        au_chart = pd.DataFrame({"DAU": dau_series, "WAU": wau_series})
        st.line_chart(au_chart, use_container_width=True)
        st.caption("DAU (ежедневные) и WAU (скользящие 7 дней) — уникальные платящие пользователи Лейки")
    else:
        st.info("Недостаточно данных для расчёта DAU/WAU/MAU.")

    # --- Карта активных пользователей Лейки по городам ---
    st.markdown("---")
    st.subheader("🗺️ Активные пользователи Лейки по городам")

    if not leyka_data.empty:
        leyka_data["city"] = leyka_data["Адрес"].fillna("").str.split(",").str[0].str.strip()
        city_users = (
            leyka_data.groupby("city")["phone_norm"]
            .nunique()
            .reset_index()
            .rename(columns={"phone_norm": "users"})
            .sort_values("users", ascending=False)
        )
        city_users = city_users[city_users["city"] != ""]

        # Добавляем координаты
        city_users["lat"] = city_users["city"].map(lambda c: CITY_COORDS.get(c, (None, None))[0])
        city_users["lon"] = city_users["city"].map(lambda c: CITY_COORDS.get(c, (None, None))[1])
        city_with_coords = city_users.dropna(subset=["lat", "lon"])

        # Таблица топ-15 городов + скачивание полного списка
        all_cities_display = city_users[["city", "users"]].rename(
            columns={"city": "Город", "users": "Уникальных пользователей"}
        )
        st.markdown("**Топ-15 городов по уникальным пользователям:**")
        st.dataframe(all_cities_display.head(15), use_container_width=True, hide_index=True)

        csv_all_cities = all_cities_display.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            label=f"📥 Скачать все города ({len(all_cities_display)})",
            data=csv_all_cities,
            file_name="active_users_by_city.csv",
            mime="text/csv",
        )

        # Карта
        if not city_with_coords.empty:
            # st.map ожидает latitude/longitude
            map_data = city_with_coords[["lat", "lon", "users"]].copy()
            map_data = map_data.rename(columns={"lat": "latitude", "lon": "longitude"})
            st.map(map_data, size="users", use_container_width=True)
            st.caption(
                f"Размер точки — количество уникальных пользователей. "
                f"Городов на карте: {len(city_with_coords)} из {len(city_users)}"
            )

        # Города без координат
        missing = city_users[city_users["lat"].isna()]["city"].tolist()
        if missing:
            with st.expander(f"⚠️ Города без координат ({len(missing)})", expanded=False):
                for c in missing:
                    st.write(f"- {c}")
    else:
        st.info("Нет данных для отображения карты.")

    # --- Подписки (FranchisingGroup) ---
    # Фильтруем записи с партнёром FranchisingGroup (учитываем возможные варианты написания)
    subscription_mask = filtered["Партнёр"].astype(str).str.strip().str.lower().str.contains("franchisinggroup", case=False, na=False)
    subscription_data = filtered[subscription_mask]
    
    # Используем "Оплачено деньгами" для суммы подписок
    subscription_total = subscription_data["Оплачено деньгами"].sum()
    subscription_unique_clients = subscription_data["Телефон"].astype(str).str.strip().nunique()
    subscription_count = len(subscription_data)
    
    # Отладочная информация
    unique_partners = filtered["Партнёр"].astype(str).str.strip().unique()
    franchising_partners = [p for p in unique_partners if "franchisinggroup" in str(p).lower()]
    
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
    
    # Показываем отладочную информацию, если сумма = 0
    if subscription_total == 0 and subscription_count == 0:
        with st.expander("🔍 Отладка: почему подписки = 0?", expanded=False):
            st.write(f"**Найдено записей с FranchisingGroup:** {subscription_count}")
            st.write(f"**Уникальные партнёры в данных:** {len(unique_partners)}")
            if franchising_partners:
                st.write(f"**Партнёры, содержащие 'franchisinggroup':** {franchising_partners}")
            else:
                st.write("**Партнёры, содержащие 'franchisinggroup':** не найдено")
                st.write("**Примеры партнёров в данных (первые 10):**")
                for partner in unique_partners[:10]:
                    st.write(f"- `{partner}`")

    # --- LTV (Lifetime Value) клиентов ---
    st.markdown("---")
    st.subheader("💰 LTV клиентов (Lifetime Value)")
    
    # Рассчитываем LTV для всех клиентов
    ltv_data = calculate_ltv(filtered)
    
    if len(ltv_data) > 0:
        avg_ltv = ltv_data["LTV"].mean()
        median_ltv = ltv_data["LTV"].median()
        total_clients_with_ltv = len(ltv_data)
        
        col_ltv1, col_ltv2, col_ltv3 = st.columns(3)
        col_ltv1.metric(
            "Средний LTV (₽)",
            f"{avg_ltv:,.2f}".replace(",", " "),
            help=f"Среднее значение LTV всех клиентов"
        )
        col_ltv2.metric(
            "Медианный LTV (₽)",
            f"{median_ltv:,.2f}".replace(",", " "),
            help=f"Медианное значение LTV всех клиентов"
        )
        col_ltv3.metric(
            "Клиентов с транзакциями",
            f"{total_clients_with_ltv:,}".replace(",", " "),
            help=f"Количество уникальных клиентов"
        )
        
        # Топ-10 клиентов по LTV (исключаем Яндекс, Т-Банк и клиентов только с бонусами)
        # Фильтруем партнёрские телефоны (Яндекс, Т-Банк)
        partner_phones = {YANDEX_PHONE, TBANK_PHONE}
        ltv_data_filtered = ltv_data[
            ~ltv_data["Телефон"].apply(normalize_phone).isin(partner_phones)
        ].copy()
        
        # Исключаем клиентов, которые оплачивают только бонусами (владельцы/операторы)
        # Проверяем, есть ли у клиента хотя бы одна транзакция с оплатой деньгами
        clients_with_cash = (
            filtered.groupby("Телефон")["Оплачено деньгами"]
            .sum()
            .reset_index()
        )
        clients_with_cash = clients_with_cash[
            clients_with_cash["Оплачено деньгами"] > 0
        ]["Телефон"].tolist()
        
        # Оставляем только клиентов, у которых есть оплата деньгами
        ltv_data_filtered = ltv_data_filtered[
            ltv_data_filtered["Телефон"].isin(clients_with_cash)
        ].copy()
        
        st.markdown("**Топ-10 клиентов по LTV (без Яндекс, Т-Банк и только бонусных):**")
        top_10_ltv = ltv_data_filtered.head(10).copy()
        top_10_ltv_display = top_10_ltv.copy()
        top_10_ltv_display["LTV_formatted"] = top_10_ltv_display["LTV"].apply(lambda x: f"{x:,.2f}".replace(",", " "))
        top_10_ltv_display = top_10_ltv_display.rename(columns={
            "Телефон": "Телефон",
            "LTV_formatted": "LTV (₽)",
            "количество_визитов": "Визитов",
            "количество_транзакций": "Транзакций"
        })
        st.dataframe(
            top_10_ltv_display[["Телефон", "LTV (₽)", "Визитов", "Транзакций"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Недостаточно данных для расчета LTV.")

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
    st.subheader("Динамика выручки по партнёрам")

    partner_daily = (
        filtered[filtered["partner_category"].isin(["Лейка", "Яндекс", "Т-Банк"])]
        .groupby(["date", "partner_category"])
        .agg(revenue=("Поступило на бокс", "sum"))
        .reset_index()
    )

    if partner_daily.empty:
        st.info("Нет данных по выбранным фильтрам для партнёров Лейка, Яндекс и Т-Банк.")
    else:
        # График 1: Лейка vs Яндекс (сопоставимые масштабы ~сотни тыс ₽)
        leyka_yandex_daily = partner_daily[
            partner_daily["partner_category"].isin(["Лейка", "Яндекс"])
        ]
        if not leyka_yandex_daily.empty:
            lya_pivot = (
                leyka_yandex_daily.pivot(
                    index="date", columns="partner_category", values="revenue"
                )
                .fillna(0)
                .sort_index()
            )
            st.line_chart(lya_pivot, use_container_width=True)
            st.caption("Лейка и Яндекс — выручка по дням (Поступило на бокс)")

        # График 2: Т-Банк отдельно (масштаб в тысячах ₽, иначе линия сливается с осью)
        tbank_daily = partner_daily[partner_daily["partner_category"] == "Т-Банк"]
        if not tbank_daily.empty:
            all_dates = sorted(filtered["date"].dropna().unique())
            tbank_by_date = (
                tbank_daily.groupby("date")["revenue"]
                .sum()
                .reindex(all_dates)
                .fillna(0)
            )
            st.line_chart(tbank_by_date, use_container_width=True)
            st.caption("Т-Банк — выручка по дням (отдельный график из-за меньшего масштаба)")

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