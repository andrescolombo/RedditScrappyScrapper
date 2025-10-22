@echo off
chcp 65001 >nul
title Reddit Scraper - Scrapy GUI

echo.
echo ========================================
echo    REDDIT SCRAPER - SCRAPY GUI
echo ========================================
echo.

echo Iniciando interfaz grafica para Scrapy...
echo.

python reddit_scrapy_gui_simple.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo    ERROR AL EJECUTAR LA GUI
    echo ========================================
    echo.
    echo Posibles soluciones:
    echo 1. Verifica que Python este instalado
    echo 2. Instala tkinter: pip install tk
    echo 3. Usa el scraper normal: run_scraper_debug.bat
    echo.
    pause
    exit /b 1
)

echo.
echo GUI cerrada exitosamente.
pause
