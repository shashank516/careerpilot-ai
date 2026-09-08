# Pathway AI

Pathway AI is a Streamlit career workspace that helps users build resumes, compare them with job descriptions, create applications, and practise interviews.

## Features

- Secure signup and login with salted password hashes
- User-specific SQLite storage for generated resumes
- AI-assisted resume generation with three PDF styles
- PDF/DOCX resume analysis against a job description
- Tailored cover letter, recruiter message, LinkedIn message, and introduction
- Role-specific mock interview feedback
- Demo fallback when no AI key is configured

## Project structure

```text
careerpilot-ai/
├── app.py                  # Streamlit user interface
├── backend/                # Authentication and SQLite storage
│   ├── auth_service.py
│   ├── database.py
│   └── resume_service.py
├── services/               # AI, parsing, and PDF-export services
│   ├── ai_service.py
│   ├── document_parser.py
│   └── resume_export.py
├── .streamlit/config.toml  # Fixed light theme
├── requirements.txt
└── PROJECT_REPORT.md
```

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Configure AI

Create a local `.env` file. It is ignored by Git and must never be uploaded.

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

You can alternatively use `OPENAI_API_KEY` and, optionally, `OPENAI_MODEL`.

Without a key, the app continues in demo mode with fallback responses.

## Deploy to Streamlit Community Cloud

1. Push the repository to GitHub.
2. In Community Cloud, select repository `shashank516/careerpilot-ai`, branch `main`, and entrypoint `app.py`.
3. Add the AI key in **App settings → Secrets**.
4. Deploy.

SQLite is suitable for local development and demonstrations. Use a managed database such as PostgreSQL or Supabase for permanent cloud user data.

## Security notes

- Passwords are stored as salted PBKDF2 hashes, never plain text.
- Every saved resume is linked to its owner and retrieved with a user-ID check.
- `.env` and local SQLite database files are excluded by `.gitignore`.
