#!/usr/bin/env python3
"""
Script para ejecutar el Reddit Scraper con Scrapy
Interfaz simple para configurar y ejecutar el scraping
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse
from datetime import datetime


def run_scraper(subreddit, sort='hot', time_filter='all', max_posts=100, max_comments=10):
    """Ejecutar el scraper de Reddit con Scrapy"""
    
    print("Reddit Scraper con Scrapy")
    print("=" * 50)
    print(f"Subreddit: r/{subreddit}")
    print(f"Método: {sort}")
    print(f"Filtro de tiempo: {time_filter}")
    print(f"Máximo posts: {max_posts}")
    print(f"Máximo comentarios por post: {max_comments}")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto Scrapy
    scrapy_dir = Path("reddit_scraper")
    if not scrapy_dir.exists():
        print("Error: Directorio del proyecto Scrapy no encontrado")
        return False
    
    # Crear directorio de salida
    output_dir = Path("scraped_data")
    output_dir.mkdir(exist_ok=True)
    
    # Comando de Scrapy
    cmd = [
        'scrapy', 'crawl', 'reddit',
        '-a', f'subreddit={subreddit}',
        '-a', f'sort={sort}',
        '-a', f'time_filter={time_filter}',
        '-a', f'max_posts={max_posts}',
        '-a', f'max_comments={max_comments}',
        '-L', 'INFO'
    ]
    
    try:
        # Cambiar al directorio de Scrapy
        os.chdir(scrapy_dir)
        
        print("Iniciando scraping...")
        print(f"Comando: {' '.join(cmd)}")
        print("-" * 50)
        print("")  # Línea vacía para separar
        
        # Ejecutar Scrapy y capturar salida en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Imprimir salida en tiempo real
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
        
        # Esperar a que termine
        return_code = process.wait()
        
        print("")  # Línea vacía para separar
        if return_code == 0:
            print("-" * 50)
            print("Scraping completado exitosamente!")
            
            # Mostrar archivos generados
            output_path = Path("../scraped_data")
            if output_path.exists():
                files = list(output_path.glob("*"))
                if files:
                    print("\nArchivos generados:")
                    for file in files:
                        if file.is_file():
                            size = file.stat().st_size
                            print(f"  Archivo: {file.name} ({size:,} bytes)")
                        elif file.is_dir():
                            count = len(list(file.rglob("*")))
                            print(f"  Carpeta: {file.name}/ ({count} archivos)")
            
            return True
        else:
            print("-" * 50)
            print("Error durante el scraping")
            return False
            
    except Exception as e:
        print(f"Error ejecutando Scrapy: {str(e)}")
        return False
    finally:
        # Volver al directorio original
        os.chdir("..")


def interactive_mode():
    """Modo interactivo para configurar el scraper"""
    print("Reddit Scraper - Modo Interactivo")
    print("=" * 40)
    
    # Configuración por defecto
    subreddit = input(f"Subreddit [NMSCoordinateExchange]: ").strip() or "NMSCoordinateExchange"
    
    print("\nMétodos de ordenamiento:")
    print("1. hot (popular)")
    print("2. new (nuevos)")
    print("3. top (más votados)")
    print("4. rising (en alza)")
    
    sort_choice = input("Método [1]: ").strip() or "1"
    sort_map = {"1": "hot", "2": "new", "3": "top", "4": "rising"}
    sort = sort_map.get(sort_choice, "hot")
    
    # Filtro de tiempo (solo para 'top')
    time_filter = "all"
    if sort == "top":
        print("\nFiltros de tiempo (solo para 'top'):")
        print("1. all (todos los tiempos)")
        print("2. hour (última hora)")
        print("3. day (hoy)")
        print("4. week (esta semana)")
        print("5. month (este mes)")
        print("6. year (este año)")
        
        time_choice = input("Filtro de tiempo [1]: ").strip() or "1"
        time_map = {"1": "all", "2": "hour", "3": "day", "4": "week", "5": "month", "6": "year"}
        time_filter = time_map.get(time_choice, "all")
    
    # Límites
    max_posts = input("Máximo posts [100]: ").strip() or "100"
    max_comments = input("Máximo comentarios por post [10]: ").strip() or "10"
    
    try:
        max_posts = int(max_posts)
        max_comments = int(max_comments)
    except ValueError:
        print("Error: Valores numéricos inválidos")
        return False
    
    # Ejecutar scraping
    return run_scraper(subreddit, sort, time_filter, max_posts, max_comments)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Reddit Scraper con Scrapy')
    parser.add_argument('--subreddit', '-s', default='NMSCoordinateExchange',
                       help='Subreddit a scrapear (default: NMSCoordinateExchange)')
    parser.add_argument('--sort', choices=['hot', 'new', 'top', 'rising'], default='hot',
                       help='Método de ordenamiento (default: hot)')
    parser.add_argument('--time-filter', '-t', choices=['all', 'hour', 'day', 'week', 'month', 'year'],
                       default='all', help='Filtro de tiempo (default: all)')
    parser.add_argument('--max-posts', '-p', type=int, default=100,
                       help='Máximo número de posts (default: 100)')
    parser.add_argument('--max-comments', '-c', type=int, default=10,
                       help='Máximo comentarios por post (default: 10)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Modo interactivo')
    
    args = parser.parse_args()
    
    if args.interactive:
        success = interactive_mode()
    else:
        success = run_scraper(
            args.subreddit, 
            args.sort, 
            args.time_filter, 
            args.max_posts, 
            args.max_comments
        )
    
    if success:
        print("\nScraping completado!")
        print("Los archivos estan en la carpeta 'scraped_data'")
    else:
        print("\nEl scraping fallo")
        sys.exit(1)


if __name__ == "__main__":
    main()
