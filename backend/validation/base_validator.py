from abc import ABC, abstractmethod


# base validator for file validation
class BaseValidator(ABC):
    """Base class for all validators."""

    @abstractmethod
    def validate(self, file_content: str, file_metadata: dict) -> tuple[bool, str]:
        """
        Validate the file.
        :param file_content: The content of the file to be validated as a string.
        :param file_metadata: Metadata such as file name, size, etc.
        :return: A tuple containing a boolean indicating if the file is valid and a message.
        """
        pass


class FileValidatorPipeline:
    """Pipeline to validate a file using multiple validators."""

    def __init__(self, validators: list[BaseValidator]):
        self.validators = validators

    def run_validations(
        self, file_content: bytes, file_metadata: dict
    ) -> tuple[bool, str]:
        """
        Run all validators and stop at the first failure.
        :return: (is_valid, error_message)
        """
        for validator in self.validators:
            is_valid, message = validator.validate(file_content, file_metadata)
            if not is_valid:
                return False, message

        return True, "File is valid."


# base validator for individual row validation
class BaseRowValidator(ABC):
    """Base class for all row validators."""

    @abstractmethod
    def validate(self, row: dict) -> tuple[bool, str]:
        """
        Validate a single row of data.
        :param row: The row to be validated as a dictionary.
        :return: A tuple containing a boolean indicating if the row is valid and a message.
        """
        pass


class RowValidatorPipeline:
    """Pipeline to validate a row using multiple validators."""

    def __init__(self, validators: list[BaseRowValidator]):
        self.validators = validators

    def run_validations(self, row: dict) -> tuple[bool, str]:
        """
        Run all validators and stop at the first failure.
        :return: (is_valid, error_message)
        """
        for validator in self.validators:
            is_valid, message = validator.validate(row)
            if not is_valid:
                return False, message

        return True, "Row is valid."
