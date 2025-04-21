import psycopg2
import os
from jinja2 import Environment, FileSystemLoader
from app.utils import slugify

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
SQL_TEMPLATE = "create_schema.tpl.sql"

# Load database credentials from .env or environment
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "maildb")

def create_schema(domain: str):
    schema_name = slugify(domain)

    # Render the SQL
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(SQL_TEMPLATE)
    sql = template.render(schema=schema_name)

    # Connect and execute
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql)

    conn.close()
