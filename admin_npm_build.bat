@echo off
title admin build
echo 当前路径是：%cd%
cd %cd%/admin
npm run build
echo.
pause > nul
