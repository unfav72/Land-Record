import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user, require_role, get_optional_user
import models
from services.excel_generator import generate_excel_export

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/excel")
def export_excel_all(db: Session = Depends(get_db), current_user: models.User = Depends(require_role("officer"))):
    """Generate and download Excel export for all records."""
    try:
        filepath = generate_excel_export(db)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Export generation failed")
            
        return FileResponse(
            path=filepath, 
            filename="land_records_export.xlsx", 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/{record_id}")
def download_pdf(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Download the verified PDF for a record."""
    record = db.query(models.LandRecord).filter(models.LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    if not record.pdf_path or not os.path.exists(record.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not generated or found")
        
    return FileResponse(
        path=record.pdf_path, 
        filename=f"Verified_Land_Record_{record_id}.pdf", 
        media_type="application/pdf"
    )


@router.get("/document/{document_id}/original")
def download_original(document_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Download or view the original uploaded document image/pdf."""
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc or not os.path.exists(doc.original_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(path=doc.original_path, filename=doc.original_filename)


@router.get("/qr/{record_id}")
def download_qr(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Download QR code image."""
    record = db.query(models.LandRecord).filter(models.LandRecord.id == record_id).first()
    if not record or not record.qr_code_path or not os.path.exists(record.qr_code_path):
        raise HTTPException(status_code=404, detail="QR Code not found")
        
    return FileResponse(path=record.qr_code_path, media_type="image/png")
