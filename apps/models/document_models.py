import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON, Text, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from apps.database import Base

class LoanApplication(Base):
    __tablename__ = "loan_application"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(PGUUID(as_uuid=True), nullable=False)
    loan_type = Column(String, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    uploaded_documents = relationship(
        "UploadedDocument", back_populates="loan_application", cascade="all, delete-orphan"
    )
    document_risk_score = relationship(
        "DocumentRiskScore", uselist=False, back_populates="loan_application", cascade="all, delete-orphan"
    )
    macro_risk_score = relationship(
        "MacroRiskScore", uselist=False, back_populates="loan_application", cascade="all, delete-orphan"
    )
    financial_risk_score = relationship(
        "FinancialRiskScore", uselist=False, back_populates="loan_application", cascade="all, delete-orphan"
    )


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_application_id = Column(PGUUID(as_uuid=True), ForeignKey("loan_application.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    sha256_hash = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    loan_application = relationship("LoanApplication", back_populates="uploaded_documents")
    analysis = relationship(
        "DocumentAnalysis", uselist=False, back_populates="uploaded_document", cascade="all, delete-orphan"
    )


class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploaded_document_id = Column(PGUUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False)
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Numeric(5, 2), nullable=True)
    extracted_fields = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    uploaded_document = relationship("UploadedDocument", back_populates="analysis")
    validation = relationship(
        "DocumentValidation", uselist=False, back_populates="analysis", cascade="all, delete-orphan"
    )
    fraud = relationship(
        "DocumentFraud", uselist=False, back_populates="analysis", cascade="all, delete-orphan"
    )


class DocumentValidation(Base):
    __tablename__ = "document_validation"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_analysis_id = Column(PGUUID(as_uuid=True), ForeignKey("document_analysis.id", ondelete="CASCADE"), nullable=False)
    rule_results = Column(JSON, nullable=True)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    analysis = relationship("DocumentAnalysis", back_populates="validation")


class DocumentFraud(Base):
    __tablename__ = "document_fraud"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_analysis_id = Column(PGUUID(as_uuid=True), ForeignKey("document_analysis.id", ondelete="CASCADE"), nullable=False)
    fraud_probability = Column(Numeric(5, 2), nullable=True)
    rule_flags = Column(JSON, nullable=True)
    ml_shap_values = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    analysis = relationship("DocumentAnalysis", back_populates="fraud")


class DocumentRiskScore(Base):
    __tablename__ = "document_risk_score"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_application_id = Column(PGUUID(as_uuid=True), ForeignKey("loan_application.id", ondelete="CASCADE"), nullable=False, unique=True)
    score = Column(Numeric(5, 2), nullable=False)
    category = Column(String, nullable=False)
    confidence = Column(Numeric(5, 2), nullable=False)
    recommendation = Column(String, nullable=False)
    issues = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    loan_application = relationship("LoanApplication", back_populates="document_risk_score")
