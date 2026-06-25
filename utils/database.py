import os
import psycopg

DB_NAME = "test_results"
DB_USER = "betul.uzun"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def log_test_result(test_name: str, browser: str, status: str, duration: float) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO test_results (test_name, browser, status, duration)
                VALUES (%s, %s, %s, %s)
                """,
                (test_name, browser, status, duration),
            )
        conn.commit()
    finally:
        conn.close()