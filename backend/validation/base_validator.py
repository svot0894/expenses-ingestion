from abc import ABC, abstractmethod
from backend.core.types import Result
import pandas as pd


# base validator for file validation
class BaseValidator(ABC):
    """Base class for all validators."""

    @abstractmethod
    def validate(self, file_content: bytes, file_metadata: dict) -> Result:
        """
        Validate the file.
        :param file_content: The content of the file to be validated.
        :param file_metadata: Metadata such as file name, size, etc.
        :return: A Result object containing success status and message.
        """
        pass


class FileValidatorPipeline:
    """Pipeline to validate a file using multiple validators."""

    def __init__(self, validators: list[BaseValidator]):
        self.validators = validators

    def run_validations(self, file_content: bytes, file_metadata: dict) -> Result:
        """
        Run all validators and stop at the first failure.
        :return: A Result object containing success status and message.
        """
        for validator in self.validators:
            result = validator.validate(file_content, file_metadata)
            if not result.success:
                return Result(
                    success=False,
                    message=result.message,
                )

        return Result(success=True, message="File is valid.")


# base validator for entire DataFrames
class BaseDataFrameValidator(ABC):
    """Base class for all DataFrame-level validators."""

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> Result:
        """
        Validates an entire DataFrame.
        Returns: <Boolean>, True for valid rows, False for invalid.
        """


class DataFrameValidatorPipeline:
    """Pipeline to validate a DataFrame using multiple validators."""

    def __init__(self, validators: list[BaseDataFrameValidator]):
        self.validators = validators

    def run_validations(self, df: pd.DataFrame) -> Result:
        """
        Run all validators and annotates the DataFrame with:
        - is_valid: bool column for overall row validity
        - error_message: concat string of all validation failures
        """
        df["is_valid"] = True
        df["error_message"] = ""

        for validator in self.validators:
            result = validator.validate(df)

            df["is_valid"] &= result.data
            df.loc[~result.data, "error_message"] += result.message + "; "

        failed_rows = (~df["is_valid"]).sum()

        if failed_rows > 0:
            return Result(
                success=False,
                message=f"{failed_rows} rows(s) failed validation.",
                data=df,
            )
        return Result(success=True, message="All rows are valid.", data=df)
