from abc import ABC, abstractmethod
from backend.core.types import Result


# base validator for file validation
class BaseValidator(ABC):
    """Base class for all validators."""

    @abstractmethod
    def validate(self, file_content: str, file_metadata: dict) -> Result:
        """
        Validate the file.
        :param file_content: The content of the file to be validated as a string.
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


# base validator for individual row validation
class BaseRowValidator(ABC):
    """Base class for all row validators."""

    @abstractmethod
    def validate(self, row: dict) -> Result:
        """
        Validate a single row of data.
        :param row: The row to be validated as a dictionary.
        :return: A Result object containing success status and message.
        """
        pass


class RowValidatorPipeline:
    """Pipeline to validate a row using multiple validators."""

    def __init__(self, validators: list[BaseRowValidator]):
        self.validators = validators

    def run_validations(self, row: dict) -> Result:
        """
        Run all validators and stop at the first failure.
        :return: A Result object containing success status and message.
        """
        for validator in self.validators:
            result = validator.validate(row)
            if not result.success:
                return Result(success=False, message=result.message)

        return Result(success=True, message="Row is valid.")
