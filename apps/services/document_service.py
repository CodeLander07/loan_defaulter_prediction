import os
import uuid
import shutil
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from apps.database import get_db
from apps.models.document_models import (
    LoanApplication,
    UploadedDocument,
    DocumentAnalysis,
    DocumentValidation,
    DocumentFraud,
    DocumentRiskScore,
)
from apps.utils.ocr import perform_ocr
from apps.utils.classifier import classify_document
from apps.utils.validation import (
    extract_fields_from_text,
    validate_extracted_fields,
    perform_cross_verification,
    evaluate_fraud_risk,
)
from apps.schemas.document import DocumentRiskResult

logger = logging.getLogger(__name__)

# Class-level storage to track task statuses across service calls
class DocumentRiskService:
    _tasks: Dict[uuid.UUID, Dict[str, Any]] = {}
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        # Ensure local storage path exists
        self.storage_dir = os.path.abspath(os.path.join(os.getcwd(), "storage", "documents"))
        os.makedirs(self.storage_dir, exist_ok=True)

    async def start_processing(
        self,
        loan_application_id: uuid.UUID,
        files: List[UploadFile],
        background_tasks: BackgroundTasks,
    ) -> uuid.UUID:
        """
        Accepts files, saves them to local storage, initializes a task,
        and triggers the background processing pipeline.
        """
        task_id = uuid.uuid4()
        self._tasks[task_id] = {
            "status": "PROCESSING",
            "result": None,
            "error": None
        }
        
        saved_files_info = []
        for file in files:
            # Generate a unique local file path
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(self.storage_dir, unique_filename)
            
            # Read contents and write to disk
            content = await file.read()
            # Calculate SHA-256 hash
            sha256_hash = hashlib.sha256(content).hexdigest()
            
            with open(file_path, "wb") as f:
                f.write(content)
                
            saved_files_info.append({
                "original_name": file.filename,
                "mime_type": file.content_type or "application/octet-stream",
                "storage_path": file_path,
                "sha256_hash": sha256_hash
            })
            
        # Enqueue pipeline to run in the background
        background_tasks.add_task(
            self._run_pipeline,
            task_id=task_id,
            loan_application_id=loan_application_id,
            files_info=saved_files_info
        )
        
        return task_id

    async def get_result(self, task_id: uuid.UUID) -> Optional[DocumentRiskResult]:
        """
        Fetches the task result from in-memory tracker if finished.
        """
        task_info = self._tasks.get(task_id)
        if not task_info:
            # Check if it was processed and stored in database previously
            # (fallback for persistence)
            score_rec = self.db.query(DocumentRiskScore).filter(
                DocumentRiskScore.id == task_id
            ).first()
            if not score_rec:
                # Also check by loan application id if task_id happens to match it
                score_rec = self.db.query(DocumentRiskScore).filter(
                    DocumentRiskScore.loan_application_id == task_id
                ).first()
                
            if score_rec:
                return DocumentRiskResult(
                    task_id=task_id,
                    score=int(score_rec.score),
                    risk_category=score_rec.category,
                    confidence=float(score_rec.confidence),
                    fraud_probability=0.0, # default/not stored directly in risk score table
                    detected_issues=score_rec.issues or [],
                    recommendation=score_rec.recommendation,
                    explainable_summary=score_rec.explanation
                )
            return None
            
        if task_info["status"] == "PROCESSING":
            return None
        if task_info["status"] == "FAILED":
            raise Exception(f"Task processing failed: {task_info['error']}")
            
        return task_info["result"]

    async def _run_pipeline(
        self,
        task_id: uuid.UUID,
        loan_application_id: uuid.UUID,
        files_info: List[Dict[str, Any]]
    ):
        """
        Synchronous pipeline orchestration running in the background.
        """
        logger.info(f"Background pipeline started for task {task_id}")
        try:
            # 1. Fetch or create dynamic stub LoanApplication to prevent FK errors
            loan_app = self.db.query(LoanApplication).filter(LoanApplication.id == loan_application_id).first()
            if not loan_app:
                logger.info(f"LoanApplication ID {loan_application_id} not found in DB. Creating stub row.")
                loan_app = LoanApplication(
                    id=loan_application_id,
                    applicant_id=loan_application_id,
                    loan_type="Unsecured Business Loan",
                    amount=100000.00
                )
                self.db.add(loan_app)
                self.db.flush()

            # 2. Process each file
            analyses = []
            ocr_confidences = []
            detected_issues = []
            uploaded_types = set()

            for file_info in files_info:
                # Create UploadedDocument row
                up_doc = UploadedDocument(
                    loan_application_id=loan_application_id,
                    file_name=file_info["original_name"],
                    mime_type=file_info["mime_type"],
                    storage_path=file_info["storage_path"],
                    sha256_hash=file_info["sha256_hash"]
                )
                self.db.add(up_doc)
                self.db.flush()
                
                # Perform OCR
                ocr_result = await perform_ocr(file_info["storage_path"])
                ocr_text = ocr_result["text"]
                ocr_confidence = ocr_result["confidence"]
                ocr_confidences.append(ocr_confidence)
                
                # Classify document
                class_result = classify_document(ocr_text, file_info["original_name"])
                doc_type = class_result["document_type"]
                uploaded_types.add(doc_type)
                
                # Create DocumentAnalysis row
                # Extract fields from text
                extracted = extract_fields_from_text(ocr_text, doc_type)
                analysis = DocumentAnalysis(
                    uploaded_document_id=up_doc.id,
                    ocr_text=ocr_text,
                    ocr_confidence=ocr_confidence,
                    extracted_fields=extracted
                )
                self.db.add(analysis)
                self.db.flush()
                
                # Run validation rules
                val_result = validate_extracted_fields(extracted, doc_type)
                doc_val = DocumentValidation(
                    document_analysis_id=analysis.id,
                    rule_results=val_result["rule_results"],
                    error_count=val_result["error_count"]
                )
                self.db.add(doc_val)
                self.db.flush()
                
                # Keep record for cross-verification
                analyses.append({
                    "document_type": doc_type,
                    "extracted_fields": extracted,
                    "error_count": val_result["error_count"],
                    "document_analysis_id": analysis.id
                })

            # 3. Cross-Verification
            cross_result = perform_cross_verification(analyses)
            consistency_score = cross_result["consistency_score"]
            for field, success in cross_result["details"].items():
                if success is False:
                    detected_issues.append(f"Cross-verification mismatch: {field.replace('_', ' ').title()}")

            # 4. Fraud Risk
            avg_ocr_confidence = sum(ocr_confidences) / len(ocr_confidences) if ocr_confidences else 1.0
            fraud_prob, rule_flags, shap_values = evaluate_fraud_risk(analyses, avg_ocr_confidence)
            
            # Save Fraud details for each analysis
            for ana in analyses:
                doc_fraud = DocumentFraud(
                    document_analysis_id=ana["document_analysis_id"],
                    fraud_probability=fraud_prob,
                    rule_flags=rule_flags,
                    ml_shap_values=shap_values
                )
                self.db.add(doc_fraud)

            # Add fraud-related issues
            if fraud_prob > 0.4:
                detected_issues.append(f"Elevated fraud risk: probability is {int(fraud_prob * 100)}%")
            for rule_name, flag in rule_flags.items():
                if flag:
                    detected_issues.append(f"Fraud Flag Triggered: {rule_name.replace('_', ' ').title()}")

            # 5. Missing Document Analysis
            # Required document types: PAN, Aadhaar (standard defaults)
            missing_docs = []
            if "PAN" not in uploaded_types:
                missing_docs.append("PAN")
            if "Aadhaar" not in uploaded_types:
                missing_docs.append("Aadhaar")
                
            for missing in missing_docs:
                detected_issues.append(f"Missing mandatory document: {missing}")

            # 6. Final Risk Scoring Formula (DocumentRisk = sum(w_i * factor_i))
            ocr_risk_factor = 1.0 - avg_ocr_confidence
            
            total_validation_errors = sum(ana["error_count"] for ana in analyses)
            val_risk_factor = min(total_validation_errors, 5) / 5.0
            
            fraud_risk_factor = fraud_prob
            cross_risk_factor = 1.0 - consistency_score
            missing_risk_factor = 1.0 if missing_docs else 0.0
            quality_risk_factor = 0.1 if avg_ocr_confidence < 0.9 else 0.0
            
            raw_risk = (
                0.15 * ocr_risk_factor +
                0.20 * val_risk_factor +
                0.30 * fraud_risk_factor +
                0.20 * cross_risk_factor +
                0.10 * missing_risk_factor +
                0.05 * quality_risk_factor
            )
            
            risk_score = int(round(raw_risk * 100))
            risk_score = max(0, min(100, risk_score))
            
            # Map score to risk category
            if risk_score <= 30:
                risk_category = "Low"
                recommendation = "Proceed with standard underwriting"
            elif risk_score <= 70:
                risk_category = "Medium"
                recommendation = "Proceed with caution – request missing documents and review flagged validations"
            else:
                risk_category = "High"
                recommendation = "Reject or route to manual senior credit risk review"
                
            summary = (
                f"Document Risk Score is {risk_category} ({risk_score}/100) with confidence {round(avg_ocr_confidence, 2)}. "
                f"Validation errors: {total_validation_errors}, Consistency: {consistency_score}, Fraud score: {fraud_prob}."
            )

            # 7. Persist Final Document Risk Score
            # Save using the task_id as the primary key so it is retrievable by it
            risk_score_record = DocumentRiskScore(
                id=task_id, # Link it directly to task_id!
                loan_application_id=loan_application_id,
                score=risk_score,
                category=risk_category,
                confidence=avg_ocr_confidence,
                recommendation=recommendation,
                issues=detected_issues,
                explanation=summary
            )
            self.db.add(risk_score_record)
            self.db.commit()

            # 8. Update class task memory
            self._tasks[task_id] = {
                "status": "COMPLETED",
                "result": DocumentRiskResult(
                    task_id=task_id,
                    score=risk_score,
                    risk_category=risk_category,
                    confidence=round(avg_ocr_confidence, 2),
                    fraud_probability=fraud_prob,
                    detected_issues=detected_issues,
                    recommendation=recommendation,
                    explainable_summary=summary
                ),
                "error": None
            }
            logger.info(f"Background pipeline completed for task {task_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error running pipeline for task {task_id}: {e}", exc_info=True)
            self._tasks[task_id] = {
                "status": "FAILED",
                "result": None,
                "error": str(e)
            }
