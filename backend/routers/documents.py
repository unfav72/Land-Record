import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, BackgroundTasks, Form
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from auth import get_current_user
import models, schemas
from config import settings
from services.processing import process_document_pipeline
from datetime import datetime

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import traceback as tb
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif"]:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Save original file
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        # Create document record
        db_document = models.Document(
            filename=unique_filename,
            original_filename=file.filename,
            original_path=file_path,
            file_size=file_size,
            file_type=file.content_type,
            uploaded_by=current_user.id,
            status="UPLOADING",
            document_type=document_type
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        # Log action
        audit = models.AuditLog(
            document_id=db_document.id,
            user_id=current_user.id,
            action="DOCUMENT_UPLOADED",
            details=f"Uploaded {file.filename}"
        )
        db.add(audit)
        db.commit()

        # Trigger background processing with a fresh session
        bg_db = SessionLocal()
        background_tasks.add_task(process_document_pipeline, db_document.id, bg_db)

        return db_document
    except HTTPException:
        raise
    except Exception as e:
        print(f"UPLOAD ERROR: {e}")
        tb.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual", response_model=schemas.LandRecordResponse)
async def create_manual_record(
    record_data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Create a placeholder document
        db_document = models.Document(
            filename="manual_entry.json",
            original_filename="Manual Entry",
            original_path="",
            file_size=0,
            file_type="application/json",
            uploaded_by=current_user.id,
            status="PROCESSED",
            document_type="Manual"
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        # Create the verified land record
        db_record = models.LandRecord(
            document_id=db_document.id,
            owner_name=record_data.get("owner_name"),
            father_spouse_name=record_data.get("father_spouse_name"),
            ownership_type=record_data.get("ownership_type"),
            survey_number=record_data.get("survey_number"),
            sub_survey_number=record_data.get("sub_survey_number"),
            khata_number=record_data.get("khata_number"),
            khasra_number=record_data.get("khasra_number"),
            village=record_data.get("village"),
            taluk_tehsil=record_data.get("taluk_tehsil"),
            district=record_data.get("district"),
            state=record_data.get("state"),
            area=record_data.get("area"),
            area_unit=record_data.get("area_unit"),
            land_type=record_data.get("land_type"),
            land_classification=record_data.get("land_classification"),
            registration_number=record_data.get("registration_number"),
            registration_date=record_data.get("registration_date"),
            mutation_number=record_data.get("mutation_number"),
            mutation_date=record_data.get("mutation_date"),
            status="VERIFIED",
            overall_confidence=1.0,
            verified_by=current_user.id,
            verified_at=datetime.utcnow()
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        # Log action
        audit = models.AuditLog(
            document_id=db_document.id,
            user_id=current_user.id,
            action="MANUAL_RECORD_CREATED",
            details="Manually entered and verified record."
        )
        db.add(audit)
        db.commit()

        # Generate PDF and QR code for this verified record
        from services.pdf_generator import generate_verified_pdf
        from services.qr_service import generate_qr_code

        qr_path = generate_qr_code(db_record.id)
        db_record.qr_code_path = qr_path
        
        pdf_path = generate_verified_pdf(db_record, db_document, qr_path)
        db_record.pdf_path = pdf_path
        
        db.commit()

        return db_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=schemas.DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/jobs", response_model=List[schemas.ProcessingJobResponse])
def get_document_jobs(document_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    jobs = db.query(models.ProcessingJob).filter(models.ProcessingJob.document_id == document_id).order_by(models.ProcessingJob.id.asc()).all()
    return jobs
