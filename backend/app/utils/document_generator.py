"""Document generator for PDF resumes, cover letters, and styled exports."""
import html
import io
import logging
from typing import Any

logger = logging.getLogger(__name__)


def generate_cover_letter_html(
    candidate_name: str,
    candidate_email: str,
    company: str,
    job_title: str,
    body_text: str,
) -> str:
    """Generate clean, printable HTML for a cover letter."""
    escaped_body = html.escape(body_text).replace("\n", "<br/>")
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #1e293b; margin: 40px; }}
  .header {{ border-bottom: 2px solid #8b5cf6; padding-bottom: 12px; margin-bottom: 24px; }}
  .name {{ font-size: 24px; font-weight: bold; color: #0f172a; }}
  .contact {{ font-size: 14px; color: #64748b; }}
  .meta {{ margin-bottom: 24px; font-size: 14px; color: #475569; }}
  .body {{ font-size: 15px; margin-bottom: 30px; text-align: justify; }}
  .signature {{ font-weight: bold; color: #0f172a; }}
</style>
</head>
<body>
  <div class="header">
    <div class="name">{html.escape(candidate_name)}</div>
    <div class="contact">{html.escape(candidate_email)}</div>
  </div>
  <div class="meta">
    <strong>To:</strong> Hiring Team at {html.escape(company)}<br/>
    <strong>Position:</strong> {html.escape(job_title)}
  </div>
  <div class="body">
    {escaped_body}
  </div>
  <div class="signature">
    Sincerely,<br/>
    {html.escape(candidate_name)}
  </div>
</body>
</html>"""


def generate_resume_html(
    resume_data: dict[str, Any],
) -> str:
    """Generate clean, printable HTML for a tailored resume."""
    name = html.escape(resume_data.get("full_name") or "Applicant")
    email = html.escape(resume_data.get("email") or "")
    phone = html.escape(resume_data.get("phone") or "")
    summary = html.escape(resume_data.get("summary") or "")

    skills = resume_data.get("technical_skills") or []
    skills_html = ", ".join(html.escape(str(s)) for s in skills)

    exp_items = resume_data.get("experience") or []
    exp_html = ""
    for item in exp_items:
        title = html.escape(item.get("title", ""))
        comp = html.escape(item.get("company", ""))
        dur = html.escape(item.get("duration", ""))
        desc = html.escape(item.get("description", ""))
        exp_html += f"""
        <div style="margin-bottom: 12px;">
            <div style="display:flex; justify-content:space-between; font-weight:bold;">
                <span>{title} — {comp}</span>
                <span style="color:#64748b;">{dur}</span>
            </div>
            <p style="margin:4px 0 0 0; color:#334155; font-size:14px;">{desc}</p>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.5; color: #0f172a; margin: 30px; }}
  h1 {{ margin: 0; color: #0f172a; font-size: 26px; }}
  .contact {{ color: #64748b; font-size: 14px; margin-bottom: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }}
  h2 {{ font-size: 16px; text-transform: uppercase; letter-spacing: 1px; color: #8b5cf6; border-bottom: 1px solid #e2e8f0; margin-top: 20px; }}
</style>
</head>
<body>
  <h1>{name}</h1>
  <div class="contact">{email} | {phone}</div>

  {f"<h2>Summary</h2><p>{summary}</p>" if summary else ""}
  
  <h2>Experience</h2>
  {exp_html}

  <h2>Skills</h2>
  <p>{skills_html}</p>
</body>
</html>"""


def generate_pdf_document(title: str, content_html_or_text: str) -> bytes:
    """
    Generate PDF bytes using fpdf2 or reportlab if installed,
    otherwise returns encoded HTML as fallback.
    """
    # Try fpdf2
    try:
        from fpdf import FPDF  # type: ignore

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        pdf.set_font("helvetica", "", 11)
        # Simple plain-text fallback
        clean_text = content_html_or_text.replace("<br/>", "\n").replace("<br>", "\n")
        # Strip simple tags
        import re

        clean_text = re.sub(r"<[^>]+>", "", clean_text)
        pdf.multi_cell(0, 7, clean_text)

        output = io.BytesIO()
        pdf.output(output)
        return output.getvalue()
    except Exception as e:
        logger.debug(f"fpdf2 PDF generation not available or failed: {e}")

    # Try reportlab
    try:
        from reportlab.lib.pagesizes import letter  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, 750, title)
        c.setFont("Helvetica", 11)

        y = 720
        clean_lines = content_html_or_text.splitlines()
        for line in clean_lines[:45]:
            c.drawString(72, y, line[:80])
            y -= 14

        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.debug(f"reportlab generation failed: {e}")

    # Fallback: return utf-8 encoded HTML
    return content_html_or_text.encode("utf-8")
