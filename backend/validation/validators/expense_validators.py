"""
Expense validators for the backend.
This module contains the validators for the expense data and data cleaning.
"""

import pandas as pd
from backend.core.types import Result
from backend.validation.base_validator import BaseDataFrameValidator


# duplicates validator
class DuplicatesValidator(BaseDataFrameValidator):
    """
    Validator to check for duplicate entries in the expense data.
    """

    def validate(self, df: pd.DataFrame) -> Result:
        duplicated = ~df.duplicated(
            subset=["TRANSACTION_DATE", "AMOUNT", "DESCRIPTION"], keep="first"
        )
        return Result(
            success=duplicated.all(), message="Duplicate entry found.", data=duplicated
        )


# date format validator
class DateFormatValidator(BaseDataFrameValidator):
    """
    Validator to check if the date format is correct.
    """

    def __init__(self, date_format: str) -> None:
        self.date_format = date_format

    def is_valid_date(self, val):
        """Function to convert dates to expected format."""
        try:
            pd.to_datetime(val, format=self.date_format)
            return True
        except Exception:
            return False

    def validate(self, df: pd.DataFrame) -> Result:
        wrong_date = df["TRANSACTION_DATE"].apply(self.is_valid_date)

        return Result(
            success=wrong_date.all(),
            message="Invalid date format found.",
            data=wrong_date,
        )
