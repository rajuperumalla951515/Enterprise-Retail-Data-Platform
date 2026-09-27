import json
import duckdb
from pathlib import Path
from datetime import datetime
from config.settings import DB_FILE_PATH, REPORTS_DATA_DIR
from config.logging_config import logger
from quality.validation_rules import DataValidationSuite

def run_data_validation_pipeline():
    """Run data quality assertions and generate markdown audit report."""
    db_path = str(DB_FILE_PATH).replace(".db", ".duckdb")
    conn = duckdb.connect(db_path)
    
    suite = DataValidationSuite(conn)
    results = suite.run_full_suite()
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results if r["status"] == "PASSED")
    failed_checks = total_checks - passed_checks
    
    report_md = f"""# Enterprise Retail Data Platform - Data Quality Audit Report
**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Target Database:** `enterprise_retail_dw.duckdb`  
**Overall Status:** {"🟢 PASSED" if failed_checks == 0 else "🔴 FAILED"}  

---

## Executive Summary
- **Total Validations Run:** {total_checks}
- **Checks Passed:** {passed_checks} ({(passed_checks/total_checks)*100:.1f}%)
- **Checks Failed:** {failed_checks}

---

## Detailed Check Results

| Check Type | Target Object | Target Column / Relation | Status | Audit Details |
|:---|:---|:---|:---|:---|
"""
    
    for r in results:
        check_type = r.get("check_name", "CUSTOM_CHECK")
        tbl = r.get("table_name", r.get("child_table", "N/A"))
        col = r.get("column", r.get("child_col", "N/A"))
        status_icon = "✅ PASSED" if r["status"] == "PASSED" else "❌ FAILED"
        
        details_str = ""
        if "details" in r:
            details_str = ", ".join([f"{k}: {v} nulls" for k, v in r["details"].items()])
        elif "duplicate_count" in r:
            details_str = f"{r['duplicate_count']} duplicates out of {r['total_rows']} rows"
        elif "violating_rows" in r:
            details_str = f"{r['violating_rows']} negative values found"
        elif "orphan_count" in r:
            details_str = f"{r['orphan_count']} orphan foreign keys found vs parent {r['parent_table']}"
            
        report_md += f"| `{check_type}` | `{tbl}` | `{col}` | {status_icon} | {details_str} |\n"

    report_md += "\n---\n*Report generated automatically by Data Validation Suite Module.*\n"
    
    REPORTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DATA_DIR / "data_quality_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    logger.info(f"Data Quality Report successfully generated at: {report_file}")
    conn.close()
    return passed_checks == total_checks

if __name__ == "__main__":
    run_data_validation_pipeline()
