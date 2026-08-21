import json
import os
from typing import Any


def _setting(name: str, default: str = "") -> str:
    value = os.getenv(name, "")
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, ImportError, KeyError):
        return default


def _client():
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


def _ask(instruction: str, payload: str, fallback: dict[str, Any]) -> dict[str, Any]:
    client = _client()
    if not client:
        return fallback
    api_key = _setting("GROQ_API_KEY") or _setting("OPENAI_API_KEY")
    model = _setting("GROQ_MODEL") or (
        "llama-3.3-70b-versatile" if api_key.startswith("gsk_") else _setting("OPENAI_MODEL") or "gpt-4o-mini"
    )
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": instruction}, {"role": "user", "content": payload}],
    )
    return json.loads(response.choices[0].message.content)


def build_resume(profile: dict[str, Any]) -> dict[str, Any]:
    fallback = {
        "name": profile["name"] or "Your Name", "contact": " | ".join(x for x in [profile["email"], profile["phone"], profile["location"]] if x),
        "target_role": profile["target_role"], "summary": profile["summary"], "skills": [x.strip() for x in profile["skills"].split(",") if x.strip()],
        "education": profile["education"], "experience": profile["experience"], "projects": profile["projects"], "certifications_achievements": profile["extras"],
    }
    instruction = "You are a truthful resume writer. Use only the supplied facts; never invent employers, metrics, dates, or skills. Return JSON with name, contact, target_role, summary, skills, education, experience, projects, certifications_achievements. Rewrite vague bullets professionally but preserve meaning."
    return _ask(instruction, json.dumps(profile), fallback)


def analyze_resume(resume_text: str, job_description: str) -> dict[str, Any]:
    resume_words = set(resume_text.lower().replace("/", " ").split())
    job_words = {word.strip(".,:;()") for word in job_description.lower().split() if len(word) > 3}
    overlap = len(resume_words & job_words)
    score = min(95, round((overlap / max(len(job_words), 1)) * 100))
    fallback = {"match_score": score, "ats_score": min(90, score + 12), "evidence_score": 65, "matching_keywords": sorted(resume_words & job_words)[:30], "missing_keywords": sorted(job_words - resume_words)[:30], "recommendations": ["Add measurable results to experience bullets.", "Mirror relevant keywords from the job description honestly.", "Keep headings simple for ATS parsing."]}
    instruction = "You are a resume reviewer. Compare the resume only with the job description. Never penalize a person for information not present without labeling it as unknown. Return JSON with match_score, ats_score, evidence_score, matching_keywords, missing_keywords, recommendations, strengths, risks."
    return _ask(instruction, f"RESUME:\n{resume_text}\n\nJOB:\n{job_description}", fallback)


def generate_application(resume: str, job: str, tone: str) -> dict[str, Any]:
    fallback = {"cover_letter": "Dear Hiring Manager,\n\nI am excited to apply for this opportunity. My background and projects align with the role's requirements, and I would welcome the chance to discuss how I can contribute.\n\nSincerely,\nYour Name", "recruiter_message": "Hello, I am interested in the role and believe my experience aligns with the team’s needs. I would be glad to connect.", "tell_me_about_yourself": "I am a motivated professional building experience in this field through hands-on projects and continuous learning."}
    instruction = "Create a truthful application pack using only supplied resume facts. Return JSON with cover_letter, recruiter_message, tell_me_about_yourself. Do not invent achievements. Tone: " + tone
    return _ask(instruction, f"RESUME:\n{resume}\n\nJOB:\n{job}", fallback)


def interview_feedback(role: str, difficulty: str, question: str, answer: str) -> dict[str, Any]:
    fallback = {"overall_score": 70, "relevance": 75, "clarity": 70, "strengths": ["You addressed the question directly."], "improvements": ["Add a specific example and measurable result.", "Use a clear Situation, Task, Action, Result structure."], "next_question": f"What is one challenge you faced while preparing for a {role} role, and how did you handle it?"}
    instruction = "You are a supportive but rigorous interview coach. Return JSON with overall_score, relevance, clarity, strengths, improvements, star_feedback, next_question. Score only the answer provided and do not invent facts."
    return _ask(instruction, json.dumps({"role": role, "difficulty": difficulty, "question": question, "answer": answer}), fallback)
