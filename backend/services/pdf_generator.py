import os
from pathlib import Path
from fpdf import FPDF
from config import settings
from models import LandRecord, Document
import uuid
from datetime import datetime


class LandRecordPDF(FPDF):
    def header(self):
        # Header text
        self.set_font("Arial", "B", 14)
        self.cell(0, 8, "GOVERNMENT OF TAMIL NADU", border=0, ln=1, align="C")
        self.set_font("Arial", "B", 11)
        self.cell(0, 6, "Ministry of Rural Development", border=0, ln=1, align="C")
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "PATTA / LAND OWNERSHIP RECORD", border=0, ln=1, align="C")
        self.line(10, 35, 200, 35)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")
        self.cell(0, 10, "Digitized by Intelligent Land Record System", 0, 0, "R")


def generate_verified_pdf(record: LandRecord, document: Document, qr_path: str = None) -> str:
    pdf = LandRecordPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Meta Info
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 6, "District :", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 6, record.district or "-", 0)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 6, "Patta No. :", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 6, str(record.id) or "-", 0, 1)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 6, "Taluk :", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 6, record.taluk_tehsil or "-", 0)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 6, "Village :", 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 6, record.village or "-", 0, 1)

    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    # 1. Details of Persons
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "1. Details of Persons / Owners", 0, 1)
    
    # Table Header
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(15, 8, "Sl. No.", border=1, align="C", fill=True)
    pdf.cell(60, 8, "Name of Patta Holder", border=1, align="C", fill=True)
    pdf.cell(60, 8, "Father's/Spouse's Name", border=1, align="C", fill=True)
    pdf.cell(55, 8, "Ownership Type", border=1, align="C", fill=True)
    pdf.ln()

    # Table Row
    pdf.set_font("Arial", "", 9)
    pdf.cell(15, 8, "1", border=1, align="C")
    pdf.cell(60, 8, (record.owner_name or "-")[:35], border=1, align="C")
    pdf.cell(60, 8, (record.father_spouse_name or "-")[:35], border=1, align="C")
    pdf.cell(55, 8, (record.ownership_type or "-")[:35], border=1, align="C")
    pdf.ln(10)

    # 2. Details of Land
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "2. Details of Land", 0, 1)

    # Table Header
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 8, "Survey No.", border=1, align="C", fill=True)
    pdf.cell(30, 8, "Subdivision No.", border=1, align="C", fill=True)
    pdf.cell(65, 8, "Land Type & Classification", border=1, align="C", fill=True)
    pdf.cell(65, 8, "Total Area", border=1, align="C", fill=True)
    pdf.ln()

    # Table Row
    pdf.set_font("Arial", "", 9)
    pdf.cell(30, 8, (record.survey_number or "-")[:15], border=1, align="C")
    pdf.cell(30, 8, (record.sub_survey_number or "-")[:15], border=1, align="C")
    ltype = f"{record.land_type or ''} / {record.land_classification or ''}".strip(' /')
    pdf.cell(65, 8, ltype[:30] or "-", border=1, align="C")
    
    area_val = f"{record.area or ''} {record.area_unit or ''}".strip()
    pdf.cell(65, 8, area_val[:30] or "-", border=1, align="C")
    pdf.ln(10)

    # 3. Registration Details
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "3. Registration & Mutation", 0, 1)
    
    # Table Header
    pdf.set_font("Arial", "B", 9)
    pdf.cell(47, 8, "Registration No.", border=1, align="C", fill=True)
    pdf.cell(48, 8, "Registration Date", border=1, align="C", fill=True)
    pdf.cell(47, 8, "Mutation No.", border=1, align="C", fill=True)
    pdf.cell(48, 8, "Mutation Date", border=1, align="C", fill=True)
    pdf.ln()

    # Table Row
    pdf.set_font("Arial", "", 9)
    pdf.cell(47, 8, str(record.registration_number or "-")[:20], border=1, align="C")
    pdf.cell(48, 8, str(record.registration_date or "-")[:20], border=1, align="C")
    pdf.cell(47, 8, str(record.mutation_number or "-")[:20], border=1, align="C")
    pdf.cell(48, 8, str(record.mutation_date or "-")[:20], border=1, align="C")
    pdf.ln(20)

    # Footer Signatures
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 8, "", 0, 0)
    pdf.cell(90, 8, "Signature / E-Sign", 0, 1, "R")
    
    pdf.set_font("Arial", "", 9)
    pdf.cell(100, 6, "", 0, 0)
    pdf.cell(90, 6, f"Name: {record.verifier.full_name if record.verifier else 'System Generated'}", 0, 1, "R")
    pdf.cell(100, 6, "", 0, 0)
    pdf.cell(90, 6, f"Designation: Verifying Officer", 0, 1, "R")
    
    date_str = record.verified_at.strftime('%d/%m/%Y') if record.verified_at else datetime.utcnow().strftime('%d/%m/%Y')
    pdf.cell(100, 6, "", 0, 0)
    pdf.cell(90, 6, f"Date: {date_str}", 0, 1, "R")

    # Add QR Code if provided
    if qr_path and os.path.exists(qr_path):
        pdf.image(qr_path, x=15, y=pdf.get_y() - 25, w=30)

    # Save
    filename = f"verified_record_{record.id}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(settings.GENERATED_DIR, filename)
    pdf.output(filepath)
    
    return filepath
