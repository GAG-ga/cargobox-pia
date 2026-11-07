@echo off
REM CargoBox: instala (la primera vez), carga datos de demo y abre Swagger en el navegador.
cd /d "%~dp0"
set DATABASE_URL=sqlite:///./cargobox_demo.db
if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual...
  py -3 -m venv .venv
)
echo Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
if not exist "cargobox_demo.db" (
  echo Cargando datos de demostracion...
  ".venv\Scripts\python.exe" scripts\cargar_demo.py
)
start "" http://localhost:8000/docs
echo.
echo API corriendo en http://localhost:8000/docs  (Ctrl+C para detener)
echo Para empezar la demo desde cero: borrar cargobox_demo.db y volver a abrir este archivo.
".venv\Scripts\python.exe" -m uvicorn src.api.main:app --port 8000
pause
