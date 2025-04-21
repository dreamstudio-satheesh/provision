# 📬 Mail Provisioner

A FastAPI-based provisioning service to automate **multi-tenant** deployment of Stalwart Mail Server across multiple Docker-enabled VMs. It dynamically injects routing into **HAProxy** and **Caddy**, and isolates tenant mail data via PostgreSQL schemas.

---

## 🧱 Folder Structure

```
.
├── docker-compose.yml               # Runs the FastAPI provisioner
└── mail-provisioner/
    ├── app/                         # Core Python modules
    ├── tenants/                     # Stores .env files and registry
    ├── templates/                   # Jinja2 templates
    ├── Dockerfile
    ├── requirements.txt
    ├── .env                         # Environment config
    └── debug.py                      # One-click local debug runner
```

---

## 🚀 Usage

### 1. Start the API Server

```bash
docker compose up -d
```

### 2. Provision a Tenant via HTTP POST

```bash
curl -X POST http://localhost:8000/provision \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

> This will:
>
> - Pick a target VM from static list
> - Generate Docker Compose & .env
> - Push files via SSH and run `docker compose up -d`
> - Create a PostgreSQL schema for the domain
> - Inject SNI-based routing into HAProxy
> - Inject JMAP/Admin routes into Caddy
> - Reload both proxies
> - Record it in `tenants.yaml`

---

## 🔧 Local Debug Script

Run this from `mail-provisioner/` to test provisioning logic directly:

```bash
python debug.py example.com
```

It will:

- Render the docker-compose and .env
- Connect to target VM via SSH
- Deploy the container and print logs
- Setup the DB schema
- Inject and reload HAProxy/Caddy configs

---

## 🔐 Environment Variables

Define these in `.env` or inject via `env_file:` in Docker Compose:

```ini
DB_HOST=db.internal
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=supersecret
DB_NAME=maildb
```

---

## 📆 Dependencies

- Python 3.12+
- FastAPI
- Paramiko (for SSH)
- psycopg2 (for PostgreSQL)
- Jinja2 (for config templating)
- HAProxy & Caddy installed in your VM containers

---

## 📊 Optional: Monitoring Stack

- Prometheus + node_exporter
- Grafana for dashboards
- Loki for central log aggregation

---

## 🔐 Security Tips

- Use SSH key-based auth only
- Use `.env` for secrets, don’t hardcode
- Add API Key or OAuth2 to secure `/provision`
- Set up a firewall between nodes
