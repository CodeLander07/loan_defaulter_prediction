import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Date, Numeric, Text, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from apps.database import Base

class MacroIndicator(Base):
    __tablename__ = "macro_indicator"
    __table_args__ = (
        UniqueConstraint("name", "region", "date", name="uq_name_region_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Numeric(12, 4), nullable=False)
    frequency = Column(String, nullable=False)


class MacroRiskScore(Base):
    __tablename__ = "macro_risk_score"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_application_id = Column(PGUUID(as_uuid=True), ForeignKey("loan_application.id", ondelete="CASCADE"), nullable=False, unique=True)
    score = Column(Numeric(5, 2), nullable=False)
    category = Column(String, nullable=False)
    confidence = Column(Numeric(5, 2), nullable=False)
    contributing_factors = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    loan_application = relationship("LoanApplication", back_populates="macro_risk_score")
