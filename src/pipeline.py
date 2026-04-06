"""ETL Pipeline — lädt Rohdaten, bereinigt sie und schreibt sie in die SQLite-DB."""

from db import init_db


def extract():
    """Rohdaten aus CSV / API laden."""
    pass  # TODO: Destatis CSV einlesen, BBSR API anfragen


def transform(raw_data):
    """Bereinigen, normalisieren, Spalten umbenennen."""
    pass  # TODO: Pandas Cleaning


def load(clean_data):
    """In SQLite schreiben."""
    pass  # TODO: DataFrame.to_sql(...)


def run():
    init_db()
    raw = extract()
    clean = transform(raw)
    load(clean)
    print("Pipeline abgeschlossen.")


if __name__ == "__main__":
    run()
