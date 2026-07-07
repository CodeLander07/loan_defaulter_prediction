from apps.models.document_models import (
    LoanApplication,
    UploadedDocument,
    DocumentAnalysis,
    DocumentValidation,
    DocumentFraud,
    DocumentRiskScore,
)
from apps.models.macro_models import (
    MacroIndicator,
    MacroRiskScore,
)

__all__ = [
    "LoanApplication",
    "UploadedDocument",
    "DocumentAnalysis",
    "DocumentValidation",
    "DocumentFraud",
    "DocumentRiskScore",
    "MacroIndicator",
    "MacroRiskScore",
]
