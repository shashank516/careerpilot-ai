import json
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


TEMPLATES = ["Classic ATS", "Modern Timeline", "Bold Minimal"]


def _text(value: object) -> str:
    if isinstance(value, list):
        return "\n".join(_text(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value or "").strip()


def _paragraph(value: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_text(value)).replace("\n", "<br/>"), style)


def _bullets(value: object, style: ParagraphStyle) -> list[Paragraph]:
    if isinstance(value, list):
        return [Paragraph(f"&#8226;&nbsp; {escape(_text(item))}", style) for item in value if _text(item)]
    return [_paragraph(value, style)] if _text(value) else []


def _section(story: list, title: str, value: object, styles: dict, accent: colors.Color) -> None:
    if not _text(value):
        return
    story.append(Paragraph(title.upper(), styles["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=accent, spaceAfter=5))
    story.extend(_bullets(value, styles["body"]))
    story.append(Spacer(1, 8))


def resume_to_pdf(resume: dict, template: str = "Classic ATS") -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=LETTER, rightMargin=.62 * inch, leftMargin=.62 * inch, topMargin=.5 * inch, bottomMargin=.5 * inch)
    base = getSampleStyleSheet()
    accent = colors.HexColor("#54758d") if template == "Modern Timeline" else colors.HexColor("#1b1b1b")
    name_color = colors.HexColor("#193047") if template == "Modern Timeline" else colors.HexColor("#111111")
    styles = {
        "name": ParagraphStyle("name", parent=base["Title"], fontName="Helvetica-Bold", fontSize=23 if template != "Bold Minimal" else 26, leading=27, textColor=name_color, alignment=TA_LEFT, spaceAfter=3),
        "role": ParagraphStyle("role", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=accent, spaceAfter=3),
        "contact": ParagraphStyle("contact", parent=base["Normal"], fontSize=8.5, leading=11, textColor=colors.HexColor("#4c5560"), spaceAfter=10),
        "section": ParagraphStyle("section", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=accent, spaceBefore=7, spaceAfter=2),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica", fontSize=8.8, leading=12, textColor=colors.HexColor("#20252a"), spaceAfter=3),
    }
    name = resume.get("name", "Your Name")
    contact = resume.get("contact", "")
    role = resume.get("target_role", "")
    story = [_paragraph(name, styles["name"])]
    if role:
        story.append(_paragraph(role, styles["role"]))
    story.append(_paragraph(contact, styles["contact"]))
    story.append(HRFlowable(width="100%", thickness=2 if template == "Bold Minimal" else 1, color=accent, spaceAfter=8))
    if template == "Modern Timeline":
        _section(story, "Profile", resume.get("summary"), styles, accent)
        _section(story, "Skills", resume.get("skills"), styles, accent)
        _section(story, "Experience", resume.get("experience"), styles, accent)
        _section(story, "Projects", resume.get("projects"), styles, accent)
        _section(story, "Education", resume.get("education"), styles, accent)
    elif template == "Bold Minimal":
        summary = [[_paragraph("PROFILE", styles["section"]), _paragraph(resume.get("summary"), styles["body"])] ] if _text(resume.get("summary")) else []
        if summary:
            table = Table(summary, colWidths=[1.05 * inch, 5.85 * inch])
            table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), .5, accent), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
            story.extend([table, Spacer(1, 5)])
        _section(story, "Key Skills", resume.get("skills"), styles, accent)
        _section(story, "Experience", resume.get("experience"), styles, accent)
        _section(story, "Education & Development", resume.get("education"), styles, accent)
        _section(story, "Projects & Achievements", resume.get("projects"), styles, accent)
    else:
        _section(story, "Summary", resume.get("summary"), styles, accent)
        _section(story, "Work Experience", resume.get("experience"), styles, accent)
        _section(story, "Projects", resume.get("projects"), styles, accent)
        _section(story, "Education", resume.get("education"), styles, accent)
        _section(story, "Skills", resume.get("skills"), styles, accent)
    _section(story, "Certifications and Achievements", resume.get("certifications_achievements"), styles, accent)
    document.build(story)
    return output.getvalue()
