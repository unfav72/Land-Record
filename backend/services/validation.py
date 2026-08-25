import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import LandRecord, ValidationResult


def validate_record(db: Session, record: LandRecord) -> List[ValidationResult]:
    """
    Run validation rules against a land record.
    Returns a list of validation results (warnings/errors).
    """
    results = []

    # 1. Check required fields
    required_fields = ["owner_name", "survey_number", "village", "area", "district"]
    for field in required_fields:
        val = getattr(record, field)
        if not val or str(val).strip() == "":
            results.append(
                ValidationResult(
                    record_id=record.id,
                    rule_name="Required Field Missing",
                    field_name=field,
                    severity="ERROR",
                    message=f"'{field.replace('_', ' ').title()}' is a required field.",
                    ai_value=None,
                )
            )

    # 2. Format validation: Survey Number
    if record.survey_number:
        if not re.match(r"^[\w/\-\.]+$", record.survey_number):
            results.append(
                ValidationResult(
                    record_id=record.id,
                    rule_name="Invalid Format",
                    field_name="survey_number",
                    severity="WARNING",
                    message="Survey number contains unusual characters.",
                    ai_value=record.survey_number,
                    expected_format="Alphanumeric, slashes, hyphens",
                )
            )

    # 3. Format validation: Area
    if record.area:
        # Just numbers and dots/commas
        area_num = re.sub(r"[^\d\.,]", "", str(record.area))
        if not area_num:
            results.append(
                ValidationResult(
                    record_id=record.id,
                    rule_name="Invalid Format",
                    field_name="area",
                    severity="WARNING",
                    message="Area does not appear to contain numeric values.",
                    ai_value=record.area,
                    expected_format="Numeric values (e.g. 2.45)",
                )
            )

    # 4. Logical validation: Confidence Checks
    if record.overall_confidence and record.overall_confidence < 0.6:
        results.append(
            ValidationResult(
                record_id=record.id,
                rule_name="Low Confidence",
                severity="WARNING",
                message=f"Overall AI confidence is low ({int(record.overall_confidence * 100)}%). Manual review strongly advised.",
            )
        )

    # Note: Duplicate detection and conflict detection are handled separately
    # as they require broader DB queries.

    # Persist validation results
    for res in results:
        db.add(res)
    
    # Optionally update record status based on validation
    if any(r.severity == "ERROR" for r in results):
        record.status = "NEEDS_REVIEW"
        
    db.commit()
    
    return results
