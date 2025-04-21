# app/core/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ssh_user: str = "root"
    ssh_key_path: str = "/root/.ssh/id_rsa"
    vm_hosts: list[str] = ["192.168.1.101", "192.168.1.102"]
    db_url: str = "postgresql://user:pass@db:5432/mail"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
