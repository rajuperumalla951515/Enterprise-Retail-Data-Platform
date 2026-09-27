from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import pandas as pd
from config.logging_config import logger

class BaseExtractor(ABC):
    """Abstract base class for all data extractors."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract raw dataset into pandas/polars DataFrame."""
        pass

    def validate_file_exists(self) -> bool:
        if not self.file_path.exists():
            logger.error(f"Source file not found: {self.file_path}")
            raise FileNotFoundError(f"Source file missing: {self.file_path}")
        return True
