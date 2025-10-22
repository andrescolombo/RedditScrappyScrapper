import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import json
import time
from datetime import datetime
import webbrowser

class RedditScrapyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Scraper - Scrapy GUI")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.is_scraping = False
        self.scraping_process = None
        
        # Configuración por defecto
        self.subreddit_var = tk.StringVar(value="NMSCoordinateExchange")
        self.max_posts_var = tk.StringVar(value="50")
        self.max_comments_var = tk.StringVar(value="10")
        self.sort_var = tk.StringVar(value="hot")
        self.time_filter_var = tk.StringVar(value="all")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Título principal
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🚀 Reddit Scraper - Scrapy GUI", 
            font=('Arial', 16, 'bold'),
            fg='white', 
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configuración
        config_frame = tk.LabelFrame(main_frame, text="⚙️ Configuración", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        config_frame.pack(fill='x', pady=5)
        
        # Subreddit
        tk.Label(config_frame, text="Subreddit:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        subreddit_entry = tk.Entry(config_frame, textvariable=self.subreddit_var, font=('Arial', 10), width=20)
        subreddit_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Método de ordenamiento
        tk.Label(config_frame, text="Método:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        sort_combo = ttk.Combobox(config_frame, textvariable=self.sort_var, values=['hot', 'new', 'top', 'rising'], width=10)
        sort_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Filtro de tiempo
        tk.Label(config_frame, text="Filtro:", font=('Arial', 10), bg='#f0f0f0').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        time_combo = ttk.Combobox(config_frame, textvariable=self.time_filter_var, values=['all', 'hour', 'day', 'week', 'month', 'year'], width=10)
        time_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Máximo posts
        tk.Label(config_frame, text="Max Posts:", font=('Arial', 10), bg='#f0f0f0').grid(row=1, column=2, sticky='w', padx=5, pady=5)
        posts_entry = tk.Entry(config_frame, textvariable=self.max_posts_var, font=('Arial', 10), width=10)
        posts_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Máximo comentarios
        tk.Label(config_frame, text="Max Comentarios:", font=('Arial', 10), bg='#f0f0f0').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        comments_entry = tk.Entry(config_frame, textvariable=self.max_comments_var, font=('Arial', 10), width=10)
        comments_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Botones de control
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill='x', pady=10)
        
        self.start_button = tk.Button(
            control_frame, 
            text="🚀 Iniciar Scraping", 
            command=self.start_scraping,
            font=('Arial', 12, 'bold'),
            bg='#27ae60', 
            fg='white',
            width=15,
            height=2
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            control_frame, 
            text="⏹️ Detener", 
            command=self.stop_scraping,
            font=('Arial', 12, 'bold'),
            bg='#e74c3c', 
            fg='white',
            width=15,
            height=2,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        self.clear_button = tk.Button(
            control_frame, 
            text="🗑️ Limpiar Datos", 
            command=self.clear_data,
            font=('Arial', 12, 'bold'),
            bg='#f39c12', 
            fg='white',
            width=15,
            height=2
        )
        self.clear_button.pack(side='left', padx=5)
        
        self.open_folder_button = tk.Button(
            control_frame, 
            text="📁 Abrir Carpeta", 
            command=self.open_results_folder,
            font=('Arial', 12, 'bold'),
            bg='#3498db', 
            fg='white',
            width=15,
            height=2
        )
        self.open_folder_button.pack(side='left', padx=5)
        
        # Barra de progreso
        progress_frame = tk.Frame(main_frame, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=5)
        
        tk.Label(progress_frame, text="Progreso:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=100)
        self.progress_bar.pack(fill='x', pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="0/0 posts (0%)", font=('Arial', 9), bg='#f0f0f0', fg='#666')
        self.progress_label.pack(anchor='w')
        
        # Panel de estadísticas en tiempo real
        stats_frame = tk.LabelFrame(main_frame, text="📊 Estadísticas en Tiempo Real", font=('Arial', 10, 'bold'), bg='#f0f0f0')
        stats_frame.pack(fill='x', pady=5)
        
        stats_inner = tk.Frame(stats_frame, bg='#f0f0f0')
        stats_inner.pack(fill='x', padx=5, pady=5)
        
        # Estadísticas en columnas
        self.posts_label = tk.Label(stats_inner, text="📝 Posts: 0/0", font=('Arial', 9), bg='#f0f0f0', fg='#2c3e50')
        self.posts_label.grid(row=0, column=0, padx=10, pady=2, sticky='w')
        
        self.images_label = tk.Label(stats_inner, text="🖼️ Imágenes: 0", font=('Arial', 9), bg='#f0f0f0', fg='#2c3e50')
        self.images_label.grid(row=0, column=1, padx=10, pady=2, sticky='w')
        
        self.comments_label = tk.Label(stats_inner, text="💬 Comentarios: 0", font=('Arial', 9), bg='#f0f0f0', fg='#2c3e50')
        self.comments_label.grid(row=0, column=2, padx=10, pady=2, sticky='w')
        
        self.time_label = tk.Label(stats_inner, text="⏱️ Tiempo: 0s", font=('Arial', 9), bg='#f0f0f0', fg='#2c3e50')
        self.time_label.grid(row=1, column=0, padx=10, pady=2, sticky='w')
        
        self.speed_label = tk.Label(stats_inner, text="📈 Velocidad: 0/min", font=('Arial', 9), bg='#f0f0f0', fg='#2c3e50')
        self.speed_label.grid(row=1, column=1, padx=10, pady=2, sticky='w')
        
        # Log de salida
        log_frame = tk.LabelFrame(main_frame, text="📋 Log de Scraping", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        log_frame.pack(fill='both', expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white'
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Estado
        self.status_label = tk.Label(
            main_frame, 
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
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0/0 posts (0%)")
        
        # Inicializar estadísticas
        self.posts_label.config(text="📝 Posts: 0/0")
        self.images_label.config(text="🖼️ Imágenes: 0")
        self.comments_label.config(text="💬 Comentarios: 0")
        self.time_label.config(text="⏱️ Tiempo: 0s")
        self.speed_label.config(text="📈 Velocidad: 0/min")
        
        self.status_label.config(text="🔄 Scraping en progreso...", fg='#f39c12')
        
        # Limpiar log
        self.log_text.delete(1.0, tk.END)
        
        # Iniciar scraping en hilo separado
        scraping_thread = threading.Thread(target=self.scrape_worker)
        scraping_thread.daemon = True
        scraping_thread.start()
        
    def scrape_worker(self):
        """Worker para el scraping"""
        try:
            self.log_message("🚀 Iniciando Reddit Scraper con Scrapy...")
            self.log_message(f"📊 Subreddit: r/{self.subreddit_var.get()}")
            self.log_message(f"📈 Método: {self.sort_var.get()}")
            self.log_message(f"⏰ Filtro: {self.time_filter_var.get()}")
            self.log_message(f"📝 Posts: {self.max_posts_var.get()}")
            self.log_message(f"💬 Comentarios: {self.max_comments_var.get()}")
            self.log_message("=" * 50)
            
            # Comando Scrapy directo para obtener logging detallado
            cmd = [
                'scrapy', 'crawl', 'reddit',
                '-a', f'subreddit={self.subreddit_var.get()}',
                '-a', f'sort={self.sort_var.get()}',
                '-a', f'time_filter={self.time_filter_var.get()}',
                '-a', f'max_posts={self.max_posts_var.get()}',
                '-a', f'max_comments={self.max_comments_var.get()}',
                '-L', 'INFO'
            ]
            
            # Cambiar al directorio de Scrapy
            os.chdir('reddit_scrappy/reddit_scraper')
            
            # Ejecutar comando
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.scraping_process = process
            
            # Variables para tracking
            posts_processed = 0
            total_posts = int(self.max_posts_var.get())
            total_images = 0
            total_comments = 0
            start_time = time.time()
            
            # Leer salida en tiempo real
            for line in iter(process.stdout.readline, ''):
                if not self.is_scraping:
                    process.terminate()
                    break
                
                line = line.strip()
                if line:
                    # Detectar progreso de posts
                    if "📝 Procesando post" in line:
                        posts_processed += 1
                        progress_percent = (posts_processed / total_posts) * 100
                        elapsed_time = time.time() - start_time
                        posts_per_minute = (posts_processed / elapsed_time) * 60 if elapsed_time > 0 else 0
                        
                        self.progress_bar['value'] = progress_percent
                        self.progress_label.config(text=f"{posts_processed}/{total_posts} posts ({progress_percent:.1f}%)")
                        
                        # Actualizar estadísticas en tiempo real
                        self.posts_label.config(text=f"📝 Posts: {posts_processed}/{total_posts}")
                        self.images_label.config(text=f"🖼️ Imágenes: {total_images}")
                        self.comments_label.config(text=f"💬 Comentarios: {total_comments}")
                        self.time_label.config(text=f"⏱️ Tiempo: {elapsed_time:.1f}s")
                        self.speed_label.config(text=f"📈 Velocidad: {posts_per_minute:.1f}/min")
                        
                        # Mostrar estadísticas detalladas
                        stats_msg = f"📊 Progreso: {posts_processed}/{total_posts} posts ({progress_percent:.1f}%) | "
                        stats_msg += f"🖼️ Imágenes: {total_images} | "
                        stats_msg += f"💬 Comentarios: {total_comments} | "
                        stats_msg += f"⏱️ Tiempo: {elapsed_time:.1f}s | "
                        stats_msg += f"📈 Velocidad: {posts_per_minute:.1f} posts/min"
                        self.log_message(stats_msg)
                    
                    # Contar imágenes encontradas
                    elif "🖼️ Imágenes encontradas:" in line:
                        try:
                            # Extraer número de imágenes del mensaje
                            import re
                            match = re.search(r'(\d+)', line)
                            if match:
                                images_count = int(match.group(1))
                                total_images += images_count
                        except:
                            pass
                        self.log_message(line)
                    
                    # Contar comentarios extraídos
                    elif "💬 Comentarios extraídos para" in line:
                        try:
                            # Extraer número de comentarios del mensaje
                            import re
                            match = re.search(r'(\d+)', line)
                            if match:
                                comments_count = int(match.group(1))
                                total_comments += comments_count
                        except:
                            pass
                        self.log_message(line)
                    
                    # Mostrar información detallada de cada post
                    elif any(keyword in line for keyword in ["📝 Procesando post", "📄 Título:", "✅ Post completado"]):
                        self.log_message(line)
                    
                    # Mostrar errores importantes
                    elif any(keyword in line for keyword in ["❌ Error", "⚠️ Warning", "ERROR", "WARNING"]):
                        self.log_message(line)
                    
                    # Mostrar información de inicio
                    elif any(keyword in line for keyword in ["🚀 Iniciando", "📡 Enviando request", "📥 Respuesta recibida", "📋 Encontrados"]):
                        self.log_message(line)
                
            process.wait()
            
            if self.is_scraping:
                total_time = time.time() - start_time
                posts_per_minute = (posts_processed / total_time) * 60 if total_time > 0 else 0
                
                self.log_message("=" * 50)
                self.log_message("✅ Scraping completado exitosamente!")
                self.log_message("=" * 50)
                self.log_message("📊 ESTADÍSTICAS FINALES:")
                self.log_message(f"📝 Posts procesados: {posts_processed}/{total_posts}")
                self.log_message(f"🖼️ Total imágenes: {total_images}")
                self.log_message(f"💬 Total comentarios: {total_comments}")
                self.log_message(f"⏱️ Tiempo total: {total_time:.1f} segundos")
                self.log_message(f"📈 Velocidad promedio: {posts_per_minute:.1f} posts/minuto")
                self.log_message("=" * 50)
                self.log_message("📁 Revisa la carpeta 'scraped_data_scrapy' para los resultados")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            
        finally:
            # Volver al directorio original
            os.chdir('../..')
            self.scraping_completed()
            
    def scraping_completed(self):
        """Scraping completado"""
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar['value'] = 100
        self.status_label.config(text="✅ Scraping completado", fg='#27ae60')
        
    def stop_scraping(self):
        """Detener el scraping"""
        if self.scraping_process:
            self.scraping_process.terminate()
        self.is_scraping = False
        self.log_message("⏹️ Scraping detenido por el usuario")
        self.scraping_completed()
        
    def clear_data(self):
        """Limpiar datos scrapeados"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar todos los datos scrapeados?"):
            try:
                self.log_message("🗑️ Limpiando datos scrapeados...")
                
                # Limpiar datos del GUI
                if os.path.exists('reddit_newbie_scrapper/scraped_data'):
                    import shutil
                    shutil.rmtree('reddit_newbie_scrapper/scraped_data')
                    self.log_message("✅ Datos del GUI eliminados")
                
                # Limpiar datos del Scrapy
                if os.path.exists('reddit_scrappy/scraped_data_scrapy'):
                    import shutil
                    shutil.rmtree('reddit_scrappy/scraped_data_scrapy')
                    self.log_message("✅ Datos del Scrapy eliminados")
                
                # Limpiar logs
                if os.path.exists('reddit_scrappy/reddit_scraper/scrapy.log'):
                    os.remove('reddit_scrappy/reddit_scraper/scrapy.log')
                    self.log_message("✅ Logs eliminados")
                
                self.log_message("🎉 Limpieza completada!")
                
            except Exception as e:
                self.log_message(f"❌ Error limpiando datos: {str(e)}")
                
    def open_results_folder(self):
        """Abrir carpeta de resultados"""
        try:
            results_path = os.path.abspath('reddit_scrappy/scraped_data_scrapy')
            if os.path.exists(results_path):
                webbrowser.open(results_path)
                self.log_message(f"📁 Abriendo carpeta: {results_path}")
            else:
                self.log_message("❌ No hay datos scrapeados aún")
        except Exception as e:
            self.log_message(f"❌ Error abriendo carpeta: {str(e)}")

def main():
    root = tk.Tk()
    app = RedditScrapyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
