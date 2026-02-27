"""
Unit tests for data_loader module.
"""

import io
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mechanics_roster.data_loader import DataLoader


@pytest.fixture
def sample_mechanic_skills():
    """Create sample mechanic skills DataFrame."""
    data = {
        "mechanic_id": [1, 2, 3],
        "aw139_af": [1, 0, 1],
        "aw139_r": [0, 1, 1],
        "aw139_av": [1, 1, 0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_base_schedule():
    """Create sample base schedule DataFrame."""
    data = {
        "base_id": [1, 1, 2, 2],
        "period": [1, 2, 1, 2],
        "shift": [1, 1, 2, 2],
        "aw139": [1, 1, 0, 0],
        "h175": [0, 0, 1, 1],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_cost_matrix():
    """Create sample cost matrix DataFrame."""
    data = {
        "id": [1, 2, 3],
        "A": [10.0, 20.0, 15.0],
        "B": [25.0, 15.0, 30.0],
        "C": [20.0, 25.0, 20.0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_avoidance_list():
    """Create sample avoidance list DataFrame."""
    data = {
        "mechanic_id": [1],
        "avoid_mechanic_id": [2],
        "penalty": [100.0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def data_loader():
    """Create DataLoader instance."""
    return DataLoader()


def test_load_data_basic(data_loader, sample_mechanic_skills, sample_base_schedule, sample_cost_matrix):
    """Test basic data loading functionality."""
    # Convert DataFrames to Excel file-like objects
    mechanic_skills_buffer = io.BytesIO()
    sample_mechanic_skills.to_excel(mechanic_skills_buffer, index=False)
    mechanic_skills_buffer.seek(0)

    base_schedule_buffer = io.BytesIO()
    sample_base_schedule.to_excel(base_schedule_buffer, index=False)
    base_schedule_buffer.seek(0)

    cost_matrix_buffer = io.BytesIO()
    sample_cost_matrix.to_excel(cost_matrix_buffer, index=False)
    cost_matrix_buffer.seek(0)

    data = data_loader.load_data(mechanic_skills_buffer, base_schedule_buffer, cost_matrix_buffer, None)

    assert "mechanics" in data
    assert "bases" in data
    assert "periods" in data
    assert "shifts" in data
    assert "cost_dict" in data
    assert len(data["mechanics"]) == 3
    assert len(data["bases"]) == 2
    assert len(data["periods"]) == 2
    assert len(data["shifts"]) == 2


def test_load_data_with_avoidance(
    data_loader, sample_mechanic_skills, sample_base_schedule, sample_cost_matrix, sample_avoidance_list
):
    """Test data loading with avoidance list."""
    # Convert DataFrames to Excel file-like objects
    mechanic_skills_buffer = io.BytesIO()
    sample_mechanic_skills.to_excel(mechanic_skills_buffer, index=False)
    mechanic_skills_buffer.seek(0)

    base_schedule_buffer = io.BytesIO()
    sample_base_schedule.to_excel(base_schedule_buffer, index=False)
    base_schedule_buffer.seek(0)

    cost_matrix_buffer = io.BytesIO()
    sample_cost_matrix.to_excel(cost_matrix_buffer, index=False)
    cost_matrix_buffer.seek(0)

    avoidance_buffer = io.BytesIO()
    sample_avoidance_list.to_excel(avoidance_buffer, index=False)
    avoidance_buffer.seek(0)

    data = data_loader.load_data(mechanic_skills_buffer, base_schedule_buffer, cost_matrix_buffer, avoidance_buffer)

    assert "avoidance_dict" in data
    assert len(data["avoidance_dict"]) > 0
    assert (1, 2) in data["avoidance_dict"]
    assert (2, 1) in data["avoidance_dict"]  # Should be symmetric


def test_cost_dict_creation(data_loader, sample_cost_matrix):
    """Test cost dictionary creation."""
    cost_matrix_buffer = io.BytesIO()
    sample_cost_matrix.to_excel(cost_matrix_buffer, index=False)
    cost_matrix_buffer.seek(0)

    # Create minimal data for testing
    mechanic_skills_buffer = io.BytesIO()
    pd.DataFrame({"mechanic_id": [1, 2, 3]}).to_excel(mechanic_skills_buffer, index=False)
    mechanic_skills_buffer.seek(0)

    base_schedule_buffer = io.BytesIO()
    pd.DataFrame({"base_id": [1, 2], "period": [1, 1], "shift": [1, 1]}).to_excel(base_schedule_buffer, index=False)
    base_schedule_buffer.seek(0)

    data = data_loader.load_data(mechanic_skills_buffer, base_schedule_buffer, cost_matrix_buffer, None)

    assert (1, 1) in data["cost_dict"]
    assert data["cost_dict"][(1, 1)] == 10.0
    assert (2, 2) in data["cost_dict"]
    assert data["cost_dict"][(2, 2)] == 15.0
