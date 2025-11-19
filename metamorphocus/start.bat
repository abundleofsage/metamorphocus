@echo off
ECHO "Starting Streamlit manager backend on port 8000..."
START "Streamlit" cmd /c "streamlit run app.py --server.port 8000 --server.headless true"

ECHO "Waiting a moment for Streamlit to start..."
timeout /t 2 /nobreak

ECHO "Starting Flask sales page on port 5000..."
python sales.py
