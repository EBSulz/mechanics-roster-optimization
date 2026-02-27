"""
Unit tests for optimizer module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mechanics_roster.optimizer import RosterOptimizer
from mechanics_roster.data_loader import DataLoader
import pandas as pd
import io


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    # Minimal data for testing
    mechanic_skills_df = pd.DataFrame({
        "mechanic_id": [1, 2],
        "aw139_af": [1, 1],
        "aw139_r": [1, 1],
        "aw139_av": [1, 0],
    })

    base_schedule_df = pd.DataFrame({
        "base_id": [1, 1],
        "period": [1, 2],
        "shift": [1, 1],
        "aw139": [1, 1],
    })

    cost_matrix_df = pd.DataFrame({
        "id": [1, 2],
        "A": [10.0, 20.0],
        "B": [15.0, 25.0],
        "C": [20.0, 30.0],
    })

    data = {
        "mechanic_skills_df": mechanic_skills_df,
        "base_schedule_df": base_schedule_df,
        "mechanics": [1, 2],
        "bases": [1],
        "periods": [1, 2],
        "shifts": [1],
        "cost_dict": {(1, 1): 10.0, (2, 1): 20.0},
        "avoidance_dict": {},
    }

    return data


@pytest.fixture
def optimizer():
    """Create RosterOptimizer instance."""
    return RosterOptimizer(solver_name="CBC")  # Use CBC for testing (more widely available)


def test_optimizer_initialization(optimizer):
    """Test optimizer initialization."""
    assert optimizer.solver_name == "CBC"
    assert optimizer.solver is None
    assert optimizer.x is None


def test_create_model(optimizer, sample_data):
    """Test model creation."""
    solver, x, mechanic_skills, mechanic_inspector_skills, inspector_req_columns, avoidance_vars = (
        optimizer.create_model(sample_data)
    )

    assert solver is not None
    assert x is not None
    assert len(x) > 0
    assert mechanic_skills is not None
    assert optimizer.solver is not None
    assert optimizer.x is not None


def test_solve_model(optimizer, sample_data):
    """Test model solving."""
    optimizer.create_model(sample_data)
    status, solve_time = optimizer.solve()

    assert status is not None
    assert solve_time >= 0


def test_extract_solution(optimizer, sample_data):
    """Test solution extraction."""
    optimizer.create_model(sample_data)
    status, _ = optimizer.solve()

    if status in [0, 1]:  # OPTIMAL or FEASIBLE
        assignments, total_cost = optimizer.extract_solution(
            sample_data["mechanics"],
            sample_data["bases"],
            sample_data["periods"],
            sample_data["shifts"],
            sample_data["cost_dict"],
        )

        assert isinstance(assignments, list)
        assert isinstance(total_cost, (int, float))
        assert total_cost >= 0


def test_solve_without_model(optimizer):
    """Test that solving without creating model raises error."""
    with pytest.raises(ValueError, match="Model must be created"):
        optimizer.solve()


def test_extract_solution_without_model(optimizer, sample_data):
    """Test that extracting solution without creating model raises error."""
    with pytest.raises(ValueError, match="Model must be created"):
        optimizer.extract_solution(
            sample_data["mechanics"],
            sample_data["bases"],
            sample_data["periods"],
            sample_data["shifts"],
            sample_data["cost_dict"],
        )
