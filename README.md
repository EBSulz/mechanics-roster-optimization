# Mechanics Roster Optimization

An operations research project that optimizes the assignment of mechanics to bases, periods, and shifts using linear programming. The solution minimizes the total cost of moving mechanics while ensuring all required aircraft maintenance skills are covered at each location and time period.

## 📋 Problem Statement

The project addresses a workforce optimization challenge where:
- **49 mechanics** with varying skills need to be assigned to **3 bases**
- Each base has different aircraft types (AW139, H175, SK92) scheduled across **2 periods** and **2 shifts** (day/night)
- Each mechanic can only be assigned to **one** base, period, and shift combination
- Each base-period-shift combination requires mechanics with specific skills:
  - **AF (Airframe)** skills
  - **R (Rotor)** skills  
  - **AV (Avionics)** skills
- The goal is to **minimize the total cost** of moving mechanics to their assigned bases

## 🎯 Features

- **Mixed Integer Programming (MIP)** optimization using Google OR-Tools
- **Skill coverage constraints** ensuring all required aircraft maintenance skills are met
- **Cost minimization** objective function
- **Flexible data input** via Excel files
- **Comprehensive solution reporting** with detailed assignments

## 🔧 Requirements

### Python Dependencies

Install the required packages using:

```bash
pip install -r requirements.txt
```

The project requires:
- `ortools` - Google's optimization library (uses SCIP or CBC solver)
- `pandas` - Data manipulation and analysis
- `openpyxl` - Excel file reading/writing

### Python Version

Python 3.7 or higher is recommended.

## 📁 Project Structure

```
mechanics-roster-optimization/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt               # Development dependencies
├── setup.py                           # Package setup configuration
├── pyproject.toml                     # Modern Python project configuration
├── pytest.ini                         # Pytest configuration
├── .flake8                            # Flake8 linting configuration
├── .gitignore                         # Git ignore rules
├── src/                               # Source code package
│   └── mechanics_roster/
│       ├── __init__.py
│       ├── app.py                     # Streamlit application
│       ├── config.py                  # Configuration management
│       ├── data_loader.py             # Data loading and processing
│       ├── optimizer.py               # Optimization model creation and solving
│       └── excel_generator.py        # Excel output generation
├── tests/                              # Unit tests
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_optimizer.py
│   └── test_config.py
├── .github/
│   └── workflows/
│       └── ci.yml                     # GitHub Actions CI workflow
├── data/                               # Data files directory
│   ├── mechanic_skills_dataset.xlsx
│   ├── base_aircraft_schedule.xlsx
│   ├── cost_matrix.xlsx
│   └── avoidance_list.xlsx
└── notebooks/                          # Jupyter notebooks
    └── mechanics_roster_optimization_dist_cost.ipynb
```

## 📊 Data Files

### 1. `mechanic_skills_dataset.xlsx`
Contains the skills matrix for all mechanics:
- **mechanic_id**: Unique identifier for each mechanic (1-49)
- **aw139_af, aw139_r, aw139_av**: Skills for AW139 aircraft (Airframe, Rotor, Avionics)
- **h175_af, h175_r, h175_av**: Skills for H175 aircraft
- **sk92_af, sk92_r, sk92_av**: Skills for SK92 aircraft
- Values: `1` = mechanic has the skill, `0` = mechanic does not have the skill

### 2. `base_aircraft_schedule.xlsx`
Defines the aircraft requirements at each base for each period and shift:
- **base_id**: Base identifier (1, 2, or 3)
- **aw139, h175, sk92**: Number of each aircraft type present
- **period**: Time period/group (1 or 2)
- **shift**: Shift type (1 = Day, 2 = Night)

### 3. `cost_matrix.xlsx`
Contains the cost of moving each mechanic to each base:
- **id**: Mechanic ID
- **A, B, C**: Cost columns corresponding to bases 1, 2, and 3 respectively

## 🚀 Usage

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/mechanics-roster-optimization.git
   cd mechanics-roster-optimization
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install in development mode** (optional, for development):
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

### Running the Streamlit App

1. **Start the Streamlit application**:
   ```bash
   streamlit run src/mechanics_roster/app.py
   ```
   
   Or use the convenience scripts:
   ```bash
   # On Linux/Mac
   ./run_app.sh
   
   # On Windows
   run_app.bat
   ```

2. **Upload the required Excel files** through the web interface:
   - Mechanic Skills Dataset
   - Base Aircraft Schedule
   - Cost Matrix
   - Avoidance List (optional)

3. **Click "Run Optimization"** to generate the optimized roster

### Running Tests

Run the test suite with pytest:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=src/mechanics_roster --cov-report=html
```

### Using the Package Programmatically

```python
from mechanics_roster.data_loader import DataLoader
from mechanics_roster.optimizer import RosterOptimizer
from mechanics_roster.excel_generator import ExcelGenerator

# Load data
loader = DataLoader()
data = loader.load_data(
    "data/mechanic_skills_dataset.xlsx",
    "data/base_aircraft_schedule.xlsx",
    "data/cost_matrix.xlsx",
    "data/avoidance_list.xlsx"  # optional
)

# Create and solve model
optimizer = RosterOptimizer(solver_name="SCIP")
optimizer.create_model(data)
status, solve_time = optimizer.solve()

# Extract solution
assignments, total_cost = optimizer.extract_solution(
    data["mechanics"],
    data["bases"],
    data["periods"],
    data["shifts"],
    data["cost_dict"]
)

# Generate Excel output
generator = ExcelGenerator()
wb = generator.generate_output(
    assignments, data, optimizer.mechanic_skills,
    optimizer.mechanic_inspector_skills,
    optimizer.inspector_req_columns,
    data["base_schedule_df"]
)
wb.save("output/roster.xlsx")
```

## 🔬 Solution Approach

### Mathematical Model

**Decision Variables:**
- `x[m, b, g, s]` ∈ {0, 1}: Binary variable indicating if mechanic `m` is assigned to base `b`, period `g`, and shift `s`

**Constraints:**

1. **Single Assignment Constraint**: Each mechanic can work in at most one assignment
   ```
   Σ(b∈Bases) Σ(g∈Periods) Σ(s∈Shifts) x[m, b, g, s] ≤ 1  ∀m ∈ Mechanics
   ```

2. **Skill Coverage Constraint**: For each base-period-shift combination, ensure all required skills are covered
   ```
   For each aircraft type a present at (b, p, s):
     Σ(m ∈ Mechanics with skill a_af) x[m, b, p, s] ≥ 1
     Σ(m ∈ Mechanics with skill a_r) x[m, b, p, s] ≥ 1
     Σ(m ∈ Mechanics with skill a_av) x[m, b, p, s] ≥ 1
   ```

**Objective Function:**
```
Minimize: Σ(m∈Mechanics) Σ(b∈Bases) Σ(g∈Periods) Σ(s∈Shifts) cost[m, b] × x[m, b, g, s]
```

### Solver

The model uses **SCIP** (Solving Constraint Integer Programs) solver, with automatic fallback to **CBC** (Coin-or Branch and Cut) if SCIP is not available.

## 📈 Results

The optimization produces:
- **Optimal total cost**: Minimum cost to assign mechanics
- **Detailed assignments**: List of all mechanic assignments showing:
  - Mechanic ID
  - Base ID
  - Period/Group
  - Shift (Day/Night)
  - Individual assignment cost
- **Unassigned mechanics**: Count of mechanics not assigned (if any)

### Example Output

```
Optimal total cost: 303.00

Mechanic Assignments:
Mechanic   Base     Group    Shift    Cost      
1          1        1        Day      18.00     
3          1        1        Day      27.00     
...
Total assignments: 24
Unassigned mechanics: 25
```

## 🔍 Model Statistics

- **Decision Variables**: 588 binary variables (49 mechanics × 3 bases × 2 periods × 2 shifts)
- **Constraints**: 115 constraints
  - 49 single assignment constraints
  - 66 skill coverage constraints
- **Solver**: SCIP 10.0.0 (or CBC fallback)

## 🎓 Key Concepts

- **Operations Research**: Application of mathematical methods to optimize decision-making
- **Linear Programming**: Optimization technique with linear objective and constraints
- **Mixed Integer Programming**: Linear programming with integer/binary decision variables
- **Constraint Satisfaction**: Ensuring all business rules and requirements are met
- **Cost Optimization**: Finding the most economical solution while meeting all constraints

## 🔄 CI/CD

This project uses GitHub Actions for continuous integration. The CI pipeline:

- **Runs on**: Python 3.8, 3.9, 3.10, and 3.11
- **Tests**: Runs pytest with coverage reporting
- **Linting**: Checks code style with flake8, black, and isort
- **Triggers**: On push to `main`/`develop` branches and on pull requests

View the workflow configuration in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

### Running CI Checks Locally

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking (optional)
mypy src/
```

## 📝 Notes

- The model ensures **feasibility** by requiring skill coverage for all aircraft types present at each base-period-shift combination
- Mechanics can be **unassigned** if not needed to meet skill requirements
- The solution is **optimal** (not just feasible) when using SCIP solver
- Cost values of `0` indicate no movement cost (mechanic already at that base or base preference)

## 🏗️ MLOps Best Practices

This project follows MLOps best practices:

- ✅ **Modular architecture**: Separated business logic from UI
- ✅ **Configuration management**: Environment-based configuration
- ✅ **Logging**: Structured logging throughout the application
- ✅ **Testing**: Comprehensive unit tests with coverage
- ✅ **CI/CD**: Automated testing and linting via GitHub Actions
- ✅ **Package structure**: Proper Python package layout with `src/` directory
- ✅ **Type hints**: Type annotations for better code maintainability
- ✅ **Documentation**: Comprehensive README and docstrings

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run linting checks (`flake8`, `black`, `isort`)
7. Commit your changes (`git commit -m 'Add some amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Development Setup

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src/mechanics_roster --cov-report=html

# Format code
black src/ tests/
isort src/ tests/
```

## 📄 License

This project is provided as-is for educational and operational research purposes.