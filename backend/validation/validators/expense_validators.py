"""
Expense validators for the backend.
This module contains the validators for the expense data and data cleaning.
"""

import pandas as pd
from backend.models.models import Expense, FileConfiguration


class ExpenseValidator:
    def __init__(self, file_config: FileConfiguration):
        self.file_config = file_config

    def clean_expense_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the expense data by converting data types.
        :param df: DataFrame containing the expense data.
        :return: Cleaned DataFrame.
        """
        # trim whitespace from columns
        df.columns = df.columns.str.strip()

        # Convert date column to expected datetime format
        df["TRANSACTION_DATE"] = pd.to_datetime(
            df["TRANSACTION_DATE"], format=self.file_config.date_format
        )

        # Convert amount column to numeric format
        df["AMOUNT"] = pd.to_numeric(df["AMOUNT"]) * self.file_config.amount_sign

        return df

    def validate_expense_row(self, row: pd.Series) -> tuple[Expense, dict]:
        """
        Validates a single row of expense data."""
        try:
            expense = Expense(
                file_id=row.file_id,
                transaction_date=row.TRANSACTION_DATE,
                amount=row.AMOUNT,
                description=row.DESCRIPTION,
                account=row.ACCOUNT,
            )
            return expense, None
        except Exception as e:
            return None, {
                "file_id": row.file_id,
                "transaction_date": str(row.TRANSACTION_DATE),
                "amount": str(row.AMOUNT),
                "description": str(row.DESCRIPTION),
                "account": str(row.ACCOUNT),
                "error_message": str(e),
            }
