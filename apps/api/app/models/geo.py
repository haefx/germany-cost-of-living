"""Geographic reference entities: German cities used in the cost comparison."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class City(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "city"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
