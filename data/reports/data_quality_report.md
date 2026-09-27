# Enterprise Retail Data Platform - Data Quality Audit Report
**Execution Date:** 2026-09-27 23:45:50  
**Target Database:** `enterprise_retail_dw.duckdb`  
**Overall Status:** 🟢 PASSED  

---

## Executive Summary
- **Total Validations Run:** 13
- **Checks Passed:** 13 (100.0%)
- **Checks Failed:** 0

---

## Detailed Check Results

| Check Type | Target Object | Target Column / Relation | Status | Audit Details |
|:---|:---|:---|:---|:---|
| `NULL_VALUE_CHECK` | `dim_store` | `N/A` | ✅ PASSED | store_id: 0 nulls, store_name: 0 nulls, region: 0 nulls |
| `NULL_VALUE_CHECK` | `dim_product` | `N/A` | ✅ PASSED | product_id: 0 nulls, product_name: 0 nulls, cost_price: 0 nulls, selling_price: 0 nulls |
| `NULL_VALUE_CHECK` | `fact_sales` | `N/A` | ✅ PASSED | sales_fact_id: 0 nulls, order_id: 0 nulls, customer_sk: 0 nulls, store_sk: 0 nulls, product_sk: 0 nulls |
| `UNIQUENESS_CHECK` | `dim_store` | `store_id` | ✅ PASSED | 0 duplicates out of 25 rows |
| `UNIQUENESS_CHECK` | `dim_product` | `product_id` | ✅ PASSED | 0 duplicates out of 144 rows |
| `UNIQUENESS_CHECK` | `dim_customer` | `customer_id` | ✅ PASSED | 0 duplicates out of 2500 rows |
| `NON_NEGATIVE_VALUE_CHECK` | `dim_product` | `selling_price` | ✅ PASSED | 0 negative values found |
| `NON_NEGATIVE_VALUE_CHECK` | `fact_sales` | `quantity` | ✅ PASSED | 0 negative values found |
| `NON_NEGATIVE_VALUE_CHECK` | `fact_inventory_snapshot` | `stock_on_hand` | ✅ PASSED | 0 negative values found |
| `REFERENTIAL_INTEGRITY_CHECK` | `fact_sales` | `customer_sk` | ✅ PASSED | 0 orphan foreign keys found vs parent dim_customer |
| `REFERENTIAL_INTEGRITY_CHECK` | `fact_sales` | `store_sk` | ✅ PASSED | 0 orphan foreign keys found vs parent dim_store |
| `REFERENTIAL_INTEGRITY_CHECK` | `fact_sales` | `product_sk` | ✅ PASSED | 0 orphan foreign keys found vs parent dim_product |
| `REFERENTIAL_INTEGRITY_CHECK` | `fact_sales` | `order_date_key` | ✅ PASSED | 0 orphan foreign keys found vs parent dim_date |

---
*Report generated automatically by Data Validation Suite Module.*
