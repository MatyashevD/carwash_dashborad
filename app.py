import streamlit as st

st.set_page_config(page_title="Дашборд", page_icon="📈", layout="wide")

dashboard = st.Page("views/dashboard.py", title="Дашборд", icon="📈", default=True)
promo = st.Page("views/promo_plan.py", title="Промо-план", icon="📊")

pg = st.navigation([dashboard, promo])
pg.run()
