from fastapi import APIRouter, Depends, HTTPException
from apps.schemas.macro import MacroRiskRequest, MacroRiskResult
from apps.services.macro_service import MacroService
from apps.middleware.auth_middleware import RoleChecker

# Secure entire router so only users with "risk_engineer" role can access it
require_risk_engineer = RoleChecker(allowed_roles=["risk_engineer"])
router = APIRouter(dependencies=[Depends(require_risk_engineer)])

@router.post("/", response_model=MacroRiskResult)
async def evaluate_macro_risk(
    request: MacroRiskRequest,
    service: MacroService = Depends(MacroService),
):
    """Evaluates the macroeconomic risk of a loan application synchronously.
    Reads current and historical macro indicators from the database,
    calculates normalized z-scores, aggregates them with weights,
    and returns a comprehensive risk assessment immediately.
    """
    try:
        result = service.evaluate_macro_risk(request)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
