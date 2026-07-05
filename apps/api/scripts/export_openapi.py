"""Exports the FastAPI app's OpenAPI schema to packages/shared/openapi/openapi.json.

Used by `npm run generate-types` (apps/web) to regenerate the TypeScript
contract, and by CI to check the checked-in schema hasn't drifted from the
live app.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.main import app

OUTPUT_PATH = Path(__file__).resolve().parents[3] / "packages" / "shared" / "openapi" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
