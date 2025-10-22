@echo off
chcp 65001 >nul
title Limpiar Datos - RAPIDO

echo.
echo ========================================
echo    LIMPIEZA RAPIDA DE DATOS
echo ========================================
echo.

echo 🗑️  Eliminando datos scrapeados...

if exist "reddit_newbie_scrapper\scraped_data" rmdir /s /q "reddit_newbie_scrapper\scraped_data"
if exist "reddit_scrappy\scraped_data_scrapy" rmdir /s /q "reddit_scrappy\scraped_data_scrapy"
if exist "reddit_scrappy\scraped_data" rmdir /s /q "reddit_scrappy\scraped_data"
if exist "reddit_scrappy\reddit_scraper\scrapy.log" del /q "reddit_scrappy\reddit_scraper\scrapy.log"
if exist "reddit_scrappy\logs" rmdir /s /q "reddit_scrappy\logs"

echo.
echo ✅ Limpieza completada!
echo.
echo Presiona cualquier tecla para salir...
pause >nul
