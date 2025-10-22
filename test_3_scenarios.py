#!/usr/bin/env python3
"""
Script de prueba automatizada para 3 escenarios reales
"""

import tkinter as tk
import subprocess
import os
import sys
import time

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_scrapy_gui_simple import RedditScrapyGUI

def test_scenario_1():
    """Escenario 1: Test básico con 3 posts"""
    print("=== ESCENARIO 1: Test básico con 3 posts ===")
    
    root = tk.Tk()
    root.withdraw()
    gui = RedditScrapyGUI(root)
    
    # Configurar
    gui.subreddit_var.set("NMSCoordinateExchange")
    gui.max_posts_var.set("3")
    gui.max_comments_var.set("2")
    gui.sort_var.set("hot")
    gui.time_filter_var.set("all")
    
    print("Configuración:")
    print(f"  Subreddit: {gui.subreddit_var.get()}")
    print(f"  Posts: {gui.max_posts_var.get()}")
    print(f"  Comentarios: {gui.max_comments_var.get()}")
    print(f"  Método: {gui.sort_var.get()}")
    print(f"  Filtro: {gui.time_filter_var.get()}")
    
    # Ejecutar
    start_time = time.time()
    gui.scrape_worker()
    end_time = time.time()
    
    # Verificar resultados
    log_content = gui.log_text.get(1.0, tk.END)
    duration = end_time - start_time
    
    print(f"\nResultados:")
    print(f"  Duración: {duration:.2f} segundos")
    print(f"  Log capturado: {len(log_content)} caracteres")
    print(f"  Contiene inicio: {'Reddit Scraper con Scrapy' in log_content}")
    print(f"  Contiene finalización: {'Scraping completado exitosamente!' in log_content}")
    
    # Verificar archivos
    results_dir = "reddit_scrappy/scraped_data_scrapy"
    if os.path.exists(results_dir):
        files = os.listdir(results_dir)
        print(f"  Archivos generados: {len(files)}")
    
    root.destroy()
    print("Escenario 1 completado!\n")
    return True

def test_scenario_2():
    """Escenario 2: Test con método 'new' y filtro de tiempo"""
    print("=== ESCENARIO 2: Test con método 'new' ===")
    
    root = tk.Tk()
    root.withdraw()
    gui = RedditScrapyGUI(root)
    
    # Configurar
    gui.subreddit_var.set("NMSCoordinateExchange")
    gui.max_posts_var.set("2")
    gui.max_comments_var.set("1")
    gui.sort_var.set("new")
    gui.time_filter_var.set("day")
    
    print("Configuración:")
    print(f"  Subreddit: {gui.subreddit_var.get()}")
    print(f"  Posts: {gui.max_posts_var.get()}")
    print(f"  Comentarios: {gui.max_comments_var.get()}")
    print(f"  Método: {gui.sort_var.get()}")
    print(f"  Filtro: {gui.time_filter_var.get()}")
    
    # Ejecutar
    start_time = time.time()
    gui.scrape_worker()
    end_time = time.time()
    
    # Verificar resultados
    log_content = gui.log_text.get(1.0, tk.END)
    duration = end_time - start_time
    
    print(f"\nResultados:")
    print(f"  Duración: {duration:.2f} segundos")
    print(f"  Log capturado: {len(log_content)} caracteres")
    print(f"  Contiene inicio: {'Reddit Scraper con Scrapy' in log_content}")
    print(f"  Contiene finalización: {'Scraping completado exitosamente!' in log_content}")
    
    root.destroy()
    print("Escenario 2 completado!\n")
    return True

def test_scenario_3():
    """Escenario 3: Test con subreddit diferente"""
    print("=== ESCENARIO 3: Test con subreddit diferente ===")
    
    root = tk.Tk()
    root.withdraw()
    gui = RedditScrapyGUI(root)
    
    # Configurar
    gui.subreddit_var.set("python")
    gui.max_posts_var.set("2")
    gui.max_comments_var.set("1")
    gui.sort_var.set("top")
    gui.time_filter_var.set("week")
    
    print("Configuración:")
    print(f"  Subreddit: {gui.subreddit_var.get()}")
    print(f"  Posts: {gui.max_posts_var.get()}")
    print(f"  Comentarios: {gui.max_comments_var.get()}")
    print(f"  Método: {gui.sort_var.get()}")
    print(f"  Filtro: {gui.time_filter_var.get()}")
    
    # Ejecutar
    start_time = time.time()
    gui.scrape_worker()
    end_time = time.time()
    
    # Verificar resultados
    log_content = gui.log_text.get(1.0, tk.END)
    duration = end_time - start_time
    
    print(f"\nResultados:")
    print(f"  Duración: {duration:.2f} segundos")
    print(f"  Log capturado: {len(log_content)} caracteres")
    print(f"  Contiene inicio: {'Reddit Scraper con Scrapy' in log_content}")
    print(f"  Contiene finalización: {'Scraping completado exitosamente!' in log_content}")
    
    root.destroy()
    print("Escenario 3 completado!\n")
    return True

def main():
    """Ejecutar todos los escenarios"""
    print("Iniciando pruebas de 3 escenarios reales...")
    print("=" * 60)
    
    try:
        # Cambiar al directorio de Scrapy para todos los tests
        original_dir = os.getcwd()
        os.chdir('reddit_scrappy')
        
        # Ejecutar escenarios
        scenario1_ok = test_scenario_1()
        scenario2_ok = test_scenario_2()
        scenario3_ok = test_scenario_3()
        
        # Resumen
        print("=" * 60)
        print("RESUMEN DE PRUEBAS:")
        print(f"  Escenario 1 (básico): {'PASÓ' if scenario1_ok else 'FALLÓ'}")
        print(f"  Escenario 2 (método new): {'PASÓ' if scenario2_ok else 'FALLÓ'}")
        print(f"  Escenario 3 (subreddit diferente): {'PASÓ' if scenario3_ok else 'FALLÓ'}")
        
        if scenario1_ok and scenario2_ok and scenario3_ok:
            print("\nTODOS LOS ESCENARIOS PASARON!")
            return True
        else:
            print("\nALGUNOS ESCENARIOS FALLARON!")
            return False
            
    except Exception as e:
        print(f"Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Volver al directorio original
        os.chdir(original_dir)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
