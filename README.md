# CareerPilot AI

CareerPilot AI is a Streamlit GenAI career studio for creating resumes, matching them to jobs, writing applications, and practicing interviews.

The resume builder includes three selectable export styles inspired by the supplied references:

- **Classic ATS:** clean section rules and conservative formatting for online applications.
- **Modern Timeline:** blue accent hierarchy and a more visual professional layout.
- **Bold Minimal:** stronger typography and compact profile-led sections.

The application writer also accepts a company name and generates a cover letter, recruiter message, LinkedIn message, and self-introduction. Mock interviews support Behavioral, Technical, HR, and Project-based modes.

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

The app works in demo mode without an API key. To enable live AI responses locally, create `.env` and add a newly created Groq key:

```env
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

For Streamlit Cloud, add the same values under the app's **Settings -> Secrets**. Do not upload `.env`.

Never commit `.env` or place a real API key in `.env.example`.
