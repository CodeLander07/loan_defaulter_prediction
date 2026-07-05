DATABASE_URL=postgresql://postgres:password@localhost:5432/loan_risk_db

uvicorn app.main:app --reload