import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import streamlit as st
import plotly.express as px

from db import query
from calculator import disposable_income, affordability_score
from components import donut_chart, city_comparison_chart

st.set_page_config(page_title="Germany Cost of Living", layout="wide")
st.title("🇩🇪 Germany Cost of Living Reality Check")

# --- Sidebar Inputs ---
st.sidebar.header("Deine Situation")

cities_data = query("SELECT id, name FROM cities ORDER BY name")
city_names = [c["name"] for c in cities_data]
city_ids   = {c["name"]: c["id"] for c in cities_data}

selected_city  = st.sidebar.selectbox("Stadt", city_names)
gross_salary   = st.sidebar.slider("Bruttogehalt (€/Monat)", 1500, 10000, 3500, 100)
household_size = st.sidebar.radio("Haushaltsgröße", [1, 2, 3])

# --- Daten laden ---
city_id = city_ids.get(selected_city)
costs = query(
    """
    SELECT r.sqm_cold * r.avg_apartment_size AS rent,
           l.utilities_month, l.groceries_month, l.transport_month
    FROM rent_prices r
    JOIN living_costs l ON l.city_id = r.city_id AND l.year = r.year
    WHERE r.city_id = ? ORDER BY r.year DESC LIMIT 1
    """,
    (city_id,),
)

if not costs:
    st.warning("Keine Daten für diese Stadt vorhanden.")
    st.stop()

c = costs[0]
disposable = disposable_income(
    gross_salary, c["rent"], c["utilities_month"], c["groceries_month"], c["transport_month"]
)
score = affordability_score(disposable, gross_salary * 0.67)

# --- KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Verfügbares Einkommen", f"€ {disposable:,.0f}")
col2.metric("Geschätzte Miete", f"€ {c['rent']:,.0f}")
col3.metric("Kaufkraft-Score", score)

# --- Charts ---
st.plotly_chart(donut_chart(c["rent"], c["utilities_month"], c["groceries_month"], c["transport_month"]), use_container_width=True)
st.plotly_chart(city_comparison_chart(gross_salary), use_container_width=True)
