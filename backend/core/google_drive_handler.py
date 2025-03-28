"""
This module provides a class `GoogleDriveHandler`:
    - Handles authentication.
    - Handles files upload.
Classes:
    GoogleDriveHandler: Handles authentication and files upload.
Usage example:
    handler = GoogleDriveHandler('path/to/credentials.json', ['https://www.googleapis.com/auth/drive'])
    handler.upload_file('path/to/local/file.txt')
"""

import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleDriveHandler:
    """Handles authentication and files upload to Google Drive"""

    def __init__(self, config_path):
        self.config = config_path
        self.service = self.authenticate()

    def authenticate(self):
        """The file token.pickle stores the user's access and refresh tokens
        Created automatically when the auth flow completes the 1st time."""
        creds = None
        token_path = "token.pickle"

        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_config = {"web": self.config["web"]}
                flow = InstalledAppFlow.from_client_config(
                    client_config, self.config.google_drive_api.scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
        service = build("drive", "v3", credentials=creds)
        return service

    def upload_file(self, uploaded_file, folder_id=None):
        """
        Uploads a file to Google Drive.

        Args:
            file_path (str): Local file path to upload.
            folder_id (str, optional): Google Drive folder ID to upload the file to.

        Returns:
            str: Uploaded file ID if successful, else None.
        """

        try:
            file_metadata = {"name": uploaded_file.name}

            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaIoBaseUpload(
                uploaded_file, mimetype="text/csv", resumable=True
            )
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

        except HttpError as error:
            print(f"An error occurred: {error}")
            file = None

        return file.get("id")
