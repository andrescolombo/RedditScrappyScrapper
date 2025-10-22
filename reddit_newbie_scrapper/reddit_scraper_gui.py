#!/usr/bin/env python3
"""
Reddit Scraper con Interfaz Gráfica
Interfaz moderna con progreso en tiempo real, estadísticas y controles
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import webbrowser
from PIL import Image, ImageTk
import io

class RedditScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Scraper - Interfaz Gráfica")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables de estado
        self.is_scraping = False
        self.scraping_thread = None
        self.start_time = None
        self.scraped_data = {}
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Crear interfaz
        self.create_widgets()
        
        # Configurar estilo
        self.setup_styles()
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Reddit Scraper", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Subreddit
        ttk.Label(config_frame, text="Subreddit:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.subreddit_var = tk.StringVar(value="NMSCoordinateExchange")
        subreddit_entry = ttk.Entry(config_frame, textvariable=self.subreddit_var, width=30)
        subreddit_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Método de ordenamiento
        ttk.Label(config_frame, text="Ordenamiento:").grid(row=0, column=2, sticky=tk.W, padx=(10, 10))
        self.sort_var = tk.StringVar(value="hot")
        sort_combo = ttk.Combobox(config_frame, textvariable=self.sort_var, 
                                 values=["hot", "new", "top", "rising"], width=10)
        sort_combo.grid(row=0, column=3, sticky=tk.W)
        
        # Filtro de tiempo
        ttk.Label(config_frame, text="Período:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.time_filter_var = tk.StringVar(value="all")
        time_combo = ttk.Combobox(config_frame, textvariable=self.time_filter_var, 
                                 values=["all", "hour", "day", "week", "month", "year"], width=10)
        time_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Etiquetas descriptivas para los filtros de tiempo
        time_labels_frame = ttk.Frame(config_frame)
        time_labels_frame.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        time_labels = {
            "all": "Todos los tiempos",
            "hour": "Última hora", 
            "day": "Hoy",
            "week": "Esta semana",
            "month": "Este mes",
            "year": "Este año"
        }
        
        self.time_label_var = tk.StringVar(value=time_labels["all"])
        time_label = ttk.Label(time_labels_frame, textvariable=self.time_label_var, 
                              font=('Arial', 9), foreground='#666666')
        time_label.grid(row=0, column=0, sticky=tk.W, padx=(10, 0))
        
        # Actualizar etiqueta cuando cambie el filtro
        def update_time_label(*args):
            self.time_label_var.set(time_labels.get(self.time_filter_var.get(), "Todos los tiempos"))
        
        self.time_filter_var.trace('w', update_time_label)
        
        # Límites
        limits_frame = ttk.Frame(config_frame)
        limits_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(limits_frame, text="Posts:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.max_posts_var = tk.IntVar(value=50)
        posts_spin = ttk.Spinbox(limits_frame, from_=1, to=1000, textvariable=self.max_posts_var, width=10)
        posts_spin.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(limits_frame, text="Comentarios por post:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.max_comments_var = tk.IntVar(value=10)
        comments_spin = ttk.Spinbox(limits_frame, from_=1, to=100, textvariable=self.max_comments_var, width=10)
        comments_spin.grid(row=0, column=3, sticky=tk.W)
        
        # Opciones
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.download_images_var = tk.BooleanVar(value=True)
        images_check = ttk.Checkbutton(options_frame, text="Descargar imágenes", 
                                      variable=self.download_images_var)
        images_check.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.save_json_var = tk.BooleanVar(value=True)
        json_check = ttk.Checkbutton(options_frame, text="Guardar JSON", 
                                   variable=self.save_json_var)
        json_check.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.save_text_var = tk.BooleanVar(value=True)
        text_check = ttk.Checkbutton(options_frame, text="Guardar texto", 
                                    variable=self.save_text_var)
        text_check.grid(row=0, column=2, sticky=tk.W)
        
        # Frame de progreso
        progress_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Barra de progreso principal
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Información de progreso
        progress_info_frame = ttk.Frame(progress_frame)
        progress_info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        progress_info_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(progress_info_frame, text="Listo para comenzar")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_label = ttk.Label(progress_info_frame, text="0/0")
        self.progress_label.grid(row=0, column=1, sticky=tk.E)
        
        # Estadísticas en tiempo real
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Crear grid para estadísticas
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        # Estadísticas izquierda
        ttk.Label(stats_frame, text="Posts procesados:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.posts_count_label = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
        self.posts_count_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_frame, text="Comentarios extraídos:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.comments_count_label = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
        self.comments_count_label.grid(row=0, column=3, sticky=tk.W)
        
        # Estadísticas derecha
        ttk.Label(stats_frame, text="Imágenes descargadas:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.images_count_label = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
        self.images_count_label.grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_frame, text="Tiempo transcurrido:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10))
        self.time_label = ttk.Label(stats_frame, text="00:00", font=('Arial', 10, 'bold'))
        self.time_label.grid(row=1, column=3, sticky=tk.W)
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        # Botones
        self.start_button = ttk.Button(controls_frame, text="Iniciar Scraping", 
                                      command=self.start_scraping, style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(controls_frame, text="Detener", 
                                    command=self.stop_scraping, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.open_folder_button = ttk.Button(controls_frame, text="Abrir Carpeta", 
                                           command=self.open_output_folder, state='disabled')
        self.open_folder_button.grid(row=0, column=2, padx=(0, 10))
        
        # Log de actividad
        log_frame = ttk.LabelFrame(main_frame, text="Log de Actividad", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid principal
        main_frame.rowconfigure(5, weight=1)
    
    def setup_styles(self):
        """Configurar estilos de la interfaz"""
        style = ttk.Style()
        
        # Configurar tema
        style.theme_use('clam')
        
        # Estilo para botón principal
        style.configure('Accent.TButton', foreground='white', background='#0078d4')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
    
    def log_message(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, current, total, status=""):
        """Actualizar barra de progreso"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{current}/{total}")
        
        if status:
            self.status_label.config(text=status)
        
        self.root.update_idletasks()
    
    def update_stats(self, posts=0, comments=0, images=0):
        """Actualizar estadísticas"""
        self.posts_count_label.config(text=str(posts))
        self.comments_count_label.config(text=str(comments))
        self.images_count_label.config(text=str(images))
        
        # Actualizar tiempo transcurrido
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            self.time_label.config(text=str(elapsed).split('.')[0])
        
        self.root.update_idletasks()
    
    def start_scraping(self):
        """Iniciar el proceso de scraping"""
        if self.is_scraping:
            return
        
        # Validar entrada
        subreddit = self.subreddit_var.get().strip()
        if not subreddit:
            messagebox.showerror("Error", "Por favor ingresa un subreddit")
            return
        
        # Configurar estado
        self.is_scraping = True
        self.start_time = datetime.now()
        
        # Actualizar interfaz
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.open_folder_button.config(state='disabled')
        
        # Limpiar log
        self.log_text.delete(1.0, tk.END)
        
        # Mostrar información del filtro de tiempo
        time_filter = self.time_filter_var.get()
        sort_method = self.sort_var.get()
        
        if sort_method == "top" and time_filter != "all":
            time_labels = {
                "hour": "última hora",
                "day": "hoy", 
                "week": "esta semana",
                "month": "este mes",
                "year": "este año"
            }
            self.log_message(f"Iniciando scraping de r/{subreddit} - Posts más votados de {time_labels.get(time_filter, time_filter)}")
        else:
            self.log_message(f"Iniciando scraping de r/{subreddit} - Método: {sort_method}")
        
        # Iniciar thread de scraping
        self.scraping_thread = threading.Thread(target=self.scrape_worker, daemon=True)
        self.scraping_thread.start()
    
    def stop_scraping(self):
        """Detener el proceso de scraping"""
        self.is_scraping = False
        self.log_message("Deteniendo scraping...")
        
        # Actualizar interfaz
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Detenido")
    
    def scrape_worker(self):
        """Worker thread para el scraping"""
        try:
            subreddit = self.subreddit_var.get().strip()
            max_posts = self.max_posts_var.get()
            max_comments = self.max_comments_var.get()
            sort_method = self.sort_var.get()
            time_filter = self.time_filter_var.get()
            
            # Configurar headers
            headers = {
                'User-Agent': 'RedditScraper/1.0 by AndresColombo'
            }
            
            # URL del subreddit con filtro de tiempo
            if sort_method == "top" and time_filter != "all":
                url = f"https://www.reddit.com/r/{subreddit}/{sort_method}.json?limit={max_posts}&t={time_filter}"
            else:
                url = f"https://www.reddit.com/r/{subreddit}/{sort_method}.json?limit={max_posts}"
            
            self.log_message(f"Accediendo a: {url}")
            self.update_progress(0, max_posts, "Conectando a Reddit...")
            
            # Hacer request inicial
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.log_message(f"Error HTTP: {response.status_code}")
                return
            
            data = response.json()
            
            if 'data' not in data or 'children' not in data['data']:
                self.log_message("Error: Estructura de datos inesperada")
                return
            
            posts = data['data']['children']
            self.log_message(f"Encontrados {len(posts)} posts")
            
            # Datos del scrape
            scraped_data = {
                'subreddit': subreddit,
                'scrape_date': datetime.now().isoformat(),
                'sort_method': sort_method,
                'time_filter': time_filter,
                'total_posts': 0,
                'total_comments': 0,
                'total_images': 0,
                'posts': []
            }
            
            # Procesar cada post
            for i, post_wrapper in enumerate(posts):
                if not self.is_scraping:
                    break
                
                try:
                    post_data_raw = post_wrapper['data']
                    
                    self.log_message(f"Procesando post {i+1}: {post_data_raw['title'][:50]}...")
                    self.update_progress(i, len(posts), f"Procesando post {i+1}/{len(posts)}")
                    
                    # Datos básicos del post
                    post_data = {
                        'id': post_data_raw['id'],
                        'title': post_data_raw['title'],
                        'author': post_data_raw.get('author', '[deleted]'),
                        'created_utc': post_data_raw['created_utc'],
                        'created_date': datetime.fromtimestamp(post_data_raw['created_utc']).isoformat(),
                        'score': post_data_raw['score'],
                        'upvote_ratio': post_data_raw.get('upvote_ratio', 0),
                        'num_comments': post_data_raw['num_comments'],
                        'url': post_data_raw.get('url', ''),
                        'permalink': f"https://reddit.com{post_data_raw['permalink']}",
                        'is_self': post_data_raw['is_self'],
                        'selftext': post_data_raw.get('selftext', ''),
                        'subreddit': post_data_raw['subreddit'],
                        'flair_text': post_data_raw.get('link_flair_text', ''),
                        'nsfw': post_data_raw.get('over_18', False),
                        'locked': post_data_raw.get('locked', False),
                        'stickied': post_data_raw.get('stickied', False),
                        'domain': post_data_raw.get('domain', ''),
                        'thumbnail': post_data_raw.get('thumbnail', ''),
                        'preview': post_data_raw.get('preview', {}),
                        'comments': [],
                        'images_downloaded': []
                    }
                    
                    # Extraer comentarios
                    if post_data['num_comments'] > 0 and not post_data['locked']:
                        self.log_message(f"  Extrayendo comentarios...")
                        
                        comments_url = f"https://www.reddit.com{post_data_raw['permalink']}.json"
                        
                        try:
                            comments_response = requests.get(comments_url, headers=headers)
                            if comments_response.status_code == 200:
                                comments_data = comments_response.json()
                                
                                if len(comments_data) > 1:
                                    comments_list = comments_data[1]['data']['children']
                                    
                                    comments_count = 0
                                    for comment_wrapper in comments_list[:max_comments]:
                                        if not self.is_scraping:
                                            break
                                        
                                        try:
                                            comment_data_raw = comment_wrapper['data']
                                            
                                            comment_data = {
                                                'id': comment_data_raw['id'],
                                                'author': comment_data_raw.get('author', '[deleted]'),
                                                'body': comment_data_raw.get('body', ''),
                                                'score': comment_data_raw.get('score', 0),
                                                'created_utc': comment_data_raw['created_utc'],
                                                'created_date': datetime.fromtimestamp(comment_data_raw['created_utc']).isoformat(),
                                                'parent_id': comment_data_raw.get('parent_id', ''),
                                                'is_submitter': comment_data_raw.get('is_submitter', False),
                                                'stickied': comment_data_raw.get('stickied', False),
                                                'depth': comment_data_raw.get('depth', 0)
                                            }
                                            
                                            post_data['comments'].append(comment_data)
                                            comments_count += 1
                                            
                                        except Exception as e:
                                            self.log_message(f"    Error procesando comentario: {str(e)}")
                                            continue
                                    
                                    self.log_message(f"  Comentarios extraídos: {comments_count}")
                                    scraped_data['total_comments'] += comments_count
                            
                        except Exception as e:
                            self.log_message(f"  Error obteniendo comentarios: {str(e)}")
                    
                    # Descargar imágenes si está habilitado
                    if self.download_images_var.get():
                        self.log_message(f"  Descargando imágenes...")
                        images_downloaded = self.download_post_images(post_data_raw, post_data['id'])
                        post_data['images_downloaded'] = images_downloaded
                        scraped_data['total_images'] += len(images_downloaded)
                        if images_downloaded:
                            self.log_message(f"  Imágenes descargadas: {len(images_downloaded)}")
                        else:
                            self.log_message(f"  No se encontraron imágenes")
                    
                    scraped_data['posts'].append(post_data)
                    scraped_data['total_posts'] += 1
                    
                    # Actualizar estadísticas
                    self.update_stats(
                        scraped_data['total_posts'],
                        scraped_data['total_comments'],
                        scraped_data['total_images']
                    )
                    
                    # Pausa para ser respetuoso con la API
                    time.sleep(1)
                    
                except Exception as e:
                    self.log_message(f"Error procesando post: {str(e)}")
                    continue
            
            # Guardar datos
            if self.is_scraping:
                self.save_scraped_data(scraped_data)
            
        except Exception as e:
            self.log_message(f"Error durante el scraping: {str(e)}")
        finally:
            # Verificar si se completó exitosamente antes de cambiar el estado
            was_scraping = self.is_scraping
            
            # Restaurar interfaz
            self.is_scraping = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.open_folder_button.config(state='normal')
            
            if was_scraping:
                self.log_message("Scraping completado exitosamente!")
                self.update_progress(100, 100, "Completado")
            else:
                self.log_message("Scraping detenido por el usuario")
    
    def download_post_images(self, post_data_raw, post_id):
        """Descargar imágenes del post"""
        images_downloaded = []
        
        try:
            # Crear directorio para imágenes
            images_dir = Path("scraped_data/images")
            images_dir.mkdir(parents=True, exist_ok=True)
            
            post_dir = images_dir / post_id
            post_dir.mkdir(exist_ok=True)
            
            # URLs de imágenes a descargar
            image_urls = []
            
            # URL principal del post
            if self.is_image_url(post_data_raw.get('url', '')):
                image_urls.append(post_data_raw['url'])
            
            # Thumbnail
            thumbnail = post_data_raw.get('thumbnail', '')
            if thumbnail and thumbnail != 'self' and self.is_image_url(thumbnail):
                image_urls.append(thumbnail)
            
            # Preview images
            preview = post_data_raw.get('preview', {})
            if preview and 'images' in preview:
                for img in preview['images']:
                    if 'source' in img:
                        image_urls.append(img['source']['url'])
            
            # Descargar imágenes
            for i, url in enumerate(image_urls):
                if not self.is_scraping:
                    break
                
                try:
                    filename = f"image_{i+1}.jpg"
                    filepath = post_dir / filename
                    
                    if not filepath.exists():
                        response = requests.get(url, timeout=30)
                        if response.status_code == 200:
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            images_downloaded.append(str(filepath))
                            self.log_message(f"    Imagen descargada: {filename}")
                    
                except Exception as e:
                    self.log_message(f"    Error descargando imagen: {str(e)}")
                    continue
            
        except Exception as e:
            self.log_message(f"Error descargando imágenes: {str(e)}")
        
        return images_downloaded
    
    def is_image_url(self, url):
        """Verificar si una URL es una imagen"""
        if not url:
            return False
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        image_domains = {'i.redd.it', 'i.imgur.com', 'imgur.com'}
        
        # Verificar extensión
        if any(url.lower().endswith(ext) for ext in image_extensions):
            return True
        
        # Verificar dominio
        if any(domain in url.lower() for domain in image_domains):
            return True
        
        return False
    
    def save_scraped_data(self, data):
        """Guardar datos scrapeados"""
        try:
            # Crear directorio de salida
            output_dir = Path("scraped_data")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Guardar JSON
            if self.save_json_var.get():
                json_file = output_dir / f"{data['subreddit']}_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.log_message(f"Datos JSON guardados: {json_file}")
            
            # Guardar texto
            if self.save_text_var.get():
                txt_file = output_dir / f"{data['subreddit']}_{timestamp}.txt"
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(f"SCRAPER DE REDDIT - REPORTE COMPLETO\n")
                    f.write(f"=" * 50 + "\n\n")
                    f.write(f"Subreddit: r/{data['subreddit']}\n")
                    f.write(f"Fecha de scrape: {data['scrape_date']}\n")
                    f.write(f"Método de ordenamiento: {data['sort_method']}\n")
                    f.write(f"Filtro de tiempo: {data.get('time_filter', 'all')}\n")
                    f.write(f"Total de posts: {data['total_posts']}\n")
                    f.write(f"Total de comentarios: {data['total_comments']}\n")
                    f.write(f"Total de imágenes: {data['total_images']}\n")
                    f.write(f"\n" + "=" * 50 + "\n\n")
                    
                    for i, post in enumerate(data['posts'], 1):
                        f.write(f"POST #{i}\n")
                        f.write(f"-" * 30 + "\n")
                        f.write(f"Título: {post['title']}\n")
                        f.write(f"Autor: {post['author']}\n")
                        f.write(f"Fecha: {post['created_date']}\n")
                        f.write(f"Score: {post['score']} (Ratio: {post['upvote_ratio']})\n")
                        f.write(f"Comentarios: {post['num_comments']}\n")
                        f.write(f"URL: {post['url']}\n")
                        f.write(f"Permalink: {post['permalink']}\n")
                        f.write(f"NSFW: {'Sí' if post['nsfw'] else 'No'}\n")
                        f.write(f"Bloqueado: {'Sí' if post['locked'] else 'No'}\n")
                        f.write(f"Sticky: {'Sí' if post['stickied'] else 'No'}\n")
                        
                        if post['flair_text']:
                            f.write(f"Flair: {post['flair_text']}\n")
                        
                        if post['selftext']:
                            f.write(f"\nContenido del post:\n{post['selftext']}\n")
                        
                        if post['images_downloaded']:
                            f.write(f"\nImágenes descargadas: {len(post['images_downloaded'])}\n")
                            for img_path in post['images_downloaded']:
                                f.write(f"  📷 {img_path}\n")
                        
                        f.write(f"\nCOMENTARIOS ({len(post['comments'])}):\n")
                        f.write("-" * 20 + "\n")
                        
                        for j, comment in enumerate(post['comments'], 1):
                            f.write(f"  Comentario #{j}\n")
                            f.write(f"  Autor: {comment['author']}\n")
                            f.write(f"  Score: {comment['score']}\n")
                            f.write(f"  Fecha: {comment['created_date']}\n")
                            f.write(f"  Contenido: {comment['body'][:200]}...\n")
                            f.write(f"  ---\n")
                        
                        f.write(f"\n" + "=" * 50 + "\n\n")
                
                self.log_message(f"Reporte de texto guardado: {txt_file}")
            
            self.scraped_data = data
            
        except Exception as e:
            self.log_message(f"Error guardando datos: {str(e)}")
    
    def open_output_folder(self):
        """Abrir carpeta de salida"""
        try:
            output_dir = Path("scraped_data").absolute()
            webbrowser.open(f"file:///{output_dir}")
        except Exception as e:
            self.log_message(f"Error abriendo carpeta: {str(e)}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = RedditScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
