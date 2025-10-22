#!/usr/bin/env python3
"""
Test funcional simple para verificar que la GUI funciona
"""

import tkinter as tk
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_scrapy_gui_simple import RedditScrapyGUI

def test_gui_basic():
    """Test básico de funcionalidad de GUI"""
    print("Iniciando test básico de GUI...")
    
    # Crear GUI
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana
    gui = RedditScrapyGUI(root)
    
    # Test 1: Inicialización
    print("Test 1: GUI se inicializa correctamente")
    assert gui.root is not None
    assert gui.subreddit_var.get() == "NMSCoordinateExchange"
    assert gui.max_posts_var.get() == "10"
    assert gui.max_comments_var.get() == "5"
    assert gui.sort_var.get() == "hot"
    assert gui.time_filter_var.get() == "all"
    assert gui.is_scraping == False
    
    # Test 2: Log message
    print("Test 2: log_message funciona")
    initial_count = int(gui.log_text.index('end-1c').split('.')[0])
    gui.log_message("Test message")
    final_count = int(gui.log_text.index('end-1c').split('.')[0])
    assert final_count == initial_count + 1
    
    # Test 3: Configuración
    print("Test 3: Configuración de parámetros")
    gui.subreddit_var.set("testsubreddit")
    gui.max_posts_var.set("5")
    gui.max_comments_var.set("3")
    assert gui.subreddit_var.get() == "testsubreddit"
    assert gui.max_posts_var.get() == "5"
    assert gui.max_comments_var.get() == "3"
    
    # Test 4: Estados de botones
    print("Test 4: Estados de botones")
    assert gui.start_button['state'] == 'normal'
    assert gui.stop_button['state'] == 'disabled'
    
    # Test 5: Completar scraping
    print("Test 5: Completar scraping")
    gui.is_scraping = True
    gui.scraping_completed()
    assert gui.is_scraping == False
    assert gui.start_button['state'] == 'normal'
    assert gui.stop_button['state'] == 'disabled'
    
    # Limpiar
    root.destroy()
    
    print("Todos los tests básicos pasaron!")

def test_real_scrapy_integration():
    """Test de integración real con Scrapy"""
    print("Iniciando test de integración real...")
    
    # Crear GUI
    root = tk.Tk()
    root.withdraw()
    gui = RedditScrapyGUI(root)
    
    # Configurar para test rápido
    gui.subreddit_var.set("NMSCoordinateExchange")
    gui.max_posts_var.set("2")  # Solo 2 posts para test rápido
    gui.max_comments_var.set("1")  # Solo 1 comentario por post
    gui.sort_var.set("hot")
    gui.time_filter_var.set("all")
    
    print("Configuración de test:")
    print(f"   Subreddit: {gui.subreddit_var.get()}")
    print(f"   Posts: {gui.max_posts_var.get()}")
    print(f"   Comentarios: {gui.max_comments_var.get()}")
    print(f"   Método: {gui.sort_var.get()}")
    print(f"   Filtro: {gui.time_filter_var.get()}")
    
    # Ejecutar scraping
    print("Ejecutando scraping...")
    gui.scrape_worker()
    
    # Verificar resultados
    print("Verificando resultados...")
    assert gui.is_scraping == False, "Scraping debería estar completado"
    
    # Verificar log
    log_content = gui.log_text.get(1.0, tk.END)
    assert "Reddit Scraper con Scrapy" in log_content, "Log debería contener mensaje de inicio"
    assert "Subreddit: r/NMSCoordinateExchange" in log_content, "Log debería contener subreddit"
    
    print(f"Log capturado ({len(log_content)} caracteres):")
    print("=" * 50)
    print(log_content[:500] + "..." if len(log_content) > 500 else log_content)
    print("=" * 50)
    
    # Verificar archivos generados
    results_dir = "reddit_scrappy/scraped_data_scrapy"
    if os.path.exists(results_dir):
        files = os.listdir(results_dir)
        print(f"Archivos generados: {len(files)}")
        for file in files:
            print(f"   - {file}")
        assert len(files) > 0, "Deberían generarse archivos de resultados"
    else:
        print("No se encontró carpeta de resultados")
    
    # Limpiar
    root.destroy()
    
    print("Test de integración completado!")

if __name__ == '__main__':
    try:
        test_gui_basic()
        print("\n" + "="*60 + "\n")
        test_real_scrapy_integration()
        print("\nTODOS LOS TESTS PASARON!")
    except Exception as e:
        print(f"Test falló: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
