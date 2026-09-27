import duckdb
from typing import Dict, List, Any
from config.logging_config import logger

class DataValidationSuite:
    """Executes Great-Expectations style data quality assertions on Data Warehouse tables."""

    def __init__(self, conn: Any):
        self.conn = conn
        self.results = []

    def check_null_counts(self, table_name: str, columns: List[str]) -> dict:
        """Assert specified columns contain 0 null values."""
        status = "PASSED"
        details = {}
        for col in columns:
            null_cnt = self.conn.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col} IS NULL").fetchone()[0]
            details[col] = null_cnt
            if null_cnt > 0:
                status = "FAILED"
                
        res = {
            "check_name": "NULL_VALUE_CHECK",
            "table_name": table_name,
            "status": status,
            "details": details
        }
        self.results.append(res)
        return res

    def check_uniqueness(self, table_name: str, column_name: str) -> dict:
        """Assert target column values are strictly unique."""
        total_rows = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        distinct_rows = self.conn.execute(f"SELECT COUNT(DISTINCT {column_name}) FROM {table_name}").fetchone()[0]
        duplicate_count = total_rows - distinct_rows
        
        status = "PASSED" if duplicate_count == 0 else "FAILED"
        res = {
            "check_name": "UNIQUENESS_CHECK",
            "table_name": table_name,
            "column": column_name,
            "status": status,
            "total_rows": total_rows,
            "duplicate_count": duplicate_count
        }
        self.results.append(res)
        return res

    def check_positive_values(self, table_name: str, column_name: str) -> dict:
        """Assert numeric column contains non-negative values."""
        negative_cnt = self.conn.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} < 0").fetchone()[0]
        status = "PASSED" if negative_cnt == 0 else "FAILED"
        res = {
            "check_name": "NON_NEGATIVE_VALUE_CHECK",
            "table_name": table_name,
            "column": column_name,
            "status": status,
            "violating_rows": negative_cnt
        }
        self.results.append(res)
        return res

    def check_referential_integrity(self, child_table: str, child_col: str, parent_table: str, parent_col: str) -> dict:
        """Assert foreign key referential integrity between tables."""
        orphan_cnt = self.conn.execute(f"""
            SELECT COUNT(*) 
            FROM {child_table} c 
            LEFT JOIN {parent_table} p ON c.{child_col} = p.{parent_col} 
            WHERE c.{child_col} IS NOT NULL AND p.{parent_col} IS NULL
        """).fetchone()[0]
        
        status = "PASSED" if orphan_cnt == 0 else "FAILED"
        res = {
            "check_name": "REFERENTIAL_INTEGRITY_CHECK",
            "child_table": child_table,
            "child_col": child_col,
            "parent_table": parent_table,
            "parent_col": parent_col,
            "status": status,
            "orphan_count": orphan_cnt
        }
        self.results.append(res)
        return res

    def run_full_suite(self) -> List[dict]:
        """Execute full array of data quality validations."""
        logger.info("Executing Data Validation Suite...")
        
        # 1. Null Checks
        self.check_null_counts("dim_store", ["store_id", "store_name", "region"])
        self.check_null_counts("dim_product", ["product_id", "product_name", "cost_price", "selling_price"])
        self.check_null_counts("fact_sales", ["sales_fact_id", "order_id", "customer_sk", "store_sk", "product_sk"])
        
        # 2. Uniqueness Checks
        self.check_uniqueness("dim_store", "store_id")
        self.check_uniqueness("dim_product", "product_id")
        self.check_uniqueness("dim_customer", "customer_id")
        
        # 3. Non-Negative Value Checks
        self.check_positive_values("dim_product", "selling_price")
        self.check_positive_values("fact_sales", "quantity")
        self.check_positive_values("fact_inventory_snapshot", "stock_on_hand")
        
        # 4. Referential Integrity Checks
        self.check_referential_integrity("fact_sales", "customer_sk", "dim_customer", "customer_sk")
        self.check_referential_integrity("fact_sales", "store_sk", "dim_store", "store_sk")
        self.check_referential_integrity("fact_sales", "product_sk", "dim_product", "product_sk")
        self.check_referential_integrity("fact_sales", "order_date_key", "dim_date", "date_key")
        
        return self.results
