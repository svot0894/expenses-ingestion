from backend.models.models import MonthlyExpenses, SavingsRate
from sqlalchemy import func, case
from sqlalchemy.dialects.postgresql import insert

class SavingsRateGenerator:
    def run(self, db_session) -> None:

        # calculate the savings rate
        # The savings rate is calculated as the total savings divided by the total earnings
        # for the month
        savings_rate_data = db_session.query(
            MonthlyExpenses.transaction_month,
            case(
                (MonthlyExpenses.total_earnings != 0,
                MonthlyExpenses.total_savings / MonthlyExpenses.total_earnings),
                else_=0).label('savings_rate')
        ).all()

        for data in savings_rate_data:
            summary_data = {
                'transaction_month': data.transaction_month,
                'savings_rate': data.savings_rate,
                'inserted_datetime': func.now()  # Use func.now() to get the current timestamp
            }

            # insert or update the savings rate monthly summary
            # Use the insert statement with on_conflict_do_update
            # to handle conflicts based on the transaction_month
            # and update the existing record
            statement = insert(SavingsRate).values(summary_data)
            statement = statement.on_conflict_do_update(
                index_elements=['transaction_month'],
                set_=summary_data
            )
            db_session.execute(statement)

        db_session.commit()