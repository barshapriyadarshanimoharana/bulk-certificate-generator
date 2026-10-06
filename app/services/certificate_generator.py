from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path("certificates")
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_certificate(
    name: str,
    email: str,
    event_name: str,
    certificate_title: str,
    recipient_id: int,
) -> str:
    output = OUTPUT_DIR / f"certificate_{recipient_id}.pdf"
    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(str(output), pagesize=(page_width, page_height))

    # Single predefined certificate template.
    pdf.setLineWidth(3)
    pdf.rect(15 * mm, 15 * mm, page_width - 30 * mm, page_height - 30 * mm)

    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(page_width / 2, page_height - 65 * mm, certificate_title)

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(page_width / 2, page_height - 90 * mm, "This certificate is proudly presented to")

    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(page_width / 2, page_height - 115 * mm, name)

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(page_width / 2, page_height - 140 * mm, f"for participating in {event_name}")

    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(page_width / 2, 30 * mm, email)

    pdf.save()
    return str(output)
