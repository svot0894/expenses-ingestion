from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
from sqlalchemy import (
    Date,
)

from backend.core.types import Result
from backend.models.models import (
    MonthlyExpenses,
    SavingsRate,
)


def get_monthly_summary(db: Session, transaction_month: Date) -> Result:
    """
    Retrieve monthly expenses summary for a given month.
    """
    result = (
        db.query(MonthlyExpenses)
        .filter_by(transaction_month=transaction_month)
        .first()
    )
    return Result(
        success=bool(result),
        data=result
    )

def get_previous_monthly_summary(db: Session, transaction_month: Date) -> Result:
    """
    Retrieve monthly expenses summary for the previous month.
    """
    previous_month = transaction_month - relativedelta(months=1)
    result = (
        db.query(MonthlyExpenses)
        .filter_by(transaction_month=previous_month)
        .first()
    )
    return Result(
        success=bool(result),
        data=result
    )

def get_savings_rate_summary(db: Session) -> Result:
    """
    Retrieve the savings rate for all available months.
    """
    result = (
        db.query(SavingsRate)
        .all()
    )

    return Result(
        success=bool(result),
        data=result
    )