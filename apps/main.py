
from fastapi import FastAPI
from apps.api import document_risk, macro_risk, financial_risk

from apps.database import engine
from apps.database import Base


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MSME Risk Intelligence API"
)

app.include_router(document_risk.router, prefix="/api/document-risk", tags=["Document Risk"])
app.include_router(macro_risk.router, prefix="/api/macro-risk", tags=["Macro Risk"])
app.include_router(financial_risk.router, prefix="/api/financial-risk", tags=["Financial Risk"])


@app.get("/")
def read_root():
    return {"message": "MSME Risk Intelligence API"}