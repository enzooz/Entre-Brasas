@echo off
rem Abre Entre Brasas. Es lo que ejecuta el icono del escritorio.
rem Todo el trabajo lo hace app\iniciar.py.

title Entre Brasas - no cerrar esta ventana
cd /d "%~dp0app"

if not exist venv\Scripts\python.exe (
    echo Entre Brasas todavia no esta instalado.
    echo Primero hace doble clic en instalar.bat.
    echo.
    pause
    exit /b 1
)

venv\Scripts\python.exe iniciar.py

if errorlevel 1 (
    echo.
    echo El sistema se cerro por un error. Sacale una foto a esta pantalla
    echo y mandasela a quien te instalo el sistema.
    echo.
    pause
)
