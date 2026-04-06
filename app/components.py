import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import plotly.express as px
import plotly.graph_objects as go

from db import query
from calculator import disposable_income


def donut_chart(rent: float, utilities: float, groceries: float, transport: float):
    labels = ["Miete", "Nebenkosten", "Lebensmittel", "Transport"]
    values = [rent, utilities, groceries, transport]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.45))
    fig.update_layout(title="Kostenaufschlüsselung (Fixkosten)")
    return fig


def city_comparison_chart(gross_salary: float):
    rows = query(
        """
        SELECT c.name,
               r.sqm_cold * r.avg_apartment_size AS rent,
               l.utilities_month, l.groceries_month, l.transport_month
        FROM cities c
        JOIN rent_prices  r ON r.city_id = c.id AND r.year = 2024
        JOIN living_costs l ON l.city_id = c.id AND l.year = 2024
        """
    )
    data = [
        {
            "Stadt": row["name"],
            "Verfügbar": disposable_income(
                gross_salary, row["rent"], row["utilities_month"],
                row["groceries_month"], row["transport_month"]
            ),
        }
        for row in rows
    ]
    fig = px.bar(data, x="Stadt", y="Verfügbar", title="Städtevergleich — Verfügbares Einkommen")
    return fig
