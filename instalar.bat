@echo off
rem Instala Entre Brasas en la compu del cliente.
rem Se corre con doble clic. Tambien sirve para ACTUALIZAR: si se reemplaza
rem el programa por una version nueva y se vuelve a correr, no se pierden datos.
rem Los datos quedan en %LOCALAPPDATA%\EntreBrasas (ver app\entre_brasas\settings.py).

setlocal
set SIN_PAUSA=0
if /i "%~1"=="--sin-pausa" set SIN_PAUSA=1
title Instalacion de Entre Brasas
cd /d "%~dp0app"

echo.
echo ============================================================
echo   Instalacion de ENTRE BRASAS
echo ============================================================
echo.

rem Python tiene que estar instalado.
python --version >nul 2>&1
if errorlevel 1 (
    echo No se encontro Python en esta computadora.
    echo.
    echo 1. Descargalo de https://www.python.org/downloads/
    echo 2. Al instalarlo, marca la casilla "Add python.exe to PATH".
    echo 3. Volve a abrir este archivo.
    echo.
    if "%SIN_PAUSA%"=="0" pause
    exit /b 1
)

rem Si la carpeta venv vino copiada de otra compu, no funciona: se rehace.
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe -c "pass" >nul 2>&1 || rmdir /s /q venv
)

if not exist venv\Scripts\python.exe (
    echo [1/4] Creando el entorno de Python...
    python -m venv venv || goto error
) else (
    echo [1/4] El entorno de Python ya existe.
)

echo [2/4] Instalando lo necesario. Puede tardar unos minutos...
venv\Scripts\python.exe -m pip install --disable-pip-version-check -q -r requirements.txt || goto error

rem Modo local del cliente: los datos van a su carpeta aparte.
set ENTRE_BRASAS_PRODUCCION=1

echo [3/4] Preparando la base de datos...
venv\Scripts\python.exe manage.py respaldar || goto error
venv\Scripts\python.exe manage.py migrate || goto error
venv\Scripts\python.exe manage.py seed_data --si-esta-vacia || goto error

echo [4/4] Creando el acceso directo en el escritorio...
rem pythonw ejecuta sin consola. El apagado se hace desde la web.
rem IconLocation = el logo de Entre Brasas en vez del icono generico de .bat.
powershell -NoProfile -Command "$d = $env:ENTRE_BRASAS_ESCRITORIO; if (-not $d) { $d = [Environment]::GetFolderPath('Desktop') }; $s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Entre Brasas.lnk')); $s.TargetPath = '%~dp0app\venv\Scripts\pythonw.exe'; $s.Arguments = [char]34 + '%~dp0app\iniciar.py' + [char]34; $s.WorkingDirectory = '%~dp0app'; $s.IconLocation = '%~dp0app\static\img\entre-brasas.ico'; $s.Save()" || goto error

echo.
echo ============================================================
echo   Listo. Entre Brasas quedo instalado.
echo.
echo   Para usarlo, hace doble clic en el icono "Entre Brasas"
echo   del escritorio.
echo   Para apagarlo, usa "Apagar sistema" dentro de la web.
echo ============================================================
echo.
if "%SIN_PAUSA%"=="0" pause
exit /b 0

:error
echo.
echo ============================================================
echo   Hubo un error en la instalacion.
echo   Revisa los mensajes de arriba o sacale una foto a esta
echo   pantalla y mandasela a quien te instalo el sistema.
echo ============================================================
echo.
if "%SIN_PAUSA%"=="0" pause
exit /b 1
