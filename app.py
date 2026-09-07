import json
import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from services.ai_service import analyze_resume, build_resume, generate_application, interview_feedback
from services.document_parser import extract_text
from services.resume_export import resume_to_pdf

load_dotenv(dotenv_path=".env")
st.set_page_config(page_title="Pathway AI", page_icon="PA", layout="wide")

TEMPLATES = ["Classic ATS", "Modern Timeline", "Bold Minimal"]
WORKFLOWS = {"Build resume", "Analyze & match", "Application writer", "Mock interview"}


def export_resume(resume: dict, template: str) -> bytes:
    """Keep deployments compatible while Cloud refreshes older module caches."""
    try:
        return resume_to_pdf(resume, template)
    except TypeError:
        return resume_to_pdf(resume)


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
    :root { --ink: #101723; --lime: #D8FF51; --coral: #FF7757; --paper: #F6F1E7; --mist: #DCE4DF; --line: rgba(246,241,231,.18); --muted: #DCE4DF; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: #101723; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }
    h1 { font-size: clamp(2.5rem, 5vw, 4.6rem) !important; line-height: .98 !important; letter-spacing: 0 !important; margin: .25rem 0 .75rem !important; }
    h2 { font-size: 1.65rem !important; letter-spacing: 0 !important; }
    h3 { font-size: 1.1rem !important; letter-spacing: 0 !important; }
    .hero { padding: 1rem 0 1.6rem; max-width: 920px; }
    .eyebrow { color: #D8FF51; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; font-size: .78rem; }
    .hero-copy { color: #DCE4DF; font-size: 1.08rem; max-width: 650px; line-height: 1.6; }
    .section-kicker { color: #FF7757; font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: 1.2rem 0 .35rem; }
    .module-card { background: #DCE4DF; color: #101723; border: 1px solid rgba(246,241,231,.18); border-radius: 1.2rem; padding: 1rem; min-height: 118px; box-shadow: 0 14px 32px rgba(0,0,0,.18); }
    .module-card strong { display: block; font-family: 'Space Grotesk', sans-serif; font-size: 1.02rem; margin-bottom: .35rem; }
    .module-card span { color: #43515A; font-size: .86rem; line-height: 1.4; }
    .panel { background: #DCE4DF; border: 1px solid rgba(16,23,35,.14); padding: 1.25rem; border-radius: 1.2rem; box-shadow: 0 14px 34px rgba(0,0,0,.16); }
    .metric { background: #D8FF51; color: #101723; padding: 1rem 1.1rem; border-radius: 1rem; box-shadow: 0 10px 22px rgba(216,255,81,.12); }
    .metric span { color: #101723; font-size: .78rem; }
    .metric strong { font-size: 1.8rem; display: block; }
    .stButton > button, .stDownloadButton > button { border-radius: 999px; font-weight: 700; min-height: 2.7rem; border-color: #D8FF51; color: #101723; background: #D8FF51; }
    [data-testid="stSidebar"] .stButton > button { text-align: left; padding-left: .9rem; }
    [data-testid="stForm"] { background: #F6F1E7; border: 1px solid rgba(16,23,35,.14); border-radius: 1rem; padding: 1.2rem; }
    [data-testid="stExpander"] { border-color: rgba(246,241,231,.18); background: #172130; }
    [data-testid="stSidebar"] h3 { margin-top: .45rem; }
</style>
""", unsafe_allow_html=True)

if "resume" not in st.session_state:
    st.session_state.resume = None
if "interview" not in st.session_state:
    st.session_state.interview = {"question": "Tell me about yourself and the work you are most proud of.", "answers": []}
saved_mode = st.query_params.get("mode", "Build resume")
if saved_mode in WORKFLOWS:
    st.session_state.mode = saved_mode
elif "mode" not in st.session_state:
    st.session_state.mode = "Build resume"
appearance = "Pathway"

st.markdown('<div class="hero"><div class="eyebrow">Generative career studio</div><h1>Pathway AI</h1><p class="hero-copy">One focused path from first draft to interview-ready confidence.</p></div>', unsafe_allow_html=True)

workflow_cards = [
    ("Build resume", "01  Build", "Create a resume from your story."),
    ("Analyze & match", "02  Match", "Find gaps against a real role."),
    ("Application writer", "03  Apply", "Write a focused application pack."),
    ("Mock interview", "04  Practice", "Train with role-specific questions."),
]
card_cols = st.columns(4)
for column, (workflow, title, detail) in zip(card_cols, workflow_cards):
    with column:
        st.markdown(f'<div class="module-card"><strong>{title}</strong><span>{detail}</span></div>', unsafe_allow_html=True)
        if st.button(f"Open {title.split('  ', 1)[-1]}", key=f"hero_{workflow}", use_container_width=True, type="primary" if st.session_state.mode == workflow else "secondary"):
            st.session_state.mode = workflow
            st.query_params["mode"] = workflow
            st.rerun()

with st.sidebar:
    st.markdown("### Pathway AI")
    st.caption("A focused workspace for your next opportunity.")
    st.markdown("<div class='section-kicker'>Workspace</div>", unsafe_allow_html=True)
    workflows = [
        ("Build resume", "01  Build your story"),
        ("Analyze & match", "02  Compare a role"),
        ("Application writer", "03  Write an application"),
        ("Mock interview", "04  Practice answers"),
    ]
    for workflow, button_label in workflows:
        if st.button(button_label, key=f"nav_{workflow}", type="primary" if st.session_state.mode == workflow else "secondary", use_container_width=True):
            st.session_state.mode = workflow
            st.query_params["mode"] = workflow
            st.rerun()
    mode = st.session_state.mode
    st.divider()
    if ai_configured():
        st.success("Live AI mode enabled")
    else:
        st.warning("Demo mode: add OPENAI_API_KEY to .env")

theme_css = """
:root { --ink: #F6F1E7; --muted: #DCE4DF; --surface: #172130; --surface-2: #223044; --line: rgba(246,241,231,.18); --accent: #FF7757; --primary: #D8FF51; }
.stApp { background: #101723; }
"""

st.markdown(f"""
<style>
    {theme_css}
    html, body, [class*="css"] {{ color: var(--ink); }}
    [data-testid="stSidebar"] {{ background: #101723; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{ color: var(--ink) !important; }}
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {{ background: var(--surface-2); color: var(--ink); border-color: var(--line); }}
    [data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] {{ color: var(--muted); }}
    h1, h2, h3, h4, [data-testid="stHeader"] {{ color: var(--ink) !important; }}
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{ color: var(--ink) !important; }}
    [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {{ color: var(--muted) !important; opacity: .8; }}
    [data-testid="stSidebar"] .stButton > button {{ color: #101723 !important; background: #DCE4DF !important; border-color: rgba(246,241,231,.18) !important; }}
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {{ color: #101723 !important; background: #D8FF51 !important; border-color: #D8FF51 !important; }}
    .panel {{ background: #DCE4DF; border-color: rgba(16,23,35,.14); }}
    .module-card, [data-testid="stForm"], [data-testid="stExpander"] {{ border-color: rgba(246,241,231,.18); }}
    .hero-copy, .module-card span {{ color: var(--muted); }}
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
    st.markdown('<div class="section-kicker">01 / Create</div>', unsafe_allow_html=True)
    st.subheader("Build from your story")
    st.write("Give Pathway AI your real details. It will structure and polish them without inventing experience.")
    template = st.selectbox(
        "Choose a resume style",
        TEMPLATES,
        help="Classic ATS is the safest choice for online applications. Modern Timeline and Bold Minimal are more visual.",
    )
    profile, submitted = collect_profile()
    if submitted:
        with st.spinner("Shaping your experience into a resume..."):
            st.session_state.resume = build_resume(profile)
    if st.session_state.resume:
        resume = st.session_state.resume
        st.divider()
        preview, data = st.columns([1.25, .75])
        with preview:
            st.markdown('<div class="section-kicker">Output / Draft resume</div>', unsafe_allow_html=True)
            st.markdown(f"### {resume.get('name', 'Your Name')}")
            st.caption(resume.get("contact", "Add your contact details"))
            st.markdown(f"**{resume.get('target_role', 'Target role')}**")
            st.write(resume.get("summary", "No summary generated yet."))
            for heading, content in [("Skills", resume.get("skills")), ("Experience", resume.get("experience")), ("Projects", resume.get("projects")), ("Education", resume.get("education"))]:
                if content:
                    st.markdown(f"**{heading}**")
                    if isinstance(content, list):
                        st.write(", ".join(str(item) for item in content))
                    else:
                        st.write(str(content))
        with data:
            st.markdown('<div class="section-kicker">Review</div>', unsafe_allow_html=True)
            st.caption("Review every AI suggestion before using it in an application.")
            with st.expander("View structured data"):
                st.json(resume)
            pdf = export_resume(resume, template)
            st.download_button("Download styled PDF resume", data=pdf, file_name=f"pathway_{template.lower().replace(' ', '_')}.pdf", mime="application/pdf", type="primary", use_container_width=True)

elif mode == "Analyze & match":
    st.markdown('<div class="section-kicker">02 / Compare</div>', unsafe_allow_html=True)
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
        with st.expander("View full analysis", expanded=True):
            st.json(result)

elif mode == "Application writer":
    st.markdown('<div class="section-kicker">03 / Apply</div>', unsafe_allow_html=True)
    st.subheader("Create an application that sounds like you")
    resume_text = st.text_area("Resume details", value=json.dumps(st.session_state.resume or {}, indent=2), height=240)
    company = st.text_input("Company", placeholder="Example Company")
    job = st.text_area("Job description", height=180)
    tone = st.selectbox("Tone", ["Professional", "Warm and confident", "Concise"])
    if st.button("Generate application pack", type="primary"):
        if not job.strip():
            st.warning("Paste a job description first.")
        else:
            with st.spinner("Writing a tailored application..."):
                st.session_state.application = generate_application(resume_text, job, company, tone)
    if "application" in st.session_state:
        st.markdown('<div class="section-kicker">Output / Application pack</div>', unsafe_allow_html=True)
        st.json(st.session_state.application)

else:
    st.markdown('<div class="section-kicker">04 / Practice</div>', unsafe_allow_html=True)
    st.subheader("Practice the conversation, not a script")
    role = st.text_input("Interview role", value="Junior Data Analyst")
    difficulty = st.select_slider("Difficulty", options=["Starter", "Standard", "Challenging"], value="Standard")
    interview_mode = st.selectbox("Interview mode", ["Behavioral", "Technical", "HR", "Project-based"])
    st.info(st.session_state.interview["question"])
    answer = st.text_area("Your answer", height=160, placeholder="Type your answer as if you were speaking to the interviewer.")
    if st.button("Submit answer", type="primary"):
        if not answer.strip():
            st.warning("Write an answer first.")
        else:
            with st.spinner("Reviewing your answer..."):
                feedback = interview_feedback(role, difficulty, interview_mode, st.session_state.interview["question"], answer)
            st.session_state.interview["answers"].append({"question": st.session_state.interview["question"], "answer": answer, "feedback": feedback})
            st.session_state.interview["question"] = feedback.get("next_question", "What would you contribute in your first 90 days?")
            st.rerun()
    if st.session_state.interview["answers"]:
        st.markdown('<div class="section-kicker">Output / Coach notes</div>', unsafe_allow_html=True)
        st.json(st.session_state.interview["answers"][-1]["feedback"])
