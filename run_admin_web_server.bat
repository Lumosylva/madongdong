@echo off
title Admin Service
echo ============================================================
echo   Start admin Service
echo ============================================================
echo.

echo Start service...
echo 当前路径是：%cd%
cd %cd%/admin
npm run dev

echo.
echo ============================================================
echo   Admin Service launched successfully！
echo ============================================================
echo.
pause > nul
