@echo off
title Web Service
echo ============================================================
echo   Start Web Service
echo ============================================================
echo.

echo Start service...
echo 当前路径是：%cd%/web
cd %cd%/web
npm run dev

echo.
echo ============================================================
echo   Web Service launched successfully！
echo ============================================================
echo.
pause > nul
