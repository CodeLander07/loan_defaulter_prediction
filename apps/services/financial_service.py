import os
import logging
import numpy as np
import pandas as pd
import joblib
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from apps.database import get_db
from apps.models.financial_models import FinancialRiskScore
from apps.models.document_models import LoanApplication
from apps.schemas.financial_risk import FinancialRiskRequest, FinancialRiskResult, IndustryScoresResult
from apps.features.ratio_mapper import map_ratios

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'storage', 'models')


class FinancialRiskService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self._load_models()

    def _load_models(self):
        try:
            ensemble = joblib.load(os.path.join(MODELS_DIR, 'financial_risk_ensemble.pkl'))
            self.polish_model = joblib.load(os.path.join(MODELS_DIR, 'polish_xgb.pkl'))
            self.industry = joblib.load(os.path.join(MODELS_DIR, 'industry_risk_model.pkl'))
            self.feature_names = ensemble.get('feature_names', [])
            self.default_rate = ensemble.get('default_rate', 0.0694)
            self.industry_scores = self.industry.get('mapped_scores', {})
            logger.info(f"Models loaded: Polish AUC=0.953, Industry AUC={self.industry.get('performance', {}).get('auc', 0.776)}")
            logger.info(f"Default rate: {self.default_rate}")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise RuntimeError("Model loading failed. Ensure storage/models/ contains all model files.")

    def evaluate(self, request: FinancialRiskRequest) -> dict:
        ratios = request.financial_ratios or {}
        n_ratios = len(ratios)

        if n_ratios > 0:
            pdf, matched = map_ratios(ratios)
            if self.feature_names:
                pdf = pdf[self.feature_names]
            prob = float(self.polish_model.predict_proba(pdf)[0, 1])
            financial_score = round(min(max(prob, 0.0), 1.0), 4)
        else:
            financial_score = self.default_rate
            matched = []

        ind_score = self._get_industry_score(request.industry_code)
        combined = round(0.6 * financial_score + 0.4 * ind_score, 4)

        if combined < 0.2:
            tier = "Low Risk"
        elif combined < 0.4:
            tier = "Moderate Risk"
        elif combined < 0.6:
            tier = "High Risk"
        else:
            tier = "Very High Risk"

        self._persist_score(request, financial_score, ind_score, combined, tier, matched)

        return FinancialRiskResult(
            loan_application_id=request.loan_application_id,
            financial_risk_score=financial_score,
            industry_risk_score=round(ind_score, 4),
            combined_score=combined,
            risk_tier=tier,
            matched_features=matched[:10],
            features_provided=n_ratios,
        )

    def _get_industry_score(self, industry_code: str) -> float:
        code = industry_code.lower().replace(' ', '_')
        if code in self.industry_scores:
            return float(self.industry_scores[code])
        if self.industry_scores:
            return float(np.median(list(self.industry_scores.values())))
        return 0.5

    def _persist_score(self, request, fin_score, ind_score, combined, tier, matched):
        loan_app_id = request.loan_application_id
        loan_app = self.db.query(LoanApplication).filter(LoanApplication.id == loan_app_id).first()
        if not loan_app:
            loan_app = LoanApplication(
                id=loan_app_id,
                applicant_id=loan_app_id,
                loan_type=request.industry_code or "unknown",
                amount=request.loan_amount or 0,
            )
            self.db.add(loan_app)
            self.db.flush()

        record = self.db.query(FinancialRiskScore).filter(
            FinancialRiskScore.loan_application_id == loan_app_id
        ).first()
        if not record:
            record = FinancialRiskScore(
                loan_application_id=loan_app_id,
                financial_score=fin_score,
                industry_score=ind_score,
                combined_score=combined,
                risk_tier=tier,
                matched_features=matched,
                features_provided=len(request.financial_ratios or {}),
            )
            self.db.add(record)
        else:
            record.financial_score = fin_score
            record.industry_score = ind_score
            record.combined_score = combined
            record.risk_tier = tier
            record.matched_features = matched
            record.features_provided = len(request.financial_ratios or {})
            record.created_at = datetime.utcnow()
        self.db.commit()

    def get_industry_scores(self) -> dict:
        return IndustryScoresResult(
            scores=self.industry_scores,
            count=len(self.industry_scores),
        )
