import sys
from app import compose_generator, ssh_client, postgres, registry

def debug(domain: str):
    print(f"\n🔍 Starting debug for: {domain}")

    # Step 1: VM selection
    target_vm = registry.select_vm(domain)
    print(f"✅ VM selected: {target_vm}")

    # Step 2: Generate Compose + .env
    compose_path, config_path, env_path = compose_generator.generate(domain)
    print(f"✅ Compose generated at: {compose_path}")
    print(f"✅ .env generated at: {env_path}")

    # Step 3: Upload and deploy via SSH
    try:
        ssh_client.upload_and_deploy(vm=target_vm, domain=domain, compose_path=compose_path,  config_path=config_path, env_path=env_path)
        print("✅ Compose deployed and container started.")
    except Exception as e:
        print(f"❌ SSH/Deploy failed: {e}")
        return

    # Step 4: PostgreSQL schema creation
    try:
        postgres.create_schema(domain)
        print("✅ PostgreSQL schema created.")
    except Exception as e:
        print(f"❌ DB schema creation failed: {e}")
        return

    # Step 5: HAProxy + Caddy updates
    try:
        registry.update_haproxy(domain, target_vm)
        print("✅ HAProxy updated and reloaded.")
    except Exception as e:
        print(f"❌ HAProxy update failed: {e}")

    try:
        registry.update_caddy(domain, target_vm)
        print("✅ Caddy updated and reloaded.")
    except Exception as e:
        print(f"❌ Caddy update failed: {e}")

    # Step 6: Register tenant
    registry.register_tenant(domain, target_vm)
    print("✅ Tenant registered successfully.\n🎉 Debug run complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug.py <domain>")
    else:
        debug(sys.argv[1])
