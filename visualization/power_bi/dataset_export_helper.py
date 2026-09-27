import duckdb
from pathlib import Path
from config.settings import DB_FILE_PATH, EXPORTS_DATA_DIR
from config.logging_config import logger

def export_power_bi_tables():
    """Export Star Schema dimension and fact tables into CSV format for Power BI Direct Import."""
    db_path = str(DB_FILE_PATH).replace(".db", ".duckdb")
    conn = duckdb.connect(db_path)
    
    pbi_dir = EXPORTS_DATA_DIR / "power_bi_import"
    pbi_dir.mkdir(parents=True, exist_ok=True)
    
    tables = ["dim_store", "dim_product", "dim_customer", "dim_date", "fact_sales", "fact_inventory_snapshot", "fact_web_events"]
    
    logger.info("Exporting Star Schema tables for Power BI import...")
    for tbl in tables:
        df = conn.execute(f"SELECT * FROM {tbl}").df()
        out_csv = pbi_dir / f"{tbl}.csv"
        df.to_csv(out_csv, index=False)
        logger.info(f"Exported {len(df)} rows of '{tbl}' to {out_csv}")
        
    conn.close()

if __name__ == "__main__":
    export_power_bi_tables()
