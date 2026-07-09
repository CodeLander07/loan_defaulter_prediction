import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from apps.database import Base


class FinancialRiskScore(Base):
    __tablename__ = "financial_risk_score"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_application_id = Column(PGUUID(as_uuid=True), ForeignKey("loan_application.id", ondelete="CASCADE"), nullable=False, unique=True)
    financial_score = Column(Numeric(6, 4), nullable=False, comment="Financial risk score (0-1) from XGBoost")
    industry_score = Column(Numeric(6, 4), nullable=False, comment="Industry risk score (0-1)")
    combined_score = Column(Numeric(6, 4), nullable=False, comment="0.6*financial + 0.4*industry")
    risk_tier = Column(String, nullable=False, comment="Low / Moderate / High / Very High Risk")
    matched_features = Column(JSON, nullable=True, comment="XGBoost feature names matched from provided ratios")
    features_provided = Column(Float, default=0, comment="Number of ratio keys provided by user")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    loan_application = relationship("LoanApplication", back_populates="financial_risk_score")
