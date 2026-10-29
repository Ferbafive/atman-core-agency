@echo off
setlocal EnableExtensions
title Preparando Llama.cpp
cd /d "%~dp0"

set "PYTHON_EXE="
set "BASE_PYTHON="
set "PYTHONW_EXE="

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -c "import sys, tkinter" >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)

if defined PYTHON_EXE goto python_ready

for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "BASE_PYTHON=%%P"
if defined BASE_PYTHON goto create_venv

where winget >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro Python ni winget. Instala Python 3 y vuelve a ejecutar este archivo.
    pause
    exit /b 1
)

echo [INFO] Instalando Python 3.12 en el perfil de usuario...
winget install --id Python.Python.3.12 --exact --scope user --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo [ERROR] No se pudo instalar Python automaticamente con winget.
    pause
    exit /b 1
)

for /f "delims=" %%P in ('py -3.12 -c "import sys; print(sys.executable)" 2^>nul') do set "BASE_PYTHON=%%P"
if not defined BASE_PYTHON (
    echo [ERROR] Python se instalo, pero el lanzador py no encuentra la instalacion.
    pause
    exit /b 1
)

:create_venv
echo [INFO] Preparando entorno Python del proyecto...
"%BASE_PYTHON%" -m venv "%~dp0.llama-venv"
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual .llama-venv.
    pause
    exit /b 1
)
set "PYTHON_EXE=%~dp0.llama-venv\Scripts\python.exe"

:python_ready
"%PYTHON_EXE%" -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El Python seleccionado no incluye Tkinter, necesario para el panel.
    pause
    exit /b 1
)

"%PYTHON_EXE%" -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando psutil automaticamente...
    "%PYTHON_EXE%" -m pip --version >nul 2>&1
    if errorlevel 1 "%PYTHON_EXE%" -m ensurepip --upgrade >nul 2>&1
    "%PYTHON_EXE%" -m pip install --disable-pip-version-check --quiet psutil
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar psutil. Comprueba la conexion a Internet y vuelve a ejecutar.
        pause
        exit /b 1
    )
)

echo [INFO] Comprobando carpeta, modelo GGUF y servidor llama.cpp...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $root='C:\Llama'; $name='Qwen_Qwen3.5-4B-Q4_K_M.gguf'; $target=Join-Path $root $name; $downloads=Join-Path $env:USERPROFILE 'Downloads'; if (-not (Test-Path -LiteralPath $root -PathType Container)) { New-Item -ItemType Directory -Path $root -Force | Out-Null }; if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { if (-not (Test-Path -LiteralPath $downloads -PathType Container)) { throw ('No existe la carpeta de Descargas: ' + $downloads) }; $matches=@(Get-ChildItem -LiteralPath $downloads -Filter $name -File -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending); if ($matches.Count -eq 0) { throw ('No se encontro ' + $name + ' en Descargas') }; if ($matches.Count -gt 1) { Write-Warning ('Hay varias copias; se movera la mas reciente: ' + $matches[0].FullName) }; Move-Item -LiteralPath $matches[0].FullName -Destination $target -ErrorAction Stop; Write-Output ('Modelo movido desde: ' + $matches[0].FullName) }; if ((Get-Item -LiteralPath $target).Length -le 0) { throw ('El modelo esta vacio: ' + $target) }; $servers=@(Get-ChildItem -LiteralPath $root -Filter 'llama-server.exe' -File -Recurse -ErrorAction SilentlyContinue); if ($servers.Count -eq 0) { throw ('No se encontro llama-server.exe bajo ' + $root) }; if (-not (Test-Path -LiteralPath (Join-Path $root 'llama-server.exe') -PathType Leaf) -and $servers.Count -gt 1) { throw 'Hay varias copias de llama-server.exe; deja la version elegida en C:\Llama.' }; Write-Output ('Modelo listo: ' + $target); Write-Output ('Servidor listo: ' + $servers[0].FullName)"
if errorlevel 1 (
    echo [ERROR] No se pudo preparar C:\Llama. Revisa los permisos, Descargas y llama-server.exe.
    pause
    exit /b 1
)

echo [INFO] Abriendo el panel y el monitor de RAM en segundo plano...
for %%I in ("%PYTHON_EXE%") do set "PYTHONW_EXE=%%~dpIpythonw.exe"
if not exist "%PYTHONW_EXE%" set "PYTHONW_EXE=%PYTHON_EXE%"
start "" "%PYTHONW_EXE%" "%~dp0tools\llama\manager.py" --auto-start
if errorlevel 1 (
    echo [ERROR] No se pudo abrir el panel de Llama.cpp.
    pause
    exit /b 1
)

exit /b 0
