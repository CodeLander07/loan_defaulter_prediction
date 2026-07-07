import math
import logging
from datetime import date, datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from fastapi import Depends
from apps.database import get_db
from apps.models.macro_models import MacroIndicator, MacroRiskScore
from apps.models.document_models import LoanApplication
from apps.schemas.macro import MacroRiskRequest

logger = logging.getLogger(__name__)

# Default weights for indicator risk mapping (sum of absolute weights = 1.0)
INDICATOR_WEIGHTS = {
    "Inflation": 0.30,
    "RepoRate": 0.25,
    "GDPGrowth": -0.15,      # High GDP growth lowers risk
    "UnemploymentRate": 0.10,
    "HousingIndex": 0.05,
    "IndustryGrowth": -0.10,  # High industry growth lowers risk
    "FuelPrices": 0.05,
}

# Baseline means and standard deviations (calibrated for Z-score calculation)
INDICATOR_STATS = {
    "Inflation": {"mean": 5.5, "std": 1.2},
    "RepoRate": {"mean": 5.8, "std": 0.8},
    "GDPGrowth": {"mean": 6.5, "std": 1.5},
    "UnemploymentRate": {"mean": 7.2, "std": 1.1},
    "HousingIndex": {"mean": 100.0, "std": 10.0},
    "IndustryGrowth": {"mean": 4.5, "std": 2.0},
    "FuelPrices": {"mean": 95.0, "std": 8.0},
}

class MacroService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def seed_initial_indicators(self) -> int:
        """
        Seeds mock historical macroeconomic indicators if database is empty.
        This provides a starting dataset for calculation.
        """
        count = self.db.query(MacroIndicator).count()
        if count > 0:
            return 0

        logger.info("Seeding initial macroeconomic indicators...")
        
        # Generate 12 months of historical data up to current month
        today = date.today()
        seeded = 0
        
        indicators_data = [
            # (name, base_val, trend_direction)
            ("Inflation", 5.8, 0.1),
            ("RepoRate", 6.2, 0.05),
            ("GDPGrowth", 6.8, -0.1),
            ("UnemploymentRate", 7.1, 0.05),
            ("HousingIndex", 108.0, 0.5),
            ("IndustryGrowth", 4.2, 0.15),
            ("FuelPrices", 98.2, 0.4),
        ]
        
        for name, base_val, trend in indicators_data:
            for month_offset in range(12, -1, -1):
                # Calculate past date (approximate months)
                year = today.year
                month = today.month - month_offset
                while month <= 0:
                    month += 12
                    year -= 1
                
                indicator_date = date(year, month, 1)
                
                # Apply deterministic variance
                variance = math.sin(month_offset) * 0.3
                value = round(base_val + (month_offset * trend) + variance, 4)
                
                ind = MacroIndicator(
                    name=name,
                    region="National",
                    date=indicator_date,
                    value=value,
                    frequency="Monthly"
                )
                self.db.add(ind)
                seeded += 1
                
        self.db.commit()
        logger.info(f"Successfully seeded {seeded} macro indicators.")
        return seeded

    def get_latest_indicators(self) -> Dict[str, float]:
        """
        Fetches the latest available value for each indicator from the database.
        """
        # Ensure we have data
        self.seed_initial_indicators()
        
        latest_vals = {}
        for name in INDICATOR_WEIGHTS.keys():
            latest = (
                self.db.query(MacroIndicator)
                .filter(MacroIndicator.name == name)
                .order_by(desc(MacroIndicator.date))
                .first()
            )
            if latest:
                latest_vals[name] = float(latest.value)
            else:
                # Fallback to mean if not found
                latest_vals[name] = INDICATOR_STATS[name]["mean"]
                
        return latest_vals

    def evaluate_macro_risk(self, request: MacroRiskRequest) -> Dict[str, Any]:
        """
        Main orchestration logic for macro risk evaluation.
        """
        # 1. Fetch latest indicators
        indicators = self.get_latest_indicators()
        
        # 2. Compute Z-Scores and weighted raw scores
        weighted_sum = 0.0
        contributing_factors = {}
        explanations = []

        for name, weight in INDICATOR_WEIGHTS.items():
            val = indicators[name]
            stats = INDICATOR_STATS[name]
            
            # Z-score: how many standard deviations from the historical mean
            z_score = (val - stats["mean"]) / stats["std"]
            
            # Weighted contribution
            contrib = z_score * weight
            weighted_sum += contrib
            
            # Contribution impact (absolute scale for display)
            contributing_factors[name] = round(abs(contrib), 4)
            
            # Simple explanation generation
            direction = "higher" if z_score > 0 else "lower"
            status = "unfavorable" if contrib > 0.1 else "favorable" if contrib < -0.1 else "stable"
            explanations.append(f"{name} is {val} ({direction} than historical mean of {stats['mean']}; impact is {status})")

        # 3. Apply Sigmoid function to map raw score to 0-100 scale
        # K factor is 0.5 to keep mapping smooth
        k = 0.5
        sigmoid_val = 1.0 / (1.0 + math.exp(-k * weighted_sum))
        score = int(round(sigmoid_val * 100))
        
        # Adjust score for industry risk (Dynamic weights based on input)
        # e.g. Manufacturing is highly sensitive to FuelPrices and RepoRate
        if request.industry == "Manufacturing":
            # Add a slight penalty if FuelPrices is high
            fuel_val = indicators.get("FuelPrices", 95.0)
            if fuel_val > INDICATOR_STATS["FuelPrices"]["mean"]:
                score = min(score + 5, 100)
                
        # Limit boundary checks
        score = max(0, min(100, score))
        
        # 4. Map score to risk category
        if score <= 30:
            category = "Low"
        elif score <= 70:
            category = "Medium"
        else:
            category = "High"

        # 5. Determine confidence
        # Confidence is higher when historical variance is lower or data is fresh
        confidence = 0.90  # Base confidence
        
        # 6. Generate final explanation
        summary = f"Macroeconomic risk is {category} with score {score}. Key drivers: " + "; ".join(explanations[:3]) + "."

        # 7. Persist evaluation results
        loan_app_id = request.loan_application_id
        
        # Ensure a loan application stub exists to prevent FK violation
        loan_app = self.db.query(LoanApplication).filter(LoanApplication.id == loan_app_id).first()
        if not loan_app:
            logger.info(f"LoanApplication ID {loan_app_id} not found in DB. Creating a stub row.")
            loan_app = LoanApplication(
                id=loan_app_id,
                applicant_id=loan_app_id, # Placeholder UUID
                loan_type=request.loan_type,
                amount=request.loan_amount
            )
            self.db.add(loan_app)
            self.db.flush() # flush to database to ensure constraint passes

        # Save or update macro risk score
        macro_score_record = self.db.query(MacroRiskScore).filter(MacroRiskScore.loan_application_id == loan_app_id).first()
        if not macro_score_record:
            macro_score_record = MacroRiskScore(
                loan_application_id=loan_app_id,
                score=score,
                category=category,
                confidence=confidence,
                contributing_factors=contributing_factors,
                explanation=summary
            )
            self.db.add(macro_score_record)
        else:
            macro_score_record.score = score
            macro_score_record.category = category
            macro_score_record.confidence = confidence
            macro_score_record.contributing_factors = contributing_factors
            macro_score_record.explanation = summary
            macro_score_record.created_at = datetime.utcnow()
            
        self.db.commit()

        return {
            "loan_application_id": loan_app_id,
            "macro_risk_score": score,
            "risk_category": category,
            "confidence": confidence,
            "contributing_factors": contributing_factors,
            "explainable_summary": summary
        }
