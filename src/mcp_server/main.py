#!/usr/bin/env python3
"""
Google Drive MCP server that integrates with a shared Postgres database.
OAuth tokens are stored in the UserToken table (managed by Node/Prisma).
"""

import os
import io
import psycopg2
from datetime import datetime
from typing import Any, Optional, Dict

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from fastmcp import FastMCP
# from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Initialize MCP server
mcp = FastMCP()


# -------------------------------
# DB Helpers
# -------------------------------
def get_user_tokens(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch tokens for a given user from Postgres."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT "accessToken", "refreshToken", "expiryDate", "scope", "tokenType"
        FROM "UserToken"
        WHERE "userId" = %s
        """,
        (user_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    return {
        "accessToken": row[0],
        "refreshToken": row[1],
        "expiryDate": row[2],
        "scope": row[3],
        "tokenType": row[4],
    }


def save_user_tokens(user_id: str, creds: Credentials):
    """Update refreshed tokens back into Postgres."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE "UserToken"
        SET "accessToken"=%s,
            "refreshToken"=%s,
            "expiryDate"=%s,
            "scope"=%s,
            "tokenType"=%s
        WHERE "userId"=%s
        """,
        (
            creds.token,
            creds.refresh_token,
            creds.expiry if creds.expiry else None,
            " ".join(creds.scopes) if creds.scopes else None,
            creds.token_uri,
            user_id,
        )
    )
    conn.commit()
    cur.close()
    conn.close()


# -------------------------------
# Google Drive Client
# -------------------------------
class GoogleDriveClient:
    """Client for interacting with Google Drive API using DB-stored tokens."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.service = self._get_service()

    def _get_credentials(self) -> Credentials:
        tokens = get_user_tokens(self.user_id)
        if not tokens:
            raise RuntimeError(f"No tokens found for user {self.user_id}")

        creds = Credentials(
            tokens["accessToken"],
            refresh_token=tokens["refreshToken"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=self.SCOPES,
        )

        # Refresh if expired
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    save_user_tokens(self.user_id, creds)
                except RefreshError as e:
                    raise RuntimeError(f"Error refreshing token: {e}")
            else:
                raise RuntimeError("Invalid or missing credentials")

        return creds

    def _get_service(self):
        creds = self._get_credentials()
        return build('drive', 'v3', credentials=creds)

    def search_files(self, query: str, page_size: int = 10) -> dict:
        """Search for files in Google Drive."""
        try:
            results = self.service.files().list(
                q=f"name contains '{query}'",
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, webViewLink)"
            ).execute()

            return {
                "files": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "mime_type": f["mimeType"],
                        "web_view_link": f["webViewLink"],
                    }
                    for f in results.get("files", [])
                ],
                "next_page_token": results.get("nextPageToken"),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_file(self, file_id: str) -> dict:
        try:
            # Get file metadata
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, webViewLink"
            ).execute()

            mime_type = file_metadata.get("mimeType")

            # Handle Google Docs/Sheets/Slides with export
            if mime_type.startswith("application/vnd.google-apps"):
                if mime_type == "application/vnd.google-apps.document":
                    export_mime = "text/plain"
                elif mime_type == "application/vnd.google-apps.spreadsheet":
                    export_mime = "text/csv"
                elif mime_type == "application/vnd.google-apps.presentation":
                    export_mime = "text/plain"
                else:
                    export_mime = "text/plain"

                exported = self.service.files().export(
                    fileId=file_id, mimeType=export_mime
                ).execute()
                # content_text= exported.lstrip("\ufeff")

                return {
                    "metadata": file_metadata,
                    "content": exported
                }

            # Otherwise, download file directly
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            return {
                "metadata": file_metadata,
                "content": fh.getvalue().decode("utf-8", errors="ignore"),
            }

        except Exception as e:
            return {"error": str(e)}


# -------------------------------
# MCP Tool Definitions
# -------------------------------
@mcp.tool()
def gdrive_search(query: str, user_id: str, page_size: int = 10) -> dict:
    """Search for files in Google Drive."""
    drive_client = GoogleDriveClient(user_id)
    return drive_client.search_files(query=query, page_size=page_size)


@mcp.tool()
def gdrive_read_file(file_id: str, user_id: str) -> dict:
    """Read file content + metadata from Google Drive."""
    drive_client = GoogleDriveClient(user_id)
    return drive_client.get_file(file_id=file_id)


# -------------------------------
# Main Entry Point
# -------------------------------
def main() -> None:
    print('started mcp Google Drive MCP server on http://localhost:8000')
    mcp.run(transport="http", port=8000)  # or HTTP if you want `--http` option


if __name__ == "__main__":
    main()
