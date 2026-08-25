from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Dict, Any
from models import LandRecord, ValidationResult

def detect_duplicates_and_conflicts(db: Session, record: LandRecord) -> List[ValidationResult]:
    """
    Check for duplicates and ownership conflicts for a given record.
    """
    results = []
    
    if not record.survey_number or not record.village:
        return results

    # Find existing records for the same survey number and village
    # that are not the current record and are verified
    existing_records = db.query(LandRecord).filter(
        LandRecord.id != record.id,
        LandRecord.survey_number == record.survey_number,
        LandRecord.village == record.village,
        LandRecord.status.in_(["VERIFIED", "NEEDS_REVIEW", "CONFLICT"])
    ).all()

    for existing in existing_records:
        # Check for potential exact duplicate
        if existing.owner_name == record.owner_name and existing.area == record.area:
            results.append(
                ValidationResult(
                    record_id=record.id,
                    rule_name="Potential Duplicate",
                    severity="WARNING",
                    message=f"This record appears to be a duplicate of Record ID {existing.id}.",
                    ai_value=f"Owner: {record.owner_name}, Area: {record.area}"
                )
            )
            continue
            
        # Check for ownership conflict (same land, different owner)
        if existing.owner_name and record.owner_name and existing.owner_name.lower() != record.owner_name.lower():
            # It might be a mutation, but we should flag it as a potential conflict
            results.append(
                ValidationResult(
                    record_id=record.id,
                    rule_name="Ownership Conflict",
                    field_name="owner_name",
                    severity="ERROR",
                    message=f"Conflict detected. Record ID {existing.id} shows owner as '{existing.owner_name}' for this survey number.",
                    ai_value=record.owner_name
                )
            )
            record.status = "CONFLICT"

    for res in results:
        db.add(res)
    db.commit()
    
    return results
