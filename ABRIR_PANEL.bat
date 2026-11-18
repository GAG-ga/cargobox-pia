@echo off
REM CargoBox: abre el panel de operaciones con doble clic.
REM - Si la API ya esta corriendo, solo abre el navegador.
REM - Si no, la arranca en una ventana minimizada "CargoBox API" (cerrarla detiene la API).
REM - La primera vez crea el entorno, instala dependencias y carga los datos de demo.
cd /d "%~dp0"
set "PY=.venv\Scripts\python.exe"
set "PANEL=http://localhost:8000/panel/"
set "DATABASE_URL=sqlite:///./cargobox_demo.db"

if exist "%PY%" (
  "%PY%" scripts\esperar_api.py --segundos 1
  if not errorlevel 1 goto abrir
)

if not exist "%PY%" (
  echo Preparando CargoBox por primera vez, espera unos minutos...
  py -3 -m venv .venv
  if errorlevel 1 goto sin_python
)

REM Reinstala dependencias solo si requirements.txt cambio desde la ultima vez
fc /b requirements.txt .venv\requirements.instalado >nul 2>&1
if errorlevel 1 (
  echo Instalando dependencias...
  "%PY%" -m pip install -q -r requirements.txt
  if errorlevel 1 goto error
  copy /y requirements.txt .venv\requirements.instalado >nul
)

if not exist "cargobox_demo.db" (
  echo Cargando datos de demostracion...
  "%PY%" scripts\cargar_demo.py
)

echo Iniciando la API...
start "CargoBox API - cierra esta ventana para detenerla" /min "%PY%" -m uvicorn src.api.main:app --port 8000
"%PY%" scripts\esperar_api.py
if errorlevel 1 goto error

:abrir
start "" "%PANEL%"
exit /b 0

:sin_python
echo.
echo No se encontro Python 3.11 o superior. Instalalo desde https://www.python.org/downloads/
echo (marca "Add python.exe to PATH") y vuelve a abrir este archivo.
pause
exit /b 1

:error
echo.
echo No se pudo iniciar la API. Revisa los mensajes de arriba o abre INICIAR.bat para ver el detalle.
pause
exit /b 1
