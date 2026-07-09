from uuid import UUID
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class FinancialRiskRequest(BaseModel):
    loan_application_id: UUID = Field(..., description="Reference UUID for the loan application")
    financial_ratios: Dict[str, float] = Field(default_factory=dict, description="User-provided financial ratios (e.g. roa, current_ratio, operating_margin)")
    industry_code: str = Field(default="unknown", description="Industry sector (e.g. it_services, manufacturing, retail)")
    loan_amount: Optional[float] = Field(None, description="Loan amount for context")


class IndustryRiskItem(BaseModel):
    sector: str
    score: float


class FinancialRiskResult(BaseModel):
    loan_application_id: UUID
    financial_risk_score: float = Field(..., ge=0.0, le=1.0, description="Financial risk score (0-1)")
    industry_risk_score: float = Field(..., ge=0.0, le=1.0, description="Industry risk score (0-1)")
    combined_score: float = Field(..., ge=0.0, le=1.0, description="Weighted combined score (0.6 fin + 0.4 ind)")
    risk_tier: str = Field(..., description="Low / Moderate / High / Very High Risk")
    matched_features: List[str] = Field(default_factory=list, description="XGBoost feature names that were matched from provided ratios")
    features_provided: int = Field(0, description="Number of ratio keys provided by user")


class IndustryScoresResult(BaseModel):
    scores: Dict[str, float]
    count: int
