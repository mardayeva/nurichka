import uuid
from django.core.files.base import ContentFile
from io import BytesIO

def generate_certificate_pdf(student_name: str, course_title: str, cert_id: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        text = (
            "SERTIFIKAT\n"
            f"Student: {student_name}\n"
            f"Course: {course_title}\n"
            f"Certificate ID: {cert_id}\n"
        )
        return text.encode("utf-8")

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(w/2, h-140, "SERTIFIKAT")

    c.setFont("Helvetica", 14)
    c.drawCentredString(w/2, h-190, "Ushbu sertifikat quyidagi tinglovchiga beriladi:")

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(w/2, h-230, student_name)

    c.setFont("Helvetica", 14)
    c.drawCentredString(w/2, h-270, "Kursni muvaffaqiyatli yakunlagani uchun:")

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-310, course_title)

    c.setFont("Helvetica", 11)
    c.drawString(60, 80, f"Certificate ID: {cert_id}")

    c.showPage()
    c.save()
    return buf.getvalue()

def new_cert_id() -> str:
    return uuid.uuid4().hex[:12].upper()

def pdf_to_file(pdf_bytes: bytes, filename: str):
    return ContentFile(pdf_bytes, name=filename)
