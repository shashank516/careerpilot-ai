"""AI generation functions with safe demo-mode fallback responses."""

import json
import os
from typing import Any


def _setting(name: str, default: str = "") -> str:
    """Read a setting from environment variables or Streamlit secrets."""
    value = os.getenv(name, "")
    if value:
        return value

    try:
        import streamlit as st

        return str(st.secrets.get(name, default))
    except (FileNotFoundError, ImportError, KeyError):
        return default


def _client():
    """Create an OpenAI-compatible client only when an API key exists."""
    api_key = _setting("GROQ_API_KEY") or _setting("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        if api_key.startswith("gsk_"):
            return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        return OpenAI(api_key=api_key)
    except ImportError:
        return None


def _available_models(api_key: str) -> list[str]:
    """Return provider-appropriate model names in fallback order."""
    if api_key.startswith("gsk_"):
        configured_model = _setting("GROQ_MODEL")
        return list(dict.fromkeys([configured_model, "llama-3.3-70b-versatile", "openai/gpt-oss-20b"]))
    return [_setting("OPENAI_MODEL") or "gpt-4o-mini"]


def _ask(instruction: str, payload: str, fallback: dict[str, Any]) -> dict[str, Any]:
    """Request JSON from the AI provider or safely return the supplied fallback."""
    client = _client()
    api_key = _setting("GROQ_API_KEY") or _setting("OPENAI_API_KEY")
    if client is None or not api_key:
        return fallback

    for model in _available_models(api_key):
        if not model:
            continue
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": payload},
                ],
            )
            return json.loads(response.choices[0].message.content)
        except Exception as error:
            # Try a second known Groq model only when the chosen model is unavailable.
            if "not found" not in str(error).lower() and "model" not in str(error).lower():
                break

    return fallback


def build_resume(profile: dict[str, Any]) -> dict[str, Any]:
    """Generate a truthful structured resume from the user's supplied profile."""
    fallback = {
        "name": profile["name"] or "Your Name",
        "contact": " | ".join(value for value in [profile["email"], profile["phone"], profile["location"]] if value),
        "target_role": profile["target_role"],
        "summary": profile["summary"],
        "skills": [skill.strip() for skill in profile["skills"].split(",") if skill.strip()],
        "education": profile["education"],
        "experience": profile["experience"],
        "projects": profile["projects"],
        "certifications_achievements": profile["extras"],
    }
    instruction = (
        "You are a truthful resume writer. Use only supplied facts and never invent "
        "employers, metrics, dates, or skills. Return JSON with name, contact, target_role, "
        "summary, skills, education, experience, projects, certifications_achievements."
    )
    return _ask(instruction, json.dumps(profile), fallback)


def analyze_resume(resume_text: str, job_description: str) -> dict[str, Any]:
    """Compare resume evidence with job-description requirements."""
    resume_words = set(resume_text.lower().replace("/", " ").split())
    job_words = {word.strip(".,:;()") for word in job_description.lower().split() if len(word) > 3}
    overlap = len(resume_words & job_words)
    score = min(95, round((overlap / max(len(job_words), 1)) * 100))
    fallback = {
        "match_score": score,
        "ats_score": min(90, score + 12),
        "evidence_score": 65,
        "matching_keywords": sorted(resume_words & job_words)[:30],
        "missing_keywords": sorted(job_words - resume_words)[:30],
        "recommendations": ["Add measurable results to experience bullets.", "Mirror relevant job keywords honestly.", "Keep headings simple for ATS parsing."],
    }
    instruction = (
        "You are a resume reviewer. Compare the resume only with the job description. "
        "Return JSON with match_score, ats_score, evidence_score, matching_keywords, "
        "missing_keywords, recommendations, strengths, and risks."
    )
    return _ask(instruction, f"RESUME:\n{resume_text}\n\nJOB:\n{job_description}", fallback)


def generate_application(resume: str, job: str, company: str, tone: str) -> dict[str, Any]:
    """Generate a truthful cover letter and short application messages."""
    fallback = {
        "cover_letter": "Dear Hiring Manager,\n\nI am excited to apply for this opportunity. My background and projects align with the role's requirements, and I would welcome the chance to discuss how I can contribute.\n\nSincerely,\nYour Name",
        "recruiter_message": "Hello, I am interested in the role and believe my experience aligns with the team's needs. I would be glad to connect.",
        "linkedin_message": f"Hello, I am interested in opportunities at {company or 'your company'} and would be glad to connect.",
        "tell_me_about_yourself": "I am a motivated professional building experience in this field through hands-on projects and continuous learning.",
    }
    instruction = (
        "Create a truthful application pack using only supplied resume facts. Return JSON with "
        "cover_letter, recruiter_message, linkedin_message, and tell_me_about_yourself. "
        f"Tone: {tone}."
    )
    payload = f"RESUME:\n{resume}\n\nCOMPANY:\n{company}\n\nJOB:\n{job}"
    return _ask(instruction, payload, fallback)


def interview_feedback(role: str, difficulty: str, interview_mode: str, question: str, answer: str) -> dict[str, Any]:
    """Score an interview answer and provide a next question."""
    fallback = {
        "overall_score": 70,
        "relevance": 75,
        "clarity": 70,
        "strengths": ["You addressed the question directly."],
        "improvements": ["Add a specific example and measurable result.", "Use a clear Situation, Task, Action, Result structure."],
        "next_question": f"What is one challenge you faced while preparing for a {role} role, and how did you handle it?",
    }
    instruction = (
        f"You are a supportive interview coach for a {interview_mode} interview. "
        "Return JSON with overall_score, relevance, clarity, strengths, improvements, "
        "star_feedback, and next_question. Score only the answer provided."
    )
    payload = json.dumps({"role": role, "difficulty": difficulty, "question": question, "answer": answer})
    return _ask(instruction, payload, fallback)
