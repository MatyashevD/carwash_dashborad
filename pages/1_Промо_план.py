"""Страница Streamlit: генератор промо-плана (RFM → Excel) без AI-токенов."""
from __future__ import annotations

import io
import re

import pandas as pd
import streamlit as st

from city_coords import CITY_COORDS, find_city_coords
from promo_pipeline import PromoConfig, generate_promo_plan, SEGMENT_ORDER, INITIATIVE_RU

st.set_page_config(page_title="Промо-план", page_icon="📊", layout="wide")
st.title("Генератор промо-плана")
st.caption("Загрузите CSV-файлы Лейки (1–3 месяца), выберите партнёра и получите готовый Excel.")

# ---------------------------------------------------------------------------
# Транслитерация для суффикса промокодов
# ---------------------------------------------------------------------------

_TRANSLIT_MAP: dict[str, str] = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l",
    "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s",
    "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch",
    "ш": "sh", "щ": "sh", "ъ": "", "ы": "y", "ь": "", "э": "e",
    "ю": "yu", "я": "ya",
}


def _translit(text: str) -> str:
    result: list[str] = []
    for ch in text:
        low = ch.lower()
        if low in _TRANSLIT_MAP:
            t = _TRANSLIT_MAP[low]
            result.append(t.upper() if ch.isupper() else t)
        else:
            result.append(ch)
    return "".join(result)


def _make_suffix(partner: str, city: str) -> str:
    city_part = _translit(city)[:2].upper() if city else "XX"
    nums = re.findall(r"\d+", partner)
    num_part = nums[0] if nums else ""
    return city_part + num_part


# ---------------------------------------------------------------------------
# Сайдбар: загрузка, выбор, настройки
# ---------------------------------------------------------------------------

st.sidebar.header("1. Загрузка данных")
uploaded = st.sidebar.file_uploader(
    "CSV-файлы Лейки (orderTable)", type=["csv"], accept_multiple_files=True,
)

if not uploaded:
    st.info("Загрузите хотя бы один CSV-файл через боковую панель.")
    st.stop()


def _read_partners(files) -> tuple[list[str], list[str], list[str]]:
    """Быстрый проход по файлам: список партнёров, первые адрес + мойка."""
    partners: set[str] = set()
    addresses: list[str] = []
    washes: list[str] = []
    for f in files:
        f.seek(0)
        try:
            df = pd.read_csv(f, sep=";", encoding="utf-8-sig", dtype=str)
        except Exception:
            continue
        if "Партнёр" in df.columns:
            partners.update(df["Партнёр"].dropna().unique())
        if "Адрес" in df.columns and not addresses:
            addresses = df["Адрес"].dropna().unique().tolist()
        if "Автомойка" in df.columns and not washes:
            washes = df["Автомойка"].dropna().unique().tolist()
    return sorted(partners), addresses, washes


with st.spinner("Чтение CSV…"):
    partners_list, addresses_list, washes_list = _read_partners(uploaded)

if not partners_list:
    st.error("В загруженных файлах нет колонки «Партнёр» или она пуста.")
    st.stop()

st.sidebar.header("2. Выбор партнёра")
selected_partner = st.sidebar.selectbox("Партнёр", partners_list)
partner_regex = re.escape(selected_partner)

# --- Автоопределение города ---
first_addr = ""
for a in addresses_list:
    if a and a.strip():
        first_addr = a.strip()
        break

found = find_city_coords(first_addr)
default_city = found[0] if found else (first_addr.split(",")[0].strip() if first_addr else "")

st.sidebar.header("3. Настройки")
city = st.sidebar.text_input("Город", value=default_city)
address_short = ""
if first_addr:
    parts = first_addr.split(",")
    if len(parts) >= 2:
        address_short = f"на {parts[1].strip()}"
address_short = st.sidebar.text_input("Локация для push (напр. «на Светлогорской»)", value=address_short)

sfx = _make_suffix(selected_partner, city)
promo_suffix = st.sidebar.text_input("Суффикс промокодов", value=sfx)

coords = None
if found:
    coords = (found[1], found[2])
elif city in CITY_COORDS:
    coords = CITY_COORDS[city]

include_weather = st.sidebar.checkbox("Включить погоду и загрузку", value=coords is not None)

# ---------------------------------------------------------------------------
# Превью
# ---------------------------------------------------------------------------

st.subheader("Превью")
col1, col2, col3 = st.columns(3)
col1.metric("Партнёр", selected_partner)
col2.metric("Город", city or "—")
col3.metric("Файлов загружено", len(uploaded))

st.markdown(f"**Суффикс промокодов:** `{promo_suffix}` · **Погода:** {'да' if include_weather and coords else 'нет'}")

# ---------------------------------------------------------------------------
# Генерация
# ---------------------------------------------------------------------------

if st.button("Сформировать промо-план", type="primary", use_container_width=True):
    progress = st.progress(0, text="Подготовка…")

    def _update_progress(v: float):
        pct = int(v * 100)
        labels = {
            5: "Чтение CSV…", 15: "Загрузка данных…", 20: "Фильтрация…",
            30: "Расчёт визитов…", 40: "RFM-сегментация…", 50: "Когорты…",
            60: "Погода…", 70: "Промо-список…", 75: "Бюджет…",
            80: "Сборка Excel…", 90: "Когорты + бюджет…", 95: "Оформление…",
            100: "Готово!",
        }
        closest = min(labels.keys(), key=lambda k: abs(k - pct))
        progress.progress(v, text=labels[closest])

    config = PromoConfig(
        partner_display_name=selected_partner,
        partner_filter=partner_regex,
        city=city,
        address_short=address_short,
        promo_suffix=promo_suffix,
        weather_coords=coords if include_weather else None,
        include_weather=include_weather and coords is not None,
    )

    buffers = []
    for f in uploaded:
        f.seek(0)
        buffers.append(io.BytesIO(f.read()))

    try:
        xlsx_buf = generate_promo_plan(config, buffers, progress_cb=_update_progress)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Ошибка генерации: {e}")
        st.stop()

    st.session_state["xlsx_buf"] = xlsx_buf.getvalue()
    st.session_state["xlsx_name"] = f"Promo_Plan_{city or 'report'}.xlsx"
    progress.progress(1.0, text="Готово!")
    st.success("Промо-план сформирован!")

# ---------------------------------------------------------------------------
# Скачивание
# ---------------------------------------------------------------------------

if "xlsx_buf" in st.session_state:
    st.divider()
    st.subheader("Результат")

    xl = pd.ExcelFile(io.BytesIO(st.session_state["xlsx_buf"]))
    tabs = st.tabs(["Сегменты", "Бюджет", "Скачать"])

    with tabs[0]:
        rfm_df = pd.read_excel(xl, sheet_name="RFM сегменты", header=3)
        rfm_df = rfm_df.dropna(how="all").head(7)
        st.dataframe(rfm_df, use_container_width=True)

    with tabs[1]:
        bud_df = pd.read_excel(xl, sheet_name="Бюджет промо", header=3)
        bud_df = bud_df.dropna(how="all").head(8)
        st.dataframe(bud_df, use_container_width=True)

    with tabs[2]:
        st.download_button(
            label=f"Скачать {st.session_state['xlsx_name']}",
            data=st.session_state["xlsx_buf"],
            file_name=st.session_state["xlsx_name"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
