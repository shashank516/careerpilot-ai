import json
import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from services.ai_service import analyze_resume, build_resume, generate_application, interview_feedback
from services.document_parser import extract_text
from services.resume_export import resume_to_pdf

load_dotenv(dotenv_path=".env")
st.set_page_config(page_title="CareerPilot AI", page_icon="CP", layout="wide")


def ai_configured() -> bool:
    if os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY"):
        return True
    try:
        return bool(st.secrets.get("OPENAI_API_KEY") or st.secrets.get("GROQ_API_KEY"))
    except (FileNotFoundError, KeyError):
        return False

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;700&display=swap');
    :root { --ink: #14213d; --coral: #ef8354; --mint: #d9f0e3; --paper: #fffdf7; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: linear-gradient(135deg, #fffdf7 0%, #eef7f2 52%, #f9e9dc 100%); }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }
    h1 { font-size: 3.4rem !important; letter-spacing: 0 !important; }
    .hero { padding: 1rem 0 1.4rem; }
    .eyebrow { color: #c8562b; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: .78rem; }
    .panel { background: rgba(255,255,255,.75); border: 1px solid rgba(20,33,61,.12); padding: 1.2rem; border-radius: 8px; }
    .metric { background: #14213d; color: white; padding: 1rem; border-radius: 8px; }
    .metric strong { font-size: 1.8rem; display: block; }
    .stButton > button { border-radius: 6px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

if "resume" not in st.session_state:
    st.session_state.resume = None
if "interview" not in st.session_state:
    st.session_state.interview = {"question": "Tell me about yourself and the work you are most proud of.", "answers": []}

st.markdown('<div class="hero"><div class="eyebrow">Generative career studio</div><h1>CareerPilot AI</h1><p>Turn your real experience into a sharper resume, a stronger application, and interview confidence.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Your workspace")
    st.caption("Build from facts. Improve with evidence. Practice with purpose.")
    appearance = st.radio("Appearance", ["System", "Light", "Dark"], horizontal=True, key="appearance")
    mode = st.radio("Go to", ["Build resume", "Analyze & match", "Application writer", "Mock interview"])
    st.divider()
    if ai_configured():
        st.success("Live AI mode enabled")
    else:
        st.warning("Demo mode: add OPENAI_API_KEY to .env")

if appearance == "Dark":
    theme_css = """
    :root { --ink: #f4f7fb; --muted: #b7c3d4; --surface: #172338; --surface-2: #22314b; --line: #3b4b64; --accent: #ff9b70; }
    .stApp { background: linear-gradient(135deg, #101927 0%, #18283a 52%, #302b35 100%); }
    """
elif appearance == "Light":
    theme_css = """
    :root { --ink: #14213d; --muted: #52627a; --surface: rgba(255,255,255,.82); --surface-2: #ffffff; --line: rgba(20,33,61,.16); --accent: #c8562b; }
    .stApp { background: linear-gradient(135deg, #fffdf7 0%, #eef7f2 52%, #f9e9dc 100%); }
    """
else:
    theme_css = """
    :root { --ink: #14213d; --muted: #52627a; --surface: rgba(255,255,255,.82); --surface-2: #ffffff; --line: rgba(20,33,61,.16); --accent: #c8562b; }
    .stApp { background: linear-gradient(135deg, #fffdf7 0%, #eef7f2 52%, #f9e9dc 100%); }
    @media (prefers-color-scheme: dark) {
        :root { --ink: #f4f7fb; --muted: #b7c3d4; --surface: rgba(23,35,56,.9); --surface-2: #22314b; --line: #3b4b64; --accent: #ff9b70; }
        .stApp { background: linear-gradient(135deg, #101927 0%, #18283a 52%, #302b35 100%); }
    }
    """

st.markdown(f"""
<style>
    {theme_css}
    html, body, [class*="css"] {{ color: var(--ink); }}
    [data-testid="stSidebar"] {{ background: var(--surface); }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{ color: var(--ink) !important; }}
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {{ background: var(--surface-2); color: var(--ink); border-color: var(--line); }}
    [data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] {{ color: var(--muted); }}
    .panel {{ background: var(--surface); border-color: var(--line); }}
    .eyebrow {{ color: var(--accent); }}
</style>
""", unsafe_allow_html=True)


def collect_profile() -> dict[str, Any]:
    with st.form("profile_form"):
        left, right = st.columns(2)
        with left:
            name = st.text_input("Full name", placeholder="Aarav Sharma")
            email = st.text_input("Email", placeholder="aarav@example.com")
            phone = st.text_input("Phone", placeholder="+91 98765 43210")
            location = st.text_input("Location", placeholder="Bengaluru, India")
            target_role = st.text_input("Target role", placeholder="Junior Data Analyst")
        with right:
            summary = st.text_area("About you", height=120, placeholder="Describe your strengths, interests, and career direction.")
            skills = st.text_area("Skills", height=100, placeholder="Python, SQL, Excel, communication")
            education = st.text_area("Education", height=100, placeholder="B.Tech Computer Science, ABC University, 2022-2026")
        experience = st.text_area("Experience", height=140, placeholder="Company | Role | Dates\nDescribe what you did and any measurable results.")
        projects = st.text_area("Projects", height=140, placeholder="Project name | technologies | what you built | result")
        extras = st.text_area("Certifications and achievements", height=100, placeholder="Certifications, awards, leadership, volunteering")
        submitted = st.form_submit_button("Generate my resume", type="primary", use_container_width=True)
    return {"name": name, "email": email, "phone": phone, "location": location, "target_role": target_role, "summary": summary, "skills": skills, "education": education, "experience": experience, "projects": projects, "extras": extras}, submitted


if mode == "Build resume":
    st.subheader("Build from your story")
    st.write("Give CareerPilot your real details. It will structure and polish them without inventing experience.")
    profile, submitted = collect_profile()
    if submitted:
        with st.spinner("Shaping your experience into a resume..."):
            st.session_state.resume = build_resume(profile)
    if st.session_state.resume:
        resume = st.session_state.resume
        st.divider()
        st.subheader("Your draft")
        st.caption("Review every AI suggestion before using it in an application.")
        st.json(resume)
        pdf = resume_to_pdf(resume)
        st.download_button("Download PDF resume", data=pdf, file_name="careerpilot_resume.pdf", mime="application/pdf", type="primary")

elif mode == "Analyze & match":
    st.subheader("Analyze a resume against a real role")
    uploaded = st.file_uploader("Upload PDF or DOCX resume", type=["pdf", "docx"])
    job = st.text_area("Paste the job description", height=220, placeholder="Responsibilities, required skills, qualifications...")
    if st.button("Analyze match", type="primary"):
        if not uploaded or not job.strip():
            st.warning("Add both a resume and a job description first.")
        else:
            with st.spinner("Comparing evidence and requirements..."):
                text = extract_text(uploaded.getvalue(), uploaded.name)
                result = analyze_resume(text, job)
            st.session_state.analysis = result
    if "analysis" in st.session_state:
        result = st.session_state.analysis
        cols = st.columns(3)
        for col, (label, value) in zip(cols, [("Overall match", result.get("match_score", 0)), ("ATS readiness", result.get("ats_score", 0)), ("Evidence strength", result.get("evidence_score", 0))]):
            col.markdown(f'<div class="metric"><span>{label}</span><strong>{value}/100</strong></div>', unsafe_allow_html=True)
        st.write("")
        st.json(result)

elif mode == "Application writer":
    st.subheader("Create an application that sounds like you")
    resume_text = st.text_area("Resume details", value=json.dumps(st.session_state.resume or {}, indent=2), height=240)
    job = st.text_area("Job description", height=180)
    tone = st.selectbox("Tone", ["Professional", "Warm and confident", "Concise"])
    if st.button("Generate application pack", type="primary"):
        if not job.strip():
            st.warning("Paste a job description first.")
        else:
            with st.spinner("Writing a tailored application..."):
                st.session_state.application = generate_application(resume_text, job, tone)
    if "application" in st.session_state:
        st.json(st.session_state.application)

else:
    st.subheader("Practice the conversation, not a script")
    role = st.text_input("Interview role", value="Junior Data Analyst")
    difficulty = st.select_slider("Difficulty", options=["Starter", "Standard", "Challenging"], value="Standard")
    st.info(st.session_state.interview["question"])
    answer = st.text_area("Your answer", height=160, placeholder="Type your answer as if you were speaking to the interviewer.")
    if st.button("Submit answer", type="primary"):
        if not answer.strip():
            st.warning("Write an answer first.")
        else:
            with st.spinner("Reviewing your answer..."):
                feedback = interview_feedback(role, difficulty, st.session_state.interview["question"], answer)
            st.session_state.interview["answers"].append({"question": st.session_state.interview["question"], "answer": answer, "feedback": feedback})
            st.session_state.interview["question"] = feedback.get("next_question", "What would you contribute in your first 90 days?")
            st.rerun()
    if st.session_state.interview["answers"]:
        st.subheader("Latest feedback")
        st.json(st.session_state.interview["answers"][-1]["feedback"])
