"""
Configuration management module.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Config:
    """Application configuration."""

    # Default values
    DEFAULT_SOLVER = "SCIP"
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_DATA_DIR = "data"

    def __init__(self):
        """Initialize configuration from environment variables or defaults."""
        self.solver = os.getenv("SOLVER", self.DEFAULT_SOLVER)
        self.log_level = os.getenv("LOG_LEVEL", self.DEFAULT_LOG_LEVEL)
        self.data_dir = Path(os.getenv("DATA_DIR", self.DEFAULT_DATA_DIR))
        
        # Validate
        self._validate()

    def _validate(self):
        """Validate configuration values."""
        valid_solvers = ["SCIP", "CBC", "GLOP"]
        if self.solver not in valid_solvers:
            logger.warning(f"Invalid solver {self.solver}, defaulting to {self.DEFAULT_SOLVER}")
            self.solver = self.DEFAULT_SOLVER

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            logger.warning(f"Invalid log level {self.log_level}, defaulting to {self.DEFAULT_LOG_LEVEL}")
            self.log_level = self.DEFAULT_LOG_LEVEL

    @classmethod
    def setup_logging(cls, log_level: Optional[str] = None):
        """
        Setup logging configuration.

        Args:
            log_level: Logging level (defaults to config value)
        """
        if log_level is None:
            config = cls()
            log_level = config.log_level

        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
