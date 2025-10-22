import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import os
from pathlib import Path


class RedditImagesPipeline(ImagesPipeline):
    """Pipeline personalizado para descargar imágenes de Reddit"""
    
    def get_media_requests(self, item, info):
        """Generar requests para descargar imágenes"""
        if 'image_urls' in item and item['image_urls']:
            for image_url in item['image_urls']:
                yield scrapy.Request(
                    url=image_url,
                    meta={
                        'post_id': item['id'],
                        'subreddit': item['subreddit']
                    }
                )
    
    def file_path(self, request, response=None, info=None, *, item=None):
        """Definir la ruta donde guardar las imágenes"""
        post_id = request.meta['post_id']
        subreddit = request.meta['subreddit']
        
        # Extraer nombre del archivo de la URL
        image_name = request.url.split('/')[-1]
        
        # Si no tiene extensión, agregar .jpg
        if '.' not in image_name:
            image_name += '.jpg'
        
        # Crear estructura de carpetas: images/subreddit/post_id/image_name
        return f'images/{subreddit}/{post_id}/{image_name}'
    
    def item_completed(self, results, item, info):
        """Procesar resultados de descarga de imágenes"""
        image_paths = []
        
        for success, result in results:
            if success:
                image_paths.append(result['path'])
            else:
                info.spider.logger.warning(f"Error descargando imagen: {result}")
        
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