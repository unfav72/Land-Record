from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    total_docs = db.query(models.Document).count()
    
    # Processed (completed processing pipeline)
    processed = db.query(models.Document).filter(models.Document.status == "COMPLETED").count()
    
    # Record statuses
    verified = db.query(models.LandRecord).filter(models.LandRecord.status == "VERIFIED").count()
    needs_review = db.query(models.LandRecord).filter(models.LandRecord.status == "NEEDS_REVIEW").count()
    conflicts = db.query(models.LandRecord).filter(models.LandRecord.status == "CONFLICT").count()
    rejected = db.query(models.LandRecord).filter(models.LandRecord.status == "REJECTED").count()
    drafts = db.query(models.LandRecord).filter(models.LandRecord.status == "DRAFT").count()
    
    # Average confidence
    avg_conf_result = db.query(func.avg(models.LandRecord.overall_confidence)).scalar()
    avg_conf = float(avg_conf_result) if avg_conf_result else 0.0

    # Group by language
    langs = db.query(models.Document.language, func.count(models.Document.id)).group_by(models.Document.language).all()
    lang_dict = {lang or "Unknown": count for lang, count in langs}
    
    # Group by doc type
    types = db.query(models.Document.document_type, func.count(models.Document.id)).group_by(models.Document.document_type).all()
    type_dict = {dtype or "Unknown": count for dtype, count in types}
    
    return schemas.DashboardStats(
        total_documents=total_docs,
        processed=processed,
        verified=verified,
        needs_review=needs_review,
        conflicts=conflicts,
        rejected=rejected,
        drafts=drafts,
        avg_confidence=avg_conf,
        languages=lang_dict,
        document_types=type_dict
    )
