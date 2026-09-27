-- =========================================================
-- ENTERPRISE RETAIL DATA PLATFORM - ANALYTICAL DATA MARTS
-- =========================================================

-- 1. Monthly Executive Sales Summary Data Mart
DROP VIEW IF EXISTS dm_sales_performance_monthly;
CREATE VIEW dm_sales_performance_monthly AS
SELECT 
    d.year_number,
    d.month_number,
    d.month_name,
    s.region,
    s.store_type,
    p.category,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    SUM(f.net_item_revenue) AS gross_revenue,
    SUM(f.discount_amount) AS total_discounts,
    SUM(f.net_item_profit) AS net_profit,
    ROUND(SUM(f.net_item_profit) / NULLIF(SUM(f.net_item_revenue), 0) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(f.net_item_revenue) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value
FROM fact_sales f
JOIN dim_date d ON f.order_date_key = d.date_key
JOIN dim_store s ON f.store_sk = s.store_sk
JOIN dim_product p ON f.product_sk = p.product_sk
WHERE f.order_status NOT IN ('Cancelled', 'Returned')
GROUP BY d.year_number, d.month_number, d.month_name, s.region, s.store_type, p.category;

-- 2. Customer RFM Segmentation Data Mart
DROP VIEW IF EXISTS dm_customer_rfm_segmentation;
CREATE VIEW dm_customer_rfm_segmentation AS
WITH customer_orders AS (
    SELECT 
        c.customer_sk,
        c.customer_id,
        c.full_name,
        c.email,
        c.customer_segment,
        MAX(f.order_timestamp) AS last_order_date,
        COUNT(DISTINCT f.order_id) AS order_frequency,
        SUM(f.net_item_revenue) AS total_monetary_spend
    FROM dim_customer c
    LEFT JOIN fact_sales f ON c.customer_sk = f.customer_sk AND f.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_sk, c.customer_id, c.full_name, c.email, c.customer_segment
)
SELECT 
    customer_sk,
    customer_id,
    full_name,
    email,
    customer_segment,
    last_order_date,
    COALESCE(order_frequency, 0) AS frequency,
    COALESCE(ROUND(total_monetary_spend, 2), 0.0) AS monetary,
    CASE 
        WHEN order_frequency >= 8 AND total_monetary_spend >= 1500 THEN 'Champions'
        WHEN order_frequency >= 4 AND total_monetary_spend >= 600 THEN 'Loyal Customers'
        WHEN order_frequency >= 2 THEN 'Potential Loyalists'
        WHEN order_frequency = 1 THEN 'New / Single Order'
        ELSE 'Inactive'
    END AS rfm_segment
FROM customer_orders;

-- 3. Inventory Health & Out-of-Stock Risk Data Mart
DROP VIEW IF EXISTS dm_inventory_health;
CREATE VIEW dm_inventory_health AS
SELECT 
    s.store_name,
    s.region,
    p.product_id,
    p.product_name,
    p.category,
    f.stock_on_hand,
    f.reorder_point,
    f.safety_stock,
    CASE 
        WHEN f.stock_on_hand = 0 THEN 'CRITICAL: OUT OF STOCK'
        WHEN f.stock_on_hand <= f.safety_stock THEN 'HIGH RISK: BELOW SAFETY STOCK'
        WHEN f.stock_on_hand <= f.reorder_point THEN 'WARNING: REORDER NEEDED'
        ELSE 'HEALTHY'
    END AS stock_status,
    (f.reorder_point + f.safety_stock - f.stock_on_hand) AS recommended_reorder_qty
FROM fact_inventory_snapshot f
JOIN dim_store s ON f.store_sk = s.store_sk
JOIN dim_product p ON f.product_sk = p.product_sk;

-- 4. Web Conversion Funnel Data Mart
DROP VIEW IF EXISTS dm_conversion_funnel;
CREATE VIEW dm_conversion_funnel AS
SELECT 
    event_type,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(event_fact_id) AS total_events,
    COUNT(DISTINCT customer_sk) AS unique_customers
FROM fact_web_events
GROUP BY event_type;
