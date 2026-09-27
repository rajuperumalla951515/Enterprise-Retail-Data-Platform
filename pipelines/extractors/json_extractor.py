import json
from pathlib import Path
import pandas as pd
from pipelines.extractors.base_extractor import BaseExtractor
from config.logging_config import logger

class JSONExtractor(BaseExtractor):
    """Extracts raw semi-structured JSON clickstream data files."""

    def extract(self) -> pd.DataFrame:
        self.validate_file_exists()
        logger.info(f"Extracting JSON dataset: {self.file_path.name}")
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        logger.info(f"Successfully extracted {len(df)} semi-structured JSON records from {self.file_path.name}")
        return df
