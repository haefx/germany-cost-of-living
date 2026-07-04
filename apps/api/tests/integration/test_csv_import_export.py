"""CSV import (preview + commit, validation, duplicate detection) and export
(including formula-injection sanitization), plus full JSON account export.
"""

from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import category_id_by_name, register_and_login

VALID_EXPENSE_CSV = (
    "label,amount,entry_date,category,merchant,notes\n"
    "Wocheneinkauf,45.90,2026-06-03,Lebensmittel,Rewe,\n"
    "Kino,15.00,2026-06-10,Freizeit,,Mit Freunden\n"
)


async def _upload(client: AsyncClient, url: str, csv_text: str):
    files = {"file": ("import.csv", csv_text, "text/csv")}
    return await client.post(url, files=files)


async def test_preview_reports_valid_rows_without_writing_anything(client: AsyncClient) -> None:
    await register_and_login(client, "import-a@example.com")

    preview_response = await _upload(client, "/api/import/expenses/preview", VALID_EXPENSE_CSV)
    assert preview_response.status_code == 200
    rows = preview_response.json()
    assert len(rows) == 2
    assert all(row["status"] == "valid" for row in rows)

    list_response = await client.get("/api/expenses")
    assert list_response.json() == []


async def test_commit_actually_imports_valid_rows(client: AsyncClient) -> None:
    await register_and_login(client, "import-b@example.com")

    commit_response = await _upload(client, "/api/import/expenses/commit", VALID_EXPENSE_CSV)
    assert commit_response.status_code == 200
    summary = commit_response.json()
    assert summary["imported"] == 2
    assert summary["skipped_duplicates"] == 0
    assert summary["errors"] == []

    list_response = await client.get("/api/expenses")
    assert len(list_response.json()) == 2


async def test_commit_twice_detects_duplicates_on_the_second_run(client: AsyncClient) -> None:
    await register_and_login(client, "import-c@example.com")

    await _upload(client, "/api/import/expenses/commit", VALID_EXPENSE_CSV)
    second_response = await _upload(client, "/api/import/expenses/commit", VALID_EXPENSE_CSV)

    summary = second_response.json()
    assert summary["imported"] == 0
    assert summary["skipped_duplicates"] == 2


async def test_invalid_rows_are_reported_with_row_numbers(client: AsyncClient) -> None:
    await register_and_login(client, "import-d@example.com")
    csv_text = (
        "label,amount,entry_date,category,merchant,notes\n"
        ",10.00,2026-06-03,,,\n"  # missing label
        "Kino,not-a-number,2026-06-10,,,\n"  # invalid amount
        "Konzert,20.00,not-a-date,,,\n"  # invalid date
        "Sonstiges,20.00,2026-06-10,Nicht-existent,,\n"  # unknown category
    )

    response = await _upload(client, "/api/import/expenses/preview", csv_text)
    rows = response.json()
    assert len(rows) == 4
    assert all(row["status"] == "error" for row in rows)
    assert [row["row_number"] for row in rows] == [2, 3, 4, 5]


async def test_upload_rejects_non_csv_file(client: AsyncClient) -> None:
    await register_and_login(client, "import-e@example.com")
    files = {"file": ("import.txt", "not a csv", "text/plain")}
    response = await client.post("/api/import/expenses/preview", files=files)
    assert response.status_code == 415


async def test_csv_export_sanitizes_formula_injection(client: AsyncClient) -> None:
    await register_and_login(client, "export-a@example.com")
    await client.post(
        "/api/expenses",
        json={"label": "=cmd|'/c calc'!A1", "amount": "5.00", "entry_date": "2026-06-01"},
    )

    response = await client.get("/api/export/expenses.csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "'=cmd" in response.text
    # The raw formula must never appear unescaped at the start of a field.
    assert "\n=cmd" not in response.text


async def test_csv_export_includes_category_name(client: AsyncClient) -> None:
    await register_and_login(client, "export-b@example.com")
    category_id = await category_id_by_name(client, "Lebensmittel")
    await client.post(
        "/api/expenses",
        json={
            "label": "Einkauf",
            "amount": "30.00",
            "entry_date": "2026-06-01",
            "category_id": category_id,
        },
    )

    response = await client.get("/api/export/expenses.csv")
    assert "Lebensmittel" in response.text


async def test_account_export_includes_every_entity_type(client: AsyncClient) -> None:
    await register_and_login(client, "export-c@example.com")
    await client.post(
        "/api/income", json={"label": "Gehalt", "amount": "3000", "entry_date": "2026-06-01"}
    )
    await client.post(
        "/api/expenses", json={"label": "Miete", "amount": "1000", "entry_date": "2026-06-01"}
    )
    await client.post("/api/savings-goals", json={"name": "Urlaub", "target_amount": "500"})

    response = await client.get("/api/export/account")
    assert response.status_code == 200
    body = response.json()
    assert body["account"]["email"] == "export-c@example.com"
    assert len(body["income_entries"]) == 1
    assert len(body["expense_entries"]) == 1
    assert len(body["savings_goals"]) == 1
    assert "hashed_password" not in body["account"]
