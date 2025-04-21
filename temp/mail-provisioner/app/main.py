# app/main.py

from fastapi import FastAPI
from app.api import provision
from app.core.settings import settings

app = FastAPI(
    title="Mail Provisioning API",
    version="1.0.0"
)

# Include routes
app.include_router(provision.router, prefix="/api")

# Root endpoint
@app.get("/")
def read_root():
    return {"status": "ok", "project": "mail-provisioner"}
