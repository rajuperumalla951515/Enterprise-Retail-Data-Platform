-- =========================================================
-- ENTERPRISE RETAIL DATA PLATFORM - DIMENSIONAL STAR SCHEMA
-- =========================================================

-- 1. DIMENSION TABLES
DROP TABLE IF EXISTS dim_store;
CREATE TABLE dim_store (
    store_sk INTEGER PRIMARY KEY,
    store_id VARCHAR(50) UNIQUE NOT NULL,
    store_name VARCHAR(150),
    store_type VARCHAR(50),
    region VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    square_feet INT,
    open_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product (
    product_sk INTEGER PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    cost_price DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    profit_margin DECIMAL(10,4),
    supplier_id VARCHAR(50),
    created_at TIMESTAMP
);

DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer (
    customer_sk INTEGER PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
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

DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY, -- YYYYMMDD format
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(15),
    day_of_month INT,
    day_of_year INT,
    month_number INT,
    month_name VARCHAR(15),
    quarter_number INT,
    year_number INT,
    is_weekend BOOLEAN
);

-- 2. FACT TABLES
DROP TABLE IF EXISTS fact_sales;
CREATE TABLE fact_sales (
    sales_fact_id VARCHAR(100) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    customer_sk INT,
    store_sk INT,
    product_sk INT,
    order_date_key INT,
    order_timestamp TIMESTAMP,
    order_status VARCHAR(50),
    payment_method VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    total_item_price DECIMAL(10,2),
    net_item_revenue DECIMAL(10,2),
    net_item_profit DECIMAL(10,2),
    FOREIGN KEY (customer_sk) REFERENCES dim_customer(customer_sk),
    FOREIGN KEY (store_sk) REFERENCES dim_store(store_sk),
    FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk),
    FOREIGN KEY (order_date_key) REFERENCES dim_date(date_key)
);

DROP TABLE IF EXISTS fact_inventory_snapshot;
CREATE TABLE fact_inventory_snapshot (
    inventory_fact_id VARCHAR(100) PRIMARY KEY,
    store_sk INT,
    product_sk INT,
    snapshot_date_key INT,
    stock_on_hand INT,
    reorder_point INT,
    safety_stock INT,
    is_out_of_stock BOOLEAN,
    needs_reorder BOOLEAN,
    FOREIGN KEY (store_sk) REFERENCES dim_store(store_sk),
    FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk),
    FOREIGN KEY (snapshot_date_key) REFERENCES dim_date(date_key)
);

DROP TABLE IF EXISTS fact_web_events;
CREATE TABLE fact_web_events (
    event_fact_id VARCHAR(100) PRIMARY KEY,
    event_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    customer_sk INT,
    product_sk INT,
    event_type VARCHAR(50),
    device_type VARCHAR(50),
    event_timestamp TIMESTAMP,
    event_date_key INT,
    FOREIGN KEY (customer_sk) REFERENCES dim_customer(customer_sk),
    FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk),
    FOREIGN KEY (event_date_key) REFERENCES dim_date(date_key)
);
