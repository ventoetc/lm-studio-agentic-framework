@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting LM Studio Chat...
streamlit run app.py --server.address=0.0.0.0
pause