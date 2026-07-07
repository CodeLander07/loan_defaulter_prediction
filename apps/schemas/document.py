from __future__ import annotations

from uuid import UUID
from typing import List

from pydantic import BaseModel, Field


class DocumentRiskResponse(BaseModel):
    """Returned after POST – contains the async task ID."""
    task_id: UUID = Field(..., description="Unique identifier for the background processing task")


class DocumentRiskResult(BaseModel):
    """Returned by GET /{task_id} once processing finishes."""
    task_id: UUID = Field(..., description="Task identifier")
    score: int = Field(..., ge=0, le=100, description="Document risk score (0‑100)")
    risk_category: str = Field(..., description="Low / Medium / High")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence (0‑1)")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Estimated fraud likelihood")
    detected_issues: List[str] = Field(default_factory=list, description="Human‑readable list of issues")
    recommendation: str = Field(..., description="Next‑step recommendation for the lender")
    explainable_summary: str = Field(..., description="One‑sentence explainable summary")
