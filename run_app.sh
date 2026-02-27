#!/bin/bash
# Run script for Streamlit app

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the Streamlit app
streamlit run src/mechanics_roster/app.py
