import sys
import os
from datetime import datetime
from config.logging_config import logger
from data_generator.generate_synthetic_data import run_data_generation
from database.execute_sql import init_database
from pipelines.python_etl_pipeline import RetailETLPipeline
from quality.run_data_validation import run_data_validation_pipeline
from visualization.power_bi.dataset_export_helper import export_power_bi_tables

def run_master_platform():
    start_time = datetime.now()
    logger.info("==================================================================")
    logger.info("  ENTERPRISE RETAIL DATA PLATFORM - MASTER ORCHESTRATION PIPELINE ")
    logger.info("==================================================================")
    
    # Step 1: Synthetic Raw Data Generation
    logger.info("\n[STAGE 1/5] Generating Synthetic Multi-Source Retail Raw Datasets...")
    run_data_generation()
    
    # Step 2: Database Schema Provisioning
    logger.info("\n[STAGE 2/5] Initializing Database Warehouse Schemas...")
    init_database()
    
    # Step 3: ETL / ELT Pipeline Execution
    logger.info("\n[STAGE 3/5] Executing End-to-End Scalable ETL/ELT Pipeline...")
    pipeline = RetailETLPipeline()
    pipeline.run_pipeline()
    
    # Step 4: Data Quality & Validation Suite
    logger.info("\n[STAGE 4/5] Executing Automated Data Quality Assertions...")
    val_success = run_data_validation_pipeline()
    
    # Step 5: Power BI & Analytics Dataset Export
    logger.info("\n[STAGE 5/5] Exporting Data Marts for Power BI & Web Dashboard...")
    export_power_bi_tables()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("==================================================================")
    logger.info(f"  MASTER PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS!  ")
    logger.info("==================================================================")
    logger.info("Artifact Summary:")
    logger.info(" - Raw Data: data/raw/")
    logger.info(" - Data Warehouse DB: data/enterprise_retail_dw.duckdb")
    logger.info(" - Power BI Datasets: data/exports/")
    logger.info(" - Quality Audit Report: data/reports/data_quality_report.md")
    logger.info(" - Web Dashboard UI: visualization/web_dashboard/index.html")

if __name__ == "__main__":
    run_master_platform()
