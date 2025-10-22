import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import time
from datetime import datetime

class RedditScrapyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Scraper - Scrapy GUI")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.is_scraping = False
        self.scraping_process = None
        
        # Configuración por defecto
        self.subreddit_var = tk.StringVar(value="NMSCoordinateExchange")
        self.max_posts_var = tk.StringVar(value="10")
        self.max_comments_var = tk.StringVar(value="5")
        self.sort_var = tk.StringVar(value="hot")
        self.time_filter_var = tk.StringVar(value="all")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Título
        title_label = tk.Label(
            self.root, 
            text="🚀 Reddit Scraper - Scrapy GUI", 
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # Frame de configuración
        config_frame = tk.LabelFrame(self.root, text="⚙️ Configuración", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        config_frame.pack(fill='x', padx=10, pady=5)
        
        # Subreddit
        tk.Label(config_frame, text="Subreddit:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        tk.Entry(config_frame, textvariable=self.subreddit_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        # Método
        tk.Label(config_frame, text="Método:", bg='#f0f0f0').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        ttk.Combobox(config_frame, textvariable=self.sort_var, values=['best', 'hot', 'new', 'top', 'rising'], width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # Filtro de tiempo (solo para Top)
        tk.Label(config_frame, text="Filtro (solo Top):", bg='#f0f0f0').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(config_frame, textvariable=self.time_filter_var, values=['all', 'hour', 'day', 'week', 'month', 'year'], width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Max posts
        tk.Label(config_frame, text="Max Posts:", bg='#f0f0f0').grid(row=1, column=2, sticky='w', padx=5, pady=5)
        tk.Entry(config_frame, textvariable=self.max_posts_var, width=10).grid(row=1, column=3, padx=5, pady=5)
        
        # Max comentarios
        tk.Label(config_frame, text="Max Comentarios:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        tk.Entry(config_frame, textvariable=self.max_comments_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        # Botones
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.start_button = tk.Button(
            button_frame, 
            text="🚀 Iniciar Scraping", 
            command=self.start_scraping,
            font=('Arial', 12, 'bold'),
            bg='#27ae60', 
            fg='white',
            width=15
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            button_frame, 
            text="⏹️ Detener", 
            command=self.stop_scraping,
            font=('Arial', 12, 'bold'),
            bg='#e74c3c', 
            fg='white',
            width=15,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        
        # Log
        log_frame = tk.LabelFrame(self.root, text="📋 Log de Scraping", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Estado
        self.status_label = tk.Label(
            self.root, 
            text="🟢 Listo para scrapear", 
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            fg='#27ae60'
        )
        self.status_label.pack(pady=5)
        
    def log_message(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def start_scraping(self):
        """Iniciar el scraping"""
        if self.is_scraping:
            return
            
        self.is_scraping = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()
        self.status_label.config(text="🔄 Scraping en progreso...", fg='#f39c12')
        
        # Limpiar log
        self.log_text.delete(1.0, tk.END)
        
        # Iniciar scraping en hilo separado
        scraping_thread = threading.Thread(target=self.scrape_worker)
        scraping_thread.daemon = True
        scraping_thread.start()
        
    def scrape_worker(self):
        """Worker para el scraping"""
        original_dir = os.getcwd()  # Mover al inicio para evitar UnboundLocalError
        
        try:
            # Usar after() para actualizar GUI desde hilo
            self.root.after(0, lambda: self.log_message("🚀 Iniciando Reddit Scraper con Scrapy..."))
            self.root.after(0, lambda: self.log_message(f"📊 Subreddit: r/{self.subreddit_var.get()}"))
            self.root.after(0, lambda: self.log_message(f"📈 Método: {self.sort_var.get()}"))
            self.root.after(0, lambda: self.log_message(f"⏰ Filtro: {self.time_filter_var.get()}"))
            self.root.after(0, lambda: self.log_message(f"📝 Posts: {self.max_posts_var.get()}"))
            self.root.after(0, lambda: self.log_message(f"💬 Comentarios: {self.max_comments_var.get()}"))
            self.root.after(0, lambda: self.log_message("=" * 50))
            
            # Usar el script run_scraper.py pero capturar la salida completa
            cmd = [
                'python', 'run_scraper.py',
                '--subreddit', self.subreddit_var.get(),
                '--sort', self.sort_var.get(),
                '--time-filter', self.time_filter_var.get(),
                '--max-posts', self.max_posts_var.get(),
                '--max-comments', self.max_comments_var.get()
            ]
            
            # Cambiar al directorio de Scrapy
            os.chdir('reddit_scrappy')
            
            # Ejecutar comando
            self.root.after(0, lambda: self.log_message(f"DEBUG: Ejecutando comando: {' '.join(cmd)}"))
            self.root.after(0, lambda: self.log_message(f"DEBUG: Directorio actual: {os.getcwd()}"))
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.scraping_process = process
            self.root.after(0, lambda: self.log_message("DEBUG: Proceso iniciado, esperando salida..."))
            
            # Leer salida en tiempo real
            while True:
                if not self.is_scraping:
                    process.terminate()
                    break
                
                line = process.stdout.readline()
                if not line:  # No hay más líneas
                    break
                
                line = line.strip()
                if line:
                    # Usar after_idle para mejor rendimiento
                    self.root.after_idle(lambda msg=line: self.log_message(msg))
                else:
                    self.root.after_idle(lambda: self.log_message(""))  # Línea vacía
                
            process.wait()
            
            if self.is_scraping:
                self.root.after(0, lambda: self.log_message("=" * 50))
                self.root.after(0, lambda: self.log_message("✅ Scraping completado exitosamente!"))
                self.root.after(0, lambda: self.log_message("📁 Revisa la carpeta 'scraped_data_scrapy' para los resultados"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Error: {str(e)}"))
            import traceback
            self.root.after(0, lambda: self.log_message(f"❌ Traceback: {traceback.format_exc()}"))
            
        finally:
            # Volver al directorio original
            os.chdir(original_dir)
            self.root.after(0, self.scraping_completed)
            
    def scraping_completed(self):
        """Scraping completado"""
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.status_label.config(text="✅ Scraping completado", fg='#27ae60')
        
    def stop_scraping(self):
        """Detener el scraping"""
        if self.scraping_process:
            self.scraping_process.terminate()
        self.is_scraping = False
        self.log_message("⏹️ Scraping detenido por el usuario")
        self.scraping_completed()

def main():
    root = tk.Tk()
    app = RedditScrapyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
