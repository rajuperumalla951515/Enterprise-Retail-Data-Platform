-- =========================================================
-- ENTERPRISE RETAIL DATA PLATFORM - STAGING TABLES
-- =========================================================

DROP TABLE IF EXISTS stg_stores;
CREATE TABLE stg_stores (
    store_id VARCHAR(50),
    store_name VARCHAR(150),
    store_type VARCHAR(50),
    region VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    square_feet INT,
    open_date DATE
);

DROP TABLE IF EXISTS stg_products;
CREATE TABLE stg_products (
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    cost_price DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    supplier_id VARCHAR(50),
    created_at TIMESTAMP
);

DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers (
    customer_id VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150),
    phone VARCHAR(50),
    gender VARCHAR(50),
    age_group VARCHAR(20),
    customer_segment VARCHAR(50),
    loyalty_points INT,
    joined_date DATE,
    state VARCHAR(50),
    city VARCHAR(100)
);

DROP TABLE IF EXISTS stg_orders;
CREATE TABLE stg_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    store_id VARCHAR(50),
    order_date TIMESTAMP,
    order_status VARCHAR(50),
    payment_method VARCHAR(50),
    shipping_cost DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2)
);

DROP TABLE IF EXISTS stg_order_items;
CREATE TABLE stg_order_items (
    order_item_id VARCHAR(50),
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10,2),
    total_item_price DECIMAL(10,2)
);

DROP TABLE IF EXISTS stg_inventory;
CREATE TABLE stg_inventory (
    inventory_id VARCHAR(50),
    store_id VARCHAR(50),
    product_id VARCHAR(50),
    stock_on_hand INT,
    reorder_point INT,
    safety_stock INT,
    last_restock_date DATE
);

DROP TABLE IF EXISTS stg_web_events;
CREATE TABLE stg_web_events (
    event_id VARCHAR(100),
    session_id VARCHAR(100),
    customer_id VARCHAR(50),
    event_type VARCHAR(50),
    product_id VARCHAR(50),
    page_url VARCHAR(255),
    device_type VARCHAR(50),
    event_timestamp TIMESTAMP,
    user_agent TEXT
);
