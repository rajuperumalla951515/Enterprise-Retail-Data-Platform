import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.logging_config import logger

try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import IntegerType, DecimalType, DateType, TimestampType, StringType
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    logger.warning("PySpark library not found in environment.")

def create_spark_session(app_name: str = "EnterpriseRetailSparkETL") -> Optional["SparkSession"]:
    """Initializes PySpark Session with optimized local memory configurations."""
    if not PYSPARK_AVAILABLE:
        logger.warning("PySpark unavailable. Falling back to Python/DuckDB ETL engine.")
        return None
        
    try:
        spark = SparkSession.builder \
            .appName(app_name) \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .config("spark.sql.shuffle.partitions", "4") \
            .getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        logger.info(f"PySpark session created successfully: {spark.version}")
        return spark
    except Exception as e:
        logger.warning(f"Failed to create PySpark session (Java JDK may not be installed): {e}")
        return None

def pyspark_transform_orders(spark: "SparkSession", raw_orders_path: Path):
    """PySpark ETL Pipeline step: Read, clean, deduplicate, and enrich Orders dataset."""
    logger.info(f"Running PySpark transformation on raw orders: {raw_orders_path}")
    
    df = spark.read.option("header", True).option("inferSchema", True).csv(str(raw_orders_path))
    
    # 1. Deduplication
    df_dedup = df.dropDuplicates(["order_id"])
    
    # 2. Schema standardization & Derived columns
    df_cleaned = df_dedup.withColumn("order_date", F.to_timestamp(F.col("order_date"))) \
        .withColumn("date_key", F.date_format(F.col("order_date"), "yyyyMMdd").cast(IntegerType())) \
        .withColumn("shipping_cost", F.col("shipping_cost").cast(DecimalType(10, 2))) \
        .withColumn("discount_amount", F.col("discount_amount").cast(DecimalType(10, 2))) \
        .withColumn("total_amount", F.col("total_amount").cast(DecimalType(10, 2)))
        
    logger.info(f"PySpark Orders Transformation Completed: {df_cleaned.count()} clean orders.")
    return df_cleaned

def pyspark_build_date_dimension(spark: "SparkSession", start_date: str = "2024-01-01", end_date: str = "2024-12-31"):
    """PySpark routine to generate a comprehensive Date Dimension dataframe."""
    logger.info(f"Generating Date Dimension via PySpark from {start_date} to {end_date}...")
    
    # Create sequence of dates
    date_df = spark.sql(f"SELECT explode(sequence(to_date('{start_date}'), to_date('{end_date}'), interval 1 day)) as full_date")
    
    dim_date = date_df.withColumn("date_key", F.date_format(F.col("full_date"), "yyyyMMdd").cast(IntegerType())) \
        .withColumn("day_of_week", F.dayofweek(F.col("full_date"))) \
        .withColumn("day_name", F.date_format(F.col("full_date"), "EEEE")) \
        .withColumn("day_of_month", F.dayofmonth(F.col("full_date"))) \
        .withColumn("day_of_year", F.dayofyear(F.col("full_date"))) \
        .withColumn("month_number", F.month(F.col("full_date"))) \
        .withColumn("month_name", F.date_format(F.col("full_date"), "MMMM")) \
        .withColumn("quarter_number", F.quarter(F.col("full_date"))) \
        .withColumn("year_number", F.year(F.col("full_date"))) \
        .withColumn("is_weekend", F.when(F.dayofweek(F.col("full_date")).isin([1, 7]), True).otherwise(False))
        
    return dim_date
