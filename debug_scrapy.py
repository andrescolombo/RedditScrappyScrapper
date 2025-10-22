#!/usr/bin/env python3
"""
Test de depuración para ver qué está pasando con la captura de salida
"""

import tkinter as tk
import subprocess
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_scrapy_gui_simple import RedditScrapyGUI

def debug_scrapy_output():
    """Debug: Ver qué está pasando con la salida de Scrapy"""
    print("=== DEBUG: Captura de salida de Scrapy ===")
    
    # Crear GUI
    root = tk.Tk()
    root.withdraw()
    gui = RedditScrapyGUI(root)
    
    # Configurar para test mínimo
    gui.subreddit_var.set("NMSCoordinateExchange")
    gui.max_posts_var.set("1")  # Solo 1 post
    gui.max_comments_var.set("1")  # Solo 1 comentario
    gui.sort_var.set("hot")
    gui.time_filter_var.get()
    
    print("Configuración:")
    print(f"  Subreddit: {gui.subreddit_var.get()}")
    print(f"  Posts: {gui.max_posts_var.get()}")
    print(f"  Comentarios: {gui.max_comments_var.get()}")
    print(f"  Método: {gui.sort_var.get()}")
    print(f"  Filtro: {gui.time_filter_var.get()}")
    
    # Construir comando
    cmd = [
        'python', 'run_scraper.py',
        '--subreddit', gui.subreddit_var.get(),
        '--sort', gui.sort_var.get(),
        '--time-filter', gui.time_filter_var.get(),
        '--max-posts', gui.max_posts_var.get(),
        '--max-comments', gui.max_comments_var.get()
    ]
    
    print(f"\nComando a ejecutar: {' '.join(cmd)}")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Cambiar al directorio de Scrapy
    original_dir = os.getcwd()
    os.chdir('reddit_scrappy')
    print(f"Directorio después de chdir: {os.getcwd()}")
    
    try:
        print("\n=== Ejecutando comando ===")
        
        # Ejecutar comando y capturar salida
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("Proceso iniciado, PID:", process.pid)
        
        # Leer salida línea por línea
        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line:
                output_lines.append(line)
                print(f"LÍNEA CAPTURADA: {line}")
            else:
                print("LÍNEA VACÍA")
        
        # Esperar a que termine
        return_code = process.wait()
        print(f"\nProceso terminado con código: {return_code}")
        
        print(f"\n=== RESUMEN ===")
        print(f"Total de líneas capturadas: {len(output_lines)}")
        print("Primeras 10 líneas:")
        for i, line in enumerate(output_lines[:10]):
            print(f"  {i+1}: {line}")
        
        if len(output_lines) > 10:
            print(f"  ... y {len(output_lines) - 10} líneas más")
        
        # Verificar si se generaron archivos
        results_dir = "scraped_data_scrapy"
        if os.path.exists(results_dir):
            files = os.listdir(results_dir)
            print(f"\nArchivos generados en {results_dir}: {len(files)}")
            for file in files:
                print(f"  - {file}")
        else:
            print(f"\nNo se encontró carpeta {results_dir}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Volver al directorio original
        os.chdir(original_dir)
        root.destroy()

if __name__ == '__main__':
    debug_scrapy_output()
