import pytest
import duckdb
from quality.validation_rules import DataValidationSuite

def test_data_validation_rules():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE test_table (id INT, name VARCHAR)")
    conn.execute("INSERT INTO test_table VALUES (1, 'Alpha'), (2, 'Beta')")
    
    suite = DataValidationSuite(conn)
    null_res = suite.check_null_counts("test_table", ["id", "name"])
    uniq_res = suite.check_uniqueness("test_table", "id")
    
    assert null_res["status"] == "PASSED"
    assert uniq_res["status"] == "PASSED"
    conn.close()
