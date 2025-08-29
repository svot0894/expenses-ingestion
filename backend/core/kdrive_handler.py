"""
This module provides a class `KDriveHandler`:
    - Handles authentication.
    - Handles files actions like upload, delete, and download.
Classes:
    KDriveHandler: Handles authentication and files actions.
Usage example:
"""

import io
import requests
from backend.core.types import Result


class KDriveHandler:
    """Handles authentication and files upload to Infomaniak KDrive"""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.base_url = self.config.kdrive.get("base_url")
        self.folder_id = self.config.kdrive.get("folder_id")
        self.token = self.config.kdrive.get("token")

    def upload_file(self, uploaded_file) -> Result:
        """
        Uploads a file to Infomaniak KDrive.

        Args:
            uploaded_file (UploadedFile): The uploaded file object.

        Returns:
            Result: Uploaded file ID if successful, else None.
        """

        try:
            response = requests.post(
                f"{self.base_url}/3/drive/{self.folder_id}/upload",
                params={"total_size": uploaded_file.size},
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={
                    "file_id": 1,
                    "file_name": uploaded_file.name,
                    "directory_id": "1452781",
                    "conflict": "version"
                }
            )
            print(response.text)
            response.raise_for_status()
            file_id = response.json().get("id")
            return Result(
                success=True,
                message="File uploaded successfully.",
                data=file_id,
            )
        except requests.RequestException as e:
            return Result(
                success=False,
                message=f"An error occurred while uploading the file: {e}",
            )

    def delete_file(self, file_id: str) -> Result:
        """Delete a file from Infomaniak KDrive.

        Args:
            file_id (str): The ID of the file to delete.

        Returns:
            Result: Result object indicating success or failure.
        """
        try:
            response = requests.delete(
                f"{self.base_url}/2/drive/{self.folder_id}/files/{file_id}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            return Result(success=True, message="File deleted successfully.")
        except requests.RequestException as e:
            return Result(
                success=False,
                message=f"An error occurred while deleting the file: {e}",
            )

    def download_file(self, file_id: str) -> Result:
        """
        Download file content from Infomaniak KDrive as Zip file.
        Function returns file content as bytes.

        Args:
            file_id (str): The ID of the file to download.

        Returns:
            Result: Result object indicating success or failure.
        """
        try:
            response = requests.get(
                f"{self.base_url}/2/drive/{self.folder_id}/files/{file_id}/download",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                timeout=10,
                allow_redirects=True,
            )
            response.raise_for_status()

            # convert zip file content to bytes
            file_content = io.BytesIO(response.content)

            return Result(
                success=True,
                message="File downloaded successfully.",
                data=file_content.getvalue(),
            )
        except requests.RequestException as e:
            return Result(
                success=False,
                message=f"An error occurred while downloading the file: {e}",
            )
