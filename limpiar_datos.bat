@echo off
chcp 65001 >nul
title Limpiar Datos Scrapeados - Reddit Scraper

echo.
echo ========================================
echo    LIMPIAR DATOS SCRAPEADOS
echo    (Borrar archivos e imagenes)
echo ========================================
echo.

echo ⚠️  ADVERTENCIA: Esto borrara TODOS los datos scrapeados
echo.
echo Archivos que se eliminaran:
echo - Datos JSON y CSV
echo - Imagenes descargadas
echo - Logs de Scrapy
echo.

set /p confirm="¿Estas seguro de que quieres continuar? (s/n): "
if /i not "%confirm%"=="s" (
    echo.
    echo Operacion cancelada.
    echo.
    pause
    exit /b 0
)

echo.
echo ========================================
echo    ELIMINANDO DATOS SCRAPEADOS
echo ========================================
echo.

echo 🗑️  Limpiando datos del scraper GUI...
if exist "reddit_newbie_scrapper\scraped_data" (
    echo    - Eliminando: reddit_newbie_scrapper\scraped_data
    rmdir /s /q "reddit_newbie_scrapper\scraped_data"
    echo    ✅ Datos del GUI eliminados
) else (
    echo    ℹ️  No hay datos del GUI para eliminar
)

echo.
echo 🗑️  Limpiando datos del scraper Scrapy...
if exist "reddit_scrappy\scraped_data_scrapy" (
    echo    - Eliminando: reddit_scrappy\scraped_data_scrapy
    rmdir /s /q "reddit_scrappy\scraped_data_scrapy"
    echo    ✅ Datos del Scrapy eliminados
) else (
    echo    ℹ️  No hay datos del Scrapy para eliminar
)

if exist "reddit_scrappy\scraped_data" (
    echo    - Eliminando: reddit_scrappy\scraped_data (remanente)
    rmdir /s /q "reddit_scrappy\scraped_data"
    echo    ✅ Carpeta remanente eliminada
)

echo.
echo 🗑️  Limpiando logs de Scrapy...
if exist "reddit_scrappy\reddit_scraper\scrapy.log" (
    echo    - Eliminando: reddit_scrappy\reddit_scraper\scrapy.log
    del /q "reddit_scrappy\reddit_scraper\scrapy.log"
    echo    ✅ Log de Scrapy eliminado
) else (
    echo    ℹ️  No hay log de Scrapy para eliminar
)

echo.
echo 🗑️  Limpiando logs adicionales...
if exist "reddit_scrappy\logs" (
    echo    - Eliminando: reddit_scrappy\logs
    rmdir /s /q "reddit_scrappy\logs"
    echo    ✅ Carpeta de logs eliminada
) else (
    echo    ℹ️  No hay carpeta de logs para eliminar
)

echo.
echo ========================================
echo    LIMPIEZA COMPLETADA
echo ========================================
echo.
echo ✅ Todos los datos scrapeados han sido eliminados
echo ✅ Puedes ejecutar el scraper de nuevo desde cero
echo.
echo Archivos .bat disponibles:
echo - run_gui.bat          (Scraper con GUI)
echo - run_scraper.bat      (Scraper Scrapy normal)
echo - run_scraper_debug.bat (Scraper Scrapy con logging)
echo.

set /p open_menu="¿Quieres abrir el menu principal? (s/n): "
if /i "%open_menu%"=="s" (
    echo.
    echo Abriendo menu principal...
    start "" "run_scraper_debug.bat"
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul
