#!/usr/bin/env python3
"""
Test de integración real para Reddit Scrapy GUI
"""

import unittest
import tkinter as tk
import subprocess
import os
import time
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_scrapy_gui_simple import RedditScrapyGUI

class TestRealIntegration(unittest.TestCase):
    """Tests de integración real con Scrapy"""
    
    def setUp(self):
        """Configurar test de integración"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.gui = RedditScrapyGUI(self.root)
    
    def tearDown(self):
        """Limpiar después de cada prueba"""
        self.root.destroy()
    
    def test_real_scrapy_execution(self):
        """Test: Ejecución real de Scrapy con 3 posts"""
        # Configurar para test rápido
        self.gui.subreddit_var.set("NMSCoordinateExchange")
        self.gui.max_posts_var.set("3")
        self.gui.max_comments_var.set("2")
        self.gui.sort_var.set("hot")
        self.gui.time_filter_var.set("all")
        
        # Ejecutar scraping
        self.gui.scrape_worker()
        
        # Verificar que se completó
        self.assertFalse(self.gui.is_scraping)
        
        # Verificar que hay contenido en el log
        log_content = self.gui.log_text.get(1.0, tk.END)
        self.assertIn("Iniciando Reddit Scraper", log_content)
        self.assertIn("Subreddit: r/NMSCoordinateExchange", log_content)
        
        # Verificar que se generaron archivos
        results_dir = "reddit_scrappy/scraped_data_scrapy"
        if os.path.exists(results_dir):
            files = os.listdir(results_dir)
            self.assertTrue(len(files) > 0, "No se generaron archivos de resultados")
    
    def test_error_handling_real(self):
        """Test: Manejo de errores con subreddit inexistente"""
        # Configurar subreddit que no existe
        self.gui.subreddit_var.set("subreddit_que_no_existe_12345")
        self.gui.max_posts_var.set("1")
        self.gui.max_comments_var.set("1")
        
        # Ejecutar scraping
        self.gui.scrape_worker()
        
        # Verificar que se manejó el error
        self.assertFalse(self.gui.is_scraping)
        log_content = self.gui.log_text.get(1.0, tk.END)
        # Debería haber algún indicador de error o finalización
        self.assertTrue(len(log_content) > 100, "Log muy corto, posible error")
    
    def test_cancellation(self):
        """Test: Cancelación manual del scraping"""
        # Configurar scraping largo
        self.gui.subreddit_var.set("NMSCoordinateExchange")
        self.gui.max_posts_var.set("50")
        self.gui.max_comments_var.set("10")
        
        # Iniciar scraping en hilo separado
        import threading
        scraping_thread = threading.Thread(target=self.gui.scrape_worker)
        scraping_thread.daemon = True
        scraping_thread.start()
        
        # Esperar un poco y cancelar
        time.sleep(2)
        self.gui.stop_scraping()
        
        # Verificar que se canceló
        self.assertFalse(self.gui.is_scraping)
        log_content = self.gui.log_text.get(1.0, tk.END)
        self.assertIn("detenido por el usuario", log_content)

if __name__ == '__main__':
    # Configurar test runner
    unittest.main(verbosity=2)
