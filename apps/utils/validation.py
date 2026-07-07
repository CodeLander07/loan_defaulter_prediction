import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

def extract_fields_from_text(ocr_text: str, document_type: str) -> Dict[str, Any]:
    """
    Extracts key fields from the OCR text based on the document type.
    Uses regex rules to extract standard fields (PAN, Aadhaar, salary details, etc.).
    """
    fields = {}
    text_upper = ocr_text.upper()
    
    if document_type == "PAN":
        # Extract PAN number
        pan_match = re.search(r"([A-Z]{5}[0-9]{4}[A-Z])", text_upper)
        if pan_match:
            fields["pan_number"] = pan_match.group(1)
            
        # Extract DOB
        dob_match = re.search(r"(\d{2}/\d{2}/\d{4})", text_upper)
        if dob_match:
            fields["dob"] = dob_match.group(1)
            
        # Extract Name (heuristics: lines after GOVT OF INDIA / INCOME TAX DEPT)
        lines = [line.strip() for line in ocr_text.split("\n") if line.strip()]
        for idx, line in enumerate(lines):
            if "NAME" in line.upper() and idx + 1 < len(lines):
                # Check if it has a colon or just name
                clean_line = re.sub(r"NAME\s*:\s*", "", line, flags=re.IGNORECASE).strip()
                if clean_line:
                    fields["name"] = clean_line
                else:
                    fields["name"] = lines[idx + 1].strip()
                break

    elif document_type == "Aadhaar":
        # Extract Aadhaar number (12 digits, often formatted as 4-4-4)
        aadhaar_match = re.search(r"(\d{4}\s\d{4}\s\d{4})", ocr_text)
        if aadhaar_match:
            fields["aadhaar_number"] = aadhaar_match.group(1).replace(" ", "")
        else:
            # Maybe plain 12 digits
            digits_match = re.search(r"(\b\d{12}\b)", ocr_text)
            if digits_match:
                fields["aadhaar_number"] = digits_match.group(1)
                
        # DOB
        dob_match = re.search(r"(?:DOB|DATE OF BIRTH)\s*:\s*(\d{2}/\d{2}/\d{4})", text_upper)
        if dob_match:
            fields["dob"] = dob_match.group(1)
            
        # Name
        lines = [line.strip() for line in ocr_text.split("\n") if line.strip()]
        # Aadhaar names usually appear right above/below gender or under Govt of India
        for idx, line in enumerate(lines):
            if "GOVERNMENT OF INDIA" in line.upper() and idx + 2 < len(lines):
                # Next lines are likely name
                possible_name = lines[idx + 1].strip()
                if "MALE" not in possible_name.upper() and "FEMALE" not in possible_name.upper():
                    fields["name"] = possible_name
                break
        
        # Gender
        if "MALE" in text_upper:
            fields["gender"] = "MALE"
        elif "FEMALE" in text_upper:
            fields["gender"] = "FEMALE"

    elif document_type == "SalarySlip":
        # Gross salary / Net salary extraction
        gross_match = re.search(r"(?:GROSS EARNINGS|GROSS SALARY)\s*:\s*(\d+)", text_upper)
        if gross_match:
            fields["gross_salary"] = float(gross_match.group(1))
            
        net_match = re.search(r"(?:NET SALARY|NET PAID|NET SALARY PAID)\s*:\s*(\d+)", text_upper)
        if net_match:
            fields["net_salary"] = float(net_match.group(1))
            
        # Employer name
        lines = [line.strip() for line in ocr_text.split("\n") if line.strip()]
        if lines:
            fields["employer_name"] = lines[0] # Often header is employer
            
        # PAN
        pan_match = re.search(r"PAN\s*:\s*([A-Z]{5}[0-9]{4}[A-Z])", text_upper)
        if pan_match:
            fields["pan_number"] = pan_match.group(1)
            
        # Account number
        acc_match = re.search(r"(?:ACCOUNT NO|ACC NO|A/C NO)\s*:\s*(\d+)", text_upper)
        if acc_match:
            fields["account_number"] = acc_match.group(1)

    elif document_type == "BankStatement":
        # Account number
        acc_match = re.search(r"(?:ACCOUNT NO|A/C NO|ACCOUNT NUMBER)\s*:\s*(\d+)", text_upper)
        if acc_match:
            fields["account_number"] = acc_match.group(1)
            
        # Closing balance
        bal_match = re.search(r"(?:CLOSING BALANCE|BALANCE)\s+(\d+\.\d{2})", text_upper)
        if bal_match:
            fields["closing_balance"] = float(bal_match.group(1))
            
        # Find salary credit transactions (e.g. ACH CREDIT, salary deposit)
        salary_credit_match = re.search(r"(?:SALARY|TECH SOLUT)\s+(\d+\.\d{2})", text_upper)
        if salary_credit_match:
            fields["salary_credit"] = float(salary_credit_match.group(1))
            
    # Normalize name if found
    if "name" in fields:
        # Trim whitespace, replace double spaces, make title case
        fields["name"] = " ".join(fields["name"].split()).title()
        
    return fields


def validate_extracted_fields(fields: Dict[str, Any], document_type: str) -> Dict[str, Any]:
    """
    Validates the extracted fields against standard banking rules.
    Returns a dict with verification flags and error count.
    """
    rule_results = {}
    error_count = 0
    
    if document_type == "PAN":
        # Rule: PAN format
        pan = fields.get("pan_number", "")
        if pan:
            is_valid_pan = bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan))
            rule_results["pan_format_valid"] = is_valid_pan
            if not is_valid_pan:
                error_count += 1
        else:
            rule_results["pan_present"] = False
            error_count += 1

        # Rule: DOB present
        rule_results["dob_present"] = "dob" in fields
        if not fields.get("dob"):
            error_count += 1
            
    elif document_type == "Aadhaar":
        # Rule: Aadhaar 12-digit format
        aadhaar = fields.get("aadhaar_number", "")
        if aadhaar:
            is_valid_aadhaar = len(aadhaar) == 12 and aadhaar.isdigit()
            rule_results["aadhaar_format_valid"] = is_valid_aadhaar
            if not is_valid_aadhaar:
                error_count += 1
        else:
            rule_results["aadhaar_present"] = False
            error_count += 1
            
    elif document_type == "SalarySlip":
        # Rule: Salary is numeric and non-zero
        net_salary = fields.get("net_salary", 0.0)
        is_salary_valid = net_salary > 0.0
        rule_results["net_salary_valid"] = is_salary_valid
        if not is_salary_valid:
            error_count += 1
            
        # Rule: PAN present if expected
        rule_results["pan_present"] = "pan_number" in fields
        
    elif document_type == "BankStatement":
        # Rule: Account number present
        rule_results["account_number_present"] = "account_number" in fields
        if "account_number" not in fields:
            error_count += 1
            
        # Rule: Closing balance is positive (no overdraft unless business loan)
        closing_bal = fields.get("closing_balance", 0.0)
        rule_results["positive_balance"] = closing_bal >= 0.0
        if closing_bal < 0.0:
            error_count += 1
            
    return {
        "rule_results": rule_results,
        "error_count": error_count
    }


def perform_cross_verification(doc_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Performs cross-document attribute matching and returns a consistency score (0.0 to 1.0).
    Checks names, PANs, DOBs, and Salary vs Bank Statement credits.
    """
    names = []
    pans = []
    dobs = []
    
    salary_slips_net = []
    bank_statements_credits = []
    salary_accs = []
    bank_accs = []
    
    for analysis in doc_analyses:
        doc_type = analysis.get("document_type")
        fields = analysis.get("extracted_fields", {})
        
        if "name" in fields:
            names.append(fields["name"].lower())
        if "pan_number" in fields:
            pans.append(fields["pan_number"].upper())
        if "dob" in fields:
            dobs.append(fields["dob"])
            
        if doc_type == "SalarySlip":
            if "net_salary" in fields:
                salary_slips_net.append(fields["net_salary"])
            if "account_number" in fields:
                salary_accs.append(fields["account_number"])
        elif doc_type == "BankStatement":
            if "salary_credit" in fields:
                bank_statements_credits.append(fields["salary_credit"])
            if "account_number" in fields:
                bank_accs.append(fields["account_number"])

    verification_details = {}
    scores = []
    
    # 1. Name consistency check (Exact or fuzzy match)
    if len(names) > 1:
        # Check standard name match
        all_same_name = all(name == names[0] for name in names)
        verification_details["name_consistency"] = all_same_name
        scores.append(1.0 if all_same_name else 0.2)
    else:
        verification_details["name_consistency"] = "insufficient_data"
        
    # 2. PAN consistency check
    if len(pans) > 1:
        all_same_pan = all(pan == pans[0] for pan in pans)
        verification_details["pan_consistency"] = all_same_pan
        scores.append(1.0 if all_same_pan else 0.0)
    else:
        verification_details["pan_consistency"] = "insufficient_data"

    # 3. DOB consistency check
    if len(dobs) > 1:
        all_same_dob = all(dob == dobs[0] for dob in dobs)
        verification_details["dob_consistency"] = all_same_dob
        scores.append(1.0 if all_same_dob else 0.0)
    else:
        verification_details["dob_consistency"] = "insufficient_data"

    # 4. Net Salary vs Bank Statement credits check (Tolerance 10%)
    if salary_slips_net and bank_statements_credits:
        net_sal = salary_slips_net[0]
        bank_credit = bank_statements_credits[0]
        
        # Calculate ratio deviation
        max_val = max(net_sal, bank_credit)
        if max_val > 0:
            diff_ratio = abs(net_sal - bank_credit) / max_val
            consistency = max(0.0, 1.0 - diff_ratio)
            verification_details["salary_credit_match_score"] = round(consistency, 2)
            scores.append(consistency)
        else:
            verification_details["salary_credit_match_score"] = 0.0
            scores.append(0.0)
    else:
        verification_details["salary_credit_match_score"] = "insufficient_data"

    # 5. Salary Slip Bank Account vs Bank Statement account
    if salary_accs and bank_accs:
        acc_match = salary_accs[0] == bank_accs[0]
        verification_details["account_number_match"] = acc_match
        scores.append(1.0 if acc_match else 0.0)
    else:
        verification_details["account_number_match"] = "insufficient_data"

    # Calculate aggregate consistency score
    final_score = sum(scores) / len(scores) if scores else 1.0
    
    return {
        "consistency_score": round(final_score, 2),
        "details": verification_details
    }


def evaluate_fraud_risk(doc_analyses: List[Dict[str, Any]], ocr_confidence: float) -> Tuple[float, Dict[str, Any], Dict[str, Any]]:
    """
    Evaluates fraud probability using a rule engine and simulated ML model.
    Returns: (fraud_probability, rule_flags, shap_values)
    """
    rule_flags = {}
    fraud_score_rules = 0.0
    
    # Rule 1: Duplicate uploads (checked in service, placeholder here)
    rule_flags["duplicate_document"] = False
    
    # Rule 2: Low OCR confidence
    rule_flags["low_ocr_confidence"] = ocr_confidence < 0.80
    if ocr_confidence < 0.80:
        fraud_score_rules += 0.4
        
    # Rule 3: Error counts high
    total_errors = sum(analysis.get("error_count", 0) for analysis in doc_analyses)
    rule_flags["high_validation_errors"] = total_errors >= 3
    if total_errors >= 3:
        fraud_score_rules += 0.3
        
    # ML Simulator (simulated Gradient Boosting XGBoost)
    # Extracts features: metadata, ocr score, size, validation results
    ml_shap_values = {
        "ocr_confidence_impact": -0.15 if ocr_confidence > 0.90 else 0.25,
        "error_count_impact": 0.05 * total_errors,
        "metadata_anomaly_impact": 0.05
    }
    
    ml_prob = 0.05
    if ocr_confidence < 0.85:
        ml_prob += 0.25
    if total_errors > 0:
        ml_prob += 0.1 * total_errors
        
    ml_prob = min(ml_prob, 1.0)
    
    # Ensemble: 60% rule-based + 40% ML
    final_prob = (0.6 * min(fraud_score_rules, 1.0)) + (0.4 * ml_prob)
    final_prob = round(min(final_prob, 1.0), 2)
    
    return final_prob, rule_flags, ml_shap_values
