from sqlalchemy import create_engine
import pandas as pd
from config.settings import POSTGRES_CONN_STR
from config.logging_config import logger

class DatabaseLoader:
    """Handles transactional loads into PostgreSQL or SQLAlchemy compliant databases."""

    def __init__(self, connection_string: str = POSTGRES_CONN_STR):
        self.connection_string = connection_string
        self.engine = create_engine(self.connection_string)

    def load_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace"):
        """Load DataFrame into targeted database table."""
        logger.info(f"Loading dataframe ({len(df)} records) into database table '{table_name}'...")
        df.to_sql(table_name, con=self.engine, if_exists=if_exists, index=False)
        logger.info(f"Successfully written to '{table_name}'.")
