@echo off
chcp 65001 >nul
title Reddit Scraper - Profesional (Scrapy)

echo.
echo ========================================
echo    REDDIT SCRAPER - PROFESIONAL
echo    (Framework Scrapy)
echo ========================================
echo.

cd reddit_scrappy

echo Configuracion rapida para r/NMSCoordinateExchange
echo.
set /p posts="Numero de posts a scrapear [50]: "
if "%posts%"=="" set posts=50

set /p comments="Comentarios por post [10]: "
if "%comments%"=="" set comments=10

echo.
echo Metodos disponibles:
echo 1. hot (popular)
echo 2. new (nuevos)  
echo 3. top (mas votados)
echo 4. rising (en alza)
echo.
set /p sort_choice="Selecciona metodo (1-4) [1]: "
if "%sort_choice%"=="" set sort_choice=1

if "%sort_choice%"=="1" set sort_method=hot
if "%sort_choice%"=="2" set sort_method=new
if "%sort_choice%"=="3" set sort_method=top
if "%sort_choice%"=="4" set sort_method=rising

set time_filter=all
if "%sort_method%"=="top" (
    echo.
    echo Filtros de tiempo para 'top':
    echo 1. all (todos los tiempos)
    echo 2. hour (ultima hora)
    echo 3. day (hoy)
    echo 4. week (esta semana)
    echo 5. month (este mes)
    echo 6. year (este año)
    echo.
    set /p time_choice="Selecciona filtro (1-6) [1]: "
    if "%time_choice%"=="" set time_choice=1
    
    if "%time_choice%"=="1" set time_filter=all
    if "%time_choice%"=="2" set time_filter=hour
    if "%time_choice%"=="3" set time_filter=day
    if "%time_choice%"=="4" set time_filter=week
    if "%time_choice%"=="5" set time_filter=month
    if "%time_choice%"=="6" set time_filter=year
)

echo.
echo ========================================
echo    INICIANDO SCRAPING PROFESIONAL
echo ========================================
echo Subreddit: r/NMSCoordinateExchange
echo Metodo: %sort_method%
echo Filtro: %time_filter%
echo Posts: %posts%
echo Comentarios: %comments%
echo ========================================
echo.

python run_scraper.py --subreddit NMSCoordinateExchange --sort %sort_method% --time-filter %time_filter% --max-posts %posts% --max-comments %comments%

echo.
echo ========================================
echo    SCRAPING COMPLETADO
echo ========================================
echo.
echo Los archivos estan en la carpeta 'scraped_data'
echo.
echo ¿Quieres abrir la carpeta de resultados? (s/n)
set /p open_folder=""
if /i "%open_folder%"=="s" start "" "scraped_data"

cd ..
echo.
echo Presiona cualquier tecla para salir...
pause >nul
