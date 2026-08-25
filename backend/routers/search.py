from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/", response_model=List[schemas.LandRecordResponse])
def search_records(
    search_params: schemas.SearchQuery,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.LandRecord).join(models.Document)

    # General text query across multiple fields
    if search_params.query:
        q = f"%{search_params.query}%"
        query = query.filter(
            or_(
                models.LandRecord.owner_name.ilike(q),
                models.LandRecord.survey_number.ilike(q),
                models.LandRecord.village.ilike(q),
                models.LandRecord.registration_number.ilike(q)
            )
        )

    # Specific field filters
    if search_params.owner_name:
        query = query.filter(models.LandRecord.owner_name.ilike(f"%{search_params.owner_name}%"))
    if search_params.survey_number:
        query = query.filter(models.LandRecord.survey_number.ilike(f"%{search_params.survey_number}%"))
    if search_params.village:
        query = query.filter(models.LandRecord.village.ilike(f"%{search_params.village}%"))
    if search_params.district:
        query = query.filter(models.LandRecord.district.ilike(f"%{search_params.district}%"))
    if search_params.status:
        query = query.filter(models.LandRecord.status == search_params.status)
        
    # Document relations
    if search_params.language:
        query = query.filter(models.Document.language == search_params.language)
    if search_params.document_type:
        query = query.filter(models.Document.document_type == search_params.document_type)

    return query.order_by(models.LandRecord.created_at.desc()).offset(search_params.skip).limit(search_params.limit).all()
