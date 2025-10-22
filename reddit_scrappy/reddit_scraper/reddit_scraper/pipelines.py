import scrapy
from scrapy.exceptions import DropItem
import os
from pathlib import Path
import re
import requests
from urllib.parse import urlparse


class RedditImagesPipeline:
    """Pipeline personalizado para descargar imágenes de Reddit usando requests"""
    
    def __init__(self, images_store):
        self.images_store = images_store
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            images_store=crawler.settings.get('IMAGES_STORE')
        )
    
    def process_item(self, item, spider):
        """Procesar item y descargar imágenes"""
        if 'image_urls' not in item or not item['image_urls']:
            item['images'] = []
            return item
        
        image_paths = []
        
        for idx, image_url in enumerate(item['image_urls']):
            try:
                # Limpiar título para nombre de archivo
                post_title = item.get('title', 'untitled')
                clean_title = re.sub(r'[<>:"/\\|?*]', '', post_title)
                clean_title = clean_title[:100].strip()
                clean_title = clean_title.replace(' ', '_')
                
                # Obtener extensión de la URL
                parsed_url = urlparse(image_url)
                url_path = parsed_url.path
                extension = url_path.split('.')[-1] if '.' in url_path else 'jpg'
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
                if extension.lower() not in valid_extensions:
                    extension = 'jpg'
                
                # Nombre de archivo con índice si hay múltiples imágenes
                if idx > 0:
                    image_name = f'{clean_title}_{idx + 1}.{extension}'
                else:
                    image_name = f'{clean_title}.{extension}'
                
                # Ruta completa
                subreddit = item['subreddit']
                relative_path = f'images/{subreddit}/{image_name}'
                full_path = os.path.join(self.images_store, relative_path)
                
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Descargar imagen con requests
                spider.logger.info(f"📥 Descargando: {image_url} -> {image_name}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.reddit.com/'
                }
                
                response = requests.get(image_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    with open(full_path, 'wb') as f:
                        f.write(response.content)
                    
                    image_paths.append(relative_path)
                    spider.logger.info(f"✅ Descargada: {image_name} ({len(response.content)} bytes)")
                else:
                    spider.logger.warning(f"❌ Error HTTP {response.status_code} descargando: {image_url}")
                    
            except Exception as e:
                spider.logger.error(f"❌ Error descargando {image_url}: {str(e)}")
                continue
        
        item['images'] = image_paths
        return item


class RedditDataPipeline:
    """Pipeline para procesar y limpiar datos de Reddit"""
    
    def process_item(self, item, spider):
        """Procesar y limpiar datos del item"""
        
        # Limpiar texto de comentarios
        if 'comments' in item and item['comments']:
            for comment in item['comments']:
                if 'body' in comment and comment['body']:
                    # Limpiar HTML entities
                    comment['body'] = self.clean_text(comment['body'])
        
        # Limpiar texto del post
        if 'selftext' in item and item['selftext']:
            item['selftext'] = self.clean_text(item['selftext'])
        
        # Limpiar título
        if 'title' in item and item['title']:
            item['title'] = self.clean_text(item['title'])
        
        return item
    
    def clean_text(self, text):
        """Limpiar texto de caracteres especiales"""
        import html
        
        # Decodificar HTML entities
        text = html.unescape(text)
        
        # Remover caracteres de control
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text.strip()


class RedditValidationPipeline:
    """Pipeline para validar datos de Reddit"""
    
    def process_item(self, item, spider):
        """Validar que el item tenga datos mínimos"""
        
        # Validar campos requeridos
        required_fields = ['id', 'title', 'author', 'subreddit']
        for field in required_fields:
            if not item.get(field):
                raise DropItem(f"Item sin campo requerido: {field}")
        
        # Validar que tenga al menos un comentario o contenido
        if not item.get('comments') and not item.get('selftext'):
            spider.logger.warning(f"Post {item['id']} sin contenido")
        
        return item
