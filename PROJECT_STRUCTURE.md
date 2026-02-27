# Project Structure Documentation

This document explains the MLOps-compliant structure of the Mechanics Roster Optimization project.

## Directory Structure

```
mechanics-roster-optimization/
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD pipeline
│
├── data/                          # Data files (not in version control)
│   ├── mechanic_skills_dataset.xlsx
│   ├── base_aircraft_schedule.xlsx
│   ├── cost_matrix.xlsx
│   └── avoidance_list.xlsx
│
├── notebooks/                      # Jupyter notebooks for exploration
│   └── mechanics_roster_optimization_dist_cost.ipynb
│
├── src/                            # Source code package
│   └── mechanics_roster/
│       ├── __init__.py            # Package initialization
│       ├── app.py                 # Streamlit application entry point
│       ├── config.py              # Configuration management
│       ├── data_loader.py         # Data loading and processing
│       ├── optimizer.py           # Optimization model creation and solving
│       └── excel_generator.py     # Excel output generation
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Shared pytest fixtures
│   ├── test_data_loader.py        # Tests for data loading
│   ├── test_optimizer.py          # Tests for optimization
│   └── test_config.py             # Tests for configuration
│
├── .flake8                         # Flake8 linting configuration
├── .gitignore                      # Git ignore rules
├── CONTRIBUTING.md                 # Contribution guidelines
├── example_usage.py                # Example script for programmatic usage
├── PROJECT_STRUCTURE.md           # This file
├── pytest.ini                      # Pytest configuration
├── pyproject.toml                  # Modern Python project configuration
├── README.md                       # Main project documentation
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── run_app.bat                     # Windows run script
├── run_app.sh                      # Linux/Mac run script
└── setup.py                        # Package setup configuration
```

## Module Descriptions

### `src/mechanics_roster/`

#### `app.py` (in `src/mechanics_roster/`)
- Streamlit web application entry point
- Handles UI interactions and file uploads
- Orchestrates the optimization workflow

#### `config.py`
- Configuration management using environment variables
- Logging setup
- Default values and validation

#### `data_loader.py`
- `DataLoader` class for loading and processing Excel files
- Handles mechanic skills, base schedules, cost matrices, and avoidance lists
- Data validation and transformation

#### `optimizer.py`
- `RosterOptimizer` class for optimization model creation
- Model solving with OR-Tools
- Solution extraction and validation

#### `excel_generator.py`
- `ExcelGenerator` class for creating formatted Excel outputs
- Handles styling, formatting, and layout

## Testing Structure

### Test Organization
- Tests mirror the source code structure
- Each module has a corresponding test file
- Shared fixtures in `conftest.py`

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mechanics_roster --cov-report=html

# Run specific test file
pytest tests/test_data_loader.py
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) performs:
1. **Multi-version testing**: Tests on Python 3.8, 3.9, 3.10, 3.11
2. **Linting**: Code style checks with flake8, black, isort
3. **Testing**: Unit tests with pytest and coverage reporting
4. **Coverage upload**: Codecov integration

## MLOps Best Practices Implemented

1. **Separation of Concerns**: Business logic separated from UI
2. **Modularity**: Each component in its own module
3. **Configuration Management**: Environment-based configuration
4. **Logging**: Structured logging throughout
5. **Testing**: Comprehensive unit test coverage
6. **CI/CD**: Automated testing and quality checks
7. **Documentation**: README, docstrings, and structure docs
8. **Package Structure**: Proper Python package layout
9. **Type Hints**: Type annotations for maintainability
10. **Version Control**: Proper .gitignore and project structure

## Development Workflow

1. **Local Development**:
   ```bash
   pip install -e ".[dev]"
   pytest
   black src/ tests/
   ```

2. **Before Committing**:
   - Run tests: `pytest`
   - Format code: `black src/ tests/`
   - Sort imports: `isort src/ tests/`
   - Lint: `flake8 src/ tests/`

3. **CI Pipeline**:
   - Automatically runs on push/PR
   - Tests on multiple Python versions
   - Checks code quality
   - Reports coverage

## Environment Variables

The application can be configured using environment variables:
- `SOLVER`: Solver to use (SCIP, CBC, GLOP) - default: SCIP
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) - default: INFO
- `DATA_DIR`: Data directory path - default: data

## Package Installation

Install as a package:
```bash
pip install -e .
```

This allows importing from anywhere:
```python
from mechanics_roster import DataLoader, RosterOptimizer
```
