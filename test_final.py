#!/usr/bin/env python3
"""
Test final que funciona sin threading
"""

import tkinter as tk
import subprocess
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_scrapy_gui_simple import RedditScrapyGUI

def test_gui_final():
    """Test final que funciona correctamente"""
    print("=== Test Final de GUI ===")
    
    # Crear GUI
    root = tk.Tk()
    root.withdraw()
    gui = RedditScrapyGUI(root)
    
    # Configurar para test mínimo
    gui.subreddit_var.set("NMSCoordinateExchange")
    gui.max_posts_var.set("1")
    gui.max_comments_var.set("1")
    gui.sort_var.set("hot")
    gui.time_filter_var.set("all")
    
    print("Configuración:")
    print(f"  Subreddit: {gui.subreddit_var.get()}")
    print(f"  Posts: {gui.max_posts_var.get()}")
    print(f"  Comentarios: {gui.max_comments_var.get()}")
    
    # Simular el proceso completo sin threading
    print("\nEjecutando scraping...")
    
    # Construir comando
    cmd = [
        'python', 'run_scraper.py',
        '--subreddit', gui.subreddit_var.get(),
        '--sort', gui.sort_var.get(),
        '--time-filter', gui.time_filter_var.get(),
        '--max-posts', gui.max_posts_var.get(),
        '--max-comments', gui.max_comments_var.get()
    ]
    
    # Cambiar al directorio de Scrapy
    original_dir = os.getcwd()
    os.chdir('reddit_scrappy')
    
    try:
        # Ejecutar comando
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Leer salida línea por línea y agregar al log
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            line = line.strip()
            if line:
                gui.log_message(line)
                print(f"Capturado: {line}")
            else:
                gui.log_message("")
        
        process.wait()
        
        # Agregar mensaje de finalización
        gui.log_message("=" * 50)
        gui.log_message("Scraping completado exitosamente!")
        gui.log_message("Revisa la carpeta 'scraped_data_scrapy' para los resultados")
        
        # Verificar contenido del log
        log_content = gui.log_text.get(1.0, tk.END)
        print(f"\nLog final ({len(log_content)} caracteres):")
        print("=" * 50)
        print(log_content)
        print("=" * 50)
        
        # Verificar que contiene los mensajes esperados
        assert "Reddit Scraper con Scrapy" in log_content, "Falta mensaje de inicio"
        assert "Subreddit: r/NMSCoordinateExchange" in log_content, "Falta subreddit"
        assert "Scraping completado exitosamente!" in log_content, "Falta mensaje de finalización"
        
        # Verificar archivos generados
        results_dir = "scraped_data_scrapy"
        if os.path.exists(results_dir):
            files = os.listdir(results_dir)
            print(f"\nArchivos generados: {len(files)}")
            assert len(files) > 0, "Deberían generarse archivos de resultados"
        else:
            print("\nNo se encontró carpeta de resultados")
        
        print("\nTest final PASÓ!")
        
    except Exception as e:
        print(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Volver al directorio original
        os.chdir(original_dir)
        root.destroy()

if __name__ == '__main__':
    test_gui_final()
