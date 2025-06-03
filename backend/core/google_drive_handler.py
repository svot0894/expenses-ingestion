"""
This module provides a class `GoogleDriveHandler`:
    - Handles authentication.
    - Handles files upload.
Classes:
    GoogleDriveHandler: Handles authentication and files upload.
Usage example:
    handler = GoogleDriveHandler(
    'path/to/credentials.json',
    ['https://www.googleapis.com/auth/drive']
    )
    handler.upload_file('path/to/local/file.txt')
"""

import io
import json
from typing import Optional
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from backend.core.types import Result


class GoogleDriveHandler:
    """Handles authentication and files upload to Google Drive"""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.service = self.authenticate()

    def authenticate(self) -> Resource:
        """Authenticates using a service account."""
        sa_info = dict(self.config.get("service_account"))

        creds = Credentials.from_service_account_info(
            sa_info, scopes=self.config.google_drive_api.scopes
        )

        service = build("drive", "v3", credentials=creds)
        return service

    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Result:
        """
        Uploads a file to Google Drive.

        Args:
            file_path (str): Local file path to upload.
            folder_id (str, optional): Google Drive folder ID to upload the file to.

        Returns:
            Result: Uploaded file ID if successful, else None.
        """

        try:
            file_metadata = {"name": file_path.name}

            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaIoBaseUpload(file_path, mimetype="text/csv", resumable=True)
            uploaded_file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            return Result(
                success=True,
                message="File uploaded successfully.",
                data=uploaded_file.get("id"),
            )

        except HttpError as error:
            return Result(
                success=False,
                message=f"An error occurred while uploading the file: {error}",
            )
        except FileNotFoundError:
            return Result(
                success=False,
                message=f"File not found: {file_path}",
            )
        except Exception as e:
            return Result(
                success=False,
                message=f"An unexpected error occurred: {e}",
            )

    def delete_file(self, file_id: str) -> Result:
        """Delete a file from Google Drive.

        Args:
            file_id (str): The ID of the file to delete.

        Returns:
            Result: Result object indicating success or failure.
        """
        try:
            body_value = {"trashed": True}
            self.service.files().update(fileId=file_id, body=body_value).execute()
            return Result(success=True, message="File deleted successfully.")
        except HttpError as error:
            return Result(
                success=False,
                message=f"An error occurred while trying to delete the file: {error}",
            )

    def download_file(self, file_id: str) -> Result:
        """Download a file from Google Drive.

        Args:
            file_id (str): The ID of the file to download.

        Returns:
            Result: Result object indicating success or failure.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()

            return Result(
                success=True,
                message="File downloaded successfully.",
                data=file.getvalue(),
            )

        except HttpError as error:
            return Result(
                success=False,
                message=f"An error occurred while trying to download the file: {error}",
            )
        except Exception as e:
            return Result(
                success=False,
                message=f"An unexpected error occurred: {e}",
            )
