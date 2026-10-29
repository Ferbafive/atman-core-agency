@echo off
title Optimizador de RAM - Simplificado
cd /d "%~dp0"

echo [INFO] Iniciando el servicio de monitoreo con entorno virtual...

:: Ejecutar directamente usando el python dentro de .venv
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe app/services/ram_optimizer.py
) else (
    echo [ERROR] No se encuentra el interprete de Python en el entorno virtual .venv
    pause
)

pause