"""SQLAlchemy models, grouped by domain: user/auth, finance, geo, reference data.

Every model module is imported here so that ``Base.metadata`` is fully
populated for Alembic's autogenerate and for ``Base.metadata.create_all``
in tests.
"""

from .base import Base
from .finance import (
    Budget,
    Category,
    CategoryKind,
    ExpenseEntry,
    IncomeEntry,
    IncomeSource,
    RecurrenceFrequency,
    RecurrenceRule,
    SavingsGoal,
    SavingsGoalContribution,
)
from .geo import City
from .reference_data import (
    CostSnapshot,
    DataSource,
    ImportRun,
    ImportRunStatus,
    InflationSnapshot,
    RentSnapshot,
    SalarySnapshot,
    TriggeredBy,
    ValidationResult,
    ValidationSeverity,
)
from .user import AccessToken, User

__all__ = [
    "Base",
    "User",
    "AccessToken",
    "Category",
    "CategoryKind",
    "RecurrenceRule",
    "RecurrenceFrequency",
    "IncomeEntry",
    "IncomeSource",
    "ExpenseEntry",
    "Budget",
    "SavingsGoal",
    "SavingsGoalContribution",
    "City",
    "DataSource",
    "ImportRun",
    "ImportRunStatus",
    "TriggeredBy",
    "SalarySnapshot",
    "RentSnapshot",
    "CostSnapshot",
    "InflationSnapshot",
    "ValidationResult",
    "ValidationSeverity",
]
