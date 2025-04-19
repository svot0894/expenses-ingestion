from backend.models.models import Expense, MonthlyExpenses
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

class MonthlySummaryGenerator:
    def run(self, db_session) -> None:

        # Aggregate data grouped by month
        monthly_data = db_session.query(
            func.date_trunc('month', Expense.transaction_date).label('month'),
            func.sum(Expense.amount).filter(Expense.category == 'Expenses').label('total_expenses'),
            func.sum(Expense.amount).filter(Expense.category == 'Salary').label('total_earnings'),
            func.sum(Expense.amount).filter(Expense.category == 'Savings').label('total_savings')
        ).group_by(func.date_trunc('month', Expense.transaction_date)).all()

        for data in monthly_data:
            summary_data = {
                'transaction_month': data.month,
                'total_expenses': data.total_expenses or 0,
                'total_earnings': data.total_earnings or 0,
                'total_savings': data.total_savings or 0,
                'inserted_datetime': func.now()  # Use func.now() to get the current timestamp
            }

            # insert or update the monthly summary
            statement = insert(MonthlyExpenses).values(summary_data)
            statement = statement.on_conflict_do_update(
                index_elements=['transaction_month'],
                set_=summary_data
            )
            db_session.execute(statement)
        
        # update ingested_datetime field in silver layer table
        db_session.query(Expense).filter(
            func.date_trunc('month', Expense.transaction_date) == data.month,
            Expense.ingested_datetime.is_(None)
        ).update(
            {Expense.ingested_datetime: func.now},
            synchronize_session=False
        )

        db_session.commit()