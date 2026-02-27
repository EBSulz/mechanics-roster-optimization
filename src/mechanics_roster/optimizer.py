"""
Optimization model creation and solving module.
"""

import logging

import pandas as pd
from ortools.linear_solver import pywraplp

logger = logging.getLogger(__name__)


class RosterOptimizer:
    """Handles optimization model creation and solving."""

    def __init__(self, solver_name="SCIP"):
        """
        Initialize the optimizer.

        Args:
            solver_name: Name of the solver to use (default: "SCIP")
        """
        self.solver_name = solver_name
        self.solver = None
        self.x = None
        self.mechanic_skills = None
        self.mechanic_inspector_skills = None
        self.inspector_req_columns = None
        self.avoidance_vars = None

    def create_model(self, data):
        """
        Create the optimization model.

        Args:
            data: Dictionary containing all input data

        Returns:
            tuple: (solver, x, mechanic_skills, mechanic_inspector_skills,
                   inspector_req_columns, avoidance_vars)
        """
        # Extract data
        mechanic_skills_df = data["mechanic_skills_df"]
        base_schedule_df = data["base_schedule_df"]
        mechanics = data["mechanics"]
        bases = data["bases"]
        periods = data["periods"]
        shifts = data["shifts"]
        cost_dict = data["cost_dict"]
        avoidance_dict = data["avoidance_dict"]

        # Create solver
        logger.info(f"Creating solver: {self.solver_name}")
        solver = pywraplp.Solver.CreateSolver(self.solver_name)
        if not solver:
            logger.warning(f"{self.solver_name} not available, falling back to CBC")
            solver = pywraplp.Solver.CreateSolver("CBC")
            self.solver_name = "CBC"

        # Create decision variables: x[m, b, g, s]
        logger.info("Creating decision variables")
        x = {}
        for m in mechanics:
            for b in bases:
                for g in periods:
                    for s in shifts:
                        var_name = f"x_m{m}_b{b}_g{g}_s{s}"
                        x[(m, b, g, s)] = solver.IntVar(0, 1, var_name)

        # Constraint 1: Each mechanic ≤ 1 assignment
        logger.info("Adding single assignment constraints")
        for m in mechanics:
            constraint = solver.Constraint(0, 1, f"mechanic_{m}_single_assignment")
            for b in bases:
                for g in periods:
                    for s in shifts:
                        constraint.SetCoefficient(x[(m, b, g, s)], 1)

        # Constraint 2: Skill coverage
        logger.info("Adding skill coverage constraints")
        aircraft_types = ["aw139", "h175", "sk92"]
        skill_types = ["_af", "_r", "_av"]

        mechanic_skills = {}
        mechanic_inspector_skills = {}
        for _, row in mechanic_skills_df.iterrows():
            m = int(row["mechanic_id"])
            mechanic_skills[m] = {}
            mechanic_inspector_skills[m] = {}
            for aircraft in aircraft_types:
                for skill in skill_types:
                    col_name = f"{aircraft}{skill}"
                    if col_name in mechanic_skills_df.columns:
                        mechanic_skills[m][col_name] = int(row[col_name])
                    inspector_col_name = f"{aircraft}{skill}_inspec"
                    if inspector_col_name in mechanic_skills_df.columns:
                        mechanic_inspector_skills[m][inspector_col_name] = int(row[inspector_col_name])

        for _, row in base_schedule_df.iterrows():
            base_id = int(row["base_id"])
            period = int(row["period"])
            shift = int(row["shift"])

            for aircraft in aircraft_types:
                if aircraft in base_schedule_df.columns and row[aircraft] > 0:
                    for skill in skill_types:
                        skill_name = f"{aircraft}{skill}"
                        constraint = solver.Constraint(
                            1, solver.infinity(), f"skill_{skill_name}_base{base_id}_period{period}_shift{shift}"
                        )
                        for m in mechanics:
                            if mechanic_skills[m].get(skill_name, 0) == 1:
                                constraint.SetCoefficient(x[(m, base_id, period, shift)], 1)

        # Constraint 3: Inspector coverage
        inspector_req_columns = [col for col in base_schedule_df.columns if col.endswith("_inspec")]
        if inspector_req_columns:
            logger.info("Adding inspector coverage constraints")
            for _, row in base_schedule_df.iterrows():
                base_id = int(row["base_id"])
                period = int(row["period"])
                shift = int(row["shift"])

                for inspector_col in inspector_req_columns:
                    if inspector_col in base_schedule_df.columns:
                        inspector_required = row[inspector_col]
                        if pd.notna(inspector_required) and inspector_required > 0:
                            constraint = solver.Constraint(
                                1,
                                solver.infinity(),
                                f"inspector_{inspector_col}_base{base_id}_period{period}_shift{shift}",
                            )
                            for m in mechanics:
                                if mechanic_inspector_skills[m].get(inspector_col, 0) == 1:
                                    constraint.SetCoefficient(x[(m, base_id, period, shift)], 1)

        # Constraint 4: No self-inspection
        if inspector_req_columns:
            logger.info("Adding no self-inspection constraints")
            for _, row in base_schedule_df.iterrows():
                base_id = int(row["base_id"])
                period = int(row["period"])
                shift = int(row["shift"])

                for inspector_col in inspector_req_columns:
                    if inspector_col in base_schedule_df.columns:
                        inspector_required = row[inspector_col]
                        if pd.notna(inspector_required) and inspector_required > 0:
                            regular_skill_name = inspector_col.replace("_inspec", "")

                            for m_inspector in mechanics:
                                if mechanic_inspector_skills[m_inspector].get(inspector_col, 0) == 1:
                                    other_mechanics_with_skill = [
                                        m
                                        for m in mechanics
                                        if m != m_inspector and mechanic_skills[m].get(regular_skill_name, 0) == 1
                                    ]

                                    if other_mechanics_with_skill:
                                        constraint = solver.Constraint(
                                            -solver.infinity(),
                                            0,
                                            f"no_self_inspect_{inspector_col}"
                                            f"_base{base_id}_period{period}_shift{shift}_inspector{m_inspector}",
                                        )
                                        constraint.SetCoefficient(x[(m_inspector, base_id, period, shift)], 1)
                                        for m_other in other_mechanics_with_skill:
                                            constraint.SetCoefficient(x[(m_other, base_id, period, shift)], -1)

        # Avoidance penalty variables
        avoidance_vars = {}
        if avoidance_dict:
            logger.info("Adding avoidance constraints")
            unique_pairs = set()
            for m1, m2 in avoidance_dict.keys():
                if m1 < m2:
                    unique_pairs.add((m1, m2))

            for m1, m2 in unique_pairs:
                for b in bases:
                    for g in periods:
                        for s in shifts:
                            var_name = f"y_avoid_m{m1}_m{m2}_b{b}_g{g}_s{s}"
                            avoidance_vars[(m1, m2, b, g, s)] = solver.IntVar(0, 1, var_name)

            # Linearization constraints
            for m1, m2 in unique_pairs:
                for b in bases:
                    for g in periods:
                        for s in shifts:
                            y_var = avoidance_vars[(m1, m2, b, g, s)]

                            c1 = solver.Constraint(-solver.infinity(), 0, f"avoid_y_le_x1_m{m1}_m{m2}_b{b}_g{g}_s{s}")
                            c1.SetCoefficient(y_var, 1)
                            c1.SetCoefficient(x[(m1, b, g, s)], -1)

                            c2 = solver.Constraint(-solver.infinity(), 0, f"avoid_y_le_x2_m{m1}_m{m2}_b{b}_g{g}_s{s}")
                            c2.SetCoefficient(y_var, 1)
                            c2.SetCoefficient(x[(m2, b, g, s)], -1)

                            c3 = solver.Constraint(-1, solver.infinity(), f"avoid_y_ge_sum_m{m1}_m{m2}_b{b}_g{g}_s{s}")
                            c3.SetCoefficient(y_var, -1)
                            c3.SetCoefficient(x[(m1, b, g, s)], 1)
                            c3.SetCoefficient(x[(m2, b, g, s)], 1)

        # Objective function
        logger.info("Setting up objective function")
        objective = solver.Objective()

        # Movement costs
        for m in mechanics:
            for b in bases:
                cost = cost_dict.get((m, b), 0)
                for g in periods:
                    for s in shifts:
                        objective.SetCoefficient(x[(m, b, g, s)], cost)

        # Avoidance penalties
        if avoidance_dict and avoidance_vars:
            unique_pairs = set()
            for m1, m2 in avoidance_dict.keys():
                if m1 < m2:
                    unique_pairs.add((m1, m2))

            for m1, m2 in unique_pairs:
                penalty = avoidance_dict[(m1, m2)]
                for b in bases:
                    for g in periods:
                        for s in shifts:
                            if (m1, m2, b, g, s) in avoidance_vars:
                                objective.SetCoefficient(avoidance_vars[(m1, m2, b, g, s)], penalty)

        objective.SetMinimization()

        self.solver = solver
        self.x = x
        self.mechanic_skills = mechanic_skills
        self.mechanic_inspector_skills = mechanic_inspector_skills
        self.inspector_req_columns = inspector_req_columns
        self.avoidance_vars = avoidance_vars

        logger.info(f"Model created: {solver.NumVariables()} variables, {solver.NumConstraints()} constraints")
        return solver, x, mechanic_skills, mechanic_inspector_skills, inspector_req_columns, avoidance_vars

    def solve(self, time_limit_seconds=None):
        """
        Solve the optimization model.

        Args:
            time_limit_seconds: Optional time limit for solving (in seconds)

        Returns:
            tuple: (status, solve_time)
        """
        if self.solver is None:
            raise ValueError("Model must be created before solving")

        if time_limit_seconds:
            self.solver.SetTimeLimit(time_limit_seconds * 1000)  # Convert to milliseconds

        logger.info("Solving optimization problem")
        import time

        start_time = time.time()
        status = self.solver.Solve()
        solve_time = time.time() - start_time

        logger.info(f"Solve completed: status={status}, time={solve_time:.2f}s")
        return status, solve_time

    def extract_solution(self, mechanics, bases, periods, shifts, cost_dict):
        """
        Extract solution from the solved model.

        Args:
            mechanics: List of mechanic IDs
            bases: List of base IDs
            periods: List of period IDs
            shifts: List of shift IDs
            cost_dict: Dictionary mapping (mechanic_id, base_id) to cost

        Returns:
            tuple: (assignments, total_cost)
        """
        if self.x is None:
            raise ValueError("Model must be created before extracting solution")

        assignments = []
        total_cost = 0

        for m in mechanics:
            for b in bases:
                for g in periods:
                    for s in shifts:
                        if self.x[(m, b, g, s)].solution_value() > 0.5:
                            cost = cost_dict.get((m, b), 0)
                            total_cost += cost
                            assignments.append(
                                {
                                    "mechanic_id": m,
                                    "base_id": b,
                                    "group": g,
                                    "shift": s,
                                    "shift_name": "Day" if s == 1 else "Night",
                                    "cost": cost,
                                }
                            )

        logger.info(f"Extracted solution: {len(assignments)} assignments, total cost: {total_cost:.2f}")
        return assignments, total_cost
