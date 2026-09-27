import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
STAGING_DATA_DIR = DATA_DIR / "staging"
EXPORTS_DATA_DIR = DATA_DIR / "exports"
REPORTS_DATA_DIR = DATA_DIR / "reports"

# Ensure all directories exist
for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, STAGING_DATA_DIR, EXPORTS_DATA_DIR, REPORTS_DATA_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Database Configurations
DB_FILE_PATH = DATA_DIR / "enterprise_retail_dw.db"
POSTGRES_CONN_STR = os.getenv("POSTGRES_CONN_STR", f"sqlite:///{DB_FILE_PATH}")

# Synthetic Data Config
SYNTHETIC_DATA_CONFIG = {
    "num_stores": 25,
    "num_products": 150,
    "num_customers": 2500,
    "num_orders": 12000,
    "num_web_events": 50000,
    "num_inventory_records": 3750,  # 25 stores * 150 products
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}

# Indian Retail Metadata
CATEGORIES = {
    "Electronics & Gadgets": ["Smartphones", "Laptops", "Audio & Headphones", "Smartwatches", "Home Appliances"],
    "Apparel & Fashion": ["Ethnic Wear & Sarees", "Men's Wear", "Women's Western", "Footwear", "Fashion Accessories"],
    "Home & Living": ["Furniture", "Cookware & Kitchen", "Bedding & Linen", "Home Decor", "Pooja & Spiritual Essentials"],
    "Beauty & Personal Care": ["Ayurvedic & Skincare", "Personal Grooming", "Cosmetics", "Wellness & Health"],
    "Groceries & Pantry": ["Spices & Atta", "Beverages & Tea", "Snacks & Sweets", "Organic Staples", "Gourmet Foods"]
}

REGIONS = ["North India", "South India", "West India", "East & Central India", "North East India"]
STORE_TYPES = ["Flagship Mega Mart", "High-Street Retail", "Express City Outlet", "Omnichannel Fulfillment Hub"]
INDIAN_BRANDS = ["Tata Apex", "Reliance Vantage", "Aditya Horizon", "Godrej Lumina", "Bajaj Echo", "ITC Omni", "Mahindra Nexus", "Wipro Spectrum"]
PAYMENT_METHODS = ["UPI (PhonePe / Google Pay / Paytm)", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery (COD)", "Bajaj Finserv No-Cost EMI"]
ORDER_STATUSES = ["Completed", "Processing", "Shipped", "Delivered", "Cancelled", "Returned"]
DEVICE_TYPES = ["Mobile Android", "Mobile iOS", "Desktop Chrome", "Desktop Edge", "Tablet"]
