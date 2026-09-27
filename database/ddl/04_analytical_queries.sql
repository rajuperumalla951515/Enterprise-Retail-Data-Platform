-- =========================================================
-- ENTERPRISE RETAIL DATA PLATFORM - ADVANCED SQL QUERIES
-- =========================================================

-- Query 1: Top 10 Revenue Generating Products with Running Sales Totals
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(f.quantity) AS units_sold,
        SUM(f.net_item_revenue) AS total_revenue,
        RANK() OVER (ORDER BY SUM(f.net_item_revenue) DESC) as revenue_rank
    FROM fact_sales f
    JOIN dim_product p ON f.product_sk = p.product_sk
    WHERE f.order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT 
    revenue_rank,
    product_id,
    product_name,
    category,
    units_sold,
    total_revenue,
    SUM(total_revenue) OVER (ORDER BY revenue_rank) AS running_cumulative_revenue
FROM product_sales
WHERE revenue_rank <= 10;

-- Query 2: Regional Store Sales Comparison & Profit Margin
SELECT 
    s.region,
    s.store_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.net_item_revenue) AS region_revenue,
    SUM(f.net_item_profit) AS region_profit,
    ROUND(SUM(f.net_item_profit) / SUM(f.net_item_revenue) * 100, 2) as profit_margin_percentage
FROM fact_sales f
JOIN dim_store s ON f.store_sk = s.store_sk
WHERE f.order_status NOT IN ('Cancelled')
GROUP BY s.region, s.store_name
ORDER BY region_revenue DESC;

-- Query 3: Web Events to Conversion Attributable Revenue
SELECT 
    e.device_type,
    COUNT(DISTINCT e.session_id) AS sessions,
    COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) AS conversions,
    ROUND(COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) * 100.0 / NULLIF(COUNT(DISTINCT e.session_id), 0), 2) AS conversion_rate_pct
FROM fact_web_events e
GROUP BY e.device_type
ORDER BY conversion_rate_pct DESC;
