@echo off

:: ============================================================================
:: Configurable Ports
:: ============================================================================
:: Set the port for the Streamlit manager backend.
:: The sales page will redirect to this port after manager login.
set STREAMLIT_PORT=8001

:: Set the port for the Flask sales page.
set FLASK_PORT=5000
:: ============================================================================

ECHO "Starting Streamlit manager backend on port %STREAMLIT_PORT%..."
START "Streamlit" cmd /c "streamlit run app.py --server.port %STREAMLIT_PORT% --server.headless true"

ECHO "Waiting a moment for Streamlit to start..."
timeout /t 2 /nobreak

ECHO "Starting Flask sales page on port %FLASK_PORT%..."
python sales.py
