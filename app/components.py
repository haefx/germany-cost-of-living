import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from db import query
from calculator import disposable_income, net_income, rent_burden_pct, savings_projection


# ---------------------------------------------------------------------------
# Donut – Kostenaufschlüsselung
# ---------------------------------------------------------------------------

def donut_chart(rent: float, utilities: float, groceries: float, transport: float, children: float = 0):
    labels = ["Miete", "Nebenkosten", "Lebensmittel", "Transport"]
    values = [rent, utilities, groceries, transport]
    if children > 0:
        labels.append("Kinder")
        values.append(children)
    colors = ["#e74c3c", "#e67e22", "#3498db", "#2ecc71", "#9b59b6"]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.48,
        marker_colors=colors[:len(labels)],
        textinfo="label+percent",
    ))
    fig.update_layout(
        title="Kostenaufschlüsselung (Fixkosten)",
        showlegend=True,
        margin=dict(t=50, b=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Waterfall – Einkommensabfluss
# ---------------------------------------------------------------------------

def waterfall_chart(
    gross: float,
    rent: float,
    utilities: float,
    groceries: float,
    transport: float,
    tax_class: int = 1,
    num_children: int = 0,
):
    from calculator import TAX_CLASS_RATES, CHILD_COST_NET
    net = net_income(gross, tax_class)
    tax_deduction = gross - net
    kids = num_children * CHILD_COST_NET

    labels  = ["Brutto", "Steuern & SV", "Netto", "Miete", "Nebenkosten", "Lebensmittel", "Transport"]
    measure = ["absolute", "relative", "total", "relative", "relative", "relative", "relative"]
    values  = [gross, -tax_deduction, net, -rent, -utilities, -groceries, -transport]
    colors  = ["#3498db", "#e74c3c", "#2980b9", "#e74c3c", "#e67e22", "#3498db", "#2ecc71"]

    if kids > 0:
        labels.append("Kinder")
        measure.append("relative")
        values.append(-kids)
        colors.append("#9b59b6")

    labels.append("Verfügbar")
    measure.append("total")
    disposable = net - rent - utilities - groceries - transport - kids
    values.append(disposable)
    colors.append("#27ae60" if disposable >= 0 else "#c0392b")

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measure,
        x=labels,
        y=values,
        connector={"line": {"color": "rgba(100,100,100,0.3)"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        increasing={"marker": {"color": "#2ecc71"}},
        totals={"marker": {"color": "#2980b9"}},
        text=[f"€ {abs(v):,.0f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Einkommensfluss — Brutto bis Verfügbar",
        yaxis_title="€ / Monat",
        showlegend=False,
        margin=dict(t=50, b=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Gauge – Kaufkraft-Score
# ---------------------------------------------------------------------------

def gauge_chart(disposable: float, net: float):
    pct = max(0, min(100, (disposable / net * 100) if net > 0 else 0))

    if pct < 10:
        color = "#e74c3c"
        label = "Kritisch"
    elif pct < 25:
        color = "#e67e22"
        label = "Eng"
    elif pct < 45:
        color = "#f1c40f"
        label = "Mittel"
    else:
        color = "#2ecc71"
        label = "Gut"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number={"suffix": "%", "font": {"size": 28}},
        title={"text": f"Verfügbar vom Netto — {label}"},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 10],  "color": "#fde8e8"},
                {"range": [10, 25], "color": "#fef3e2"},
                {"range": [25, 45], "color": "#fefbe2"},
                {"range": [45, 100],"color": "#e8f8f0"},
            ],
            "threshold": {"line": {"color": "black", "width": 2}, "value": pct},
        },
    ))
    fig.update_layout(margin=dict(t=60, b=20))
    return fig


# ---------------------------------------------------------------------------
# Städtevergleich – Verfügbares Einkommen
# ---------------------------------------------------------------------------

def city_comparison_chart(gross_salary: float, tax_class: int = 1, num_children: int = 0):
    rows = query(
        """
        SELECT c.name,
               r.sqm_cold * r.avg_apartment_size AS rent,
               l.utilities_month, l.groceries_month, l.transport_month
        FROM cities c
        JOIN rent_prices  r ON r.city_id = c.id AND r.year = 2023
        JOIN living_costs l ON l.city_id = c.id AND l.year = 2023
        """
    )
    data = [
        {
            "Stadt": row["name"],
            "Verfügbar": disposable_income(
                gross_salary,
                row["rent"],
                row["utilities_month"],
                row["groceries_month"],
                row["transport_month"],
                tax_class,
                num_children,
            ),
        }
        for row in rows
    ]
    df = pd.DataFrame(data).sort_values("Verfügbar", ascending=False)
    colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in df["Verfügbar"]]
    fig = px.bar(
        df, x="Stadt", y="Verfügbar",
        title="Städtevergleich — Verfügbares Einkommen nach Fixkosten",
        color="Verfügbar",
        color_continuous_scale=["#e74c3c", "#f1c40f", "#2ecc71"],
        text=df["Verfügbar"].apply(lambda v: f"€ {v:,.0f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_title="€ / Monat",
        margin=dict(t=50, b=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Mietbelastungsquote je Stadt
# ---------------------------------------------------------------------------

def rent_burden_chart(gross_salary: float, tax_class: int = 1):
    rows = query(
        """
        SELECT c.name,
               r.sqm_cold * r.avg_apartment_size AS rent
        FROM cities c
        JOIN rent_prices r ON r.city_id = c.id AND r.year = 2023
        """
    )
    net = net_income(gross_salary, tax_class)
    data = [
        {
            "Stadt": row["name"],
            "Mietbelastung %": rent_burden_pct(row["rent"], net),
        }
        for row in rows
    ]
    df = pd.DataFrame(data).sort_values("Mietbelastung %", ascending=False)
    fig = px.bar(
        df, x="Stadt", y="Mietbelastung %",
        title="Mietbelastungsquote — Anteil Miete am Nettoeinkommen",
        color="Mietbelastung %",
        color_continuous_scale=["#2ecc71", "#f1c40f", "#e74c3c"],
        text=df["Mietbelastung %"].apply(lambda v: f"{v:.1f}%"),
    )
    fig.update_traces(textposition="outside")
    fig.add_hline(y=30, line_dash="dash", line_color="orange",
                  annotation_text="30%-Grenze (Empfehlung)", annotation_position="top right")
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_title="% des Nettoeinkommens",
        margin=dict(t=50, b=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Miete vs. Gehalt – Scatter
# ---------------------------------------------------------------------------

def rent_vs_salary_chart():
    rows = query(
        """
        SELECT c.name,
               r.sqm_cold * r.avg_apartment_size AS rent,
               s.median_gross AS salary
        FROM cities c
        JOIN rent_prices r ON r.city_id = c.id AND r.year = 2023
        JOIN salaries    s ON s.city_id = c.id AND s.year = 2023
        """
    )
    df = pd.DataFrame(rows)
    df.columns = ["Stadt", "Miete", "Median-Brutto"]
    fig = px.scatter(
        df, x="Median-Brutto", y="Miete",
        text="Stadt",
        title="Miete vs. Median-Gehalt je Stadt",
        size="Miete",
        color="Miete",
        color_continuous_scale=["#2ecc71", "#e74c3c"],
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Median-Bruttogehalt (€/Monat)",
        yaxis_title="Geschätzte Kaltmiete (€/Monat)",
        margin=dict(t=50, b=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Sparprojektion
# ---------------------------------------------------------------------------

def savings_chart(monthly_savings: float, years: int = 10, annual_return: float = 0.04):
    rows = savings_projection(monthly_savings, years, annual_return)
    df = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Jahr"], y=df["Eingezahlt"],
        name="Eingezahlt",
        marker_color="#3498db",
    ))
    fig.add_trace(go.Bar(
        x=df["Jahr"], y=df["Zinsen"],
        name="Zinseszins",
        marker_color="#2ecc71",
    ))
    fig.add_trace(go.Scatter(
        x=df["Jahr"], y=df["Gesamt"],
        name="Gesamtbetrag",
        mode="lines+markers",
        line=dict(color="#e74c3c", width=2),
    ))
    fig.update_layout(
        barmode="stack",
        title=f"Sparprognose — {years} Jahre bei {annual_return*100:.0f}% p.a.",
        xaxis_title="Jahr",
        yaxis_title="€",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=50, b=60),
    )
    return fig
