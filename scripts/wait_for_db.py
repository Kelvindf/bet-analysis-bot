import time, os, sys
import psycopg2

def db_ready():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.close()
        return True
    except Exception:
        return False

def main():
    timeout = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
    start = time.time()
    while time.time() - start < timeout:
        if db_ready():
            print("[wait_for_db] Banco pronto.")
            return 0
        print("[wait_for_db] Aguardando banco...", flush=True)
        time.sleep(2)
    print("[wait_for_db] Timeout aguardando banco.", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
