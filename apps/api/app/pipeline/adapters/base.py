"""The adapter boundary: anything that can produce raw city cost rows.

``LocalReferenceCsvAdapter`` is the only implementation today, but every
later stage depends on this ``Protocol``, not on it directly — swapping in
a real government-API adapter later means implementing ``extract()``
against this interface, not touching validate/normalize/transform/load.
"""

from __future__ import annotations

from typing import Protocol


class SourceAdapter(Protocol):
    def extract(self) -> list[dict[str, str]]: ...
