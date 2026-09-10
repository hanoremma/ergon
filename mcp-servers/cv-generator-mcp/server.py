"""
cv-generator-mcp — MCP Server for CV Enhancement & Generation
Tools:
  - enhance_cv: Apply suggestions to a CV and generate improved version
  - export_cv_pdf: Export enhanced CV as PDF (base64)
  - export_cv_docx: Export enhanced CV as DOCX (base64)
"""
import os
import re
import json
import base64
import httpx
from io import BytesIO
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(override=True)

mcp = FastMCP(
    name="cv-generator-mcp",
    instructions="MCP server untuk menghasilkan CV yang sudah direvisi berdasarkan saran perbaikan, dalam format PDF atau DOCX.",
)

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")


async def call_granite(prompt: str, max_tokens: int = 2000) -> str:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            token_resp = await client.post(
                "https://iam.cloud.ibm.com/identity/token",
                data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": WATSONX_API_KEY},
            )
            token_resp.raise_for_status()
            iam_token = token_resp.json()["access_token"]
            resp = await client.post(
                f"{WATSONX_URL}/ml/v1/text/generation?version=2024-05-31",
                headers={"Authorization": f"Bearer {iam_token}", "Content-Type": "application/json"},
                json={
                    "model_id": "ibm/granite-13b-instruct-v2",
                    "project_id": WATSONX_PROJECT_ID,
                    "input": prompt,
                    "parameters": {"max_new_tokens": max_tokens, "temperature": 0.2},
                },
            )
            resp.raise_for_status()
            return resp.json()["results"][0]["generated_text"]
    except Exception as e:
        return ""


@mcp.tool()
async def enhance_cv(
    cv_data: dict,
    suggestions: list[dict],
    job_data: dict = {},
    selected_suggestions: list[int] = [],
) -> dict:
    """
    Terapkan saran perbaikan ke CV dan generate versi yang sudah direvisi.

    Args:
        cv_data: Output dari resume-parser-mcp (struktur CV asli)
        suggestions: Output dari scoring-engine-mcp (daftar saran perbaikan)
        job_data: Output dari job-scraper-mcp (untuk konteks)
        selected_suggestions: List rank saran yang ingin diterapkan (kosong = terapkan semua)

    Returns:
        Dict berisi enhanced_cv_data (struktur CV baru yang sudah direvisi)
    """
    # Filter suggestions to apply
    if selected_suggestions:
        apply_suggestions = [s for s in suggestions if s.get("rank") in selected_suggestions]
    else:
        apply_suggestions = suggestions

    suggestions_text = "\n".join([
        f"{i+1}. {s.get('title', '')}: {s.get('detail', '')}"
        for i, s in enumerate(apply_suggestions)
    ])

    # Build CV text representation
    cv_text = build_cv_text(cv_data)
    job_context = f"Posisi: {job_data.get('position', '')} di {job_data.get('company', '')}"

    prompt = f"""Kamu adalah seorang konsultan CV profesional. Revisi CV berikut berdasarkan saran yang diberikan.

CV Asli:
{cv_text[:3000]}

Target loker: {job_context}

Saran yang harus diterapkan:
{suggestions_text}

Buat versi CV yang sudah direvisi dalam format JSON terstruktur yang sama dengan input.
Perubahan harus konkret dan spesifik. JANGAN buat-buat pengalaman atau skill yang tidak ada di CV asli.
Hanya perbaiki framing, kuantifikasi yang wajar, dan urutan/penekanan.

Format JSON (sama dengan struktur cv_data input):
{{
  "personal_info": {{...}},
  "summary": "summary yang sudah diperbaiki",
  "work_experience": [...],
  "education": [...],
  "skills": {{...}},
  "certifications": [...],
  "enhancement_notes": ["perubahan yang dilakukan 1", "perubahan 2"]
}}

JSON:"""

    try:
        llm_output = await call_granite(prompt)
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if json_match:
            enhanced = json.loads(json_match.group())
            if "enhancement_notes" not in enhanced:
                enhanced["enhancement_notes"] = [s.get("title", "") for s in apply_suggestions]
            return {"enhanced_cv": enhanced, "suggestions_applied": len(apply_suggestions)}
    except Exception as e:
        pass

    # Fallback: return original with notes
    return {
        "enhanced_cv": {
            **cv_data,
            "enhancement_notes": [
                f"[DITERAPKAN] {s.get('title', '')}" for s in apply_suggestions
            ],
        },
        "suggestions_applied": len(apply_suggestions),
        "note": "Enhancement otomatis tidak optimal — silakan terapkan saran secara manual",
    }


def build_cv_text(cv_data: dict) -> str:
    """Convert structured CV data to readable text."""
    lines = []
    info = cv_data.get("personal_info") or {}
    if info.get("name"):
        lines.append(f"NAMA: {info['name']}")
    if info.get("email"):
        lines.append(f"Email: {info['email']}")
    if info.get("phone"):
        lines.append(f"Telepon: {info['phone']}")
    if cv_data.get("summary"):
        lines.append(f"\nSUMMARY:\n{cv_data['summary']}")
    if cv_data.get("work_experience"):
        lines.append("\nPENGALAMAN KERJA:")
        for exp in cv_data["work_experience"]:
            lines.append(f"  {exp.get('position', '')} — {exp.get('company', '')} ({exp.get('duration', '')})")
            for r in (exp.get("responsibilities") or [])[:3]:
                lines.append(f"    • {r}")
            for a in (exp.get("achievements") or [])[:2]:
                lines.append(f"    ✓ {a}")
    if cv_data.get("skills"):
        skills = cv_data["skills"]
        if isinstance(skills, dict):
            all_skills = (skills.get("technical") or []) + (skills.get("tools") or [])
            lines.append(f"\nSKILL: {', '.join(all_skills[:15])}")
    return "\n".join(lines)


def generate_pdf_from_cv(cv_data: dict, job_position: str = "") -> bytes:
    """Generate PDF from enhanced CV data using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle(
        "CVTitle", parent=styles["Heading1"],
        fontSize=20, textColor=colors.HexColor("#211D3D"),
        spaceAfter=4,
    )
    section_style = ParagraphStyle(
        "CVSection", parent=styles["Heading2"],
        fontSize=11, textColor=colors.HexColor("#5B4FE5"),
        spaceBefore=12, spaceAfter=4, borderPad=2,
    )
    body_style = ParagraphStyle(
        "CVBody", parent=styles["Normal"],
        fontSize=9.5, textColor=colors.HexColor("#4A4570"),
        spaceAfter=3,
    )
    sub_style = ParagraphStyle(
        "CVSub", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#9E98C9"),
    )

    story = []
    info = cv_data.get("personal_info") or {}

    # Name
    name = info.get("name", "CV Hasil Revisi — Ergon")
    story.append(Paragraph(name, title_style))

    # Contact
    contact_parts = [x for x in [
        info.get("email"), info.get("phone"), info.get("location"),
        info.get("linkedin"), info.get("github"),
    ] if x]
    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), sub_style))

    if job_position:
        story.append(Paragraph(f"Melamar untuk: {job_position}", sub_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#C9C3F0")))
    story.append(Spacer(1, 4))

    # Summary
    if cv_data.get("summary"):
        story.append(Paragraph("PROFIL", section_style))
        story.append(Paragraph(cv_data["summary"], body_style))

    # Work Experience
    work_exp = cv_data.get("work_experience") or []
    if work_exp:
        story.append(Paragraph("PENGALAMAN KERJA", section_style))
        for exp in work_exp:
            pos_line = f"<b>{exp.get('position', '')}</b> — {exp.get('company', '')} | {exp.get('duration', '')}"
            story.append(Paragraph(pos_line, body_style))
            for resp in (exp.get("responsibilities") or [])[:4]:
                story.append(Paragraph(f"• {resp}", body_style))
            for ach in (exp.get("achievements") or [])[:2]:
                story.append(Paragraph(f"✓ {ach}", body_style))
            story.append(Spacer(1, 4))

    # Education
    edu = cv_data.get("education") or []
    if edu:
        story.append(Paragraph("PENDIDIKAN", section_style))
        for e in edu:
            story.append(Paragraph(
                f"<b>{e.get('degree', '')} {e.get('field', '')}</b> — {e.get('institution', '')} ({e.get('year', '')})",
                body_style,
            ))

    # Skills
    skills_data = cv_data.get("skills") or {}
    if isinstance(skills_data, dict):
        all_skills = (skills_data.get("technical") or []) + (skills_data.get("tools") or [])
        if all_skills:
            story.append(Paragraph("SKILL", section_style))
            story.append(Paragraph(", ".join(all_skills[:20]), body_style))
        soft_skills = skills_data.get("soft") or []
        if soft_skills:
            story.append(Paragraph("SOFT SKILL: " + ", ".join(soft_skills[:8]), body_style))

    # Enhancement notes
    notes = cv_data.get("enhancement_notes") or []
    if notes:
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E7E3FC")))
        story.append(Paragraph(
            '<font size="8" color="#9E98C9">CV ini dioptimalkan oleh Ergon · estimasi kecocokan, bukan jaminan diterima</font>',
            body_style,
        ))

    doc.build(story)
    return buffer.getvalue()


@mcp.tool()
async def export_cv_pdf(
    enhanced_cv: dict,
    job_data: dict = {},
) -> dict:
    """
    Export CV yang sudah direvisi sebagai PDF.

    Args:
        enhanced_cv: Output dari enhance_cv tool (enhanced_cv field)
        job_data: Data loker untuk context (optional)

    Returns:
        Dict dengan pdf_base64 (base64 encoded PDF) dan filename
    """
    try:
        pdf_bytes = generate_pdf_from_cv(enhanced_cv, job_data.get("position", ""))
        pdf_b64 = base64.b64encode(pdf_bytes).decode()
        name = (enhanced_cv.get("personal_info") or {}).get("name", "cv")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", name).lower()
        return {
            "pdf_base64": pdf_b64,
            "filename": f"ergon-{safe_name}-revisi.pdf",
            "size_bytes": len(pdf_bytes),
        }
    except Exception as e:
        return {"error": f"Gagal generate PDF: {str(e)}"}


@mcp.tool()
async def export_cv_docx(
    enhanced_cv: dict,
    job_data: dict = {},
) -> dict:
    """
    Export CV yang sudah direvisi sebagai DOCX (Word).

    Args:
        enhanced_cv: Output dari enhance_cv tool (enhanced_cv field)
        job_data: Data loker untuk context (optional)

    Returns:
        Dict dengan docx_base64 (base64 encoded DOCX) dan filename
    """
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Margins
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    info = enhanced_cv.get("personal_info") or {}

    # Name
    name_para = doc.add_heading(info.get("name", "CV Hasil Revisi"), 0)
    name_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if name_para.runs:
        name_para.runs[0].font.color.rgb = RGBColor(0x21, 0x1D, 0x3D)

    # Contact
    contact = " | ".join(filter(None, [
        info.get("email"), info.get("phone"),
        info.get("location"), info.get("linkedin"),
    ]))
    if contact:
        p = doc.add_paragraph(contact)
        p.runs[0].font.size = Pt(9)
        p.runs[0].font.color.rgb = RGBColor(0x9E, 0x98, 0xC9)

    doc.add_paragraph()

    # Summary
    if enhanced_cv.get("summary"):
        h = doc.add_heading("PROFIL", level=2)
        h.runs[0].font.color.rgb = RGBColor(0x5B, 0x4F, 0xE5)
        doc.add_paragraph(enhanced_cv["summary"])

    # Work Experience
    work_exp = enhanced_cv.get("work_experience") or []
    if work_exp:
        h = doc.add_heading("PENGALAMAN KERJA", level=2)
        h.runs[0].font.color.rgb = RGBColor(0x5B, 0x4F, 0xE5)
        for exp in work_exp:
            p = doc.add_paragraph()
            run = p.add_run(f"{exp.get('position', '')} — {exp.get('company', '')}")
            run.bold = True
            p.add_run(f" | {exp.get('duration', '')}")
            for resp in (exp.get("responsibilities") or [])[:4]:
                doc.add_paragraph(resp, style="List Bullet")
            for ach in (exp.get("achievements") or [])[:2]:
                doc.add_paragraph(f"✓ {ach}", style="List Bullet")

    # Education
    edu = enhanced_cv.get("education") or []
    if edu:
        h = doc.add_heading("PENDIDIKAN", level=2)
        h.runs[0].font.color.rgb = RGBColor(0x5B, 0x4F, 0xE5)
        for e in edu:
            doc.add_paragraph(
                f"{e.get('degree', '')} {e.get('field', '')} — {e.get('institution', '')} ({e.get('year', '')})"
            )

    # Skills
    skills_data = enhanced_cv.get("skills") or {}
    if isinstance(skills_data, dict):
        all_skills = (skills_data.get("technical") or []) + (skills_data.get("tools") or [])
        if all_skills:
            h = doc.add_heading("SKILL", level=2)
            h.runs[0].font.color.rgb = RGBColor(0x5B, 0x4F, 0xE5)
            doc.add_paragraph(", ".join(all_skills[:20]))

    # Footer note
    doc.add_paragraph()
    footer_p = doc.add_paragraph("CV ini dioptimalkan oleh Ergon · estimasi kecocokan, bukan jaminan diterima")
    footer_p.runs[0].font.size = Pt(8)
    footer_p.runs[0].font.color.rgb = RGBColor(0x9E, 0x98, 0xC9)

    buffer = BytesIO()
    doc.save(buffer)
    docx_bytes = buffer.getvalue()
    docx_b64 = base64.b64encode(docx_bytes).decode()

    name = info.get("name", "cv")
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", name).lower()
    return {
        "docx_base64": docx_b64,
        "filename": f"ergon-{safe_name}-revisi.docx",
        "size_bytes": len(docx_bytes),
    }


if __name__ == "__main__":
    port = int(os.getenv("CV_GENERATOR_MCP_PORT", "8006"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
