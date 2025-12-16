"""
Google Drive Client
Handles OAuth authentication and file operations with Google Drive API
"""
import os
import io
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pickle

# Allow insecure transport for local development (HTTP instead of HTTPS)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveClient:
    """Client for interacting with Google Drive API"""
    
    def __init__(self, credentials=None):
        """
        Initialize the Google Drive client with authentication
        
        Args:
            credentials: Optional pre-authenticated credentials object
        """
        self.credentials = credentials
        self.service = None
        if credentials:
            self.service = build('drive', 'v3', credentials=credentials)
        else:
            self._authenticate()
    
    def _authenticate(self):
        """Handle OAuth 2.0 authentication flow using environment variables"""
        creds = None
        token_path = os.getenv('GOOGLE_DRIVE_TOKEN_PATH', 'token.pickle')
        
        # Load saved credentials if available
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed credentials
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            else:
                # Need to initiate OAuth flow
                raise Exception(
                    "No valid credentials found. Please authenticate via the web interface first."
                )
        
        self.credentials = creds
        self.service = build('drive', 'v3', credentials=creds)
    
    @staticmethod
    def create_oauth_flow(redirect_uri=None):
        """
        Create OAuth2 flow for authentication
        
        Args:
            redirect_uri: Optional redirect URI (defaults to env variable)
            
        Returns:
            Flow object for OAuth authentication
        """
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = redirect_uri or os.getenv('GOOGLE_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError(
                "Missing OAuth credentials. Please set GOOGLE_CLIENT_ID, "
                "GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI in environment."
            )
        
        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        return flow
    
    @staticmethod
    def get_authorization_url():
        """
        Get the authorization URL for OAuth flow
        
        Returns:
            tuple: (authorization_url, state)
        """
        flow = GoogleDriveClient.create_oauth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return authorization_url, state
    
    @staticmethod
    def handle_oauth_callback(authorization_response, state=None):
        """
        Handle OAuth callback and exchange code for credentials
        
        Args:
            authorization_response: Full callback URL with code
            state: Optional state parameter for validation
            
        Returns:
            Credentials object
        """
        flow = GoogleDriveClient.create_oauth_flow()
        if state:
            flow.state = state
        
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials
        
        # Save credentials for future use
        token_path = os.getenv('GOOGLE_DRIVE_TOKEN_PATH', 'token.pickle')
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        return creds
    
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
