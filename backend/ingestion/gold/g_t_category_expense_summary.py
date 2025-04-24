from backend.models.models import Expense, CategoryExpenses
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

class CategoryExpenseSummaryGenerator:
    def run(self, db_session) -> None:

        # Aggregate data grouped by month and category
        monthly_data = db_session.query(
            func.date_trunc('month', Expense.transaction_date).label('month'),
            Expense.category,
            func.sum(Expense.amount).label('total_expenses')
        ).group_by(
            func.date_trunc('month', Expense.transaction_date),
            Expense.category
        ).all()

        for data in monthly_data:
            summary_data = {
                'transaction_month': data.month,
                'category': data.category,
                'total_expenses': data.total_expenses or 0,
                'inserted_datetime': func.now()
            }

            # insert or update the monthly summary
            # Use the insert statement with on_conflict_do_update
            # to handle conflicts based on the transaction_month
            # and update the existing record
            statement = insert(CategoryExpenses).values(summary_data)
            statement = statement.on_conflict_do_update(
                index_elements=['transaction_month', 'category'],
                set_=summary_data
            )
            db_session.execute(statement)

        db_session.commit()