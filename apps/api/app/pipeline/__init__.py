"""Idempotent data pipeline for the public cost-of-living reference dataset.

Stages: extract -> validate -> normalize -> transform -> load -> publish.
See docs/architecture/decisions/0003-reference-data-not-live-scraping.md for
why this reads a local reference file rather than a live API, and why that
is a swappable implementation detail rather than a permanent limitation.
"""
