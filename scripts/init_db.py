import os
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path

def load_database_url():
    # Prefer DATABASE_URL; fallback to discrete vars.
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    user = os.getenv("POSTGRES_USER", "appuser")
    pwd = os.getenv("POSTGRES_PASSWORD", "apppass")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db   = os.getenv("POSTGRES_DB", "appdb")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

def main():
    sql_file = Path(__file__).with_name("create_tables.sql")
    if not sql_file.exists():
        raise SystemExit(f"Arquivo SQL não encontrado: {sql_file}")
    db_url = load_database_url()
    print(f"[init_db] Conectando em: {db_url}")
    conn = psycopg2.connect(db_url)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql_file.read_text(encoding="utf-8"))
        print("[init_db] Tabelas criadas/atualizadas com sucesso.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
