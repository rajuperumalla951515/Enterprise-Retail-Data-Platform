import pytest
import duckdb
from pipelines.python_etl_pipeline import RetailETLPipeline
from config.settings import DB_FILE_PATH, RAW_DATA_DIR

def test_etl_pipeline_execution(tmp_path):
    test_db = tmp_path / "test_dw.duckdb"
    pipeline = RetailETLPipeline(raw_dir=RAW_DATA_DIR, db_path=test_db)
    datasets = pipeline.extract_raw_datasets()
    pipeline.load_staging_tables(datasets)
    pipeline.transform_star_schema()
    
    conn = duckdb.connect(str(test_db))
    sales_cnt = conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    cust_cnt = conn.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0]
    conn.close()
    
    assert sales_cnt > 0
    assert cust_cnt > 0
