@echo off
title web build
echo 当前路径是：%cd%
cd %cd%/web
npm run build
echo.
pause > nul
