import csv
from io import StringIO
from abc import ABC, abstractmethod
from backend.core.file_handler import FileHandler
from backend.models.expenses_file import ExpensesFile

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

class ChecksumValidator(BaseValidator):
    """Validator to check if a file with the same checksum already exists."""

    def __init__(self):
        self.file_handler = FileHandler()

    def validate(self, file_content: bytes, file_metadata: dict) -> tuple[bool, str]:
        checksum = ExpensesFile.generate_checksum(file_content)
        existing_file = self.file_handler.get_file_by_checksum(checksum)

        if existing_file:
            return False, f"⚠️ Duplicated file detected: {file_metadata['file_name']}"
        
        file_metadata["checksum"] = checksum
        return True, "File is unique."

class SchemaValidator(BaseValidator):
    """Validator to check if the file schema is valid."""

    def __init__(self, expected_schema: dict):
        self.expected_schema = expected_schema

    def validate(self, file_content: str, file_metadata: dict) -> tuple[bool, str]:
        try:
            decoded_content = file_content.decode("Windows-1252")
        except UnicodeDecodeError:
            return False, "⚠️ File encoding is not Windows-1252."
        
        reader = csv.reader(StringIO(decoded_content), delimiter=";")
        header = next(reader, None)

        if not header:
            return False, "⚠️ File is empty or has no header."
        
        missing_columns = self.expected_schema - set(header)

        if missing_columns:
            return False, f"⚠️ Missing columns: {', '.join(missing_columns)}"
        
        return True, "File schema is valid."
    
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