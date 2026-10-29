@echo off
setlocal EnableExtensions
title Llama.cpp y Optimizador de RAM - Definitivo
cd /d "%~dp0"

echo [INFO] Localizando entorno virtual Python...

:: Buscar el Python del entorno virtual (.llama-venv o .venv)
set "PYTHON_EXE="
if exist "%~dp0.llama-venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.llama-venv\Scripts\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)

if not defined PYTHON_EXE (
    echo [ERROR CRITICO] No se encuentra ningun entorno virtual Python.
    goto fin
)

echo [INFO] Usando Python en: %PYTHON_EXE%
echo.

:: Lanzar el Optimizador de RAM en segundo plano
if exist "app\services\ram_optimizer.py" (
    echo [INFO] Iniciando Monitor de RAM en segundo plano...
    start /min "" "%PYTHON_EXE%" app\services\ram_optimizer.py
)

:: Lanzar el Gestor Principal de Llama sin argumentos de capas sobrantes
if exist "tools\llama\manager.py" (
    echo [INFO] Abriendo Panel de Control de Llama...
    echo.
    "%PYTHON_EXE%" tools\llama\manager.py --auto-start
) else (
    echo [ERROR CRITICO] No se encuentra el archivo 'tools\llama\manager.py'.
    goto fin
)

goto exit_script

:fin
echo.
echo ========================================================
echo [!] El script se detuvo debido a un error.
echo ========================================================
pause

:exit_script
endlocal
exit /b 0