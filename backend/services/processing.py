import traceback
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import Document, LandRecord, ProcessingJob, AuditLog
from services.preprocessing import preprocess_image
from services.ocr import get_ocr_service
from services.extraction import get_extraction_service
from services.classification import classify_document
from services.handwriting import detect_handwriting
from services.validation import validate_record
from services.duplicate_detection import detect_duplicates_and_conflicts


def process_document_pipeline(document_id: int, db: Session):
    """
    Main orchestration pipeline for processing a scanned document.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return

    try:
        doc.processing_started_at = datetime.now(timezone.utc)
        doc.status = "PREPROCESSING"
        db.commit()

        # 1. Preprocessing
        _log_job(db, doc.id, "PREPROCESSING", "RUNNING")
        preprocess_results = preprocess_image(doc.original_path)
        doc.processed_path = preprocess_results["processed_path"]
        _log_job(db, doc.id, "PREPROCESSING", "COMPLETED", preprocess_results)

        # 2. OCR & Handwriting Detection
        doc.status = "OCR"
        db.commit()
        _log_job(db, doc.id, "OCR", "RUNNING")
        
        ocr_service = get_ocr_service()
        ocr_results = ocr_service.extract_text(doc.processed_path)
        
        hw_results = detect_handwriting(doc.processed_path)
        
        doc.ocr_text = ocr_results["raw_text"]
        doc.ocr_confidence = ocr_results["confidence"]
        doc.language = ocr_results["language"]
        doc.handwriting_confidence = hw_results["confidence"]
        
        _log_job(db, doc.id, "OCR", "COMPLETED", {"engine": ocr_results.get("engine"), "confidence": doc.ocr_confidence})

        # 3. Classification
        doc.status = "CLASSIFICATION"
        db.commit()
        _log_job(db, doc.id, "CLASSIFICATION", "RUNNING")
        
        class_results = classify_document(doc.ocr_text, doc.original_filename)
        doc.document_type = class_results["type"]
        doc.document_type_confidence = class_results["confidence"]
        
        _log_job(db, doc.id, "CLASSIFICATION", "COMPLETED", class_results)

        # 4. Extraction
        doc.status = "EXTRACTING"
        db.commit()
        _log_job(db, doc.id, "EXTRACTION", "RUNNING")
        
        extraction_service = get_extraction_service()
        extracted_fields = extraction_service.extract_fields(doc.ocr_text, doc.processed_path)
        
        _log_job(db, doc.id, "EXTRACTION", "COMPLETED")

        # 5. Build Land Record
        record = _build_land_record(doc.id, extracted_fields)
        db.add(record)
        db.commit()
        db.refresh(record)

        # Log AI extraction to audit
        audit = AuditLog(
            record_id=record.id,
            document_id=doc.id,
            action="AI_EXTRACTION_COMPLETED",
            details="AI successfully extracted fields from document."
        )
        db.add(audit)
        db.commit()

        # 6. Validation & Duplicates
        doc.status = "VALIDATING"
        db.commit()
        _log_job(db, doc.id, "VALIDATION", "RUNNING")
        
        validate_record(db, record)
        detect_duplicates_and_conflicts(db, record)
        
        _log_job(db, doc.id, "VALIDATION", "COMPLETED")

        # Finalize
        doc.status = "COMPLETED"
        doc.processing_completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        db.rollback()
        error_msg = f"Processing failed: {str(e)}\n{traceback.format_exc()}"
        doc.status = "FAILED"
        doc.error_message = str(e)
        doc.processing_completed_at = datetime.now(timezone.utc)
        
        # Log failed job
        failed_job = db.query(ProcessingJob).filter(
            ProcessingJob.document_id == doc.id, 
            ProcessingJob.status == "RUNNING"
        ).first()
        if failed_job:
            failed_job.status = "FAILED"
            failed_job.error_message = str(e)
            failed_job.completed_at = datetime.now(timezone.utc)
            
        db.commit()


def _log_job(db: Session, doc_id: int, stage: str, status: str, result_data: dict = None):
    if status == "RUNNING":
        job = ProcessingJob(document_id=doc_id, stage=stage, status=status, started_at=datetime.now(timezone.utc))
        db.add(job)
    else:
        job = db.query(ProcessingJob).filter(
            ProcessingJob.document_id == doc_id, 
            ProcessingJob.stage == stage
        ).order_by(ProcessingJob.id.desc()).first()
        if job:
            job.status = status
            job.completed_at = datetime.now(timezone.utc)
            if result_data:
                job.result_data = json.dumps(result_data)
    db.commit()


def _build_land_record(document_id: int, fields: dict) -> LandRecord:
    record = LandRecord(document_id=document_id, status="NEEDS_REVIEW")
    
    confidences = {}
    sources = {}
    
    for key, data in fields.items():
        if hasattr(record, key):
            setattr(record, key, data.get("value"))
            confidences[key] = data.get("confidence")
            sources[key] = data.get("source_text")
            
    record.field_confidences = json.dumps(confidences)
    record.field_sources = json.dumps(sources)
    
    if confidences:
        record.overall_confidence = sum(confidences.values()) / len(confidences)
    else:
        record.overall_confidence = 0.0
        
    return record
