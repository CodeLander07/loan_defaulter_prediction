from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from uuid import UUID
from typing import List

from apps.schemas.document import DocumentRiskResponse, DocumentRiskResult
from apps.services.document_service import DocumentRiskService
from apps.middleware.auth_middleware import RoleChecker

# Secure entire router so only users with "risk_engineer" role can access it
require_risk_engineer = RoleChecker(allowed_roles=["risk_engineer"])
router = APIRouter(dependencies=[Depends(require_risk_engineer)])

@router.post("/", response_model=DocumentRiskResponse)
async def evaluate_document_risk(
    loan_application_id: UUID,
    documents: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: DocumentRiskService = Depends(DocumentRiskService),
):
    """Accept documents, kick off async processing, and return a task ID.
    The heavy pipeline runs in a background task; the client can poll
    GET /api/document-risk/{task_id} for the final result.
    """
    try:
        task_id = await service.start_processing(
            loan_application_id=loan_application_id,
            files=documents,
            background_tasks=background_tasks,
        )
        return DocumentRiskResponse(task_id=task_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{task_id}", response_model=DocumentRiskResult)
async def get_document_risk_result(
    task_id: UUID,
    service: DocumentRiskService = Depends(DocumentRiskService),
):
    """Fetch the completed risk result for a previously submitted request."""
    try:
        result = await service.get_result(task_id)
        if result is None:
            # Task is still processing
            raise HTTPException(
                status_code=202,
                detail="Evaluation is still in progress. Please poll again in a few seconds."
            )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
