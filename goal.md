google_drive_ai_summarizer/
│
├── core/                          # Django project (platform shell)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                # env loading, installed apps
│   ├── urls.py                    # routes to dashboard
│   └── wsgi.py
│
├── dashboard/                     # UI + output layer
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                  # (intentionally empty)
│   ├── urls.py                    # index, csv download
│   ├── views.py                   # calls FastAPI, renders results
│   ├── templates/
│   │   └── dashboard/
│   │       └── index.html         # simple table UI
│   └── migrations/
│
├── ai_service/                    # FastAPI + GenAI logic
│   ├── __init__.py
│   ├── main.py                    # FastAPI app + endpoint
│   ├── drive_client.py            # Google Drive OAuth + download
│   ├── parsers.py                 # PDF/DOCX/TXT extraction
│   └── summarizer.py              # OpenAI summarization
│
├── .env                           # real secrets (ignored)
├── .env.example                   # documented variables
├── .gitignore
├── requirements.txt
├── manage.py
└── README.md
