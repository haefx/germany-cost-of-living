"""Structured logging for the pipeline: one JSON line per stage per city,
so a failed or unusual run can be diagnosed from logs alone.
"""

from __future__ import annotations

import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)

get_logger = structlog.get_logger
