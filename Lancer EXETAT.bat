@echo off
title Plateforme EXETAT
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python n'est pas installe. Telechargez-le sur https://www.python.org/downloads/ et cochez "Add Python to PATH".
  pause
  exit /b 1
)
python lancer.py
pause
