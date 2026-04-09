@echo off
title Backend Service
setlocal
echo ============================================================
echo   Start Service
echo ============================================================
echo.

echo Start market data service...
call .venv\Scripts\activate && uvicorn app.main:app --reload

echo.
echo ============================================================
echo   Service launched successfully£¡
echo ============================================================
echo.
pause > nul
