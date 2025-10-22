#!/usr/bin/env python3
"""
Tests unitarios para Reddit Scrapy GUI
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_scrapy_gui_simple import RedditScrapyGUI

class TestRedditScrapyGUI(unittest.TestCase):
    """Tests unitarios para la GUI de Scrapy"""
    
    def setUp(self):
        """Configurar test antes de cada prueba"""
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar ventana durante tests
        self.gui = RedditScrapyGUI(self.root)
    
    def tearDown(self):
        """Limpiar después de cada prueba"""
        self.root.destroy()
    
    def test_gui_initialization(self):
        """Test: GUI se inicializa correctamente"""
        self.assertIsNotNone(self.gui.root)
        self.assertIsNotNone(self.gui.subreddit_var)
        self.assertIsNotNone(self.gui.max_posts_var)
        self.assertIsNotNone(self.gui.max_comments_var)
        self.assertIsNotNone(self.gui.sort_var)
        self.assertIsNotNone(self.gui.time_filter_var)
        self.assertFalse(self.gui.is_scraping)
    
    def test_default_values(self):
        """Test: Valores por defecto son correctos"""
        self.assertEqual(self.gui.subreddit_var.get(), "NMSCoordinateExchange")
        self.assertEqual(self.gui.max_posts_var.get(), "10")
        self.assertEqual(self.gui.max_comments_var.get(), "5")
        self.assertEqual(self.gui.sort_var.get(), "hot")
        self.assertEqual(self.gui.time_filter_var.get(), "all")
    
    def test_log_message(self):
        """Test: log_message funciona correctamente"""
        initial_count = int(self.gui.log_text.index('end-1c').split('.')[0])
        self.gui.log_message("Test message")
        final_count = int(self.gui.log_text.index('end-1c').split('.')[0])
        self.assertEqual(final_count, initial_count + 1)
    
    def test_start_scraping_state(self):
        """Test: Estado inicial de scraping"""
        self.assertFalse(self.gui.is_scraping)
        self.assertEqual(self.gui.start_button['state'], 'normal')
        self.assertEqual(self.gui.stop_button['state'], 'disabled')
    
    @patch('subprocess.Popen')
    def test_scrape_worker_command(self, mock_popen):
        """Test: Comando de scraping se construye correctamente"""
        # Mock del proceso
        mock_process = Mock()
        mock_process.stdout.readline.side_effect = ['line1\n', 'line2\n', '']
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Configurar valores de test
        self.gui.subreddit_var.set("testsubreddit")
        self.gui.max_posts_var.set("5")
        self.gui.max_comments_var.set("3")
        self.gui.sort_var.set("new")
        self.gui.time_filter_var.set("day")
        
        # Ejecutar worker
        with patch('os.chdir'):
            self.gui.scrape_worker()
        
        # Verificar que se llamó con los parámetros correctos
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertIn('python', call_args)
        self.assertIn('run_scraper.py', call_args)
        self.assertIn('--subreddit', call_args)
        self.assertIn('testsubreddit', call_args)
        self.assertIn('--max-posts', call_args)
        self.assertIn('5', call_args)
    
    def test_input_validation(self):
        """Test: Validación de entrada"""
        # Test con valores válidos
        self.gui.subreddit_var.set("valid_subreddit")
        self.gui.max_posts_var.set("50")
        self.gui.max_comments_var.set("20")
        
        # No debería lanzar excepciones
        self.assertEqual(self.gui.subreddit_var.get(), "valid_subreddit")
        self.assertEqual(self.gui.max_posts_var.get(), "50")
        self.assertEqual(self.gui.max_comments_var.get(), "20")
    
    def test_scraping_completed_state(self):
        """Test: Estado después de completar scraping"""
        self.gui.is_scraping = True
        self.gui.scraping_completed()
        
        self.assertFalse(self.gui.is_scraping)
        self.assertEqual(self.gui.start_button['state'], 'normal')
        self.assertEqual(self.gui.stop_button['state'], 'disabled')
        self.assertEqual(self.gui.status_label['text'], "✅ Scraping completado")
    
    def test_stop_scraping(self):
        """Test: Detener scraping"""
        self.gui.is_scraping = True
        self.gui.scraping_process = Mock()
        
        self.gui.stop_scraping()
        
        self.assertFalse(self.gui.is_scraping)
        self.gui.scraping_process.terminate.assert_called_once()

class TestScrapyIntegration(unittest.TestCase):
    """Tests de integración con Scrapy"""
    
    def setUp(self):
        """Configurar test de integración"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.gui = RedditScrapyGUI(self.root)
    
    def tearDown(self):
        """Limpiar después de cada prueba"""
        self.root.destroy()
    
    @patch('subprocess.Popen')
    def test_scrapy_output_capture(self, mock_popen):
        """Test: Captura de salida de Scrapy"""
        # Simular salida de Scrapy
        scrapy_output = [
            "Reddit Scraper con Scrapy\n",
            "==================================================\n",
            "Subreddit: r/NMSCoordinateExchange\n",
            "Método: hot\n",
            "Filtro de tiempo: all\n",
            "Máximo posts: 3\n",
            "Máximo comentarios por post: 2\n",
            "==================================================\n",
            "Iniciando scraping...\n",
            "Comando: scrapy crawl reddit -a subreddit=NMSCoordinateExchange -a sort=hot -a time_filter=all -a max_posts=3 -a max_comments=2 -L INFO\n",
            "--------------------------------------------------\n",
            "--------------------------------------------------\n",
            "Scraping completado exitosamente!\n",
            ""
        ]
        
        mock_process = Mock()
        mock_process.stdout.readline.side_effect = scrapy_output
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Ejecutar worker
        with patch('os.chdir'):
            self.gui.scrape_worker()
        
        # Procesar eventos de tkinter para que se ejecuten los after()
        self.root.update()
        self.root.update_idletasks()
        
        # Verificar que se capturó la salida
        log_content = self.gui.log_text.get(1.0, tk.END)
        self.assertIn("🚀 Iniciando Reddit Scraper con Scrapy", log_content)
        self.assertIn("📊 Subreddit: r/NMSCoordinateExchange", log_content)
        self.assertIn("✅ Scraping completado exitosamente!", log_content)
    
    @patch('subprocess.Popen')
    def test_error_handling(self, mock_popen):
        """Test: Manejo de errores"""
        # Simular error
        mock_process = Mock()
        mock_process.stdout.readline.side_effect = Exception("Test error")
        mock_popen.return_value = mock_process
        
        # Ejecutar worker
        with patch('os.chdir'):
            self.gui.scrape_worker()
        
        # Procesar eventos de tkinter para que se ejecuten los after()
        self.root.update()
        self.root.update_idletasks()
        
        # Verificar que se manejó el error
        log_content = self.gui.log_text.get(1.0, tk.END)
        self.assertIn("❌ Error", log_content)

if __name__ == '__main__':
    # Configurar test runner
    unittest.main(verbosity=2)
