@echo off
echo Activating conda environment: mechanics-roster-optimization
call conda activate mechanics-roster-optimization
echo Starting Streamlit app...
streamlit run app.py
pause
