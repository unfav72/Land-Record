from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="officer")  # officer, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    original_path = Column(String(500), nullable=False)
    processed_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)

    # Processing status: UPLOADING, PREPROCESSING, OCR, EXTRACTING, VALIDATING, COMPLETED, FAILED
    status = Column(String(50), default="UPLOADING")

    document_type = Column(String(100), nullable=True)
    document_type_confidence = Column(Float, nullable=True)
    language = Column(String(50), nullable=True)

    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    handwriting_confidence = Column(Float, nullable=True)

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    upload_time = Column(DateTime, default=utcnow)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    land_record = relationship("LandRecord", back_populates="document", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="document", foreign_keys="AuditLog.document_id")
    processing_jobs = relationship("ProcessingJob", back_populates="document")
    uploader = relationship("User", foreign_keys=[uploaded_by])


class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # Owner Details
    owner_name = Column(String(200), nullable=True)
    father_spouse_name = Column(String(200), nullable=True)
    ownership_type = Column(String(100), nullable=True)

    # Land Identification
    survey_number = Column(String(50), nullable=True)
    sub_survey_number = Column(String(50), nullable=True)
    khasra_number = Column(String(50), nullable=True)
    khata_number = Column(String(50), nullable=True)
    plot_number = Column(String(50), nullable=True)

    # Location
    village = Column(String(100), nullable=True)
    taluk_tehsil = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)

    # Land Details
    area = Column(String(50), nullable=True)
    area_unit = Column(String(50), nullable=True)
    land_classification = Column(String(100), nullable=True)
    land_type = Column(String(100), nullable=True)

    # Registration
    registration_number = Column(String(100), nullable=True)
    registration_date = Column(String(50), nullable=True)

    # Mutation
    mutation_number = Column(String(100), nullable=True)
    mutation_date = Column(String(50), nullable=True)
    previous_owner = Column(String(200), nullable=True)
    current_owner = Column(String(200), nullable=True)

    # Confidence
    overall_confidence = Column(Float, nullable=True)
    field_confidences = Column(Text, nullable=True)  # JSON string
    field_sources = Column(Text, nullable=True)  # JSON string

    # Status: DRAFT, NEEDS_REVIEW, VERIFIED, REJECTED
    status = Column(String(50), default="DRAFT")

    # Verification
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Generated files
    pdf_path = Column(String(500), nullable=True)
    qr_code_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    document = relationship("Document", back_populates="land_record")
    field_corrections = relationship("FieldCorrection", back_populates="record", order_by="FieldCorrection.corrected_at.desc()")
    validation_results = relationship("ValidationResult", back_populates="record")
    audit_logs = relationship("AuditLog", back_populates="record", foreign_keys="AuditLog.record_id")
    verifier = relationship("User", foreign_keys=[verified_by])


class FieldCorrection(Base):
    __tablename__ = "field_corrections"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    ai_value = Column(Text, nullable=True)
    officer_value = Column(Text, nullable=True)
    final_value = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    corrected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    corrected_at = Column(DateTime, default=utcnow)
    reason = Column(Text, nullable=True)

    record = relationship("LandRecord", back_populates="field_corrections")
    corrector = relationship("User", foreign_keys=[corrected_by])


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    rule_name = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=True)
    severity = Column(String(20), default="WARNING")  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    ai_value = Column(Text, nullable=True)
    expected_format = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    record = relationship("LandRecord", back_populates="validation_results")
    resolver = relationship("User", foreign_keys=[resolved_by])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("land_records.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=True)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utcnow)

    record = relationship("LandRecord", back_populates="audit_logs", foreign_keys=[record_id])
    document = relationship("Document", back_populates="audit_logs", foreign_keys=[document_id])
    user = relationship("User", foreign_keys=[user_id])


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    stage = Column(String(50), nullable=False)  # PREPROCESSING, OCR, EXTRACTION, VALIDATION, CLASSIFICATION
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result_data = Column(Text, nullable=True)  # JSON

    document = relationship("Document", back_populates="processing_jobs")
