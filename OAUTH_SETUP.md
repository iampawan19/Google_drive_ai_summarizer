# Google OAuth2 Setup Guide

## Overview
This application now uses OAuth2 to authenticate with Google Drive, allowing secure access to your Drive folders without requiring a `credentials.json` file download.

## Setup Steps

### 1. Configure Environment Variables
Make sure your `.env` file contains the following OAuth credentials:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8001/oauth/callback
GOOGLE_DRIVE_FOLDER_ID=your-folder-id-here
OPENAI_API_KEY=your-openai-api-key
```

### 2. Google Cloud Console Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Select **Web application** as the application type
6. Add authorized redirect URI: `http://localhost:8001/oauth/callback`
7. Copy the Client ID and Client Secret to your `.env` file

### 3. Start the Application

```bash
# Start Django server
python manage.py runserver 8001

# In another terminal, start FastAPI service
cd ai_service
uvicorn main:app --reload --port 8000
```

### 4. Authenticate

1. Open your browser to `http://localhost:8001`
2. Click the **"Connect to Google Drive"** button
3. Sign in with your Google account
4. Grant permissions to access Google Drive (read-only)
5. You'll be redirected back to the dashboard

### 5. Use the Application

Once authenticated:
- The token is saved in `token.pickle` for future sessions
- Enter a Google Drive folder ID
- Select file types to process
- Click "Summarize Files"

## OAuth Flow Details

### Authentication Process

1. **Authorization Request**: User clicks "Connect to Google Drive" → Redirected to Google's consent page
2. **User Consent**: User signs in and grants permissions
3. **Callback**: Google redirects to `/oauth/callback` with authorization code
4. **Token Exchange**: Application exchanges code for access & refresh tokens
5. **Token Storage**: Tokens saved in `token.pickle` for reuse
6. **API Access**: Application uses tokens to access Google Drive API

### Token Refresh

- Access tokens expire after 1 hour
- The application automatically refreshes using the refresh token
- No need to re-authenticate unless refresh token is revoked

### Security Notes

- OAuth tokens are stored locally in `token.pickle`
- Add `token.pickle` to `.gitignore` to prevent committing tokens
- Never share your Client Secret or API keys
- Use read-only scope to minimize security risks

## Troubleshooting

### "No valid credentials found" Error
- Click "Connect to Google Drive" to authenticate
- Delete `token.pickle` and re-authenticate if corrupted

### Redirect URI Mismatch
- Ensure the redirect URI in `.env` matches Google Cloud Console settings
- Must be exactly: `http://localhost:8001/oauth/callback`

### Access Denied
- Check that Google Drive API is enabled in Google Cloud Console
- Verify the folder ID is correct and accessible by your Google account

## Code Structure

- **`ai_service/drive_client.py`**: OAuth2 flow implementation
  - `get_authorization_url()`: Generate consent page URL
  - `handle_oauth_callback()`: Exchange code for tokens
  - `create_oauth_flow()`: Create Flow object from env vars

- **`dashboard/views.py`**: Django views for OAuth
  - `oauth_authorize()`: Initiate OAuth flow
  - `oauth_callback()`: Handle Google's callback
  - `index()`: Check authentication status

- **`dashboard/urls.py`**: OAuth routes
  - `/oauth/authorize/`: Start OAuth flow
  - `/oauth/callback/`: OAuth callback endpoint
