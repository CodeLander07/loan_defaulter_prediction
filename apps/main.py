from fastapi import FastAPI

from apps.database import engine
from apps.database import Base


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MSME Risk Intelligence API"
)


@app.get("/")
def read_root():
    return {"message": "MSME Risk Intelligence API"}