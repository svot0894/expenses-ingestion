import pandas as pd
from backend.validation.cleaning.base_cleaner import BaseCleaner


class TrimColumnCleaner(BaseCleaner):
    """
    Cleans the column by trimming whitespace from the beginning and end of each string.
    """

    def clean(self, row: pd.Series) -> pd.Series:
        row["DESCRIPTION"] = row["DESCRIPTION"].strip()
        return row


class FormatDateCleaner(BaseCleaner):
    """
    Cleans the column by converting it to the expected datetime format.
    """

    def __init__(self, date_format: str):
        self.date_format = date_format

    def clean(self, row: pd.Series) -> pd.Series:
        row["TRANSACTION_DATE"] = pd.to_datetime(
            row.TRANSACTION_DATE, format=self.date_format
        )
        return row


class FormatAmountSignCleaner(BaseCleaner):
    """
    Cleans the column by multiplying the amount by a sign.
    """

    def __init__(self, amount_sign: int):
        self.amount_sign = amount_sign

    def clean(self, row: pd.Series) -> pd.Series:
        row["AMOUNT"] = row["AMOUNT"] * self.amount_sign
        return row
