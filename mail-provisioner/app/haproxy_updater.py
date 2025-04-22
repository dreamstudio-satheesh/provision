import os
from jinja2 import Environment, FileSystemLoader
from app.ssh_client import run_remote_command, upload_file
from app.utils import slugify

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
CONFIG_FILE_NAME = "haproxy.cfg"
REMOTE_CONFIG_PATH = "/etc/haproxy/haproxy.cfg"
REMOTE_TMP_PATH = "/tmp/haproxy.cfg"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def inject_backend(domain: str, tenant_slug: str, vm: str):
    """
    Renders a tenant-specific backend block and appends it to the HAProxy config on the VM.
    """
    template = env.get_template("haproxy_backend.tpl.cfg")
    rendered = template.render(domain=domain, tenant=tenant_slug)

    # Pull current HAProxy config (or assume it's mounted on host)
    # For simplicity, we append rendered snippet to a static config base
    with open(os.path.join(TEMPLATES_DIR, CONFIG_FILE_NAME), "r") as f:
        base_cfg = f.read()

    new_cfg = base_cfg + "\n\n" + rendered

    # Write new config to tmp
    with open("/tmp/haproxy.cfg", "w") as f:
        f.write(new_cfg)

    # Upload new config to remote
    upload_file(vm, "/tmp/haproxy.cfg", REMOTE_TMP_PATH)

    # Move into place (atomic) — handled in `reload()`
    run_remote_command(vm, f"mv {REMOTE_TMP_PATH} {REMOTE_CONFIG_PATH}")

def reload(vm: str):
    """
    Reload HAProxy with zero downtime using a hot reload signal.
    """
    run_remote_command(vm, "docker kill -s HUP haproxy")

def update(domain: str, tenant_slug: str, vm: str = "10.1.0.3"):
    inject_backend(domain, tenant_slug, vm)
    reload(vm)
