"""Domain calculations and deterministic insight rules.

This package has no dependency on FastAPI, SQLAlchemy, or any web framework
so that the financial math and insight rules can be unit-tested and reasoned
about in isolation. It is imported by the API's service layer and by the
data pipeline's transform stage.
"""
