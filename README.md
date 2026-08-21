# CareerPilot AI

CareerPilot AI is a Streamlit GenAI career studio for creating resumes, matching them to jobs, writing applications, and practicing interviews.

## Run on Windows

Open PowerShell in this folder and run:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

If the virtual environment does not exist yet:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app works in demo mode without an API key. To enable live AI responses, copy `.env.example` to `.env` and replace the placeholder with a newly created API key.

Never commit `.env` or place a real API key in `.env.example`.
