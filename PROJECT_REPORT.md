# Pathway AI
## An Intelligent Resume and Interview Coaching Platform

**Project Type:** Generative Artificial Intelligence Application  
**Technology:** Python, Streamlit, OpenAI-compatible LLM API  
**Repository:** https://github.com/shashank516/careerpilot-ai

---

## 1. Abstract

Pathway AI is a Generative AI-based career development platform designed to help students and job seekers prepare for employment. The application creates professional resumes from user-provided information, analyzes existing PDF and DOCX resumes, compares resumes with job descriptions, generates tailored application content, and provides personalized mock interview feedback.

The system uses an OpenAI-compatible language model interface to understand user information and generate structured career content. It also includes a demo fallback mode, allowing the core interface to operate without an API key. The application is designed with a truthfulness rule: generated content must use only information supplied by the user and must not invent employers, skills, achievements, dates, or performance metrics.

CareerPilot AI combines resume creation, resume evaluation, job matching, application writing, and interview practice in one platform. This creates a complete career preparation workflow rather than a basic chatbot or isolated resume generator.

**Keywords:** Generative AI, resume builder, ATS analysis, job matching, interview coaching, natural language processing, Streamlit.

---

## 2. Introduction

A resume is often the first document reviewed by an employer or an Applicant Tracking System (ATS). Many students and job seekers find it difficult to describe their skills, present projects professionally, identify missing job requirements, and prepare for interviews. Existing tools frequently provide only one service, such as resume templates or grammar correction.

CareerPilot AI addresses this problem by providing multiple connected services in one application. A user can enter personal and professional details, generate a resume, compare it with a target job, create an application pack, and practice interview answers based on the selected role.

The project demonstrates how Generative AI can be applied to a practical career-support problem while keeping the user in control of final content.

---

## 3. Problem Statement

Students and job seekers commonly face the following difficulties:

- Lack of knowledge about professional resume structure
- Difficulty converting simple descriptions into strong achievement-oriented statements
- Inability to identify keywords required by a job description
- Low awareness of ATS-friendly resume formatting
- Difficulty writing tailored cover letters and recruiter messages
- Limited access to realistic interview practice
- Lack of useful feedback on communication and answer structure
- Risk of using inaccurate or exaggerated AI-generated content

There is a need for one accessible system that helps users create, improve, and use a resume while also preparing them for interviews.

---

## 4. Proposed Solution

CareerPilot AI provides a unified web application with four major workflows:

1. **Build Resume:** Collect user information and generate a structured professional resume.
2. **Analyze and Match:** Read an existing resume and compare it with a job description.
3. **Write Application:** Generate a cover letter, recruiter message, and self-introduction.
4. **Practice Interview:** Ask role-specific questions and evaluate the user's answers.

The application is implemented as a Streamlit interface. An AI service handles generation and analysis. Document parsing services extract text from PDF and DOCX files, while a PDF export service creates a downloadable resume.

---

## 5. Objectives

### Primary Objectives

- Develop a Generative AI-based career assistance application.
- Generate professional resumes from structured user information.
- Analyze resumes for relevance, ATS readiness, and evidence quality.
- Match resume content with job-description requirements.
- Generate tailored application materials.
- Conduct interactive text-based mock interviews.
- Provide useful, understandable feedback to users.

### Secondary Objectives

- Prevent fabricated user information.
- Provide a demo mode for testing without an API key.
- Support PDF and DOCX resume uploads.
- Allow the generated resume to be downloaded as a PDF.
- Build an interface that is simple for students and first-time users.

---

## 6. Scope of the Project

### Included in the MVP

- Resume information form
- AI-assisted resume generation
- Resume PDF export
- PDF resume text extraction
- DOCX resume text extraction
- Resume and job-description keyword comparison
- ATS and evidence scoring
- Cover-letter generation
- Recruiter-message generation
- Mock interview questions and feedback
- System and dark appearance modes
- Demo mode without a configured AI key

### Future Scope

- User authentication
- Database-backed profiles
- Multiple resume templates
- DOCX export
- Voice interview mode
- Speech-to-text and filler-word analysis
- Skill-gap learning roadmap
- Progress dashboard
- Cloud file storage
- Multi-language support
- Job-board integrations

---

## 7. System Modules

### 7.1 Resume Builder

The user provides their name, contact details, target role, summary, skills, education, experience, projects, certifications, and achievements. The AI organizes this content into a professional resume structure.

The system improves wording while preserving the user's meaning. For example, the input "Made a Python project for predicting house prices" can become "Developed a Python-based house price prediction model using regression algorithms and data preprocessing techniques."

The application displays the generated structured data and provides a PDF download.

### 7.2 Resume Analyzer

The user uploads a PDF or DOCX resume. The parser extracts the document text. The analyzer checks the resume against a supplied job description and returns:

- Overall match score
- ATS readiness score
- Evidence strength score
- Matching keywords
- Missing keywords
- Strengths
- Risks
- Recommendations

The analysis helps the user understand what to improve without claiming that an ATS score guarantees employment.

### 7.3 Job Description Matcher

The user pastes a job description. The system compares the words and concepts in the job description with the resume. It identifies relevant overlaps and missing terms. AI-generated review adds context and recommendations.

The matching result should be treated as guidance rather than a definitive hiring prediction.

### 7.4 Application Writer

The system uses resume details and a target job description to generate:

- Tailored cover letter
- Recruiter email or message
- "Tell me about yourself" response

The AI prompt instructs the system not to invent work history, achievements, or qualifications.

### 7.5 Mock Interview Coach

The user selects a role and difficulty level. The AI asks one question at a time. After the user submits an answer, the system evaluates relevance and clarity, identifies strengths and improvements, and creates a follow-up question.

Behavioral answers are evaluated using the STAR model:

- Situation
- Task
- Action
- Result

### 7.6 Appearance Control

The application provides System, Light, and Dark appearance options in the sidebar. System mode follows the browser or operating-system preference through CSS media queries. Light and Dark modes apply explicit application styles.

### 7.7 Security and Truthfulness Controls

The project includes the following controls:

- `.env` is excluded through `.gitignore`.
- API credentials are not included in the GitHub repository.
- The application supports demo mode when no credential is present.
- AI instructions prohibit fabricated experience and achievements.
- Users are told to review generated content before using it.

---

## 8. System Architecture

```text
+---------------------------+
|       Streamlit UI        |
| Forms, upload, navigation |
+-------------+-------------+
              |
              v
+---------------------------+
|       Application Layer   |
| Resume, match, interview  |
+-------------+-------------+
              |
      +-------+--------+
      |                |
      v                v
+-----------+    +------------+
| AI Service|    | File Tools |
| LLM calls |    | PDF/DOCX   |
+-----------+    +------------+
      |                |
      v                v
+---------------------------+
|     Output and Storage    |
| JSON results and PDF file |
+---------------------------+
```

### Architecture Explanation

1. The user interacts with the Streamlit interface.
2. The interface collects structured information or uploaded files.
3. The application layer sends requests to the appropriate service.
4. The AI service generates structured responses using an OpenAI-compatible API.
5. The document parser extracts text from PDF and DOCX files.
6. The resume export service creates a PDF from structured resume data.
7. The result is displayed or downloaded by the user.

---

## 9. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web interface and application runtime |
| OpenAI-compatible API | Generative AI responses |
| Groq-compatible endpoint | Optional support for `gsk_` keys |
| PyMuPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| ReportLab | PDF resume generation |
| python-dotenv | Local environment configuration |
| Git and GitHub | Version control and project hosting |
| HTML and CSS | Custom interface styling |

---

## 10. Project Structure

```text
careerpilot-ai/
|
|-- app.py
|-- requirements.txt
|-- README.md
|-- PROJECT_REPORT.md
|-- .env.example
|-- .gitignore
|
|-- services/
    |-- __init__.py
    |-- ai_service.py
    |-- document_parser.py
    |-- resume_export.py
```

### File Responsibilities

- `app.py`: Streamlit interface, navigation, forms, upload controls, appearance control, and session state.
- `services/ai_service.py`: AI client setup, resume generation, resume analysis, application generation, and interview feedback.
- `services/document_parser.py`: PDF and DOCX text extraction.
- `services/resume_export.py`: PDF resume generation.
- `requirements.txt`: Python dependencies.
- `.env.example`: Safe configuration template without a real credential.
- `.gitignore`: Prevents `.env`, `.venv`, and cache files from being uploaded.
- `README.md`: Installation and usage instructions.

---

## 11. AI Design

### Resume Generation Prompt Rules

The resume-generation service instructs the model to:

- Act as a truthful resume writer.
- Use only facts supplied by the user.
- Never invent employers, dates, skills, metrics, or achievements.
- Return predictable JSON fields.
- Rewrite vague content without changing its meaning.

### Analysis Prompt Rules

The analysis service instructs the model to:

- Compare the resume only with the supplied job description.
- Identify missing keywords as unknown requirements, not as proven deficiencies.
- Return scores and recommendations in structured JSON.
- Separate strengths, risks, and recommendations.

### Interview Prompt Rules

The interview service instructs the model to:

- Act as a supportive but rigorous coach.
- Evaluate only the answer that was provided.
- Use relevance and clarity criteria.
- Recommend improvements using the STAR method where appropriate.
- Generate the next question based on the selected role.

### Fallback Behavior

When no API key or compatible client is available, the system returns a local fallback response. This allows the interface, PDF generation, and basic matching features to be demonstrated without making an external API call.

---

## 12. Installation and Execution

### Requirements

- Windows, macOS, or Linux
- Python 3.10 or later recommended
- Internet connection for live AI responses
- An API key for live AI mode

### Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Environment Configuration

Create a file named `.env` in the project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

For a Groq key beginning with `gsk_`, use:

```env
OPENAI_API_KEY=your_groq_key_here
OPENAI_MODEL=llama-3.3-70b-versatile
```

### Start the Application

```powershell
streamlit run app.py
```

Open `http://localhost:8501` in a browser.

### Deployment

The project can be deployed through Streamlit Community Cloud using:

- Repository: `shashank516/careerpilot-ai`
- Branch: `main`
- Main file: `app.py`

The API key must be entered in Streamlit Cloud Secrets, not committed to GitHub.

---

## 13. User Workflow

```text
Start application
       |
       v
Choose a module
       |
       +--> Build resume --> Enter details --> Generate --> Download PDF
       |
       +--> Analyze match --> Upload resume --> Paste job --> Review scores
       |
       +--> Application writer --> Add resume and job --> Generate application
       |
       +--> Mock interview --> Select role --> Answer --> Receive feedback
```

---

## 14. Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | The system shall collect user resume information. |
| FR2 | The system shall generate structured resume content. |
| FR3 | The system shall export generated resume content as PDF. |
| FR4 | The system shall accept PDF resume uploads. |
| FR5 | The system shall accept DOCX resume uploads. |
| FR6 | The system shall extract text from uploaded documents. |
| FR7 | The system shall compare resume text with a job description. |
| FR8 | The system shall display matching and missing keywords. |
| FR9 | The system shall generate application materials. |
| FR10 | The system shall ask mock interview questions. |
| FR11 | The system shall provide feedback on interview answers. |
| FR12 | The system shall provide System, Light, and Dark appearance choices. |
| FR13 | The system shall work in fallback mode when no API key is configured. |

---

## 15. Non-Functional Requirements

- **Usability:** The interface should be understandable to a beginner.
- **Performance:** Common form operations should return within a reasonable time.
- **Reliability:** Missing inputs should produce a clear warning rather than a crash.
- **Security:** API keys must remain outside source control.
- **Maintainability:** AI, parsing, and PDF export logic should remain separated into services.
- **Portability:** The application should run wherever Python and the listed packages are available.
- **Transparency:** Users should know that AI output must be reviewed.

---

## 16. Testing Plan

### Test Cases

| Test ID | Test | Expected Result |
|---|---|---|
| T01 | Open the application without an API key | App loads in demo mode. |
| T02 | Enter resume details and generate | Structured resume output is displayed. |
| T03 | Download generated resume | A readable PDF is downloaded. |
| T04 | Upload a valid PDF | Resume text is extracted. |
| T05 | Upload a valid DOCX | Resume text is extracted. |
| T06 | Analyze without a file | A validation warning is displayed. |
| T07 | Analyze without a job description | A validation warning is displayed. |
| T08 | Match a resume with a job description | Scores and keyword lists are displayed. |
| T09 | Generate an application without job text | A validation warning is displayed. |
| T10 | Submit an empty interview answer | A validation warning is displayed. |
| T11 | Submit a valid interview answer | Feedback and a follow-up question are displayed. |
| T12 | Select Dark appearance | Dark colors apply to the interface. |
| T13 | Select Light appearance | Light colors apply to the interface. |
| T14 | Select System appearance | Browser preference determines appearance. |
| T15 | Check Git status | `.env` is not included in tracked files. |

### Validation Performed

- Python syntax compilation completed successfully.
- Pylance/editor diagnostics reported no errors in the main application files.
- Streamlit successfully started on `http://localhost:8501` using the project virtual environment.
- The project was committed and pushed to the GitHub `main` branch.

---

## 17. Limitations

- AI quality depends on the selected model and the quality of user input.
- Keyword overlap does not fully represent semantic job suitability.
- ATS scoring is an estimate and not a guarantee of recruiter behavior.
- The current MVP does not include persistent user accounts or database storage.
- The current interview mode is text-based.
- PDF generation uses a simple template and does not yet provide a template selector.
- API usage may require an external provider account and can incur usage costs.
- Users must review all generated content for accuracy.

---

## 18. Future Enhancements

1. Add login and user profiles.
2. Store resumes, applications, and interview history in SQLite or PostgreSQL.
3. Add multiple ATS-friendly and modern resume templates.
4. Add DOCX resume export.
5. Add voice-based interviews using speech-to-text.
6. Analyze filler words, pauses, speaking speed, and confidence.
7. Generate a personalized skill-gap learning roadmap.
8. Add progress charts for interview performance.
9. Add multilingual resume generation.
10. Add explainable recommendations showing which resume evidence supports each suggestion.
11. Add privacy controls for deleting uploaded files and stored history.
12. Integrate job-board links and application tracking.

---

## 19. Expected Benefits

- Saves time when preparing resumes and applications.
- Helps users describe projects and experience more clearly.
- Improves alignment between resumes and job requirements.
- Gives students access to repeatable interview practice.
- Encourages evidence-based and truthful career content.
- Demonstrates a practical use of Generative AI beyond ordinary chat.

---

## 20. Conclusion

CareerPilot AI demonstrates how Generative AI can support the complete early-career preparation process. Instead of focusing on one isolated task, the system connects resume creation, resume analysis, job matching, application writing, and mock interviewing.

The project is practical, extensible, and suitable for students and job seekers. Its modular architecture makes it possible to add authentication, persistence, voice interaction, learning roadmaps, and advanced analytics in future versions. The truthfulness constraints and secret-management practices also make the system more responsible and suitable for real-world experimentation.

---

## 21. Viva Questions and Answers

### Q1. Why did you choose Generative AI for this project?

Generative AI can understand unstructured career information and transform it into useful text such as professional summaries, resume bullets, cover letters, and interview feedback.

### Q2. What is the role of Streamlit?

Streamlit provides the interactive web interface using Python. It allows rapid development of forms, upload controls, buttons, navigation, and downloadable outputs.

### Q3. What is an ATS?

An Applicant Tracking System is software used by employers to filter, organize, and search job applications. CareerPilot AI checks for simple ATS-related issues such as relevant keywords and readable section structure.

### Q4. Can the AI invent achievements?

The prompts explicitly instruct the AI not to invent achievements, employers, dates, skills, or metrics. The user must still review every generated result.

### Q5. Why is the API key not in GitHub?

An API key is a secret credential. Publishing it can allow unauthorized usage and unexpected charges. The `.env` file is ignored by Git, and deployment secrets are configured privately.

### Q6. What happens without an API key?

The application uses fallback responses for demonstration. The interface and non-LLM functionality remain available, while live generation requires an API key.

### Q7. How does the application read resumes?

PyMuPDF extracts text from PDF files, and python-docx extracts paragraph text from DOCX files.

### Q8. What is the STAR method?

STAR means Situation, Task, Action, and Result. It is a structure for answering behavioral interview questions with a specific example.

### Q9. What are the main limitations?

The project does not guarantee hiring outcomes, uses estimated matching scores, depends on model quality, and currently lacks persistent accounts and voice analysis.

### Q10. How can the project be improved?

Future versions can add authentication, databases, multiple templates, voice interviews, skill-roadmap generation, progress tracking, and multilingual support.

---

## 22. References

- Streamlit documentation: https://docs.streamlit.io/
- Python documentation: https://docs.python.org/3/
- PyMuPDF documentation: https://pymupdf.readthedocs.io/
- python-docx documentation: https://python-docx.readthedocs.io/
- ReportLab documentation: https://docs.reportlab.com/
- Git documentation: https://git-scm.com/doc
- GitHub documentation: https://docs.github.com/
