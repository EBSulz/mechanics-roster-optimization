@echo off
REM Run script for Streamlit app on Windows

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the Streamlit app
streamlit run src/mechanics_roster/app.py
