"""Страница Streamlit: генератор промо-плана (RFM → Excel) без AI-токенов."""
from __future__ import annotations

import io
import re
import zipfile

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Промо-план", page_icon="📊", layout="wide")
st.title("Генератор промо-плана")
st.caption("Загрузите данные Лейки (1–3 месяца), выберите агента — система сформирует промо-план.")

# ---------------------------------------------------------------------------
# Утилиты
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
    out: list[str] = []
    for ch in text:
        low = ch.lower()
        if low in _TRANSLIT_MAP:
            t = _TRANSLIT_MAP[low]
            out.append(t.upper() if ch.isupper() else t)
        else:
            out.append(ch)
    return "".join(out)


def _make_suffix(partner: str, city: str) -> str:
    city_part = _translit(city)[:2].upper() if city else "XX"
    nums = re.findall(r"\d+", partner)
    return city_part + (nums[0] if nums else "")


def _extract_csv_buffers(uploaded_files) -> list[tuple[str, io.BytesIO]]:
    """CSV и ZIP → список (имя, BytesIO с CSV)."""
    result: list[tuple[str, io.BytesIO]] = []
    for f in uploaded_files:
        f.seek(0)
        if f.name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(f.read())) as zf:
                    for name in zf.namelist():
                        if name.lower().endswith(".csv") and not name.startswith("__"):
                            result.append((name, io.BytesIO(zf.read(name))))
            except zipfile.BadZipFile:
                pass
        else:
            result.append((f.name, io.BytesIO(f.read())))
    return result


def _auto_location(addresses: list[str], city: str) -> str:
    """Авто-локация для push: улица если одна мойка, иначе город."""
    if len(addresses) == 1 and addresses[0]:
        parts = addresses[0].split(",")
        if len(parts) >= 2:
            street = parts[1].strip()
            if street:
                return f"на {street}"
    if city:
        return f"в г. {city}"
    return ""


def _safe_filename(partner: str) -> str:
    """Имя партнёра → безопасное имя файла."""
    safe = re.sub(r'[<>:"/\\|?*]', '', partner).strip()
    safe = re.sub(r'\s+', ' ', safe)
    return safe


# ---------------------------------------------------------------------------
# 1. Загрузка данных
# ---------------------------------------------------------------------------

st.sidebar.header("1. Загрузите данные")
st.sidebar.caption("💡 Для Cloud рекомендуем ZIP — сжатие ~7×")
uploaded = st.sidebar.file_uploader(
    "CSV или ZIP с orderTable",
    type=["csv", "zip"],
    accept_multiple_files=True,
)

if not uploaded:
    st.info("⬅ Загрузите файлы orderTable через боковую панель (CSV или ZIP с CSV).")
    st.stop()

csv_files = _extract_csv_buffers(uploaded)
if not csv_files:
    st.error("Не найдено ни одного CSV в загруженных файлах.")
    st.stop()

# ---------------------------------------------------------------------------
# 2. Парсинг метаданных: партнёр → адреса/мойки
# ---------------------------------------------------------------------------

files_key = [name for name, _ in csv_files]
if "meta_cache" not in st.session_state or st.session_state.get("_fk") != files_key:
    rows: list[pd.DataFrame] = []
    for _, buf in csv_files:
        buf.seek(0)
        try:
            chunk = pd.read_csv(
                buf, sep=";", encoding="utf-8-sig", dtype=str, nrows=50_000,
                usecols=lambda c: c in ("Партнёр", "Адрес", "Автомойка"),
            )
            rows.append(chunk)
        except Exception:
            continue

    if rows:
        meta_df = pd.concat(rows, ignore_index=True)
    else:
        meta_df = pd.DataFrame()

    partners = sorted(meta_df["Партнёр"].dropna().unique()) if "Партнёр" in meta_df.columns else []

    partner_meta: dict[str, dict] = {}
    for p in partners:
        sub = meta_df[meta_df["Партнёр"] == p]
        addrs = sub["Адрес"].dropna().unique().tolist() if "Адрес" in sub.columns else []
        wshs = sub["Автомойка"].dropna().unique().tolist() if "Автомойка" in sub.columns else []
        partner_meta[p] = {"addresses": addrs, "washes": wshs}

    st.session_state["meta_cache"] = {"partners": partners, "partner_meta": partner_meta}
    st.session_state["_fk"] = files_key

meta = st.session_state["meta_cache"]

if not meta["partners"]:
    st.error("В файлах нет колонки «Партнёр» или она пуста.")
    st.stop()

# ---------------------------------------------------------------------------
# 3. Выбор агента → определение города/адреса
# ---------------------------------------------------------------------------

st.sidebar.header("2. Выберите агента")
selected_partner = st.sidebar.selectbox(
    "Агент", meta["partners"],
    help="После выбора агента нажмите «Сформировать промо-план»",
)

pm = meta["partner_meta"].get(selected_partner, {"addresses": [], "washes": []})

from city_coords import CITY_COORDS, find_city_coords

first_addr = next((a for a in pm["addresses"] if a and a.strip()), "")
found = find_city_coords(first_addr)
city = found[0] if found else (first_addr.split(",")[0].strip() if first_addr else "")
coords = (found[1], found[2]) if found else CITY_COORDS.get(city)
location = _auto_location(pm["addresses"], city)
sfx = _make_suffix(selected_partner, city)

# ---------------------------------------------------------------------------
# 4. Дополнительные настройки (свёрнуты)
# ---------------------------------------------------------------------------

with st.sidebar.expander("Дополнительные настройки"):
    city = st.text_input("Город", value=city)
    location = st.text_input("Локация для push", value=location,
                             help="Авто: улица (1 мойка) или город (несколько)")
    sfx = st.text_input("Суффикс промокодов", value=sfx)
    include_weather = st.checkbox("Включить погоду", value=coords is not None)

# ---------------------------------------------------------------------------
# 5. Основная область: инфо + кнопка
# ---------------------------------------------------------------------------

n_locations = len(pm["addresses"]) or "—"
st.info(
    f"**Агент:** {selected_partner}  \n"
    f"**Город:** {city or '—'} · **Объектов (адресов):** {n_locations} · "
    f"**Файлов данных:** {len(csv_files)}"
)

out_name = f"{_safe_filename(selected_partner)}_Promo_Plan.xlsx"

if st.button("Сформировать промо-план", type="primary", use_container_width=True):
    bar = st.progress(0, text="Подготовка…")

    _LABELS = {
        5: "Чтение CSV…", 15: "Загрузка…", 20: "Фильтрация…",
        30: "Визиты…", 40: "RFM-сегментация…", 50: "Когорты…",
        60: "Погода…", 70: "Промо-список…", 75: "Бюджет…",
        80: "Excel…", 90: "Оформление…", 95: "Стилизация…", 100: "Готово!",
    }

    def _progress(v: float):
        closest = min(_LABELS, key=lambda k: abs(k - int(v * 100)))
        bar.progress(v, text=_LABELS[closest])

    from promo_pipeline import PromoConfig, generate_promo_plan

    config = PromoConfig(
        partner_display_name=selected_partner,
        partner_filter=re.escape(selected_partner),
        city=city,
        address_short=location,
        promo_suffix=sfx,
        weather_coords=coords if include_weather else None,
        include_weather=include_weather and coords is not None,
    )

    buffers = []
    for _, buf in csv_files:
        buf.seek(0)
        buffers.append(io.BytesIO(buf.read()))

    try:
        xlsx_buf = generate_promo_plan(config, buffers, progress_cb=_progress)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Ошибка: {e}")
        st.stop()

    st.session_state["xlsx_buf"] = xlsx_buf.getvalue()
    st.session_state["xlsx_name"] = out_name
    bar.progress(1.0, text="Готово!")

# ---------------------------------------------------------------------------
# 6. Результат
# ---------------------------------------------------------------------------

if "xlsx_buf" in st.session_state:
    st.divider()
    st.success("Промо-план готов!")

    st.download_button(
        label=f"⬇ Скачать {st.session_state['xlsx_name']}",
        data=st.session_state["xlsx_buf"],
        file_name=st.session_state["xlsx_name"],
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
    )

    with st.expander("Предпросмотр: RFM-сегменты"):
        xl = pd.ExcelFile(io.BytesIO(st.session_state["xlsx_buf"]))
        rfm_df = pd.read_excel(xl, sheet_name="RFM сегменты", header=3)
        st.dataframe(rfm_df.dropna(how="all").head(7), use_container_width=True)

    with st.expander("Предпросмотр: Бюджет"):
        bud_df = pd.read_excel(xl, sheet_name="Бюджет промо", header=3)
        st.dataframe(bud_df.dropna(how="all").head(8), use_container_width=True)
