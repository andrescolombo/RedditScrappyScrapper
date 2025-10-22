@echo off
chcp 65001 >nul
title Reddit Scraper - GUI (tkinter)

echo.
echo ========================================
echo    REDDIT SCRAPER CON INTERFAZ GRAFICA
echo    (Version con tkinter)
echo ========================================
echo.

cd scraper_original

echo Iniciando interfaz grafica...
echo.
echo Si aparece un error, asegurate de que tengas tkinter instalado.
echo En Windows generalmente viene incluido con Python.
echo.

python reddit_scraper_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo ejecutar la interfaz grafica.
    echo.
    echo Posibles soluciones:
    echo 1. Verifica que Python este instalado
    echo 2. Instala tkinter: pip install tk
    echo 3. Usa el scraper de Scrapy: ../scraper_scrapy/run_scraper_scrapy.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Interfaz grafica cerrada.
echo Los archivos estan en la carpeta 'scraped_data'
echo.
echo ¿Quieres abrir la carpeta de resultados? (s/n)
set /p open_folder=""
if /i "%open_folder%"=="s" start "" "scraped_data"

cd ..
echo.
echo Presiona cualquier tecla para salir...
pause >nul
