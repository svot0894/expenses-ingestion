from abc import ABC, abstractmethod
import pandas as pd


class BaseCleaner(ABC):
    """
    Abstract base class for all cleaners.
    """

    @abstractmethod
    def clean(self, row: pd.Series) -> pd.Series:
        """Cleans a singles row and returns the cleaned row."""


class CleaningPipeline:
    """
    A pipeline that runs a series of cleaners on a row of data.
    """

    def __init__(self, cleaners: list[BaseCleaner]):
        self.cleaners = cleaners

    def run(self, row: pd.Series) -> pd.Series:
        """Runner function."""
        for cleaner in self.cleaners:
            row = cleaner.clean(row)
        return row
