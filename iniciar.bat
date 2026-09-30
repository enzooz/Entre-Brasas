@echo off
rem Abre Entre Brasas sin mantener una consola abierta.
rem Todo el trabajo lo hace app\iniciar.py.

title Entre Brasas
cd /d "%~dp0app"

if not exist venv\Scripts\python.exe (
    echo Entre Brasas todavia no esta instalado.
    echo Primero hace doble clic en instalar.bat.
    echo.
    pause
    exit /b 1
)

start "" "venv\Scripts\pythonw.exe" "iniciar.py"
exit /b
