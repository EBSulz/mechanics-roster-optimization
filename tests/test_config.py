"""
Unit tests for config module.
"""

import os
import sys
from pathlib import Path

import pytest

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mechanics_roster.config import Config


def test_config_defaults():
    """Test configuration with default values."""
    config = Config()
    assert config.solver == "SCIP"
    assert config.log_level == "INFO"
    assert config.data_dir is not None


def test_config_solver_validation(monkeypatch):
    """Test solver validation."""
    monkeypatch.setenv("SOLVER", "INVALID_SOLVER")
    config = Config()
    # Should default to SCIP if invalid
    assert config.solver == "SCIP"


def test_config_log_level_validation(monkeypatch):
    """Test log level validation."""
    monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")
    config = Config()
    # Should default to INFO if invalid
    assert config.log_level == "INFO"


def test_config_environment_variables(monkeypatch):
    """Test configuration from environment variables."""
    monkeypatch.setenv("SOLVER", "CBC")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATA_DIR", "/custom/path")

    config = Config()
    assert config.solver == "CBC"
    assert config.log_level == "DEBUG"
    # Compare Path objects to handle platform-specific path separators
    assert config.data_dir == Path("/custom/path")


def test_setup_logging():
    """Test logging setup."""
    Config.setup_logging("INFO")
    # If no exception is raised, logging was set up successfully
    assert True
