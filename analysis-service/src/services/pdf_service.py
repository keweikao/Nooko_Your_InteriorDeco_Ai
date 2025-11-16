from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO

def generate_pdf_report(analysis_data: dict) -> bytes:
    """
    Generates a PDF report from analysis data.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    story = []
    
    # Title
    story.append(Paragraph("Nooko 裝潢 AI 夥伴 - 您的專屬藍圖", styles['h1']))
    story.append(Spacer(1, 12))
    
    # Summary
    summary = analysis_data.get("questionnaire_summary", "無摘要")
    story.append(Paragraph("需求摘要:", styles['h2']))
    for line in summary.split('\n'):
        story.append(Paragraph(line, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Construction Spec
    spec = analysis_data.get("construction_spec", {})
    story.append(Paragraph("工程規格建議:", styles['h2']))
    for key, value in spec.items():
        story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
