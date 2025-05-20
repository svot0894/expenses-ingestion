import csv
import ast
from io import StringIO
from backend.validation.base_validator import BaseValidator
from backend.core.file_handler import FileHandler
from backend.models.models import Files, FileConfiguration


class ChecksumValidator(BaseValidator):
    """Validator to check if a file with the same checksum already exists."""

    def __init__(self):
        self.file_handler = FileHandler()

    def validate(self, file_content: bytes, file_metadata: dict) -> tuple[bool, str]:
        checksum = Files.generate_checksum(file_content)
        file_found, message = self.file_handler.get_file_by_checksum(checksum)

        if file_found:
            return False, f"⚠️ Duplicated file detected: {file_metadata['file_name']}"

        file_metadata["checksum"] = checksum
        return True, "File is unique."


class SchemaValidator(BaseValidator):
    """Validator to check if the file schema is valid."""

    def __init__(self, file_config: FileConfiguration):
        self.expected_schema = ast.literal_eval(file_config.expected_schema)
        self.encoding = file_config.encoding
        self.file_delimiter = file_config.delimiter

    def validate(self, file_content: str, file_metadata: dict) -> tuple[bool, str]:
        try:
            decoded_content = file_content.decode(self.encoding)
        except UnicodeDecodeError:
            return False, f"⚠️ File encoding is not {self.encoding}."

        reader = csv.reader(StringIO(decoded_content), delimiter=self.file_delimiter)
        header = next(reader, None)

        if not header:
            return False, "⚠️ File is empty or has no header."

        missing_columns = self.expected_schema - set(header)

        if missing_columns:
            return False, f"⚠️ Missing columns: {', '.join(missing_columns)}"

        return True, "File schema is valid."
