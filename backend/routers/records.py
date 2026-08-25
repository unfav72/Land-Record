from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
from auth import get_current_user, require_role
import models, schemas
import json

router = APIRouter(prefix="/api/records", tags=["records"])

@router.get("/", response_model=List[schemas.LandRecordResponse])
def list_records(skip: int = 0, limit: int = 50, status: str = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.LandRecord)
    if status:
        query = query.filter(models.LandRecord.status == status)
    return query.order_by(models.LandRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{record_id}", response_model=schemas.LandRecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.LandRecord).filter(models.LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.get("/{record_id}/validation", response_model=List[schemas.ValidationResultResponse])
def get_record_validation(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.ValidationResult).filter(models.ValidationResult.record_id == record_id).all()


@router.get("/{record_id}/corrections", response_model=List[schemas.FieldCorrectionResponse])
def get_record_corrections(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.FieldCorrection).filter(models.FieldCorrection.record_id == record_id).order_by(models.FieldCorrection.corrected_at.desc()).all()


@router.post("/{record_id}/correct", response_model=schemas.FieldCorrectionResponse)
def correct_field(
    record_id: int, 
    correction: schemas.FieldCorrectionCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(require_role("officer"))
):
    record = db.query(models.LandRecord).filter(models.LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    if record.status == "VERIFIED":
        raise HTTPException(status_code=400, detail="Cannot edit a verified record")
        
    if not hasattr(record, correction.field_name):
        raise HTTPException(status_code=400, detail=f"Invalid field name: {correction.field_name}")

    # Get current (AI) value
    old_value = str(getattr(record, correction.field_name) or "")
    
    # Get AI confidence for this field
    conf_dict = {}
    if record.field_confidences:
        try:
            conf_dict = json.loads(record.field_confidences)
        except:
            pass
    field_conf = conf_dict.get(correction.field_name)

    # Save correction
    corr = models.FieldCorrection(
        record_id=record_id,
        field_name=correction.field_name,
        ai_value=old_value,
        officer_value=correction.officer_value,
        final_value=correction.officer_value,
        confidence=field_conf,
        corrected_by=current_user.id,
        reason=correction.reason
    )
    db.add(corr)
    
    # Update record
    setattr(record, correction.field_name, correction.officer_value)
    
    # Audit log
    audit = models.AuditLog(
        record_id=record_id,
        user_id=current_user.id,
        action="FIELD_CORRECTED",
        field_name=correction.field_name,
        previous_value=old_value,
        new_value=correction.officer_value,
        details=correction.reason
    )
    db.add(audit)
    
    db.commit()
    db.refresh(corr)
    return corr


@router.post("/{record_id}/action", response_model=schemas.LandRecordResponse)
def action_record(
    record_id: int, 
    action_data: schemas.RecordAction, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(require_role("officer"))
):
    record = db.query(models.LandRecord).filter(models.LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    action = action_data.action.lower()
    
    if action == "approve":
        record.status = "VERIFIED"
        record.verified_by = current_user.id
        record.verified_at = datetime.now(timezone.utc)
        
        # Trigger PDF and QR generation
        from services.pdf_generator import generate_verified_pdf
        from services.qr_service import generate_qr_code
        
        qr_path = generate_qr_code(record.id)
        record.qr_code_path = qr_path
        
        pdf_path = generate_verified_pdf(record, record.document, qr_path)
        record.pdf_path = pdf_path
        
        log_msg = "Record approved and verified"
        
    elif action == "reject":
        record.status = "REJECTED"
        record.rejection_reason = action_data.rejection_reason
        log_msg = f"Record rejected: {action_data.rejection_reason}"
        
    elif action == "save_draft":
        record.status = "DRAFT"
        log_msg = "Record saved as draft"
        
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    audit = models.AuditLog(
        record_id=record_id,
        user_id=current_user.id,
        action=f"STATUS_CHANGED_{action.upper()}",
        details=log_msg
    )
    db.add(audit)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_record(
    record_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(require_role("officer"))
):
    record = db.query(models.LandRecord).filter(models.LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    # Also delete associated document if it exists
    if record.document_id:
        doc = db.query(models.Document).filter(models.Document.id == record.document_id).first()
        if doc:
            db.delete(doc)
            
    db.delete(record)
    db.commit()
    return None
