"""
Expense validators for the backend.
This module contains the validators for the expense data and data cleaning.
"""

import pandas as pd
from backend.models.models import Expense, FileConfiguration
from backend.validation.base_validator import BaseRowValidator


# duplicates validator
class DuplicatesValidator(BaseRowValidator):
    """
    Validator to check for duplicate entries in the expense data.
    """

    def __init__(self):
        self.duplicate = set()

    def validate(self, row):
        key = (row.TRANSACTION_DATE, row.AMOUNT, row.DESCRIPTION)
        if key in self.duplicate:
            return False, "Duplicate entry found."
        self.duplicate.add(key)
        return True, None


# date format validator
class DateFormatValidator(BaseRowValidator):
    """
    Validator to check if the date format is correct.
    """

    def __init__(self, date_format: str):
        self.date_format = date_format

    def validate(self, row):
        try:
            if pd.isna(row.TRANSACTION_DATE):
                return False, "Date is missing."
            pd.to_datetime(row.TRANSACTION_DATE, format=self.date_format)
            return True, None
        except ValueError:
            return False, "Invalid date format."
