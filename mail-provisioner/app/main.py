import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from app import ssh_client, compose_generator, postgres, registry
from app.utils import slugify
app = FastAPI()

class ProvisionRequest(BaseModel):
    domain: str

@app.post("/provision")
async def provision_tenant(request: ProvisionRequest):
    domain = request.domain.strip().lower()

    if registry.tenant_exists(domain):
        raise HTTPException(status_code=400, detail="Tenant already provisioned.")

    try:
        # 1. Select target VM (static for now)
        target_vm = registry.select_vm(domain)

        # 🔧 Compute slug once and use everywhere
        tenant_slug = slugify(domain)

        # 2. Render docker-compose + env
        compose_path, config_path, env_path = compose_generator.generate(domain)

        # 3. Upload files and deploy
        ssh_client.upload_and_deploy(
            vm=target_vm,
            domain=domain,
            compose_path=compose_path,
            config_path=config_path,
            env_path=env_path,
        )

        # 4. Create PostgreSQL schema
        postgres.create_schema(domain)

        # 5. Update HAProxy + Caddy
        registry.update_haproxy(domain, tenant_slug)
        registry.update_caddy(domain, tenant_slug)

        # 6. Register tenant
        registry.register_tenant(domain, target_vm)

        return {"status": "success", "domain": domain, "vm": target_vm}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

