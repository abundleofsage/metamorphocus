#!/bin/bash

# Start Streamlit manager backend on port 8000 in the background
streamlit run app.py --server.port 8000 --server.headless true &

# Wait a moment for Streamlit to start
sleep 2

# Start Flask sales page on port 5000 in the foreground
python sales.py
