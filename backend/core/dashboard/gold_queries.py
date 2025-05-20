from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
from sqlalchemy import (
    Date,
)

from backend.models.models import (
    MonthlyExpenses,
    SavingsRate,
)


def get_monthly_summary(db: Session, transaction_month: Date) -> tuple[bool, MonthlyExpenses]:
    result = (
        db.query(MonthlyExpenses)
        .filter_by(transaction_month=transaction_month)
        .first()
    )
    return (bool(result), result)

def get_previous_monthly_summary(db: Session, transaction_month: Date) -> tuple[bool, MonthlyExpenses]:
    # retrieve previous month
    previous_month = transaction_month - relativedelta(months=1)
    result = (
        db.query(MonthlyExpenses)
        .filter_by(transaction_month=previous_month)
        .first()
    )
    return (bool(result), result)

def get_savings_rate_summary(db: Session) -> tuple[bool, SavingsRate]:
    # retrieve all monthly expenses
    result = (
        db.query(SavingsRate)
        .all()
    )
    return (bool(result), result)