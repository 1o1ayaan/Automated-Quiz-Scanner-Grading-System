@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo Creating virtual environment...
  python -m venv venv
  venv\Scripts\pip install -r requirements.txt
)
echo Starting Quiz Scanner at http://127.0.0.1:5000
venv\Scripts\python src\app.py
