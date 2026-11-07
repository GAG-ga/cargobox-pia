@echo off
REM CargoBox: lint + todas las pruebas con cobertura + reporte HTML.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
".venv\Scripts\python.exe" -m ruff check src tests
".venv\Scripts\python.exe" -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
start "" htmlcov\index.html
pause
