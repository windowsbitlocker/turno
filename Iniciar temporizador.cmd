@echo off
setlocal
cd /d "%~dp0"
where pyw.exe >nul 2>nul
if not errorlevel 1 (
    start "" /d "%~dp0" pyw.exe "%~dp0temporizador_debate_v13.py"
    exit /b
)
where pythonw.exe >nul 2>nul
if not errorlevel 1 (
    start "" /d "%~dp0" pythonw.exe "%~dp0temporizador_debate_v13.py"
    exit /b
)
echo No se encontro Python. Instala Python con Tkinter y vuelve a abrir este archivo.
pause
