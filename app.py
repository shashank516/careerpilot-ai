import json
import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from backend.auth_service import authenticate_user, register_user
from backend.resume_service import get_saved_resume, list_saved_resumes, save_resume
from services.ai_service import analyze_resume, build_resume, generate_application, interview_feedback
from services.document_parser import extract_text
from services.resume_export import resume_to_pdf

load_dotenv(dotenv_path=".env")
st.set_page_config(page_title="Pathway AI", page_icon=":material/route:", layout="wide")

TEMPLATES = ["Classic ATS", "Modern Timeline", "Bold Minimal"]
WORKFLOWS = {"Build resume", "Analyze & match", "Application writer", "Mock interview", "My resumes"}


def export_resume(resume: dict, template: str) -> bytes:
    """Support both current and older PDF-export function signatures."""
    try:
        return resume_to_pdf(resume, template)
    except TypeError:
        return resume_to_pdf(resume)


def ai_configured() -> bool:
    """Check whether a live AI provider key is available."""
    if os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY"):
        return True
    try:
        return bool(st.secrets.get("OPENAI_API_KEY") or st.secrets.get("GROQ_API_KEY"))
    except (FileNotFoundError, KeyError):
        return False


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
.stApp,[data-testid="stAppViewContainer"]{background:#f6f7fb}.main .block-container{max-width:1240px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;color:#18213d!important;letter-spacing:-.025em}h1{font-size:clamp(2.2rem,4vw,3.55rem)!important;line-height:1.04!important}
.eyebrow{color:#5b5ce2;font-size:.72rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase}.section-kicker{color:#5b5ce2;font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin:1.5rem 0 .4rem}
.hero-shell{background:linear-gradient(130deg,#191d42,#36358d 58%,#5b5ce2);border-radius:1.5rem;padding:2.1rem 2.2rem;box-shadow:0 18px 45px rgba(46,48,137,.18)}.hero-shell h1,.hero-shell .eyebrow,.hero-shell p,.auth-intro h1,.auth-intro p,.auth-intro .eyebrow{color:#fff!important}.hero-shell .eyebrow,.hero-shell p{opacity:.86}.hero-shell p{font-size:1.05rem;line-height:1.6;max-width:650px;margin:0}
.workspace-note{background:#fff;border:1px solid #dde2f1;border-radius:1.15rem;padding:1.2rem;height:100%}.workspace-note strong{color:#18213d;display:block;font-family:'Space Grotesk',sans-serif;margin:.4rem 0}.workspace-note span{color:#53617a;font-size:.9rem;line-height:1.5}
.feature-card{background:#fff;border:1px solid #dde2f1;border-radius:1rem;min-height:138px;padding:1.15rem;box-shadow:0 8px 22px rgba(25,32,73,.06)}.feature-number{color:#5b5ce2;font-size:.72rem;font-weight:700;letter-spacing:.12em;margin-bottom:.55rem}.feature-card h3{color:#18213d!important;font-size:1.08rem!important;margin:0 0 .45rem!important}.feature-card p{color:#53617a!important;font-size:.88rem;line-height:1.5;margin:0}
.auth-intro{background:linear-gradient(145deg,#1b2049,#5b5ce2);border-radius:1.5rem;padding:2.4rem}.auth-intro p{opacity:.86;line-height:1.6}.metric{background:#fff;border:1px solid #dde2f1;color:#18213d;padding:1rem 1.1rem;border-radius:1rem}.metric span{color:#53617a;font-size:.78rem}.metric strong{color:#5b5ce2;display:block;font-size:1.8rem}
[data-testid="stSidebar"]{background:#fff}[data-testid="stSidebar"] .stButton>button{background:#fff;color:#18213d;border-color:#dde2f1;text-align:left}[data-testid="stForm"],[data-testid="stExpander"]{border-color:#dde2f1;border-radius:1rem}[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:#fff;color:#18213d;border-color:#d9ddea}[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{color:#7d859b;opacity:1}[data-testid="stForm"] p,[data-testid="stForm"] label,[data-testid="stTextInput"] label,[data-testid="stTextArea"] label{color:#18213d!important}
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("resume", None)
st.session_state.setdefault("interview", {"question": "Tell me about yourself and the work you are most proud of.", "answers": []})
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("current_user", None)


def show_authentication_screen() -> None:
    """Show account forms before a visitor can access private career data."""
    intro, account = st.columns([1.15, .85], gap="large", vertical_alignment="center")
    with intro:
        st.markdown('<div class="auth-intro"><div class="eyebrow">Pathway AI</div><h1>Your next opportunity starts here.</h1><p>Build a thoughtful resume, match it to a role, and practise the conversations that matter.</p></div>', unsafe_allow_html=True)
    with account:
        with st.container(border=True):
            st.subheader("Welcome back")
            st.caption("Sign in or create an account to keep your work in one place.")
            login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
            with login_tab:
                with st.form("login_form", border=False):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Sign in", type="primary", width="stretch")
                if submitted:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.authenticated, st.session_state.current_user = True, user
                        st.rerun()
                    st.error("Invalid email or password.")
            with signup_tab:
                with st.form("signup_form", border=False):
                    full_name = st.text_input("Full name", placeholder="Aarav Sharma")
                    email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                    password = st.text_input("Password", type="password", key="signup_password", help="Use at least 8 characters.")
                    submitted = st.form_submit_button("Create account", type="primary", width="stretch")
                if submitted:
                    success, message = register_user(full_name, email, password)
                    (st.success if success else st.error)(message)


if not st.session_state.authenticated:
    show_authentication_screen()
    st.stop()

if "mode" not in st.session_state:
    requested_mode = st.query_params.get("mode", "Build resume")
    st.session_state.mode = requested_mode if requested_mode in WORKFLOWS else "Build resume"

header, status = st.columns([1.4, .6], gap="large", vertical_alignment="center")
with header:
    st.markdown('<div class="hero-shell"><div class="eyebrow">Generative career studio</div><h1>Make your next move with clarity.</h1><p>One focused workspace for resumes, applications, and interview confidence.</p></div>', unsafe_allow_html=True)
with status:
    st.markdown('<div class="workspace-note"><div class="eyebrow">Your workspace</div><strong>Build at your own pace</strong><span>Your drafts and saved resumes stay private to your account.</span></div>', unsafe_allow_html=True)

st.markdown('<div class="section-kicker">Choose your next step</div>', unsafe_allow_html=True)
workflow_cards = [
    ("Build resume", "01", "Build your resume", "Turn your education, skills, projects, and experience into a professional resume.", "Open resume builder"),
    ("Analyze & match", "02", "Analyze a role", "Compare an existing resume against a job description and find the important gaps.", "Open resume analysis"),
    ("Application writer", "03", "Write an application", "Create a tailored application pack using your resume and the job details.", "Open application writer"),
    ("Mock interview", "04", "Practice interviews", "Answer role-specific questions and receive clear coaching feedback.", "Open interview practice"),
    ("My resumes", "05", "My saved resumes", "Open, review, and download the resumes stored securely in your account.", "Open saved resumes"),
]
for card_row in (workflow_cards[:3], workflow_cards[3:]):
    columns = st.columns(len(card_row), gap="medium")
    for column, (workflow, number, title, description, button_label) in zip(columns, card_row):
        with column:
            with st.container(border=True):
                st.markdown(f'<div class="feature-card"><div class="feature-number">{number}</div><h3>{title}</h3><p>{description}</p></div>', unsafe_allow_html=True)
                if st.button(button_label, key=f"open_{workflow}", width="stretch", type="primary" if st.session_state.mode == workflow else "secondary"):
                    st.session_state.mode, st.query_params["mode"] = workflow, workflow
                    st.rerun()

with st.sidebar:
    st.markdown("## Pathway AI")
    st.badge("Private workspace", color="blue")
    st.markdown(f"### {st.session_state.current_user['full_name']}")
    st.caption(st.session_state.current_user["email"])
    if st.button("Log out", width="stretch"):
        st.session_state.authenticated, st.session_state.current_user = False, None
        st.rerun()
    st.space("medium")
    st.caption("Your private space for career planning, drafting, and practice.")
    if ai_configured(): st.success("Live AI mode enabled", icon=":material/check_circle:")
    else: st.warning("Demo mode: add OPENAI_API_KEY to .env", icon=":material/info:")


def collect_profile() -> tuple[dict[str, Any], bool]:
    """Collect resume inputs together and submit them in one request."""
    with st.form("profile_form"):
        left, right = st.columns(2)
        with left:
            name = st.text_input("Full name", placeholder="Aarav Sharma")
            email = st.text_input("Email", placeholder="aarav@example.com", key="resume_email")
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
        submitted = st.form_submit_button("Generate my resume", type="primary", width="stretch")
    return {"name": name, "email": email, "phone": phone, "location": location, "target_role": target_role, "summary": summary, "skills": skills, "education": education, "experience": experience, "projects": projects, "extras": extras}, submitted


mode = st.session_state.mode
if mode == "Build resume":
    st.markdown('<div class="section-kicker">01 / Create</div>', unsafe_allow_html=True)
    st.subheader("Build from your story")
    st.write("Give Pathway AI your real details. It will structure and polish them without inventing experience.")
    template = st.selectbox("Choose a resume style", TEMPLATES, help="Classic ATS is safest for online applications.")
    profile, submitted = collect_profile()
    if submitted:
        with st.spinner("Shaping your experience into a resume..."): st.session_state.resume = build_resume(profile)
    if st.session_state.resume:
        resume = st.session_state.resume
        preview, review = st.columns([1.25, .75], gap="large")
        with preview:
            with st.container(border=True):
                st.markdown('<div class="section-kicker">Output / Draft resume</div>', unsafe_allow_html=True)
                st.markdown(f"### {resume.get('name', 'Your Name')}")
                st.caption(resume.get("contact", "Add your contact details"))
                st.markdown(f"**{resume.get('target_role', 'Target role')}**")
                st.write(resume.get("summary", "No summary generated yet."))
                for heading, content in [("Skills", resume.get("skills")), ("Experience", resume.get("experience")), ("Projects", resume.get("projects")), ("Education", resume.get("education"))]:
                    if content:
                        st.markdown(f"**{heading}**")
                        st.write(", ".join(map(str, content)) if isinstance(content, list) else str(content))
        with review:
            with st.container(border=True):
                st.subheader("Review and save")
                st.caption("Review every AI suggestion before using it in an application.")
                with st.expander("View structured data"): st.json(resume)
                if st.button("Save to My resumes", key="save_current_resume", type="primary", width="stretch"):
                    saved, message = save_resume(st.session_state.current_user["id"], resume, template)
                    (st.success if saved else st.error)(message)
                st.download_button("Download styled PDF resume", data=export_resume(resume, template), file_name=f"pathway_{template.lower().replace(' ', '_')}.pdf", mime="application/pdf", type="primary", width="stretch")

elif mode == "Analyze & match":
    st.markdown('<div class="section-kicker">02 / Compare</div>', unsafe_allow_html=True)
    st.subheader("Analyze a resume against a real role")
    with st.container(border=True):
        uploaded = st.file_uploader("Upload PDF or DOCX resume", type=["pdf", "docx"])
        job = st.text_area("Paste the job description", height=220, placeholder="Responsibilities, required skills, qualifications...")
        if st.button("Analyze match", type="primary"):
            if not uploaded or not job.strip(): st.warning("Add both a resume and a job description first.")
            else:
                with st.spinner("Comparing evidence and requirements..."): st.session_state.analysis = analyze_resume(extract_text(uploaded.getvalue(), uploaded.name), job)
    if "analysis" in st.session_state:
        result = st.session_state.analysis
        for col, (label, value) in zip(st.columns(3), [("Overall match", result.get("match_score", 0)), ("ATS readiness", result.get("ats_score", 0)), ("Evidence strength", result.get("evidence_score", 0))]): col.markdown(f'<div class="metric"><span>{label}</span><strong>{value}/100</strong></div>', unsafe_allow_html=True)
        with st.expander("View full analysis", expanded=True): st.json(result)

elif mode == "Application writer":
    st.markdown('<div class="section-kicker">03 / Apply</div>', unsafe_allow_html=True)
    st.subheader("Create an application that sounds like you")
    with st.container(border=True):
        resume_text = st.text_area("Resume details", value=json.dumps(st.session_state.resume or {}, indent=2), height=240)
        company = st.text_input("Company", placeholder="Example Company")
        job = st.text_area("Job description", height=180)
        tone = st.selectbox("Tone", ["Professional", "Warm and confident", "Concise"])
        if st.button("Generate application pack", type="primary"):
            if not job.strip(): st.warning("Paste a job description first.")
            else:
                with st.spinner("Writing a tailored application..."): st.session_state.application = generate_application(resume_text, job, company, tone)
    if "application" in st.session_state: st.json(st.session_state.application)

elif mode == "Mock interview":
    st.markdown('<div class="section-kicker">04 / Practice</div>', unsafe_allow_html=True)
    st.subheader("Practice the conversation, not a script")
    with st.container(border=True):
        role = st.text_input("Interview role", value="Junior Data Analyst")
        difficulty = st.select_slider("Difficulty", options=["Starter", "Standard", "Challenging"], value="Standard")
        interview_mode = st.selectbox("Interview mode", ["Behavioral", "Technical", "HR", "Project-based"])
        st.info(st.session_state.interview["question"])
        answer = st.text_area("Your answer", height=160, placeholder="Type your answer as if you were speaking to the interviewer.")
        if st.button("Submit answer", type="primary"):
            if not answer.strip(): st.warning("Write an answer first.")
            else:
                with st.spinner("Reviewing your answer..."): feedback = interview_feedback(role, difficulty, interview_mode, st.session_state.interview["question"], answer)
                st.session_state.interview["answers"].append({"question": st.session_state.interview["question"], "answer": answer, "feedback": feedback})
                st.session_state.interview["question"] = feedback.get("next_question", "What would you contribute in your first 90 days?")
                st.rerun()
    if st.session_state.interview["answers"]: st.json(st.session_state.interview["answers"][-1]["feedback"])

else:
    st.markdown('<div class="section-kicker">05 / Saved work</div>', unsafe_allow_html=True)
    st.subheader("My resumes")
    st.caption("Your saved resumes are private to your account and remain available after you sign out.")
    saved_resumes = list_saved_resumes(st.session_state.current_user["id"])
    if not saved_resumes: st.info("You have not saved a resume yet. Create one in Build resume, then select Save to My resumes.")
    for saved in saved_resumes:
        with st.expander(f"{saved['display_name']} — {saved['target_role']}"):
            st.caption(f"Saved on {saved['created_at']} · {saved['template_name']} template")
            saved_resume = get_saved_resume(st.session_state.current_user["id"], saved["id"])
            if saved_resume is None: st.error("This resume could not be loaded.")
            else:
                st.json(saved_resume)
                st.download_button("Download PDF", data=export_resume(saved_resume, saved["template_name"]), file_name=f"pathway_saved_{saved['id']}.pdf", mime="application/pdf", key=f"download_saved_resume_{saved['id']}", type="primary", width="stretch")
