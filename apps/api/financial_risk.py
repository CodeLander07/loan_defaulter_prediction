from fastapi import APIRouter, Depends, HTTPException
from apps.schemas.financial_risk import FinancialRiskRequest, FinancialRiskResult, IndustryScoresResult
from apps.services.financial_service import FinancialRiskService
from apps.middleware.auth_middleware import RoleChecker

require_risk_engineer = RoleChecker(allowed_roles=["risk_engineer"])
router = APIRouter(dependencies=[Depends(require_risk_engineer)])


@router.post("/", response_model=FinancialRiskResult)
async def evaluate_financial_risk(
    request: FinancialRiskRequest,
    service: FinancialRiskService = Depends(FinancialRiskService),
):
    """Evaluates financial + industry risk using XGBoost models.
    Maps user-provided financial ratios to 5 verified Polish XGBoost features
    and returns a combined risk score with industry context.
    """
    try:
        result = service.evaluate(request)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/industry-scores", response_model=IndustryScoresResult)
async def get_industry_scores(
    service: FinancialRiskService = Depends(FinancialRiskService),
):
    """Returns all 10 industry sector risk scores."""
    return service.get_industry_scores()
