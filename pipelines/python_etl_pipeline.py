import json
import duckdb
import pandas as pd
from pathlib import Path
from datetime import datetime

from config.settings import RAW_DATA_DIR, EXPORTS_DATA_DIR, DB_FILE_PATH
from config.logging_config import logger
from pipelines.extractors.csv_extractor import CSVExtractor
from pipelines.extractors.json_extractor import JSONExtractor

class RetailETLPipeline:
    """End-to-End Retail ETL/ELT Pipeline Executor using Python, Pandas & DuckDB."""

    def __init__(self, raw_dir: Path = RAW_DATA_DIR, db_path: Path = DB_FILE_PATH):
        self.raw_dir = raw_dir
        self.db_path = str(db_path).replace(".db", ".duckdb")
        self.conn = duckdb.connect(self.db_path)
        
    def extract_raw_datasets(self) -> dict:
        """Extract all raw datasets into Pandas DataFrames."""
        logger.info("=== STEP 1: EXTRACTING RAW DATASETS ===")
        extracted = {}
        
        extracted["stores"] = CSVExtractor(self.raw_dir / "stores.csv").extract()
        extracted["products"] = CSVExtractor(self.raw_dir / "products.csv").extract()
        extracted["customers"] = CSVExtractor(self.raw_dir / "customers.csv").extract()
        extracted["orders"] = CSVExtractor(self.raw_dir / "orders.csv").extract()
        extracted["order_items"] = CSVExtractor(self.raw_dir / "order_items.csv").extract()
        extracted["inventory"] = CSVExtractor(self.raw_dir / "inventory.csv").extract()
        extracted["web_events"] = JSONExtractor(self.raw_dir / "web_events.json").extract()
        
        return extracted

    def load_staging_tables(self, datasets: dict):
        """Load extracted raw DataFrames into DuckDB staging tables."""
        logger.info("=== STEP 2: LOADING STAGING TABLES ===")
        for table_name, df in datasets.items():
            stg_table = f"stg_{table_name}"
            logger.info(f"Loading {len(df)} records into staging table: {stg_table}")
            self.conn.register(f"df_{table_name}", df)
            self.conn.execute(f"CREATE OR REPLACE TABLE {stg_table} AS SELECT * FROM df_{table_name}")

    def transform_star_schema(self):
        """Execute SQL ELT transformations to populate Star Schema dimensions and fact tables."""
        logger.info("=== STEP 3: TRANSFORMING STAR SCHEMA (ELT) ===")
        
        # Drop existing tables with CASCADE to reset schema cleanly
        logger.info("Cleaning up existing DW tables with CASCADE...")
        self.conn.execute("""
            DROP TABLE IF EXISTS fact_sales CASCADE;
            DROP TABLE IF EXISTS fact_inventory_snapshot CASCADE;
            DROP TABLE IF EXISTS fact_web_events CASCADE;
            DROP TABLE IF EXISTS dim_customer CASCADE;
            DROP TABLE IF EXISTS dim_product CASCADE;
            DROP TABLE IF EXISTS dim_store CASCADE;
            DROP TABLE IF EXISTS dim_date CASCADE;
        """)

        # 1. Populate dim_store
        logger.info("Populating dim_store...")
        self.conn.execute("""
            CREATE TABLE dim_store AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY store_id) AS store_sk,
                store_id,
                store_name,
                store_type,
                region,
                city,
                state,
                postal_code,
                square_feet,
                CAST(open_date AS DATE) AS open_date,
                TRUE AS is_active
            FROM stg_stores;
        """)

        # 2. Populate dim_product
        logger.info("Populating dim_product...")
        self.conn.execute("""
            CREATE OR REPLACE TABLE dim_product AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY product_id) AS product_sk,
                product_id,
                product_name,
                category,
                subcategory,
                brand,
                cost_price,
                selling_price,
                ROUND((selling_price - cost_price) / NULLIF(selling_price, 0), 4) AS profit_margin,
                supplier_id,
                CAST(created_at AS TIMESTAMP) AS created_at
            FROM stg_products;
        """)

        # 3. Populate dim_customer
        logger.info("Populating dim_customer...")
        self.conn.execute("""
            CREATE OR REPLACE TABLE dim_customer AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_sk,
                customer_id,
                first_name,
                last_name,
                COALESCE(first_name || ' ' || last_name, 'Unknown Customer') AS full_name,
                COALESCE(email, 'unregistered@retail.com') AS email,
                phone,
                gender,
                age_group,
                customer_segment,
                loyalty_points,
                CAST(joined_date AS DATE) AS joined_date,
                state,
                city
            FROM stg_customers;
        """)

        # 4. Generate dim_date
        logger.info("Generating dim_date dimension...")
        self.conn.execute("""
            CREATE OR REPLACE TABLE dim_date AS
            WITH date_range AS (
                SELECT UNNEST(generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL '1 day')) AS full_date
            )
            SELECT 
                CAST(strftime(full_date, '%Y%m%d') AS INTEGER) AS date_key,
                full_date,
                DAYOFWEEK(full_date) AS day_of_week,
                strftime(full_date, '%A') AS day_name,
                DAYOFMONTH(full_date) AS day_of_month,
                DAYOFYEAR(full_date) AS day_of_year,
                MONTH(full_date) AS month_number,
                strftime(full_date, '%B') AS month_name,
                QUARTER(full_date) AS quarter_number,
                YEAR(full_date) AS year_number,
                CASE WHEN DAYOFWEEK(full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
            FROM date_range;
        """)

        # 5. Build fact_sales (Deduplicating orders and calculating profit)
        logger.info("Populating fact_sales...")
        self.conn.execute("""
            CREATE OR REPLACE TABLE fact_sales AS
            WITH dedup_orders AS (
                SELECT DISTINCT * FROM stg_orders
            )
            SELECT 
                i.order_item_id || '-' || o.order_id AS sales_fact_id,
                o.order_id,
                c.customer_sk,
                s.store_sk,
                p.product_sk,
                CAST(strftime(CAST(o.order_date AS TIMESTAMP), '%Y%m%d') AS INTEGER) AS order_date_key,
                CAST(o.order_date AS TIMESTAMP) AS order_timestamp,
                o.order_status,
                o.payment_method,
                i.quantity,
                i.unit_price,
                p.cost_price,
                o.discount_amount / COUNT(i.order_item_id) OVER (PARTITION BY o.order_id) AS discount_amount,
                o.shipping_cost / COUNT(i.order_item_id) OVER (PARTITION BY o.order_id) AS shipping_cost,
                i.total_item_price,
                ROUND(i.total_item_price - (o.discount_amount / COUNT(i.order_item_id) OVER (PARTITION BY o.order_id)), 2) AS net_item_revenue,
                ROUND((i.total_item_price - (o.discount_amount / COUNT(i.order_item_id) OVER (PARTITION BY o.order_id))) - (i.quantity * p.cost_price), 2) AS net_item_profit
            FROM dedup_orders o
            JOIN stg_order_items i ON o.order_id = i.order_id
            JOIN dim_customer c ON o.customer_id = c.customer_id
            JOIN dim_store s ON o.store_id = s.store_id
            JOIN dim_product p ON i.product_id = p.product_id;
        """)

        # 6. Build fact_inventory_snapshot
        logger.info("Populating fact_inventory_snapshot...")
        self.conn.execute("""
            CREATE OR REPLACE TABLE fact_inventory_snapshot AS
            SELECT 
                inv.inventory_id AS inventory_fact_id,
                s.store_sk,
                p.product_sk,
                CAST(strftime(CAST(inv.last_restock_date AS DATE), '%Y%m%d') AS INTEGER) AS snapshot_date_key,
                inv.stock_on_hand,
                inv.reorder_point,
                inv.safety_stock,
                CASE WHEN inv.stock_on_hand = 0 THEN TRUE ELSE FALSE END AS is_out_of_stock,
                CASE WHEN inv.stock_on_hand <= inv.reorder_point THEN TRUE ELSE FALSE END AS needs_reorder
            FROM stg_inventory inv
            JOIN dim_store s ON inv.store_id = s.store_id
            JOIN dim_product p ON inv.product_id = p.product_id;
        """)

        # 7. Build fact_web_events
        logger.info("Populating fact_web_events...")
        self.conn.execute("""
            CREATE OR REPLACE TABLE fact_web_events AS
            SELECT 
                w.event_id AS event_fact_id,
                w.event_id,
                w.session_id,
                c.customer_sk,
                p.product_sk,
                w.event_type,
                w.device_type,
                CAST(w.event_timestamp AS TIMESTAMP) AS event_timestamp,
                CAST(strftime(CAST(w.event_timestamp AS TIMESTAMP), '%Y%m%d') AS INTEGER) AS event_date_key
            FROM stg_web_events w
            LEFT JOIN dim_customer c ON w.customer_id = c.customer_id
            LEFT JOIN dim_product p ON w.product_id = p.product_id;
        """)

    def export_data_marts(self):
        """Export aggregated data marts into CSV & Parquet for Power BI ingestion."""
        logger.info("=== STEP 4: EXPORTING DATA MARTS FOR POWER BI ===")
        EXPORTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        marts = [
            "dm_sales_performance_monthly",
            "dm_customer_rfm_segmentation",
            "dm_inventory_health",
            "dm_conversion_funnel"
        ]
        
        for mart in marts:
            df = self.conn.execute(f"SELECT * FROM {mart}").df()
            csv_path = EXPORTS_DATA_DIR / f"{mart}.csv"
            parquet_path = EXPORTS_DATA_DIR / f"{mart}.parquet"
            
            df.to_csv(csv_path, index=False)
            df.to_parquet(parquet_path, index=False)
            logger.info(f"Exported {len(df)} rows to {csv_path.name} and {parquet_path.name}")

    def run_pipeline(self):
        """Execute complete ETL workflow."""
        start_time = datetime.now()
        logger.info("Starting Enterprise Retail ETL Pipeline execution...")
        
        datasets = self.extract_raw_datasets()
        self.load_staging_tables(datasets)
        self.transform_star_schema()
        self.export_data_marts()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"=== ETL PIPELINE EXECUTED SUCCESSFULLY IN {elapsed:.2f} SECONDS ===")
        self.conn.close()

if __name__ == "__main__":
    pipeline = RetailETLPipeline()
    pipeline.run_pipeline()
