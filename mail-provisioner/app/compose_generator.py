from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from the mail-provisioner root directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
TENANTS_ENV_DIR = os.path.join(os.path.dirname(__file__), '..', 'tenants', 'envs')
TEMP_OUTPUT_DIR = "/tmp/mail_compose"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def slugify(domain: str) -> str:
    return domain.replace(".", "_")

def generate(domain: str) -> tuple[str, str, str]:
    tenant_id = slugify(domain)
    Path(TEMP_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Load DB config from .env
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "supersecret")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_name = os.getenv("DB_NAME", "maildb")

    # ── Render docker-compose template ──
    compose_template = env.get_template("docker-compose.tpl.yml")
    rendered_compose = compose_template.render(domain=domain, tenant=tenant_id)
    compose_path = os.path.join(TEMP_OUTPUT_DIR, f"{tenant_id}_docker-compose.yml")
    with open(compose_path, "w") as f:
        f.write(rendered_compose)

    # ── Render config.toml ──
    config_template = env.get_template("config.tpl.toml")
    rendered_config = config_template.render(
        domain=domain,
        db_user=db_user,
        db_password=db_pass,
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
    )
    config_path = os.path.join(TEMP_OUTPUT_DIR, f"{tenant_id}_config.toml")
    with open(config_path, "w") as f:
        f.write(rendered_config)

    # ── Create tenant .env ──
    env_path = os.path.join(TENANTS_ENV_DIR, f"{tenant_id}.env")
    with open(env_path, "w") as f:
        f.write(f"DOMAIN={domain}\n")
        f.write(f"TENANT={tenant_id}\n")
        f.write(f"DB_USER={db_user}\n")
        f.write(f"DB_PASSWORD={db_pass}\n")

    return compose_path, env_path, config_path
