import streamlit as st

st.set_page_config(page_title="Дашборд", page_icon="📈", layout="wide")

dashboard = st.Page("pages/0_Дашборд.py", title="Дашборд", icon="📈", default=True)
promo = st.Page("pages/1_Промо_план.py", title="Промо-план", icon="📊")

pg = st.navigation([dashboard, promo])
pg.run()
