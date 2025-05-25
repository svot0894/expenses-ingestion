"""
Expense validators for the backend.
This module contains the validators for the expense data and data cleaning.
"""

import pandas as pd
from backend.core.types import Result
from backend.validation.base_validator import BaseRowValidator


# duplicates validator
class DuplicatesValidator(BaseRowValidator):
    """
    Validator to check for duplicate entries in the expense data.
    """

    def __init__(self) -> None:
        self.duplicate = set()

    def validate(self, row) -> Result:
        key = (row.TRANSACTION_DATE, row.AMOUNT, row.DESCRIPTION)
        if key in self.duplicate:
            return Result(success=False, message="Duplicate entry found.")
        self.duplicate.add(key)
        return Result(success=True, message=None)


# date format validator
class DateFormatValidator(BaseRowValidator):
    """
    Validator to check if the date format is correct.
    """

    def __init__(self, date_format: str) -> None:
        self.date_format = date_format

    def validate(self, row) -> Result:
        try:
            if pd.isna(row.TRANSACTION_DATE):
                return Result(success=False, message="Date is missing.")
            pd.to_datetime(row.TRANSACTION_DATE, format=self.date_format)
            return Result(success=True, message=None)
        except ValueError:
            return Result(success=False, message="Invalid date format.")
