"""
Data loading and processing module for mechanics roster optimization.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and processing of input data files."""

    def __init__(self):
        """Initialize the DataLoader."""
        self.base_column_mapping = {"A": 1, "B": 2, "C": 3}

    def load_data(self, mechanic_skills_file, base_schedule_file, cost_matrix_file, avoidance_list_file=None):
        """
        Load and process all input data files.

        Args:
            mechanic_skills_file: Path or file-like object for mechanic skills dataset
            base_schedule_file: Path or file-like object for base aircraft schedule
            cost_matrix_file: Path or file-like object for cost matrix
            avoidance_list_file: Optional path or file-like object for avoidance list

        Returns:
            dict: Dictionary containing all processed data
        """
        data = {}

        # Load mechanic skills dataset
        logger.info("Loading mechanic skills dataset")
        mechanic_skills_df = pd.read_excel(mechanic_skills_file)
        mechanics = sorted(mechanic_skills_df["mechanic_id"].unique().tolist())
        data["mechanic_skills_df"] = mechanic_skills_df
        data["mechanics"] = mechanics

        # Load base aircraft schedule
        logger.info("Loading base aircraft schedule")
        base_schedule_df = pd.read_excel(base_schedule_file)
        bases = sorted(base_schedule_df["base_id"].unique().tolist())
        periods = sorted(base_schedule_df["period"].unique().tolist())
        shifts = sorted(base_schedule_df["shift"].unique().tolist())
        data["base_schedule_df"] = base_schedule_df
        data["bases"] = bases
        data["periods"] = periods
        data["shifts"] = shifts

        # Load cost matrix
        logger.info("Loading cost matrix")
        cost_matrix_df = pd.read_excel(cost_matrix_file)
        cost_dict = {}
        for _, row in cost_matrix_df.iterrows():
            mechanic_id = int(row["id"])
            for col, base_id in self.base_column_mapping.items():
                if col in cost_matrix_df.columns:
                    cost_dict[(mechanic_id, base_id)] = float(row[col])
        data["cost_matrix_df"] = cost_matrix_df
        data["cost_dict"] = cost_dict
        data["base_column_mapping"] = self.base_column_mapping

        # Load avoidance list (optional)
        avoidance_dict = {}
        if avoidance_list_file is not None:
            try:
                logger.info("Loading avoidance list")
                avoidance_df = pd.read_excel(avoidance_list_file)
                for _, row in avoidance_df.iterrows():
                    m1 = int(row["mechanic_id"])
                    m2 = int(row["avoid_mechanic_id"])
                    penalty = float(row["penalty"])
                    avoidance_dict[(m1, m2)] = penalty
                    avoidance_dict[(m2, m1)] = penalty
            except Exception as e:
                logger.warning(f"Could not load avoidance list: {e}")
        data["avoidance_dict"] = avoidance_dict

        logger.info(
            f"Loaded data: {len(mechanics)} mechanics, {len(bases)} bases, " f"{len(periods)} periods, {len(shifts)} shifts"
        )
        return data
