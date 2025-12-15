# 📄 Google Drive AI Summarizer

An intelligent document processing system that automatically extracts and summarizes files from Google Drive folders using AI-powered text analysis.

## 🎯 Project Overview

This application combines Django and FastAPI to provide a seamless document summarization workflow:

- **Django** serves the web interface and handles user interactions
- **FastAPI** processes files and generates AI summaries using OpenAI's GPT models
- **Google Drive API** provides secure access to cloud-stored documents
- **OpenAI API** generates intelligent, contextual summaries

## 🏗️ Architecture

```
google_drive_ai_summarizer/
│
├── core/                          # Django project (platform shell)
│   ├── settings.py                # Configuration with env loading
│   ├── urls.py                    # Routes to dashboard
│   └── ...
│
├── dashboard/                     # UI + output layer
│   ├── urls.py                    # Dashboard routes
│   ├── views.py                   # Calls FastAPI, renders results
│   └── templates/
│       └── dashboard/
│           └── index.html         # Interactive UI
│
├── ai_service/                    # FastAPI + GenAI logic
│   ├── main.py                    # FastAPI app + endpoints
│   ├── drive_client.py            # Google Drive OAuth + download
│   ├── parsers.py                 # PDF/DOCX/TXT extraction
│   └── summarizer.py              # OpenAI summarization
│
├── .env                           # Environment variables (create from .env.example)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## ✨ Features

- 🔐 **Secure OAuth 2.0** authentication with Google Drive
- 📁 **Batch Processing** of multiple files from any folder
- 📄 **Multi-Format Support**: PDF, DOCX, and TXT files
- 🤖 **AI-Powered Summaries** using OpenAI GPT models
- 📊 **Interactive Dashboard** with real-time results
- 📥 **CSV Export** for easy data management
- ⚡ **Fast Processing** with asynchronous operations
- 🎨 **Modern UI** with responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud Console account (for Drive API)
- OpenAI API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Google_drive_ai_summarizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
```

Required environment variables:
- `DJANGO_SECRET_KEY`: Django secret key for security
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_DRIVE_CREDENTIALS_PATH`: Path to your Google OAuth credentials file
- `FASTAPI_SERVICE_URL`: URL where FastAPI will run (default: http://127.0.0.1:8000)

### 3. Set Up Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Drive API**
4. Create **OAuth 2.0 credentials** (Desktop application type)
5. Download the credentials file as `credentials.json`
6. Place `credentials.json` in the project root directory

### 4. Get OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Add it to your `.env` file

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start the Applications

You need to run both services simultaneously in separate terminals:

**Terminal 1 - FastAPI Service (AI Backend):**
```bash
uvicorn ai_service.main:app --reload
# Runs on http://127.0.0.1:8000
```

**Terminal 2 - Django Application (Web Interface):**
```bash
python manage.py runserver 8001
# Runs on http://127.0.0.1:8001
```

> **Note:** Django runs on port 8001 to avoid conflict with FastAPI on port 8000

### 7. Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:8001
```

The Django web interface (port 8001) will communicate with the FastAPI service (port 8000) in the background.

## 📖 How to Use

1. **Get Your Folder ID**
   - Open the Google Drive folder you want to process
   - Copy the folder ID from the URL
   - Example: `https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ`
   - Folder ID: `1aBcDeFgHiJkLmNoPqRsTuVwXyZ`

2. **Process Files**
   - Paste the folder ID in the dashboard
   - Select file types to process (PDF, DOCX, TXT)
   - Click "Summarize Files"
   - Wait for the AI to process your documents

3. **View Results**
   - Review summaries in the interactive table
   - Check statistics (total files, successful, errors)
   - Download results as CSV for further analysis

## 🔧 Configuration

### OpenAI Model Selection

You can change the AI model in `.env`:

```env
# Options: gpt-3.5-turbo (faster, cheaper) or gpt-4 (more accurate)
OPENAI_MODEL=gpt-3.5-turbo
```

### File Type Support

The application currently supports:
- **PDF**: Using PyPDF2 for text extraction
- **DOCX**: Using python-docx for document parsing
- **TXT**: Direct text file reading with encoding detection

### Customizing Summary Length

Edit `ai_service/summarizer.py` to adjust the `max_tokens` parameter:

```python
def summarize_text(text: str, filename: str = "", max_tokens: int = 500):
    # Increase max_tokens for longer summaries
    pass
```

## 🛠️ API Endpoints

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

## 🐛 Troubleshooting

### "Cannot connect to AI service"
- Ensure FastAPI is running on port 8000
- Check `FASTAPI_SERVICE_URL` in `.env`

### "Google Drive credentials not found"
- Verify `credentials.json` is in the project root
- Check `GOOGLE_DRIVE_CREDENTIALS_PATH` in `.env`

### "OpenAI API error"
- Verify your API key is correct
- Check your OpenAI account has available credits
- Ensure `OPENAI_API_KEY` is set in `.env`

### "Error extracting text from PDF"
- Some PDFs may be scanned images without text
- Try using OCR tools to extract text first
- Check if the PDF is password-protected

## 📝 Development

### Running Tests

```bash
# Django tests
python manage.py test

# FastAPI tests (if implemented)
pytest ai_service/
```

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .
```

## 🔒 Security Notes

- Never commit `.env` file or `credentials.json` to version control
- Use strong, unique secret keys in production
- Set `DJANGO_DEBUG=False` in production
- Regularly rotate API keys
- Use HTTPS in production deployments

## 📦 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in Django settings
- [ ] Use a production-grade database (PostgreSQL, MySQL)
- [ ] Configure static file serving
- [ ] Set up HTTPS/SSL certificates
- [ ] Use environment-specific settings
- [ ] Implement proper logging
- [ ] Set up monitoring and error tracking
- [ ] Configure CORS properly
- [ ] Use production ASGI server (Gunicorn + Uvicorn)

### Suggested Stack

- **Web Server**: Nginx
- **ASGI Server**: Gunicorn + Uvicorn workers
- **Database**: PostgreSQL
- **Caching**: Redis
- **Hosting**: AWS, Google Cloud, or Azure

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- OpenAI for GPT models
- Google for Drive API
- Django and FastAPI communities

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review error logs

---

**Built with ❤️ using Django, FastAPI, and OpenAI**
