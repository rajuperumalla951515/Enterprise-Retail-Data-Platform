import json
import csv
import random
import uuid
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

from config.settings import (
    RAW_DATA_DIR, SYNTHETIC_DATA_CONFIG, CATEGORIES, REGIONS, 
    STORE_TYPES, PAYMENT_METHODS, ORDER_STATUSES, DEVICE_TYPES, INDIAN_BRANDS
)
from config.logging_config import logger
from data_generator.schemas import FIRST_NAMES, LAST_NAMES, CITIES_BY_REGION, generate_random_date

class RetailDataGenerator:
    """Generates realistic Indian enterprise retail datasets."""
    
    def __init__(self, output_dir: Path = RAW_DATA_DIR, config: dict = SYNTHETIC_DATA_CONFIG):
        self.output_dir = output_dir
        self.config = config
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_stores(self) -> pd.DataFrame:
        logger.info(f"Generating {self.config['num_stores']} Indian store locations...")
        stores = []
        for i in range(1, self.config['num_stores'] + 1):
            region = random.choice(REGIONS)
            city, state = random.choice(CITIES_BY_REGION[region])
            stores.append({
                "store_id": f"STR-IND-{i:04d}",
                "store_name": f"{city} Retail Center #{i}",
                "store_type": random.choice(STORE_TYPES),
                "region": region,
                "city": city,
                "state": state,
                "postal_code": f"{random.randint(110001, 700099)}",
                "square_feet": random.randint(15000, 180000),
                "open_date": generate_random_date("2015-01-01", "2023-12-31")[:10]
            })
        df = pd.DataFrame(stores)
        df.to_csv(self.output_dir / "stores.csv", index=False)
        return df

    def generate_products(self) -> pd.DataFrame:
        logger.info(f"Generating {self.config['num_products']} retail product catalog items...")
        products = []
        prod_idx = 1
        for category, subcategories in CATEGORIES.items():
            for subcat in subcategories:
                num_items = max(2, self.config['num_products'] // 25)
                for _ in range(num_items):
                    cost = round(random.uniform(250.0, 45000.0), 2)
                    markup = random.uniform(1.25, 2.2)
                    price = round(cost * markup, 2)
                    brand = random.choice(INDIAN_BRANDS)
                    products.append({
                        "product_id": f"PRD-IND-{prod_idx:05d}",
                        "product_name": f"{subcat} Model {chr(65 + random.randint(0, 25))}{random.randint(100, 999)}",
                        "category": category,
                        "subcategory": subcat,
                        "brand": brand,
                        "cost_price": cost,
                        "selling_price": price,
                        "supplier_id": f"SUP-IND-{random.randint(10, 99):03d}",
                        "created_at": generate_random_date("2020-01-01", "2023-12-31")
                    })
                    prod_idx += 1
        df = pd.DataFrame(products)
        df.to_csv(self.output_dir / "products.csv", index=False)
        return df

    def generate_customers(self) -> pd.DataFrame:
        logger.info(f"Generating {self.config['num_customers']} Indian customer profiles...")
        customers = []
        for i in range(1, self.config['num_customers'] + 1):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            region = random.choice(REGIONS)
            city, state = random.choice(CITIES_BY_REGION[region])
            segment = random.choices(["VIP Club Premier", "Gold Privilege", "Regular Shopper", "Festival Occasional"], weights=[0.12, 0.28, 0.45, 0.15])[0]
            
            # Injecting realistic data anomalies (e.g., missing emails for 3% records)
            email = f"{fname.lower()}.{lname.lower()}{random.randint(1,999)}@gmail.com" if random.random() > 0.03 else None
            
            customers.append({
                "customer_id": f"CUST-IND-{i:06d}",
                "first_name": fname,
                "last_name": lname,
                "email": email,
                "phone": f"+91-{random.randint(70,99)}{random.randint(1000000,9999999)}",
                "gender": random.choice(["Male", "Female", "Prefer Not to Say"]),
                "age_group": random.choice(["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]),
                "customer_segment": segment,
                "loyalty_points": random.randint(100, 45000),
                "joined_date": generate_random_date("2021-01-01", "2024-06-30")[:10],
                "state": state,
                "city": city
            })
        df = pd.DataFrame(customers)
        df.to_csv(self.output_dir / "customers.csv", index=False)
        return df

    def generate_orders_and_items(self, store_ids: List[str], product_df: pd.DataFrame, customer_ids: List[str]):
        logger.info(f"Generating {self.config['num_orders']} customer orders and item details...")
        orders = []
        order_items = []
        prod_list = product_df.to_dict('records')
        
        for i in range(1, self.config['num_orders'] + 1):
            order_id = f"ORD-IND-{i:07d}"
            customer_id = random.choice(customer_ids)
            store_id = random.choice(store_ids)
            order_date = generate_random_date(self.config['start_date'], self.config['end_date'])
            status = random.choices(ORDER_STATUSES, weights=[0.78, 0.04, 0.07, 0.06, 0.03, 0.02])[0]
            payment_method = random.choice(PAYMENT_METHODS)
            
            num_items = random.randint(1, 5)
            selected_prods = random.sample(prod_list, num_items)
            
            subtotal = 0.0
            for item_idx, prod in enumerate(selected_prods, 1):
                qty = random.randint(1, 4)
                unit_price = float(prod['selling_price'])
                item_total = round(qty * unit_price, 2)
                subtotal += item_total
                
                order_items.append({
                    "order_item_id": f"ITEM-IND-{i:07d}-{item_idx}",
                    "order_id": order_id,
                    "product_id": prod['product_id'],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "total_item_price": item_total
                })
                
            discount = round(subtotal * random.choice([0.0, 0.05, 0.1, 0.15, 0.2]), 2)
            shipping = 0.0 if subtotal > 1499 else 99.0
            total_amount = round(subtotal - discount + shipping, 2)
            
            orders.append({
                "order_id": order_id,
                "customer_id": customer_id,
                "store_id": store_id,
                "order_date": order_date,
                "order_status": status,
                "payment_method": payment_method,
                "shipping_cost": shipping,
                "discount_amount": discount,
                "total_amount": total_amount
            })
            
        # Introduce a few intentional duplicate rows (0.5%) for ETL deduplication testing
        orders_df = pd.DataFrame(orders)
        dup_orders = orders_df.sample(frac=0.005)
        orders_df = pd.concat([orders_df, dup_orders], ignore_index=True)
        orders_df.to_csv(self.output_dir / "orders.csv", index=False)
        
        items_df = pd.DataFrame(order_items)
        items_df.to_csv(self.output_dir / "order_items.csv", index=False)
        return orders_df, items_df

    def generate_inventory(self, store_ids: List[str], product_ids: List[str]) -> pd.DataFrame:
        logger.info(f"Generating inventory records across Indian retail stores...")
        inventory = []
        inv_id = 1
        for store_id in store_ids:
            for prod_id in product_ids:
                stock = random.randint(0, 500)
                reorder = random.randint(25, 60)
                safety = random.randint(15, 35)
                inventory.append({
                    "inventory_id": f"INV-IND-{inv_id:06d}",
                    "store_id": store_id,
                    "product_id": prod_id,
                    "stock_on_hand": stock,
                    "reorder_point": reorder,
                    "safety_stock": safety,
                    "last_restock_date": generate_random_date("2024-01-01", "2024-12-31")[:10]
                })
                inv_id += 1
        df = pd.DataFrame(inventory)
        df.to_csv(self.output_dir / "inventory.csv", index=False)
        return df

    def generate_web_clickstream_json(self, customer_ids: List[str], product_ids: List[str]):
        logger.info(f"Generating {self.config['num_web_events']} Indian clickstream JSON event records...")
        event_types = ["page_view", "product_click", "add_to_cart", "remove_from_cart", "checkout_init", "purchase"]
        weights = [0.45, 0.25, 0.15, 0.05, 0.06, 0.04]
        
        events = []
        for _ in range(self.config['num_web_events']):
            event_type = random.choices(event_types, weights=weights)[0]
            prod_id = random.choice(product_ids) if event_type in ["product_click", "add_to_cart", "remove_from_cart"] else None
            cust_id = random.choice(customer_ids) if random.random() > 0.2 else None
            
            events.append({
                "event_id": str(uuid.uuid4()),
                "session_id": f"SES-IND-{random.randint(100000, 999999)}",
                "customer_id": cust_id,
                "event_type": event_type,
                "product_id": prod_id,
                "page_url": f"https://retail.enterprise.in/{event_type.replace('_', '/')}",
                "device_type": random.choice(DEVICE_TYPES),
                "event_timestamp": generate_random_date(self.config['start_date'], self.config['end_date']),
                "user_agent": f"Mozilla/5.0 ({random.choice(['Windows NT 10.0', 'Android 13; Mobile', 'iPhone; CPU iPhone OS 17_0'])})"
            })
            
        with open(self.output_dir / "web_events.json", "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)
            
        logger.info("Synthetic raw Indian retail dataset generation completed successfully!")

def run_data_generation():
    generator = RetailDataGenerator()
    stores_df = generator.generate_stores()
    products_df = generator.generate_products()
    customers_df = generator.generate_customers()
    generator.generate_orders_and_items(
        store_ids=stores_df['store_id'].tolist(),
        product_df=products_df,
        customer_ids=customers_df['customer_id'].tolist()
    )
    generator.generate_inventory(
        store_ids=stores_df['store_id'].tolist(),
        product_ids=products_df['product_id'].tolist()
    )
    generator.generate_web_clickstream_json(
        customer_ids=customers_df['customer_id'].tolist(),
        product_ids=products_df['product_id'].tolist()
    )

if __name__ == "__main__":
    run_data_generation()
