import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import streamlit as st

from db import query
from calculator import (
    net_income,
    disposable_income,
    affordability_score,
    rent_burden_pct,
    children_costs,
    savings_projection,
    CHILD_COST_NET,
)
from components import (
    donut_chart,
    waterfall_chart,
    gauge_chart,
    city_comparison_chart,
    rent_burden_chart,
    rent_vs_salary_chart,
    savings_chart,
)
from lookup import plz_to_city, fetch_city_costs

st.set_page_config(page_title="Germany Cost of Living", layout="wide")
st.title("🇩🇪 Germany Cost of Living — Reality Check")

# ===========================================================================
# SIDEBAR
# ===========================================================================

st.sidebar.header("Meine Situation")

# --- Standort ---
st.sidebar.subheader("📍 Standort")

cities_data = query("SELECT id, name FROM cities ORDER BY name")
city_names  = [c["name"] for c in cities_data]
city_ids    = {c["name"]: c["id"] for c in cities_data}

plz_input = st.sidebar.text_input("PLZ eingeben (on-the-fly Suche)", placeholder="z.B. 32108")
live_data = None
live_city_name = None

if plz_input and len(plz_input.strip()) == 5 and plz_input.strip().isdigit():
    with st.sidebar:
        with st.spinner("Suche PLZ..."):
            location = plz_to_city(plz_input.strip())
    if location:
        live_city_name = location["city"]
        st.sidebar.success(f"📌 {live_city_name}, {location['state']}")
        with st.sidebar:
            with st.spinner(f"Lade Numbeo-Daten für {live_city_name}..."):
                live_data = fetch_city_costs(live_city_name)
        if live_data and "error" in live_data:
            st.sidebar.warning(f"Numbeo: {live_data['error']}")
            live_data = None
    else:
        st.sidebar.error("PLZ nicht gefunden.")

st.sidebar.markdown("**Oder Stadt aus DB wählen:**")
selected_city = st.sidebar.selectbox("Stadt", city_names, disabled=bool(live_data))

# --- Einkommen ---
st.sidebar.subheader("💶 Einkommen")
gross_salary = st.sidebar.slider("Bruttogehalt (€/Monat)", 1_500, 10_000, 3_500, 100)
tax_class    = st.sidebar.selectbox(
    "Steuerklasse",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: {
        1: "1 — Ledig / geschieden",
        2: "2 — Alleinerziehend",
        3: "3 — Verheiratet (Hauptverdiener)",
        4: "4 — Verheiratet (gleich)",
        5: "5 — Verheiratet (Geringverdiener)",
    }[x],
)

# --- Haushalt ---
st.sidebar.subheader("👨‍👩‍👧 Haushalt")
household_size = st.sidebar.radio("Erwachsene im Haushalt", [1, 2])
num_children   = st.sidebar.slider("Kinder (Schätzung ~550 €/Kind nach Kindergeld)", 0, 4, 0)

# --- Wohnen ---
st.sidebar.subheader("🏠 Wohnen")
apt_size_override = st.sidebar.slider("Wohnfläche (m²)", 20, 150, 70, 5)

# --- Sparen ---
st.sidebar.subheader("💰 Sparprognose")
savings_pct   = st.sidebar.slider("Sparquote vom Verfügbaren (%)", 0, 80, 20, 5)
proj_years    = st.sidebar.slider("Projektionszeitraum (Jahre)", 1, 30, 10)
annual_return = st.sidebar.slider("Jährliche Rendite (%)", 0, 10, 4) / 100

# ===========================================================================
# DATEN ZUSAMMENFÜHREN
# ===========================================================================

if live_data and not live_data.get("error"):
    # Live-Daten von Numbeo (PLZ-Suche)
    sqm       = live_data["sqm"]
    rent      = sqm * apt_size_override
    utilities = live_data["utilities"]
    groceries = live_data["groceries"]
    transport = live_data["transport"]
    city_label = f"{live_city_name} (Live via Numbeo)"
    numbeo_url = live_data.get("numbeo_url")
else:
    # DB-Daten
    city_id = city_ids.get(selected_city)
    costs = query(
        """
        SELECT r.sqm_cold, r.avg_apartment_size,
               l.utilities_month, l.groceries_month, l.transport_month
        FROM rent_prices  r
        JOIN living_costs l ON l.city_id = r.city_id AND l.year = r.year
        WHERE r.city_id = ? ORDER BY r.year DESC LIMIT 1
        """,
        (city_id,),
    )
    if not costs:
        st.error("Keine Daten für diese Stadt in der DB.")
        st.stop()
    c         = costs[0]
    sqm       = c["sqm_cold"]
    rent      = sqm * apt_size_override
    utilities = c["utilities_month"]
    groceries = c["groceries_month"]
    transport = c["transport_month"]
    city_label = selected_city
    numbeo_url = None

# Berechnungen
net           = net_income(gross_salary, tax_class)
kids_cost     = children_costs(num_children)
disposable    = disposable_income(gross_salary, rent, utilities, groceries, transport, tax_class, num_children)
score_label, score_color = affordability_score(disposable, net)
rent_pct      = rent_burden_pct(rent, net)
monthly_savings = max(0, disposable * savings_pct / 100)
total_fixed   = rent + utilities + groceries + transport + kids_cost

# ===========================================================================
# TABS
# ===========================================================================

tab1, tab2, tab3 = st.tabs(["🏠 Mein Haushalt", "🏙️ Städtevergleich", "📈 Sparprognose"])

# ---------------------------------------------------------------------------
# TAB 1 — MEIN HAUSHALT
# ---------------------------------------------------------------------------

with tab1:
    st.subheader(f"Analyse für: **{city_label}**")
    if numbeo_url:
        st.caption(f"Datenquelle: [Numbeo]({numbeo_url})")

    # KPI-Karten
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Brutto", f"€ {gross_salary:,.0f}")
    k2.metric("Netto", f"€ {net:,.0f}", delta=f"-€ {gross_salary - net:,.0f} Steuern/SV")
    k3.metric("Fixkosten gesamt", f"€ {total_fixed:,.0f}")
    k4.metric(
        "Verfügbar",
        f"€ {disposable:,.0f}",
        delta=f"{disposable / net * 100:.1f}% des Nettos" if net > 0 else None,
        delta_color="normal" if disposable >= 0 else "inverse",
    )
    k5.metric(
        "Mietbelastung",
        f"{rent_pct:.1f}%",
        delta="⚠️ über 30%" if rent_pct > 30 else "✓ unter 30%",
        delta_color="inverse" if rent_pct > 30 else "normal",
    )

    st.markdown("---")

    # Gauge + Donut nebeneinander
    col_gauge, col_donut = st.columns(2)
    with col_gauge:
        st.plotly_chart(gauge_chart(disposable, net), use_container_width=True)
    with col_donut:
        st.plotly_chart(
            donut_chart(rent, utilities, groceries, transport, kids_cost),
            use_container_width=True,
        )

    # Waterfall
    st.plotly_chart(
        waterfall_chart(gross_salary, rent, utilities, groceries, transport, tax_class, num_children),
        use_container_width=True,
    )

    # Detailtabelle
    with st.expander("Detailaufschlüsselung anzeigen"):
        st.table({
            "Position": ["Bruttogehalt", "Steuern & Sozialabgaben", "Nettoeinkommen",
                         f"Miete ({apt_size_override} m² × {sqm:.2f} €/m²)",
                         "Nebenkosten", "Lebensmittel", "Transport",
                         f"Kinder ({num_children}×)" if num_children > 0 else None,
                         "Verfügbares Einkommen"],
            "€ / Monat": [
                f"{gross_salary:,.2f}",
                f"-{gross_salary - net:,.2f}",
                f"{net:,.2f}",
                f"-{rent:,.2f}",
                f"-{utilities:,.2f}",
                f"-{groceries:,.2f}",
                f"-{transport:,.2f}",
                f"-{kids_cost:,.2f}" if num_children > 0 else None,
                f"{disposable:,.2f}",
            ],
        } if not num_children else {
            "Position": ["Bruttogehalt", "Steuern & Sozialabgaben", "Nettoeinkommen",
                         f"Miete ({apt_size_override} m² × {sqm:.2f} €/m²)",
                         "Nebenkosten", "Lebensmittel", "Transport",
                         f"Kinder ({num_children}×, je ~{CHILD_COST_NET} €)",
                         "Verfügbares Einkommen"],
            "€ / Monat": [
                f"{gross_salary:,.2f}",
                f"-{gross_salary - net:,.2f}",
                f"{net:,.2f}",
                f"-{rent:,.2f}",
                f"-{utilities:,.2f}",
                f"-{groceries:,.2f}",
                f"-{transport:,.2f}",
                f"-{kids_cost:,.2f}",
                f"{disposable:,.2f}",
            ],
        })

# ---------------------------------------------------------------------------
# TAB 2 — STÄDTEVERGLEICH
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Vergleich aller Städte in der Datenbank")
    st.caption("Wohnfläche und Steuerklasse aus der Sidebar werden berücksichtigt.")

    st.plotly_chart(
        city_comparison_chart(gross_salary, tax_class, num_children),
        use_container_width=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(rent_burden_chart(gross_salary, tax_class), use_container_width=True)
    with col_b:
        st.plotly_chart(rent_vs_salary_chart(), use_container_width=True)

    # Rangliste als Tabelle
    with st.expander("Rangliste anzeigen"):
        rows = query(
            """
            SELECT c.name,
                   r.sqm_cold * r.avg_apartment_size AS rent,
                   l.utilities_month, l.groceries_month, l.transport_month,
                   s.median_gross
            FROM cities c
            JOIN rent_prices  r ON r.city_id = c.id AND r.year = 2023
            JOIN living_costs l ON l.city_id = c.id AND l.year = 2023
            JOIN salaries     s ON s.city_id = c.id AND s.year = 2023
            """
        )
        import pandas as pd
        table_data = []
        for row in rows:
            n   = net_income(gross_salary, tax_class)
            disp = disposable_income(
                gross_salary, row["rent"], row["utilities_month"],
                row["groceries_month"], row["transport_month"], tax_class, num_children,
            )
            table_data.append({
                "Stadt":            row["name"],
                "Median-Brutto":    f"€ {row['median_gross']:,.0f}",
                "Miete":            f"€ {row['rent']:,.0f}",
                "Mietbelastung":    f"{rent_burden_pct(row['rent'], n):.1f}%",
                "Verfügbar":        f"€ {disp:,.0f}",
            })
        df_table = pd.DataFrame(table_data).sort_values("Verfügbar", ascending=False)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# TAB 3 — SPARPROGNOSE
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("Sparprognose mit Zinseszins")

    if monthly_savings <= 0:
        st.info(
            f"Mit deinen aktuellen Einstellungen bleibt kein Betrag zum Sparen übrig "
            f"(Verfügbar: € {disposable:,.0f}). Passe Bruttogehalt oder Sparquote an."
        )
    else:
        # KPIs
        proj = savings_projection(monthly_savings, proj_years, annual_return)
        final = proj[-1] if proj else {"Gesamt": 0, "Eingezahlt": 0, "Zinsen": 0}

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Monatlich gespart", f"€ {monthly_savings:,.0f}")
        s2.metric(f"Nach {proj_years} Jahren", f"€ {final['Gesamt']:,.0f}")
        s3.metric("Davon eingezahlt", f"€ {final['Eingezahlt']:,.0f}")
        s4.metric("Davon Zinsen", f"€ {final['Zinsen']:,.0f}",
                  delta=f"+{final['Zinsen'] / final['Eingezahlt'] * 100:.1f}%" if final['Eingezahlt'] > 0 else None)

        st.plotly_chart(
            savings_chart(monthly_savings, proj_years, annual_return),
            use_container_width=True,
        )

        # Meilensteine
        milestones = [1_000, 5_000, 10_000, 25_000, 50_000, 100_000]
        reached = []
        for row in proj:
            for m in milestones:
                if row["Gesamt"] >= m and m not in [r[0] for r in reached]:
                    reached.append((m, row["Jahr"]))

        if reached:
            with st.expander("Meilensteine"):
                for amount, year in reached:
                    st.write(f"✅ **€ {amount:,.0f}** erreicht nach **{year} Jahr{'en' if year > 1 else ''}**")
