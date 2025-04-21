import os
from jinja2 import Environment, FileSystemLoader
from app.ssh_client import run_remote_command, upload_file
from app.utils import slugify

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
CADDYFILE_NAME = "Caddyfile"
REMOTE_CONFIG_PATH = "/etc/caddy/Caddyfile"
REMOTE_TMP_PATH = "/tmp/Caddyfile"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def inject_routes(domain: str, tenant_slug: str, vm: str):
    """
    Appends tenant-specific JMAP and Admin routes to the Caddyfile.
    """
    template = env.get_template("caddy_routes.tpl.caddy")
    rendered = template.render(tenant=tenant_slug)

    with open(os.path.join(TEMPLATES_DIR, CADDYFILE_NAME), "r") as f:
        base_cfg = f.read()

    full_cfg = base_cfg + "\n\n" + rendered

    with open("/tmp/Caddyfile", "w") as f:
        f.write(full_cfg)

    upload_file(vm, "/tmp/Caddyfile", REMOTE_TMP_PATH)
    run_remote_command(vm, f"mv {REMOTE_TMP_PATH} {REMOTE_CONFIG_PATH}")

def reload(vm: str):
    """
    Reloads Caddy configuration with zero downtime.
    """
    run_remote_command(vm, "docker exec caddy caddy reload --config /etc/caddy/Caddyfile")
