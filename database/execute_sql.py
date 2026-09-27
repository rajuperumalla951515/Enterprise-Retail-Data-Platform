import sqlite3
from pathlib import Path
from config.settings import DB_FILE_PATH, BASE_DIR
from config.logging_config import logger

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    duckdb = None

def init_database(use_duckdb: bool = True):
    """Initializes the database warehouse schema, dimensions, facts, and views."""
    ddl_dir = BASE_DIR / "database" / "ddl"
    sql_files = [
        ddl_dir / "01_staging_tables.sql",
        ddl_dir / "02_dw_star_schema.sql",
        ddl_dir / "03_data_marts.sql"
    ]

    use_duckdb_effective = use_duckdb and DUCKDB_AVAILABLE
    logger.info(f"Initializing database warehouse using {'DuckDB' if use_duckdb_effective else 'SQLite'}...")

    if use_duckdb_effective and duckdb is not None:
        db_path = str(DB_FILE_PATH).replace(".db", ".duckdb")
        conn = duckdb.connect(db_path)
        cursor = conn.cursor()
        for sql_file in sql_files:
            logger.info(f"Executing SQL script: {sql_file.name}")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
                for stmt in statements:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        logger.warning(f"SQL statement execution warning: {e}")
        conn.commit()
        conn.close()
        logger.info(f"DuckDB Data Warehouse initialized successfully at: {db_path}")
    else:
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()
        for sql_file in sql_files:
            logger.info(f"Executing SQL script: {sql_file.name}")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        logger.info(f"SQLite Data Warehouse initialized successfully at: {DB_FILE_PATH}")

if __name__ == "__main__":
    init_database()
