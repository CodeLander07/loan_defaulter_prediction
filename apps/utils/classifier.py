import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

def classify_document(ocr_text: str, file_name: str = "") -> Dict[str, Any]:
    """
    Classifies a document based on its OCR text content and filename.
    Uses a hybrid approach:
    1. Heuristic regex matches on headers (PAN, Aadhaar, Salary Slip, Bank Statement)
    2. Simulated CNN classifier if heuristics are low-confidence.
    """
    ocr_text_upper = ocr_text.upper()
    file_name_lower = file_name.lower()
    
    # Define heuristic scoring
    heuristics = {
        "PAN": 0.0,
        "Aadhaar": 0.0,
        "SalarySlip": 0.0,
        "BankStatement": 0.0
    }
    
    # Heuristic checks for PAN
    if "INCOME TAX DEPARTMENT" in ocr_text_upper or "PERMANENT ACCOUNT NUMBER" in ocr_text_upper:
        heuristics["PAN"] += 0.6
    if re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", ocr_text_upper):
        heuristics["PAN"] += 0.4
    if "pan" in file_name_lower:
        heuristics["PAN"] += 0.2
        
    # Heuristic checks for Aadhaar
    if "GOVERNMENT OF INDIA" in ocr_text_upper or "UNIQUE IDENTIFICATION" in ocr_text_upper or "AADHAAR" in ocr_text_upper:
        heuristics["Aadhaar"] += 0.6
    if re.search(r"\d{4}\s\d{4}\s\d{4}", ocr_text_upper):
        heuristics["Aadhaar"] += 0.4
    if "aadhaar" in file_name_lower or "aadhar" in file_name_lower:
        heuristics["Aadhaar"] += 0.2
        
    # Heuristic checks for Salary Slip
    if "SALARY SLIP" in ocr_text_upper or "PAY SLIP" in ocr_text_upper or "EARNINGS" in ocr_text_upper:
        heuristics["SalarySlip"] += 0.6
    if "NET SALARY" in ocr_text_upper or "GROSS EARNINGS" in ocr_text_upper:
        heuristics["SalarySlip"] += 0.3
    if "salary" in file_name_lower or "pay" in file_name_lower or "slip" in file_name_lower:
        heuristics["SalarySlip"] += 0.2

    # Heuristic checks for Bank Statement
    if "STATEMENT OF ACCOUNT" in ocr_text_upper or "ACCOUNT STATEMENT" in ocr_text_upper or "CLOSING BALANCE" in ocr_text_upper:
        heuristics["BankStatement"] += 0.6
    if "WITHDRAWAL" in ocr_text_upper and "DEPOSIT" in ocr_text_upper:
        heuristics["BankStatement"] += 0.3
    if "bank" in file_name_lower or "statement" in file_name_lower:
        heuristics["BankStatement"] += 0.2

    # Find highest heuristic match
    best_heuristic_type = max(heuristics, key=heuristics.get)
    best_heuristic_score = heuristics[best_heuristic_type]
    
    logger.info(f"Heuristic classifier result: {best_heuristic_type} (Score: {best_heuristic_score})")

    # If heuristic confidence > 0.85, accept and return
    if best_heuristic_score >= 0.85:
        return {
            "document_type": best_heuristic_type,
            "confidence": min(float(best_heuristic_score), 1.0),
            "method": "HeuristicHeader"
        }
    
    # Otherwise, simulate the CNN-based classifier (MobileNetV3)
    # In a real environment, you would run torch/onnx model here.
    logger.info("Heuristics low confidence. Running simulated MobileNetV3 CNN classifier.")
    
    # Determine fallback class based on best guess
    ml_confidence = 0.85 if best_heuristic_score > 0.2 else 0.5
    final_type = best_heuristic_type if ml_confidence >= 0.8 else "OTHER"
    
    return {
        "document_type": final_type,
        "confidence": float(ml_confidence),
        "method": "MobileNetV3-Simulated"
    }
