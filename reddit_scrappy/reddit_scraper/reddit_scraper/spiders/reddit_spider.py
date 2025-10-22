import scrapy
import json
import time
from datetime import datetime
from urllib.parse import urljoin
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import os


class RedditPostItem(scrapy.Item):
    """Item para almacenar datos de posts de Reddit"""
    # Datos básicos del post
    id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    created_utc = scrapy.Field()
    created_date = scrapy.Field()
    score = scrapy.Field()
    upvote_ratio = scrapy.Field()
    num_comments = scrapy.Field()
    url = scrapy.Field()
    permalink = scrapy.Field()
    is_self = scrapy.Field()
    selftext = scrapy.Field()
    subreddit = scrapy.Field()
    flair_text = scrapy.Field()
    nsfw = scrapy.Field()
    locked = scrapy.Field()
    stickied = scrapy.Field()
    domain = scrapy.Field()
    thumbnail = scrapy.Field()
    
    # Metadatos del scraping
    scrape_date = scrapy.Field()
    sort_method = scrapy.Field()
    time_filter = scrapy.Field()
    
    # Comentarios
    comments = scrapy.Field()
    
    # Imágenes
    image_urls = scrapy.Field()
    images = scrapy.Field()


class RedditCommentItem(scrapy.Item):
    """Item para almacenar datos de comentarios"""
    id = scrapy.Field()
    author = scrapy.Field()
    body = scrapy.Field()
    score = scrapy.Field()
    created_utc = scrapy.Field()
    created_date = scrapy.Field()
    parent_id = scrapy.Field()
    is_submitter = scrapy.Field()
    stickied = scrapy.Field()
    depth = scrapy.Field()
    post_id = scrapy.Field()


class RedditSpider(scrapy.Spider):
    """Spider principal para scrapear Reddit"""
    name = 'reddit'
    
    def __init__(self, subreddit='NMSCoordinateExchange', sort='hot', time_filter='all', 
                 max_posts=100, max_comments=10, *args, **kwargs):
        super(RedditSpider, self).__init__(*args, **kwargs)
        
        self.subreddit = subreddit
        self.sort = sort
        self.time_filter = time_filter
        self.max_posts = int(max_posts)
        self.max_comments = int(max_comments)
        
        # Contador de posts procesados
        self.posts_scraped = 0
        
        # Construir URL inicial (con limit=100 para obtener más posts por request)
        if sort == 'top' and time_filter != 'all':
            self.start_urls = [
                f'https://www.reddit.com/r/{subreddit}/{sort}.json?limit=100&t={time_filter}'
            ]
        else:
            self.start_urls = [
                f'https://www.reddit.com/r/{subreddit}/{sort}.json?limit=100'
            ]
        
        self.logger.info(f"🚀 Iniciando scraping de r/{subreddit}")
        self.logger.info(f"📊 Método: {sort}, Filtro: {time_filter}")
        self.logger.info(f"📈 Máximo posts: {max_posts}, Máximo comentarios: {max_comments}")
        self.logger.info(f"🌐 URL inicial: {self.start_urls[0]}")
    
    def start_requests(self):
        """Generar requests iniciales"""
        headers = {
            'User-Agent': 'RedditScraper/1.0 by AndresColombo'
        }
        
        for url in self.start_urls:
            self.logger.info(f"📡 Enviando request a: {url}")
            yield Request(
                url=url,
                headers=headers,
                callback=self.parse,
                meta={'dont_cache': True},
                errback=self.handle_error
            )
    
    def parse(self, response):
        """Parsear la respuesta principal de Reddit"""
        try:
            self.logger.info(f"📥 Respuesta recibida - Status: {response.status}")
            self.logger.info(f"📏 Tamaño de respuesta: {len(response.text)} caracteres")
            
            data = json.loads(response.text)
            
            if 'data' not in data or 'children' not in data['data']:
                self.logger.error("❌ Estructura de datos inesperada")
                self.logger.error(f"🔍 Claves disponibles: {list(data.keys())}")
                return
            
            posts = data['data']['children']
            after = data['data'].get('after')  # Token para siguiente página
            
            self.logger.info(f"📋 Encontrados {len(posts)} posts en esta página")
            self.logger.info(f"📊 Posts scrapeados hasta ahora: {self.posts_scraped}/{self.max_posts}")
            
            for i, post_wrapper in enumerate(posts, 1):
                # Verificar si ya alcanzamos el límite
                if self.posts_scraped >= self.max_posts:
                    self.logger.info(f"✅ Límite de {self.max_posts} posts alcanzado")
                    return
                
                post_data = post_wrapper['data']
                post_id = post_data['id']
                
                self.posts_scraped += 1
                
                self.logger.info(f"📝 Procesando post {self.posts_scraped}/{self.max_posts}: {post_id}")
                self.logger.info(f"📄 Título: {post_data['title'][:50]}...")
                
                # Crear item del post
                post_item = RedditPostItem()
                
                # Datos básicos
                post_item['id'] = post_data['id']
                post_item['title'] = post_data['title']
                post_item['author'] = post_data.get('author', '[deleted]')
                post_item['created_utc'] = post_data['created_utc']
                post_item['created_date'] = datetime.fromtimestamp(post_data['created_utc']).isoformat()
                post_item['score'] = post_data['score']
                post_item['upvote_ratio'] = post_data.get('upvote_ratio', 0)
                post_item['num_comments'] = post_data['num_comments']
                post_item['url'] = post_data.get('url', '')
                post_item['permalink'] = f"https://reddit.com{post_data['permalink']}"
                post_item['is_self'] = post_data['is_self']
                post_item['selftext'] = post_data.get('selftext', '')
                post_item['subreddit'] = post_data['subreddit']
                post_item['flair_text'] = post_data.get('link_flair_text', '')
                post_item['nsfw'] = post_data.get('over_18', False)
                post_item['locked'] = post_data.get('locked', False)
                post_item['stickied'] = post_data.get('stickied', False)
                post_item['domain'] = post_data.get('domain', '')
                post_item['thumbnail'] = post_data.get('thumbnail', '')
                
                # Metadatos del scraping
                post_item['scrape_date'] = datetime.now().isoformat()
                post_item['sort_method'] = self.sort
                post_item['time_filter'] = self.time_filter
                
                # Inicializar listas
                post_item['comments'] = []
                post_item['image_urls'] = []
                
                # Extraer URLs de imágenes
                image_urls = self.extract_image_urls(post_data)
                post_item['image_urls'] = image_urls
                self.logger.info(f"🖼️ Imágenes encontradas: {len(image_urls)}")
                
                # Si hay comentarios y no está bloqueado, obtenerlos
                if post_item['num_comments'] > 0 and not post_item['locked']:
                    comments_url = f"https://www.reddit.com{post_data['permalink']}.json"
                    self.logger.info(f"💬 Obteniendo comentarios de: {comments_url}")
                    
                    yield Request(
                        url=comments_url,
                        headers={'User-Agent': 'RedditScraper/1.0 by AndresColombo'},
                        callback=self.parse_comments,
                        meta={
                            'post_item': post_item,
                            'post_id': post_data['id']
                        },
                        errback=self.handle_error
                    )
                else:
                    # Si no hay comentarios, yield el post directamente
                    self.logger.info(f"⏭️ Post sin comentarios, enviando directamente")
                    yield post_item
                
                # Pausa para ser respetuoso
                time.sleep(0.5)
            
            # Si hay más posts y no alcanzamos el límite, obtener la siguiente página
            if after and self.posts_scraped < self.max_posts:
                remaining = self.max_posts - self.posts_scraped
                self.logger.info(f"📄 Obteniendo siguiente página (quedan {remaining} posts)")
                
                # Construir URL de siguiente página
                if self.sort == 'top' and self.time_filter != 'all':
                    next_url = f'https://www.reddit.com/r/{self.subreddit}/{self.sort}.json?limit=100&t={self.time_filter}&after={after}'
                else:
                    next_url = f'https://www.reddit.com/r/{self.subreddit}/{self.sort}.json?limit=100&after={after}'
                
                self.logger.info(f"🔗 URL siguiente página: {next_url}")
                
                yield Request(
                    url=next_url,
                    headers={'User-Agent': 'RedditScraper/1.0 by AndresColombo'},
                    callback=self.parse,
                    meta={'dont_cache': True},
                    errback=self.handle_error
                )
            else:
                if not after:
                    self.logger.info(f"✅ No hay más páginas disponibles")
                else:
                    self.logger.info(f"✅ Límite de posts alcanzado")
                
        except Exception as e:
            self.logger.error(f"❌ Error parseando respuesta principal: {str(e)}")
            self.logger.error(f"🔍 Tipo de error: {type(e).__name__}")
    
    def parse_comments(self, response):
        """Parsear comentarios de un post"""
        try:
            post_item = response.meta['post_item']
            post_id = response.meta['post_id']
            
            data = json.loads(response.text)
            
            if len(data) > 1:
                comments_list = data[1]['data']['children']
                
                comments_count = 0
                for comment_wrapper in comments_list[:self.max_comments]:
                    try:
                        comment_data = comment_wrapper['data']
                        
                        # Saltar si es un comentario eliminado o muy corto
                        if comment_data.get('body') in ['[deleted]', '[removed]'] or len(comment_data.get('body', '')) < 3:
                            continue
                        
                        comment_item = {
                            'id': comment_data['id'],
                            'author': comment_data.get('author', '[deleted]'),
                            'body': comment_data.get('body', ''),
                            'score': comment_data.get('score', 0),
                            'created_utc': comment_data['created_utc'],
                            'created_date': datetime.fromtimestamp(comment_data['created_utc']).isoformat(),
                            'parent_id': comment_data.get('parent_id', ''),
                            'is_submitter': comment_data.get('is_submitter', False),
                            'stickied': comment_data.get('stickied', False),
                            'depth': comment_data.get('depth', 0),
                            'post_id': post_id
                        }
                        
                        post_item['comments'].append(comment_item)
                        comments_count += 1
                        
                        # Log detallado de cada comentario
                        self.logger.info(f"💬 Comentario {comments_count}/{self.max_comments}: {comment_data.get('author', 'unknown')} - {comment_data.get('body', '')[:50]}...")
                        
                    except Exception as e:
                        self.logger.error(f"Error procesando comentario: {str(e)}")
                        continue
                
                self.logger.info(f"💬 Comentarios extraídos para {post_id}: {comments_count}")
            
            self.logger.info(f"✅ Post {post_id} completado con {len(post_item['comments'])} comentarios")
            yield post_item
            
        except Exception as e:
            self.logger.error(f"❌ Error parseando comentarios: {str(e)}")
            self.logger.error(f"🔍 Tipo de error: {type(e).__name__}")
            # Yield el post sin comentarios
            yield response.meta['post_item']
    
    def extract_image_urls(self, post_data):
        """Extraer URLs de imágenes del post (priorizando calidad alta)"""
        import html
        image_urls = []
        
        try:
            # Prioridad 1: URL principal del post (i.redd.it - mejor calidad y sin redirecciones)
            url = post_data.get('url', '')
            if url and 'i.redd.it' in url:
                clean_url = html.unescape(url)
                image_urls.append(clean_url)
                self.logger.info(f"📸 URL i.redd.it encontrada: {clean_url}")
            
            # Prioridad 2: Gallery (media_metadata - URLs directas de i.redd.it)
            if 'gallery_data' in post_data and 'items' in post_data['gallery_data']:
                media_metadata = post_data.get('media_metadata', {})
                for item in post_data['gallery_data']['items']:
                    media_id = item.get('media_id')
                    if media_id and media_id in media_metadata:
                        media = media_metadata[media_id]
                        # Obtener la URL de la imagen más grande (en 's')
                        if 's' in media and 'u' in media['s']:
                            gallery_url = html.unescape(media['s']['u'])
                            # Convertir preview.redd.it a i.redd.it si es necesario
                            gallery_url = gallery_url.replace('preview.redd.it', 'i.redd.it')
                            # Remover parámetros de query para obtener la imagen original
                            gallery_url = gallery_url.split('?')[0]
                            if gallery_url not in image_urls:
                                image_urls.append(gallery_url)
                                self.logger.info(f"📸 Gallery image encontrada: {gallery_url}")
            
            # Prioridad 3: Preview images (convertir a i.redd.it)
            if not image_urls:  # Solo si no encontramos i.redd.it directo
                preview = post_data.get('preview', {})
                if preview and 'images' in preview:
                    for img in preview['images']:
                        if 'source' in img:
                            source_url = html.unescape(img['source']['url'])
                            # Convertir preview.redd.it a i.redd.it
                            source_url = source_url.replace('preview.redd.it', 'i.redd.it')
                            # Remover parámetros de query
                            source_url = source_url.split('?')[0]
                            if source_url not in image_urls:
                                image_urls.append(source_url)
                                self.logger.info(f"📸 Preview image convertida: {source_url}")
            
            # Prioridad 4: Otras URLs de imagen
            if not image_urls and url and self.is_image_url(url):
                if 'reddit.com' not in url:
                    clean_url = html.unescape(url)
                    image_urls.append(clean_url)
                    self.logger.info(f"📸 URL externa encontrada: {clean_url}")
            
            # Prioridad 5: Extraer imágenes del texto del post
            if post_data.get('is_self') and post_data.get('selftext'):
                text_images = self.extract_images_from_text(post_data['selftext'])
                for text_img in text_images:
                    text_img = html.unescape(text_img)
                    # Convertir preview.redd.it a i.redd.it
                    text_img = text_img.replace('preview.redd.it', 'i.redd.it')
                    text_img = text_img.split('?')[0]
                    if text_img not in image_urls:
                        image_urls.append(text_img)
                        self.logger.info(f"📸 Text image encontrada: {text_img}")
            
        except Exception as e:
            self.logger.error(f"Error extrayendo imágenes: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return image_urls
    
    def is_image_url(self, url):
        """Verificar si una URL es una imagen"""
        if not url:
            return False
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg'}
        image_domains = {
            'i.redd.it', 'i.imgur.com', 'imgur.com', 'gyazo.com', 
            'postimg.cc', 'ibb.co', 'imgbb.com', 'flickr.com',
            'deviantart.com', 'artstation.com', 'preview.redd.it'
        }
        
        # Verificar extensión
        if any(url.lower().endswith(ext) for ext in image_extensions):
            return True
        
        # Verificar dominio
        if any(domain in url.lower() for domain in image_domains):
            return True
        
        return False
    
    def extract_images_from_text(self, text):
        """Extraer URLs de imágenes del texto"""
        import re
        
        if not text:
            return []
        
        # Patrones para encontrar URLs de imágenes
        patterns = [
            r'https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp|bmp|tiff|svg)',
            r'https?://i\.redd\.it/[^\s]+',
            r'https?://i\.imgur\.com/[^\s]+',
            r'https?://imgur\.com/[^\s]+',
            r'https?://[^\s]*imgur[^\s]*',
            r'https?://[^\s]*gyazo[^\s]*',
            r'https?://preview\.redd\.it/[^\s]+'
        ]
        
        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        
        # Limpiar URLs
        cleaned_urls = []
        for url in urls:
            # Remover caracteres de puntuación al final
            url = re.sub(r'[.,;:!?]+$', '', url)
            # Remover paréntesis si están al final
            url = re.sub(r'\)+$', '', url)
            cleaned_urls.append(url)
        
        return list(set(cleaned_urls))  # Remover duplicados
    
    def handle_error(self, failure):
        """Manejar errores de requests"""
        self.logger.error(f"❌ Error en request: {failure.value}")
        self.logger.error(f"🔍 Tipo de error: {type(failure.value).__name__}")
        
        # Si es un error de request, intentar continuar
        if hasattr(failure.value, 'response'):
            response = failure.value.response
            self.logger.error(f"📊 Status code: {response.status}")
            self.logger.error(f"📄 URL que falló: {response.url}")
        
        # Re-yield el post item si existe en meta
        if 'post_item' in failure.request.meta:
            self.logger.info("🔄 Reintentando con post sin comentarios")
            yield failure.request.meta['post_item']
