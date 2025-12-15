"""
Google Drive Client
Handles OAuth authentication and file operations with Google Drive API
"""
import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pickle

# Scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveClient:
    """Client for interacting with Google Drive API"""
    
    def __init__(self):
        """Initialize the Google Drive client with authentication"""
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Handle OAuth 2.0 authentication flow"""
        creds = None
        token_path = os.getenv('GOOGLE_DRIVE_TOKEN_PATH', 'token.pickle')
        credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', 'credentials.json')
        
        # Load saved credentials if available
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"Google Drive credentials file not found at {credentials_path}. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.service = build('drive', 'v3', credentials=creds)
    
    def list_files_in_folder(self, folder_id: str, file_types: list = None):
        """
        List files in a Google Drive folder
        
        Args:
            folder_id: Google Drive folder ID
            file_types: List of file extensions to filter (e.g., ['pdf', 'docx'])
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            # Build query
            query = f"'{folder_id}' in parents and trashed=false"
            
            # Add file type filter if specified
            if file_types:
                mime_types = []
                for ext in file_types:
                    if ext.lower() == 'pdf':
                        mime_types.append("mimeType='application/pdf'")
                    elif ext.lower() == 'docx':
                        mime_types.append("mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'")
                    elif ext.lower() == 'txt':
                        mime_types.append("mimeType='text/plain'")
                
                if mime_types:
                    query += " and (" + " or ".join(mime_types) + ")"
            
            # Execute API call
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime)",
                pageSize=100
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            raise Exception(f"Error listing files from Google Drive: {str(e)}")
    
    def download_file(self, file_id: str, file_name: str, download_dir: str = 'temp_downloads'):
        """
        Download a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            file_name: Name of the file
            download_dir: Directory to save downloaded files
            
        Returns:
            Path to downloaded file
        """
        try:
            # Create download directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            
            # Build file path
            file_path = os.path.join(download_dir, file_name)
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Error downloading file {file_name}: {str(e)}")
    
    def get_folder_metadata(self, folder_id: str):
        """
        Get metadata for a specific folder
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            Folder metadata dictionary
        """
        try:
            folder = self.service.files().get(
                fileId=folder_id,
                fields="id, name, mimeType, createdTime"
            ).execute()
            return folder
        except Exception as e:
            raise Exception(f"Error getting folder metadata: {str(e)}")
