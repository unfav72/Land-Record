from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─── Auth Schemas ───────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "officer"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ─── Document Schemas ───────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    status: str
    document_type: Optional[str] = None
    document_type_confidence: Optional[float] = None
    language: Optional[str] = None
    ocr_confidence: Optional[float] = None
    handwriting_confidence: Optional[float] = None
    upload_time: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    uploaded_by: Optional[int] = None

    model_config = {"from_attributes": True}


# ─── Land Record Schemas ────────────────────────────────────────────────────────

class LandRecordResponse(BaseModel):
    id: int
    document_id: int

    # Owner
    owner_name: Optional[str] = None
    father_spouse_name: Optional[str] = None
    ownership_type: Optional[str] = None

    # Land ID
    survey_number: Optional[str] = None
    sub_survey_number: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_number: Optional[str] = None

    # Location
    village: Optional[str] = None
    taluk_tehsil: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None

    # Land Details
    area: Optional[str] = None
    area_unit: Optional[str] = None
    land_classification: Optional[str] = None
    land_type: Optional[str] = None

    # Registration
    registration_number: Optional[str] = None
    registration_date: Optional[str] = None

    # Mutation
    mutation_number: Optional[str] = None
    mutation_date: Optional[str] = None
    previous_owner: Optional[str] = None
    current_owner: Optional[str] = None

    # Confidence
    overall_confidence: Optional[float] = None
    field_confidences: Optional[str] = None
    field_sources: Optional[str] = None

    # Status
    status: str
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    pdf_path: Optional[str] = None
    qr_code_path: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LandRecordUpdate(BaseModel):
    owner_name: Optional[str] = None
    father_spouse_name: Optional[str] = None
    ownership_type: Optional[str] = None
    survey_number: Optional[str] = None
    sub_survey_number: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_number: Optional[str] = None
    village: Optional[str] = None
    taluk_tehsil: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    area: Optional[str] = None
    area_unit: Optional[str] = None
    land_classification: Optional[str] = None
    land_type: Optional[str] = None
    registration_number: Optional[str] = None
    registration_date: Optional[str] = None
    mutation_number: Optional[str] = None
    mutation_date: Optional[str] = None
    previous_owner: Optional[str] = None
    current_owner: Optional[str] = None


# ─── Field Correction Schemas ───────────────────────────────────────────────────

class FieldCorrectionCreate(BaseModel):
    field_name: str
    officer_value: str
    reason: Optional[str] = None


class FieldCorrectionResponse(BaseModel):
    id: int
    record_id: int
    field_name: str
    ai_value: Optional[str] = None
    officer_value: Optional[str] = None
    final_value: Optional[str] = None
    confidence: Optional[float] = None
    corrected_by: Optional[int] = None
    corrected_at: datetime
    reason: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Validation Schemas ─────────────────────────────────────────────────────────

class ValidationResultResponse(BaseModel):
    id: int
    record_id: int
    rule_name: str
    field_name: Optional[str] = None
    severity: str
    message: str
    ai_value: Optional[str] = None
    expected_format: Optional[str] = None
    is_resolved: bool
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Audit Log Schemas ──────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: int
    record_id: Optional[int] = None
    document_id: Optional[int] = None
    user_id: Optional[int] = None
    action: str
    field_name: Optional[str] = None
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


# ─── Record Approval ────────────────────────────────────────────────────────────

class RecordAction(BaseModel):
    action: str  # approve, reject, save_draft
    rejection_reason: Optional[str] = None


# ─── Dashboard Schemas ──────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_documents: int
    processed: int
    verified: int
    needs_review: int
    conflicts: int
    rejected: int
    drafts: int
    avg_confidence: float
    languages: dict
    document_types: dict


class ProcessingJobResponse(BaseModel):
    id: int
    document_id: int
    stage: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Search Schemas ─────────────────────────────────────────────────────────────

class SearchQuery(BaseModel):
    query: Optional[str] = None
    owner_name: Optional[str] = None
    survey_number: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    village: Optional[str] = None
    taluk: Optional[str] = None
    district: Optional[str] = None
    record_id: Optional[int] = None
    registration_number: Optional[str] = None
    mutation_number: Optional[str] = None
    status: Optional[str] = None
    language: Optional[str] = None
    document_type: Optional[str] = None
    skip: int = 0
    limit: int = 20
