@echo off
title JARVIS (Hermes Agent)
:loop
C:\Windows\System32\wsl.exe -d Ubuntu -- bash -lc "cd ~ && hermes"
echo.
echo [JARVIS session ended. Restarting in 3s... Press Ctrl+C to exit]
timeout /t 3 /nobreak >nul
goto loop
