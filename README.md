# 📄 Google Drive AI Summarizer

An intelligent document processing system that automatically extracts and summarizes files from Google Drive folders using AI-powered text analysis.

## 🎯 Project Overview

This application combines Django and FastAPI to provide a seamless document summarization workflow:

- **Django** (Port 8001) - Web interface and user interactions
- **FastAPI** (Port 8000) - AI processing backend with Google Drive integration
- **Google Drive API** - Secure OAuth 2.0 access to cloud documents
- **OpenAI/Gemini API** - Intelligent text summarization

## 🏗️ Architecture

```
Google_drive_ai_summarizer/
│
├── core/                          # Django project configuration
│   ├── settings.py                # Django settings with env loading
│   ├── urls.py                    # Main URL routing
│   └── wsgi.py                    # WSGI application
│
├── dashboard/                     # Web interface
│   ├── views.py                   # View logic (calls FastAPI)
│   ├── urls.py                    # Dashboard routes
│   └── templates/
│       └── dashboard/
│           └── index.html         # Main UI
│
├── ai_service/                    # FastAPI AI backend
│   ├── main.py                    # FastAPI app + endpoints
│   ├── drive_client.py            # Google Drive OAuth + file download
│   ├── parsers.py                 # PDF/DOCX/TXT text extraction
│   └── summarizer.py              # AI summarization logic
│
├── .env                           # Environment variables (YOU CREATE THIS)
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── manage.py                      # Django management script
└── README.md                      # This file
```

## ✨ Features

- 🔐 **OAuth 2.0** - Secure Google Drive authentication
- 📁 **Batch Processing** - Process multiple files at once
- 📄 **Multi-Format** - PDF, DOCX, TXT support
- 🤖 **AI Summaries** - Powered by OpenAI/Gemini
- 📊 **Dashboard** - Interactive results display
- 📥 **CSV Export** - Download summaries as CSV
- ⚡ **Async Processing** - Fast parallel operations

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **pip** package manager
- **Google Cloud Console account** (free tier works)
- **OpenAI API key** OR **Google Gemini API key**
- **Git** (optional, for cloning)

---

## 🚀 Complete Setup Guide

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <your-repo-url>
cd Google_drive_ai_summarizer

# Or download and extract ZIP, then navigate to the folder
```

### Step 2: Create Virtual Environment

**On Windows (PowerShell or CMD):**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1  

# You should see (venv) in your terminal prompt
```

**On Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
# You should see (venv) in your terminal prompt
```

> **Important:** Keep this terminal open! You'll use it later.

### Step 3: Install Dependencies

With virtual environment activated:

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r .\requirements.txt
```

This will install Django, FastAPI, Google Drive API, OpenAI, and other dependencies.

### Step 4: Set Up Environment Variables

1. **Create your `.env` file:**

**Windows:**
```bash
copy .env.example .env
```

**Linux/macOS:**
```bash
cp .env.example .env
```

2. **Edit the `.env` file** with your text editor and fill in these values:

```env
# Google OAuth Credentials (from Step 5)
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth/callback
GOOGLE_DRIVE_FOLDER_ID=your-default-folder-id (optional)

# AI API Keys (at least one required)
GOOGLE_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### Step 5: Configure Google Drive API

1. **Go to Google Cloud Console:** https://console.cloud.google.com/

2. **Create/Select a Project:**
   - Click "Select a project" → "New Project"
   - Name it (e.g., "Drive Summarizer")
   - Click "Create"

3. **Enable Google Drive API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click it and press "Enable"

4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure the OAuth consent screen:
     - Choose "External" (unless you have Google Workspace)
     - Fill in app name and your email
     - Add scopes: `./auth/drive.readonly`
     - Add test users (your email)
     - Save and continue
   - Back to Create OAuth client ID:
     - Application type: **Web application**
     - Name: "Drive Summarizer Client"
     - Authorized redirect URIs: `http://localhost:8000/oauth/callback`
     - Click "Create"

5. **Copy Credentials:**
   - Copy the **Client ID** and **Client Secret**
   - Paste them into your `.env` file

### Step 6: Get AI API Key

**Option A - Google Gemini (Free tier available):**
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key to `GOOGLE_API_KEY` in `.env`

**Option B - OpenAI:**
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key to `OPENAI_API_KEY` in `.env`

### Step 7: Initialize Database

```bash
# Run Django migrations
python manage.py migrate
```

You should see output like "Applying contenttypes.0001_initial... OK"

---

## ▶️ Running the Application

You need to run **TWO services simultaneously** in **TWO separate terminals**.

### Terminal 1: FastAPI Backend (AI Service)

**Windows:**
```bash
# Navigate to project folder
cd C:\Users\lenovo\.matplotlib\Google_drive_ai_summarizer

# Activate virtual environment
.\.venv\Scripts\Activate.ps1  

# Start FastAPI on port 8000
python -m uvicorn ai_service.main:app --reload --port 8000
```

**Linux/macOS:**
```bash
# Navigate to project folder
cd ~/Google_drive_ai_summarizer

# Activate virtual environment
source venv/bin/activate

# Start FastAPI on port 8000
python -m uvicorn ai_service.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Leave this terminal running!**

### Terminal 2: Django Web Interface

Open a **NEW terminal window/tab**:

**Windows:**
```bash
# Navigate to project folder
cd C:\Users\lenovo\.matplotlib\Google_drive_ai_summarizer

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start Django on port 8001
python manage.py runserver 8001
```

**Linux/macOS:**
```bash
# Navigate to project folder
cd ~/Google_drive_ai_summarizer

# Activate virtual environment
source venv/bin/activate

# Start Django on port 8001
python manage.py runserver 8001
```

**Expected Output:**
```
Django version X.X.X, using settings 'core.settings'
Starting development server at http://127.0.0.1:8001/
Quit the server with CTRL-BREAK (or CTRL-C on Linux).
```

✅ **Leave this terminal running too!**

---

## 🌐 Access the Application

1. **Open your browser** and go to:
   ```
   http://127.0.0.1:8001
   ```
   or
   ```
   http://localhost:8001
   ```

2. **You should see the dashboard!**

---

## 📖 How to Use

### First Time: Authenticate with Google Drive

1. Click **"Connect to Google Drive"** button on the dashboard
2. Sign in with your Google account
3. Grant permissions (read-only access to Drive)
4. You'll be redirected back to the dashboard
5. Authentication is saved - you won't need to do this again

### Processing Files

1. **Get Your Folder ID:**
   - Open Google Drive in your browser
   - Navigate to the folder you want to process
   - Copy the folder ID from the URL:
     ```
     https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ
                                             └─────────────┬─────────────┘
                                                      Folder ID
     ```

2. **Enter Folder ID** in the dashboard input field

3. **Select File Types** you want to process (PDF, DOCX, TXT)

4. **Click "Summarize Files"**

5. **Wait for Processing** - you'll see:
   - Files being downloaded
   - Text extraction
   - AI summarization
   - Results displayed in table

6. **Download Results** - Click "Download CSV" to export summaries

---

## 🔧 Configuration Options

### Change AI Model

Edit `.env`:
```env
# For OpenAI
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4 for better quality

# For Gemini (handled automatically)
GOOGLE_API_KEY=your-key
```

### Adjust Summary Length

Edit `ai_service/summarizer.py`:
```python
def summarize_text(text: str, filename: str = "", max_tokens: int = 500):
    # Change max_tokens for longer/shorter summaries
```

### Change Ports

If ports 8000 or 8001 are in use:

**FastAPI:**
```bash
python -m uvicorn ai_service.main:app --reload --port 8002
```

**Django:**
```bash
python manage.py runserver 8003
```

Update `GOOGLE_REDIRECT_URI` in `.env` accordingly.

---

## �️ API Endpoints

### FastAPI Service (Port 8000)

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /summarize` - Process files and generate summaries

**Example Request:**
```json
{
  "folder_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
  "file_types": ["pdf", "docx", "txt"]
}
```

**Example Response:**
```json
{
  "files": [
    {
      "name": "document.pdf",
      "type": "application/pdf",
      "size": "1.2MB",
      "summary": "This document discusses...",
      "status": "success"
    }
  ],
  "total_files": 1
}
```

### Django Application (Port 8001)

- `GET /` - Main dashboard
- `POST /summarize/` - Forward request to FastAPI
- `GET /download-csv/` - Download results as CSV

---

## 🐛 Troubleshooting

### Problem: "Cannot connect to AI service"
**Solution:**
- Make sure FastAPI is running on port 8000 (check Terminal 1)
- Verify the terminal shows "Uvicorn running on http://127.0.0.1:8000"
- Check if any firewall is blocking port 8000

### Problem: "Module not found" errors
**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall requirements
pip install -r requirements.txt
```

### Problem: "Google Drive authentication fails"
**Solution:**
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
- Check that redirect URI in Google Cloud Console is: `http://localhost:8000/oauth/callback`
- Make sure FastAPI is running when you click "Connect to Google Drive"
- Clear browser cookies and try again

### Problem: "OpenAI/Gemini API error"
**Solution:**
- Verify your API key is correct in `.env`
- Check your API account has available credits/quota
- For Gemini: Ensure you're using the correct API key format
- For OpenAI: Check https://platform.openai.com/account/usage

### Problem: "Error extracting text from PDF"
**Solution:**
- Some PDFs are scanned images without selectable text (need OCR)
- Check if PDF is password-protected
- Try opening the PDF in a reader first to verify it has text

### Problem: "Port already in use"
**Solution:**
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/macOS - Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different ports (see Configuration Options above)
```

### Problem: Virtual environment not activating
**Solution:**

**Windows PowerShell Execution Policy Error:**
```bash
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
venv\Scripts\activate
```

**Linux/macOS Permission Error:**
```bash
# Make activate script executable
chmod +x venv/bin/activate

# Then activate
source venv/bin/activate
```

---

## 📝 Quick Command Reference

### Deactivate Virtual Environment
```bash
# Both Windows and Linux/macOS
deactivate
```

### Restart Both Services
**Windows (Terminal 1):**
```bash
cd C:\Users\lenovo\.matplotlib\Google_drive_ai_summarizer
venv\Scripts\activate
python -m uvicorn ai_service.main:app --reload --port 8000
```

**Windows (Terminal 2):**
```bash
cd C:\Users\lenovo\.matplotlib\Google_drive_ai_summarizer
venv\Scripts\activate
python manage.py runserver 8001
```

**Linux/macOS (Terminal 1):**
```bash
cd ~/Google_drive_ai_summarizer
source venv/bin/activate
python -m uvicorn ai_service.main:app --reload --port 8000
```

**Linux/macOS (Terminal 2):**
```bash
cd ~/Google_drive_ai_summarizer
source venv/bin/activate
python manage.py runserver 8001
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Reset Database
```bash
# Delete database
rm db.sqlite3  # Linux/macOS
del db.sqlite3  # Windows

# Recreate
python manage.py migrate
```

---

## 🔒 Security Best Practices

- ✅ **Never commit** `.env` file to Git
- ✅ **Never commit** `token.pickle` or OAuth tokens
- ✅ Add `.env` and `token.pickle` to `.gitignore`
- ✅ Use strong, unique API keys
- ✅ Set `DJANGO_DEBUG=False` in production
- ✅ Rotate API keys regularly
- ✅ Use HTTPS in production
- ✅ Limit OAuth scopes to read-only

---

## 📦 Project Structure Explained

```
Google_drive_ai_summarizer/
│
├── ai_service/              # FastAPI backend (Port 8000)
│   ├── main.py             # API endpoints (health, summarize)
│   ├── drive_client.py     # Google Drive OAuth & file download
│   ├── parsers.py          # Extract text from PDF/DOCX/TXT
│   └── summarizer.py       # Call OpenAI/Gemini for summaries
│
├── dashboard/              # Django frontend (Port 8001)
│   ├── views.py           # Handle requests, call FastAPI
│   ├── urls.py            # URL routing
│   └── templates/         # HTML templates
│
├── core/                  # Django project settings
│   ├── settings.py        # Configuration (loads .env)
│   └── urls.py            # Root URL config
│
├── .env                   # YOUR secrets (create from .env.example)
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
├── manage.py              # Django CLI tool
├── db.sqlite3            # SQLite database (auto-created)
└── README.md             # This file
```

---

## 🚀 What Happens When You Run the App?

1. **FastAPI (Port 8000)** starts and waits for requests
2. **Django (Port 8001)** serves the web interface
3. **User visits** `http://localhost:8001` in browser
4. **User authenticates** with Google (OAuth via FastAPI)
5. **User enters** Google Drive folder ID
6. **Django receives** the request and forwards to FastAPI
7. **FastAPI:**
   - Downloads files from Google Drive
   - Extracts text using parsers
   - Sends text to OpenAI/Gemini
   - Returns summaries to Django
8. **Django displays** results in the web interface
9. **User downloads** CSV export

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs via issues
- Suggest features
- Submit pull requests
- Improve documentation

---

## 📄 License

MIT License - Feel free to use for personal or commercial projects.

---

## 🙏 Credits

Built with:
- **Django** - Web framework
- **FastAPI** - API framework
- **Google Drive API** - File access
- **OpenAI GPT / Google Gemini** - AI summarization
- **Python** - Programming language

---

## 📞 Support

Need help?
1. Check the **Troubleshooting** section above
2. Review error messages in both terminals
3. Open an issue on GitHub
4. Check logs in terminal output

---

**Made with ❤️ for automating document summarization**

**Happy Summarizing! 🎉**
