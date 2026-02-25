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
├── operations_research.ipynb         # Main optimization notebook
├── mechanic_skills_dataset.xlsx      # Mechanic skills data
├── base_aircraft_schedule.xlsx       # Base schedule with aircraft requirements
└── cost_matrix.xlsx                  # Cost of moving each mechanic to each base
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

1. **Ensure all data files are in the project directory**:
   - `mechanic_skills_dataset.xlsx`
   - `base_aircraft_schedule.xlsx`
   - `cost_matrix.xlsx`

2. **Open and run the Jupyter notebook**:
   ```bash
   jupyter notebook operations_research.ipynb
   ```

3. **Execute all cells** in sequence. The notebook will:
   - Load and validate the input data
   - Set up the optimization model
   - Define constraints and objective function
   - Solve the optimization problem
   - Display the optimal assignments

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

## 📝 Notes

- The model ensures **feasibility** by requiring skill coverage for all aircraft types present at each base-period-shift combination
- Mechanics can be **unassigned** if not needed to meet skill requirements
- The solution is **optimal** (not just feasible) when using SCIP solver
- Cost values of `0` indicate no movement cost (mechanic already at that base or base preference)

## 🤝 Contributing

Feel free to extend this project by:
- Adding additional constraints (e.g., mechanic preferences, workload balancing)
- Implementing different objective functions (e.g., maximize skill utilization)
- Adding visualization tools for the assignments
- Creating a web interface for easier interaction

## 📄 License

This project is provided as-is for educational and operational research purposes.