import pytest
import pandas as pd
from pathlib import Path
from data_generator.generate_synthetic_data import RetailDataGenerator
from config.settings import RAW_DATA_DIR

def test_data_generation_files_created(tmp_path):
    generator = RetailDataGenerator(output_dir=tmp_path)
    stores_df = generator.generate_stores()
    products_df = generator.generate_products()
    customers_df = generator.generate_customers()
    
    assert (tmp_path / "stores.csv").exists()
    assert (tmp_path / "products.csv").exists()
    assert (tmp_path / "customers.csv").exists()
    
    assert len(stores_df) > 0
    assert len(products_df) > 0
    assert len(customers_df) > 0
