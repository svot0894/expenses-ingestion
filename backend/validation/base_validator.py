from abc import ABC, abstractmethod

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

    def run_validations(self, file_content: bytes, file_metadata: dict) -> tuple[bool, str]:
        """
        Run all validators and stop at the first failure.
        :return: (is_valid, error_message)
        """
        for validator in self.validators:
            is_valid, message = validator.validate(file_content, file_metadata)
            if not is_valid:
                return False, message
        
        return True, "File is valid."