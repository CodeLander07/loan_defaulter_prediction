from __future__ import annotations

from uuid import UUID
from typing import List, Dict

from pydantic import BaseModel, Field


class MacroRiskRequest(BaseModel):
    """Payload for the macro‑risk POST endpoint."""
    loan_amount: float = Field(..., description="Requested loan amount")
    loan_type: str = Field(..., description="Loan product type (e.g., SME, Home)")
    industry: str = Field(..., description="Borrower industry")
    location: str = Field(..., description="Geographic location / region")
    employment_sector: str = Field(..., description="Employment sector (Private, Govt, Self‑Employed)")


class MacroRiskResponse(BaseModel):
    """Returned after POST – contains the async task ID."""
    task_id: UUID = Field(..., description="Unique identifier for the background processing task")


class MacroRiskResult(BaseModel):
    """Returned by GET /{task_id} once processing finishes."""
    task_id: UUID = Field(..., description="Task identifier")
    score: int = Field(..., ge=0, le=100, description="Macro‑risk score (0‑100)")
    risk_category: str = Field(..., description="Low / Medium / High")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence (0‑1)")
    contributing_factors: Dict[str, float] = Field(default_factory=dict, description="Weight‑adjusted factor contributions")
    explainable_summary: str = Field(..., description="Human‑readable explanation")
