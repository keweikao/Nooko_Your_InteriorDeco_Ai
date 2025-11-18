import logging
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback when reportlab missing
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)

def generate_pdf_report(analysis_data: dict) -> bytes:
    """
    Generates a PDF report from analysis data.
    """
    buffer = BytesIO()

    if REPORTLAB_AVAILABLE:
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        story = []
        story.append(Paragraph("HouseIQ 裝潢 AI 夥伴 - 您的專屬藍圖", styles["h1"]))
        story.append(Spacer(1, 12))

        summary = analysis_data.get("questionnaire_summary", "無摘要")
        story.append(Paragraph("需求摘要:", styles["h2"]))
        for line in summary.split("\n"):
            story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 12))

        spec = analysis_data.get("construction_spec", {})
        story.append(Paragraph("工程規格建議:", styles["h2"]))
        for key, value in spec.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
        story.append(Spacer(1, 12))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    # Fallback：沒有 reportlab 時回傳簡易文字 PDF（其實是純文字）
    logger.warning("reportlab not installed, using plain-text PDF fallback.")
    summary = analysis_data.get("questionnaire_summary", "無摘要")
    spec = analysis_data.get("construction_spec", {})

    content_lines = [
        "HouseIQ 裝潢 AI 夥伴 - 您的專屬藍圖",
        "==============================",
        "需求摘要:",
        summary,
        "",
        "工程規格建議:",
    ]
    for key, value in spec.items():
        content_lines.append(f"- {key}: {value}")

    buffer.write("\n".join(content_lines).encode("utf-8"))
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
