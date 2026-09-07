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

TEMPLATES = ["Classic ATS", "Modern Timeline", "Bold Minimal"]


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
    :root { --ink: #263747; --coral: #b86f57; --mint: #dce8f0; --paper: #f5eee4; --line: rgba(38,55,71,.14); --muted: #687785; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: linear-gradient(135deg, #f5eee4 0%, #e9f0f5 54%, #f1e5dc 100%); }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }
    h1 { font-size: clamp(2.5rem, 5vw, 4.6rem) !important; line-height: .98 !important; letter-spacing: 0 !important; margin: .25rem 0 .75rem !important; }
    h2 { font-size: 1.65rem !important; letter-spacing: 0 !important; }
    h3 { font-size: 1.1rem !important; letter-spacing: 0 !important; }
    .hero { padding: .8rem 0 1.6rem; max-width: 860px; }
    .eyebrow { color: #a95e49; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: .78rem; }
    .hero-copy { color: var(--muted); font-size: 1.08rem; max-width: 650px; line-height: 1.6; }
    .section-kicker { color: #a95e49; font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: 1.2rem 0 .35rem; }
    .module-card { background: rgba(255,255,255,.64); border: 1px solid var(--line); border-radius: 10px; padding: 1rem; min-height: 118px; box-shadow: 0 12px 30px rgba(20,33,61,.05); }
    .module-card strong { display: block; font-family: 'Space Grotesk', sans-serif; font-size: 1.02rem; margin-bottom: .35rem; }
    .module-card span { color: var(--muted); font-size: .86rem; line-height: 1.4; }
    .panel { background: rgba(255,255,255,.75); border: 1px solid var(--line); padding: 1.25rem; border-radius: 10px; box-shadow: 0 14px 34px rgba(20,33,61,.06); }
    .metric { background: #334e64; color: white; padding: 1rem 1.1rem; border-radius: 10px; box-shadow: 0 10px 22px rgba(38,55,71,.12); }
    .metric span { color: #dce8f0; font-size: .78rem; }
    .metric strong { font-size: 1.8rem; display: block; }
    .stButton > button, .stDownloadButton > button { border-radius: 7px; font-weight: 700; min-height: 2.7rem; border-color: rgba(38,53,47,.16); }
    [data-testid="stSidebar"] .stButton > button { text-align: left; padding-left: .9rem; }
    [data-testid="stForm"] { background: rgba(255,255,255,.48); border: 1px solid var(--line); border-radius: 10px; padding: 1.2rem; }
    [data-testid="stExpander"] { border-color: var(--line); background: rgba(255,255,255,.38); }
    [data-testid="stSidebar"] h3 { margin-top: .45rem; }
</style>
""", unsafe_allow_html=True)

if "resume" not in st.session_state:
    st.session_state.resume = None
if "interview" not in st.session_state:
    st.session_state.interview = {"question": "Tell me about yourself and the work you are most proud of.", "answers": []}

st.markdown('<div class="hero"><div class="eyebrow">Generative career studio</div><h1>CareerPilot AI</h1><p class="hero-copy">Make your next move feel more prepared. Turn your real experience into a sharper resume, a tailored application, and interview practice that gets better with every answer.</p></div>', unsafe_allow_html=True)

card_cols = st.columns(4)
for column, title, detail in zip(card_cols, ["Build", "Match", "Apply", "Practice"], ["Create a resume from your story.", "Find gaps against a real role.", "Write a focused application pack.", "Train with role-specific questions."]):
    column.markdown(f'<div class="module-card"><strong>{title}</strong><span>{detail}</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### CareerPilot AI")
    st.caption("A focused workspace for your next opportunity.")
    with st.expander("Appearance", expanded=False):
        appearance = st.selectbox("Theme", ["Light", "System", "Dark"], index=0, key="appearance")
    st.markdown("<div class='section-kicker'>Workspace</div>", unsafe_allow_html=True)
    workflows = [
        ("Build resume", "01  Build your story"),
        ("Analyze & match", "02  Compare a role"),
        ("Application writer", "03  Write an application"),
        ("Mock interview", "04  Practice answers"),
    ]
    if "mode" not in st.session_state:
        st.session_state.mode = "Build resume"
    for workflow, button_label in workflows:
        if st.button(button_label, key=f"nav_{workflow}", type="primary" if st.session_state.mode == workflow else "secondary", use_container_width=True):
            st.session_state.mode = workflow
            st.rerun()
    mode = st.session_state.mode
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
    :root { --ink: #263747; --muted: #687785; --surface: rgba(255,252,246,.84); --surface-2: #fffdf9; --line: rgba(38,55,71,.15); --accent: #a95e49; }
    .stApp { background: linear-gradient(135deg, #f5eee4 0%, #e9f0f5 54%, #f1e5dc 100%); }
    """
else:
    theme_css = """
    :root { --ink: #263747; --muted: #687785; --surface: rgba(255,252,246,.84); --surface-2: #fffdf9; --line: rgba(38,55,71,.15); --accent: #a95e49; }
    .stApp { background: linear-gradient(135deg, #f5eee4 0%, #e9f0f5 54%, #f1e5dc 100%); }
    @media (prefers-color-scheme: dark) {
        :root { --ink: #f4f1eb; --muted: #c3ccd4; --surface: rgba(36,49,62,.92); --surface-2: #334e64; --line: #536879; --accent: #e0a184; }
        .stApp { background: linear-gradient(135deg, #202b34 0%, #2d4050 52%, #493b39 100%); }
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
    .module-card, [data-testid="stForm"], [data-testid="stExpander"] {{ background: var(--surface); border-color: var(--line); }}
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
    st.write("Give CareerPilot your real details. It will structure and polish them without inventing experience.")
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
            st.download_button("Download styled PDF resume", data=pdf, file_name=f"careerpilot_{template.lower().replace(' ', '_')}.pdf", mime="application/pdf", type="primary", use_container_width=True)

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
    job = st.text_area("Job description", height=180)
    tone = st.selectbox("Tone", ["Professional", "Warm and confident", "Concise"])
    if st.button("Generate application pack", type="primary"):
        if not job.strip():
            st.warning("Paste a job description first.")
        else:
            with st.spinner("Writing a tailored application..."):
                st.session_state.application = generate_application(resume_text, job, tone)
    if "application" in st.session_state:
        st.markdown('<div class="section-kicker">Output / Application pack</div>', unsafe_allow_html=True)
        st.json(st.session_state.application)

else:
    st.markdown('<div class="section-kicker">04 / Practice</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="section-kicker">Output / Coach notes</div>', unsafe_allow_html=True)
        st.json(st.session_state.interview["answers"][-1]["feedback"])
