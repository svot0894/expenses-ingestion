"""
Expense validators for the backend.
This module validates expense data in a DataFrame.
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
        # The ~ negates so that True means unique and False means duplicate.
        valid_mask = ~df.duplicated(
            subset=["TRANSACTION_DATE", "AMOUNT", "DESCRIPTION"], keep="first"
        )
        return Result(
            success=True,
            message="Duplicate rows identified and flagged.",
            data=valid_mask
        )


# internal transfers validator
class InternalTransfersValidator(BaseDataFrameValidator):
    """
    Validator to identify and exclude internal transfers.

    Internal transfers are identified as matching entries with:
    - Same transaction date
    - Same absolute amount
    - Not within the same account

    Only the negative (outgoing) entries are removed.
    """

    def validate(self, df: pd.DataFrame) -> Result:
        df["abs_AMOUNT"] = df["AMOUNT"].abs()
        grouped = df.groupby(["TRANSACTION_DATE", "abs_AMOUNT"])

        to_remove = set()

        for _, group in grouped:
            has_positive = (group["AMOUNT"] > 0).any()
            has_negative = (group["AMOUNT"] < 0).any()
            multi_account = group["ACCOUNT"].nunique() > 1

            if len(group) > 1 and multi_account and has_positive and has_negative:
                to_remove.update(group[group["AMOUNT"] < 0].index)

        df.drop(columns=["abs_AMOUNT"], inplace=True)
        valid_mask = ~df.index.isin(to_remove)

        return Result(
            success=True,
            message="Internal transfers identified and excluded.",
            data=valid_mask
        )


# date format validator
class DateFormatValidator(BaseDataFrameValidator):
    """
    Validator to check if the date format is correct.
    """

    def __init__(self, date_format: str) -> None:
        self.date_format = date_format

    def is_valid_date(self, val) -> bool:
        """Function to convert dates to expected format."""
        try:
            pd.to_datetime(val, format=self.date_format)
            return True
        except ValueError:
            return False

    def validate(self, df: pd.DataFrame) -> Result:
        wrong_date = df["TRANSACTION_DATE"].apply(self.is_valid_date)

        return Result(
            success=wrong_date.all(),
            message="Invalid date format found.",
            data=wrong_date
        )
