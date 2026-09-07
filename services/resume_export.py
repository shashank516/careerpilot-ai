from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def resume_to_pdf(resume: dict) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=LETTER, rightMargin=.65 * inch, leftMargin=.65 * inch, topMargin=.55 * inch, bottomMargin=.55 * inch)
    styles = getSampleStyleSheet()
    story = [Paragraph(str(resume.get("name", "Your Name")), styles["Title"]), Paragraph(str(resume.get("contact", "")), styles["Normal"]), Spacer(1, 10)]
    skills = resume.get("skills", [])
    skills_text = ", ".join(str(item) for item in skills) if isinstance(skills, list) else str(skills)
    sections = [("Summary", resume.get("summary")), ("Skills", skills_text), ("Education", resume.get("education")), ("Experience", resume.get("experience")), ("Projects", resume.get("projects")), ("Certifications and Achievements", resume.get("certifications_achievements"))]
    for heading, content in sections:
        if content:
            story.extend([Paragraph(heading, styles["Heading2"]), Paragraph(str(content).replace("\n", "<br/>"), styles["BodyText"]), Spacer(1, 7)])
    document.build(story)
    return output.getvalue()
