from pathlib import Path
import pandas as pd
from pipelines.extractors.base_extractor import BaseExtractor
from config.logging_config import logger

class CSVExtractor(BaseExtractor):
    """Extracts raw structured CSV data files."""

    def extract(self) -> pd.DataFrame:
        self.validate_file_exists()
        logger.info(f"Extracting CSV dataset: {self.file_path.name}")
        df = pd.read_csv(self.file_path)
        logger.info(f"Successfully extracted {len(df)} records from {self.file_path.name}")
        return df
