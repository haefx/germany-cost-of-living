"""Deterministic, rule-based savings/budget insights.

This is a thin wrapper: it assembles an ``InsightContext`` from the current
user's own data and calls the shared engine in packages/analytics. Rule
logic itself is tested there, not here.
"""

from __future__ import annotations

from datetime import date

from analytics.insights.engine import run_all
from fastapi import APIRouter, Depends

from ..deps import (
    CurrentUser,
    DbSession,
    get_budget_repository,
    get_category_repository,
    get_expense_repository,
    get_income_repository,
    get_savings_goal_contribution_repository,
    get_savings_goal_repository,
)
from ..repositories.category import CategoryRepository
from ..repositories.finance import (
    BudgetRepository,
    ExpenseRepository,
    IncomeRepository,
    SavingsGoalContributionRepository,
    SavingsGoalRepository,
)
from ..schemas.insights import InsightRead, InsightsResponse
from ..services.insights_service import build_insight_context

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("", response_model=InsightsResponse)
async def get_insights(
    user: CurrentUser,
    session: DbSession,
    month: date | None = None,
    income_repo: IncomeRepository = Depends(get_income_repository),
    expense_repo: ExpenseRepository = Depends(get_expense_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository),
    category_repo: CategoryRepository = Depends(get_category_repository),
    goal_repo: SavingsGoalRepository = Depends(get_savings_goal_repository),
    contribution_repo: SavingsGoalContributionRepository = Depends(
        get_savings_goal_contribution_repository
    ),
) -> InsightsResponse:
    effective_month = month or date.today()
    context = await build_insight_context(
        session,
        user.id,
        effective_month,
        income_repo,
        expense_repo,
        budget_repo,
        category_repo,
        goal_repo,
        contribution_repo,
    )
    report = run_all(context)
    return InsightsResponse(
        month=effective_month.isoformat(),
        insights=[InsightRead(**vars(insight)) for insight in report.insights],
        failed_rules=list(report.failed_rules),
    )
