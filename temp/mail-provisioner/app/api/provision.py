# app/api/provision.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.provisioner import provision_tenant

router = APIRouter()

class ProvisionRequest(BaseModel):
    domain: str

@router.post("/provision")
async def provision(request: ProvisionRequest):
    try:
        result = await provision_tenant(request.domain)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
