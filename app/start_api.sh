#!/bin/bash

# Start FastAPI using Uvicorn
echo "Starting FastAPI..."
uvicorn fast_api.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Streamlit
echo "Starting Streamlit..."
streamlit run streamlit/app.py --server.address 0.0.0.0 --server.port 8501
