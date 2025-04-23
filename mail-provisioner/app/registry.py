import yaml
import os
from pathlib import Path
from app import haproxy_updater, caddy_updater
from app.utils import slugify

TENANTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'tenants', 'tenants.yaml')

# For demo: simple round-robin/static list
""" AVAILABLE_VMS = [
    "alpha.local",
    "beta.local",
    "gamma.local",
] """
AVAILABLE_VMS = ["10.1.0.3"]

def load_registry() -> dict:
    if not os.path.exists(TENANTS_FILE):
        return {}
    with open(TENANTS_FILE, "r") as f:
        return yaml.safe_load(f) or {}

def save_registry(data: dict):
    with open(TENANTS_FILE, "w") as f:
        yaml.dump(data, f)

def tenant_exists(domain: str) -> bool:
    tenants = load_registry()
    return domain in tenants

def register_tenant(domain: str, vm: str):
    tenants = load_registry()
    tenants[domain] = {
        "vm": vm,
        "slug": slugify(domain)
    }
    save_registry(tenants)

def update_haproxy(domain: str, slug: str):
    vm = select_vm(domain)
    haproxy_updater.update(domain, slug, vm)

def update_caddy(domain: str, slug: str):
    vm = select_vm(domain)
    caddy_updater.update(domain, slug, vm)


# Simple static round-robin fallback
_next = 0
def select_vm(domain: str) -> str:
    return "alpha.sercp.com"