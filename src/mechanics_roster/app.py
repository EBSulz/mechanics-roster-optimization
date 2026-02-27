"""
Streamlit application entry point.
"""

import sys
from pathlib import Path

# Add src directory to Python path to allow imports
# This handles cases where the app is run directly without installing the package
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import io
from datetime import datetime

import pandas as pd
import streamlit as st
from ortools.linear_solver import pywraplp

from mechanics_roster.config import Config
from mechanics_roster.data_loader import DataLoader
from mechanics_roster.excel_generator import ExcelGenerator
from mechanics_roster.optimizer import RosterOptimizer

# Setup logging
Config.setup_logging()
import logging

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Mechanics Roster Optimization",
    page_icon="🔧",
    layout="wide",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    """Main Streamlit app."""
    st.markdown(
        '<h1 class="main-header">🔧 Mechanics Roster Optimization</h1>',
        unsafe_allow_html=True,
    )

    st.sidebar.header("📁 Upload Files")

    mechanic_skills_file = st.sidebar.file_uploader(
        "Mechanic Skills Dataset",
        type=["xlsx"],
        help="Upload mechanic_skills_dataset.xlsx",
    )

    base_schedule_file = st.sidebar.file_uploader(
        "Base Aircraft Schedule",
        type=["xlsx"],
        help="Upload base_aircraft_schedule.xlsx",
    )

    cost_matrix_file = st.sidebar.file_uploader(
        "Cost Matrix",
        type=["xlsx"],
        help="Upload cost_matrix.xlsx",
    )

    avoidance_list_file = st.sidebar.file_uploader(
        "Avoidance List (Optional)",
        type=["xlsx"],
        help="Upload avoidance_list.xlsx (optional)",
    )

    if st.sidebar.button("🚀 Run Optimization", type="primary"):
        if not all([mechanic_skills_file, base_schedule_file, cost_matrix_file]):
            st.error(
                "❌ Please upload all required files: Mechanic Skills Dataset, " "Base Aircraft Schedule, and Cost Matrix"
            )
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Load data
                status_text.text("📥 Loading data files...")
                progress_bar.progress(0.1)
                data_loader = DataLoader()
                config = Config()
                data = data_loader.load_data(
                    mechanic_skills_file,
                    base_schedule_file,
                    cost_matrix_file,
                    avoidance_list_file,
                )
                progress_bar.progress(0.3)

                # Data summary
                with st.expander("📊 Data Summary", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Mechanics", len(data["mechanics"]))
                    with col2:
                        st.metric("Bases", len(data["bases"]))
                    with col3:
                        st.metric("Periods", len(data["periods"]))
                    with col4:
                        st.metric("Shifts", len(data["shifts"]))

                # Create model
                status_text.text("⚙️ Creating optimization model...")
                progress_bar.progress(0.4)
                optimizer = RosterOptimizer(solver_name=config.solver)
                (
                    solver,
                    x,
                    mechanic_skills,
                    mechanic_inspector_skills,
                    inspector_req_columns,
                    avoidance_vars,
                ) = optimizer.create_model(data)
                progress_bar.progress(0.7)

                # Model info
                with st.expander("🔧 Model Information", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Variables:** {solver.NumVariables()}")
                        st.write(f"**Constraints:** {solver.NumConstraints()}")
                    with col2:
                        st.write(f"**Solver:** {solver.SolverVersion()}")
                        if data["avoidance_dict"]:
                            unique_pairs = {(min(k), max(k)) for k in data["avoidance_dict"].keys()}
                            st.write(f"**Avoidance Pairs:** {len(unique_pairs)}")

                # Solve
                status_text.text("🔄 Solving optimization problem...")
                progress_bar.progress(0.8)
                status, solve_time = optimizer.solve()
                progress_bar.progress(1.0)

                if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
                    status_text.text("✅ Solution found! Extracting results...")

                    assignments, total_cost = optimizer.extract_solution(
                        data["mechanics"],
                        data["bases"],
                        data["periods"],
                        data["shifts"],
                        data["cost_dict"],
                    )

                    # Avoidance penalties
                    total_avoidance_penalty = 0
                    if data["avoidance_dict"] and avoidance_vars:
                        unique_pairs = {(m1, m2) for (m1, m2) in data["avoidance_dict"].keys() if m1 < m2}
                        for m1, m2 in unique_pairs:
                            penalty = data["avoidance_dict"][(m1, m2)]
                            for b in data["bases"]:
                                for g in data["periods"]:
                                    for s in data["shifts"]:
                                        key = (m1, m2, b, g, s)
                                        if key in avoidance_vars and avoidance_vars[key].solution_value() > 0.5:
                                            total_avoidance_penalty += penalty

                    objective_value = solver.Objective().Value()

                    st.success("✅ Optimization completed successfully!")

                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Assignments", len(assignments))
                    with col2:
                        st.metric("Movement Cost", f"${total_cost:.2f}")
                    with col3:
                        st.metric(
                            "Avoidance Penalty",
                            f"${total_avoidance_penalty:.2f}",
                        )
                    with col4:
                        st.metric("Total Objective", f"${objective_value:.2f}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Unassigned Mechanics",
                            len(data["mechanics"]) - len(assignments),
                        )
                    with col2:
                        st.metric("Solve Time", f"{solve_time:.2f}s")

                    # Excel generation
                    status_text.text("📝 Generating Excel output...")
                    excel_generator = ExcelGenerator()
                    wb = excel_generator.generate_output(
                        assignments,
                        data,
                        mechanic_skills,
                        mechanic_inspector_skills,
                        inspector_req_columns,
                        data["base_schedule_df"],
                    )

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)

                    status_text.text("✅ Ready for download!")
                    progress_bar.empty()

                    st.download_button(
                        label="📥 Download Roster Output (Excel)",
                        data=output,
                        file_name=f"roster_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

                    with st.expander("📋 View Assignments", expanded=False):
                        assignments_df = pd.DataFrame(assignments)
                        st.dataframe(assignments_df, use_container_width=True)

                elif status == pywraplp.Solver.INFEASIBLE:
                    st.error("❌ Problem is infeasible - no solution exists that satisfies all constraints")
                    status_text.text("❌ Infeasible problem")
                else:
                    st.warning(f"⚠️ Solver status: {status}")
                    status_text.text(f"⚠️ Status: {status}")

            except Exception as e:
                logger.exception("Error during optimization")
                st.error(f"❌ Error: {str(e)}")
                status_text.text("❌ Error occurred")
                import traceback

                with st.expander("Error Details"):
                    st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
