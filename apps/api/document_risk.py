from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from uuid import UUID
from typing import List

from apps.schemas.document import DocumentRiskRequest, DocumentRiskResponse
from apps.services.document_service import DocumentRiskService

router = APIRouter()

@router.post("/", response_model=DocumentRiskResponse)
async def evaluate_document_risk(
    loan_application_id: UUID,
    documents: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks,
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
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return DocumentRiskResponse(task_id=task_id)

@router.get("/{task_id}", response_model=DocumentRiskResponse)
async def get_document_risk_result(
    task_id: UUID,
    service: DocumentRiskService = Depends(DocumentRiskService),
):
    """Fetch the completed risk result for a previously submitted request."""
    result = await service.get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found or still processing")
    return result
