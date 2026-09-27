# Power BI Enterprise Retail Analytics Data Model Blueprint

This document provides the exact DAX measures, Star Schema relationship specifications, and recommended visual canvas layout for importing the Enterprise Retail Data Platform into **Power BI Desktop**.

---

## 1. Data Model Relationships (Star Schema)

| Fact Table | Fact Column | Dimension Table | Dimension Column | Cardinality | Cross Filter Direction |
|:---|:---|:---|:---|:---|:---|
| `fact_sales` | `customer_sk` | `dim_customer` | `customer_sk` | Many to One (*:1) | Single |
| `fact_sales` | `store_sk` | `dim_store` | `store_sk` | Many to One (*:1) | Single |
| `fact_sales` | `product_sk` | `dim_product` | `product_sk` | Many to One (*:1) | Single |
| `fact_sales` | `order_date_key` | `dim_date` | `date_key` | Many to One (*:1) | Single |
| `fact_inventory_snapshot` | `store_sk` | `dim_store` | `store_sk` | Many to One (*:1) | Single |
| `fact_inventory_snapshot` | `product_sk` | `dim_product` | `product_sk` | Many to One (*:1) | Single |
| `fact_web_events` | `customer_sk` | `dim_customer` | `customer_sk` | Many to One (*:1) | Single |
| `fact_web_events` | `product_sk` | `dim_product` | `product_sk` | Many to One (*:1) | Single |

---

## 2. Core DAX Measures (`_MeasuresTable`)

### Financial Metrics
```dax
Total Revenue = SUM(fact_sales[net_item_revenue])

Total Net Profit = SUM(fact_sales[net_item_profit])

Profit Margin % = 
DIVIDE(
    [Total Net Profit],
    [Total Revenue],
    0
)

Total Units Sold = SUM(fact_sales[quantity])

Total Orders = DISTINCTCOUNT(fact_sales[order_id])

Average Order Value (AOV) = 
DIVIDE(
    [Total Revenue],
    [Total Orders],
    0
)
```

### Time Intelligence Metrics (YTD, MoM Growth)
```dax
Revenue YTD = 
TOTALYTD(
    [Total Revenue],
    dim_date[full_date]
)

Prior Month Revenue = 
CALCULATE(
    [Total Revenue],
    DATEADD(dim_date[full_date], -1, MONTH)
)

MoM Revenue Growth % = 
VAR _Current = [Total Revenue]
VAR _Prior = [Prior Month Revenue]
RETURN 
DIVIDE(_Current - _Prior, _Prior, 0)
```

### Customer & Inventory Metrics
```dax
Active Customers Count = 
CALCULATE(
    DISTINCTCOUNT(fact_sales[customer_sk]),
    fact_sales[order_status] = "Completed"
)

Out of Stock Products = 
CALCULATE(
    COUNTROWS(fact_inventory_snapshot),
    fact_inventory_snapshot[is_out_of_stock] = TRUE()
)

Reorder Alert Count = 
CALCULATE(
    COUNTROWS(fact_inventory_snapshot),
    fact_inventory_snapshot[needs_reorder] = TRUE()
)
```

---

## 3. Recommended Canvas Page Layout

### Page 1: Executive Sales Overview
- **Header KPI Cards**: Total Revenue, Total Net Profit, Profit Margin %, Total Orders, AOV.
- **Main Visual (Combo Chart)**: Monthly Gross Revenue vs Net Profit Margin Trend (X-axis: Month Year, Bar: Revenue, Line: Profit Margin %).
- **Donut Chart**: Revenue Share by Product Category.
- **Bar Chart**: Top 5 Stores by Net Revenue.
- **Slicers**: Region, Date Range, Store Type, Order Status.

### Page 2: Customer Segmentation & Behavioral RFM
- **Scattered / Cluster Visual**: Customer Frequency vs Monetary Spend by RFM Segment.
- **Bar Chart**: Customer Count by RFM Tier (Champions, Loyal, At-Risk, Inactive).
- **Table Visual**: Customer Top Spenders List with Loyalty Points.

### Page 3: Supply Chain & Inventory Health
- **Gauge Visual**: Total Stock Health Index (% of healthy SKUs).
- **Matrix Visual**: Store Name vs Product Category showing Out-of-Stock count & Recommended Reorder Quantity.
- **Card Alerts**: Critical Out-of-Stock SKUs.
