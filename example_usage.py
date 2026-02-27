"""
Example script demonstrating programmatic usage of the mechanics roster optimization package.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from mechanics_roster.data_loader import DataLoader
from mechanics_roster.optimizer import RosterOptimizer
from mechanics_roster.excel_generator import ExcelGenerator
from mechanics_roster.config import Config

# Setup logging
Config.setup_logging("INFO")


def main():
    """Example usage of the optimization package."""
    # Configuration
    data_dir = Path("data")
    
    # Load data
    print("Loading data...")
    loader = DataLoader()
    data = loader.load_data(
        data_dir / "mechanic_skills_dataset.xlsx",
        data_dir / "base_aircraft_schedule.xlsx",
        data_dir / "cost_matrix.xlsx",
        data_dir / "avoidance_list.xlsx",  # Optional
    )
    
    print(f"Loaded: {len(data['mechanics'])} mechanics, {len(data['bases'])} bases")
    
    # Create and solve model
    print("\nCreating optimization model...")
    config = Config()
    optimizer = RosterOptimizer(solver_name=config.solver)
    optimizer.create_model(data)
    
    print(f"Model created: {optimizer.solver.NumVariables()} variables, "
          f"{optimizer.solver.NumConstraints()} constraints")
    
    # Solve
    print("\nSolving optimization problem...")
    status, solve_time = optimizer.solve()
    
    if status in [0, 1]:  # OPTIMAL or FEASIBLE
        print(f"Solution found in {solve_time:.2f} seconds")
        
        # Extract solution
        assignments, total_cost = optimizer.extract_solution(
            data["mechanics"],
            data["bases"],
            data["periods"],
            data["shifts"],
            data["cost_dict"],
        )
        
        print(f"\nResults:")
        print(f"  Total assignments: {len(assignments)}")
        print(f"  Total cost: ${total_cost:.2f}")
        print(f"  Unassigned mechanics: {len(data['mechanics']) - len(assignments)}")
        
        # Generate Excel output
        print("\nGenerating Excel output...")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        generator = ExcelGenerator()
        wb = generator.generate_output(
            assignments,
            data,
            optimizer.mechanic_skills,
            optimizer.mechanic_inspector_skills,
            optimizer.inspector_req_columns,
            data["base_schedule_df"],
        )
        
        output_file = output_dir / "roster_output.xlsx"
        wb.save(output_file)
        print(f"Excel file saved to: {output_file}")
    else:
        print(f"Optimization failed with status: {status}")


if __name__ == "__main__":
    main()
