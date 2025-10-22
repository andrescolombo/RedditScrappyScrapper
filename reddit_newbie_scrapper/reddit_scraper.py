import praw
import os
import json
import time
import re
import io
import asyncio
import aiohttp
import aiofiles
from datetime import datetime
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv
from tqdm import tqdm
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
from PIL import Image
import requests
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageDownloader:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.images_dir = output_dir / 'images'
        self.images_dir.mkdir(exist_ok=True)
        self.downloaded_urls: Set[str] = set()
        
    def is_image_url(self, url: str) -> bool:
        """Verificar si una URL es una imagen"""
        if not url:
            return False
        
        # Extensiones de imagen comunes
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg'}
        
        # Verificar extensión
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Verificar si termina con extensión de imagen
        if any(path.endswith(ext) for ext in image_extensions):
            return True
        
        # Verificar dominios conocidos de imágenes
        image_domains = {
            'i.redd.it', 'i.imgur.com', 'imgur.com', 'gyazo.com', 
            'postimg.cc', 'ibb.co', 'imgbb.com', 'flickr.com',
            'deviantart.com', 'artstation.com', 'pinterest.com'
        }
        
        domain = parsed_url.netloc.lower()
        return any(img_domain in domain for img_domain in image_domains)
    
    def extract_images_from_text(self, text: str) -> List[str]:
        """Extraer URLs de imágenes del texto"""
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
            r'https?://[^\s]*postimg[^\s]*',
            r'https?://[^\s]*ibb\.co[^\s]*',
            r'https?://[^\s]*imgbb[^\s]*'
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
    
    async def download_image_async(self, session: aiohttp.ClientSession, url: str, filename: str) -> bool:
        """Descargar una imagen de forma asíncrona"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Verificar que sea realmente una imagen
                    if self.is_valid_image(content):
                        async with aiofiles.open(filename, 'wb') as f:
                            await f.write(content)
                        return True
                    
        except Exception as e:
            logger.error(f"Error descargando imagen {url}: {str(e)}")
        
        return False
    
    def is_valid_image(self, content: bytes) -> bool:
        """Verificar si el contenido es una imagen válida"""
        try:
            Image.open(io.BytesIO(content))
            return True
        except:
            return False
    
    def download_image_sync(self, url: str, filename: str) -> bool:
        """Descargar una imagen de forma síncrona"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                content = response.content
                
                # Verificar que sea realmente una imagen
                if self.is_valid_image(content):
                    with open(filename, 'wb') as f:
                        f.write(content)
                    return True
                    
        except Exception as e:
            logger.error(f"Error descargando imagen {url}: {str(e)}")
        
        return False
    
    def get_filename_from_url(self, url: str, post_id: str, comment_id: str = None) -> str:
        """Generar nombre de archivo único para la imagen"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Extraer nombre del archivo
        filename = os.path.basename(path)
        if not filename or '.' not in filename:
            filename = f"image_{post_id}"
        
        # Limpiar nombre de archivo
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Agregar prefijo con IDs
        if comment_id:
            name, ext = os.path.splitext(filename)
            filename = f"{post_id}_{comment_id}_{name}{ext}"
        else:
            name, ext = os.path.splitext(filename)
            filename = f"{post_id}_{name}{ext}"
        
        return filename
    
    async def download_images_async(self, image_urls: List[str], post_id: str, comment_id: str = None) -> List[str]:
        """Descargar múltiples imágenes de forma asíncrona"""
        downloaded_files = []
        
        if not image_urls:
            return downloaded_files
        
        # Crear directorio específico para el post
        post_dir = self.images_dir / post_id
        post_dir.mkdir(exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for url in image_urls:
                if url in self.downloaded_urls:
                    continue
                
                filename = self.get_filename_from_url(url, post_id, comment_id)
                filepath = post_dir / filename
                
                # Evitar descargar el mismo archivo dos veces
                if filepath.exists():
                    downloaded_files.append(str(filepath))
                    continue
                
                task = self.download_image_async(session, url, str(filepath))
                tasks.append((task, url, filepath))
            
            # Ejecutar todas las descargas en paralelo
            for task, url, filepath in tasks:
                success = await task
                if success:
                    downloaded_files.append(str(filepath))
                    self.downloaded_urls.add(url)
                    logger.info(f"Imagen descargada: {filepath}")
        
        return downloaded_files
    
    def download_images_sync(self, image_urls: List[str], post_id: str, comment_id: str = None) -> List[str]:
        """Descargar múltiples imágenes de forma síncrona"""
        downloaded_files = []
        
        if not image_urls:
            return downloaded_files
        
        # Crear directorio específico para el post
        post_dir = self.images_dir / post_id
        post_dir.mkdir(exist_ok=True)
        
        for url in image_urls:
            if url in self.downloaded_urls:
                continue
            
            filename = self.get_filename_from_url(url, post_id, comment_id)
            filepath = post_dir / filename
            
            # Evitar descargar el mismo archivo dos veces
            if filepath.exists():
                downloaded_files.append(str(filepath))
                continue
            
            success = self.download_image_sync(url, str(filepath))
            if success:
                downloaded_files.append(str(filepath))
                self.downloaded_urls.add(url)
                logger.info(f"Imagen descargada: {filepath}")
        
        return downloaded_files

class RedditScraper:
    def __init__(self):
        """Inicializar el scraper de Reddit"""
        load_dotenv()
        
        # Configuración de Reddit API
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'RedditScraper/1.0 by AndresColombo')
        )
        
        # Configuración del scraper
        self.max_posts = int(os.getenv('MAX_POSTS', '1000'))
        self.max_comments_per_post = int(os.getenv('MAX_COMMENTS_PER_POST', '100'))
        self.download_images = os.getenv('DOWNLOAD_IMAGES', 'true').lower() == 'true'
        self.output_dir = Path(os.getenv('OUTPUT_DIR', 'scraped_data'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Inicializar descargador de imágenes
        self.image_downloader = ImageDownloader(self.output_dir)
        
        logger.info("Reddit Scraper inicializado correctamente")
        logger.info(f"Descarga de imágenes: {'Habilitada' if self.download_images else 'Deshabilitada'}")
    
    def scrape_subreddit(self, subreddit_name: str, sort_by: str = 'hot', time_filter: str = 'all') -> Dict:
        """
        Scrapear un subreddit completo
        
        Args:
            subreddit_name: Nombre del subreddit (sin r/)
            sort_by: Método de ordenamiento (hot, new, top, rising)
            time_filter: Filtro de tiempo (all, year, month, week, day, hour)
        """
        logger.info(f"Iniciando scrape del subreddit: r/{subreddit_name}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Obtener posts según el método de ordenamiento
            if sort_by == 'hot':
                posts = subreddit.hot(limit=self.max_posts)
            elif sort_by == 'new':
                posts = subreddit.new(limit=self.max_posts)
            elif sort_by == 'top':
                posts = subreddit.top(time_filter=time_filter, limit=self.max_posts)
            elif sort_by == 'rising':
                posts = subreddit.rising(limit=self.max_posts)
            else:
                raise ValueError(f"Método de ordenamiento no válido: {sort_by}")
            
            scraped_data = {
                'subreddit': subreddit_name,
                'scrape_date': datetime.now().isoformat(),
                'sort_method': sort_by,
                'time_filter': time_filter,
                'total_posts': 0,
                'total_images_downloaded': 0,
                'posts': []
            }
            
            # Procesar cada post
            for post in tqdm(posts, desc=f"Procesando posts de r/{subreddit_name}"):
                try:
                    post_data = self._extract_post_data(post)
                    scraped_data['posts'].append(post_data)
                    scraped_data['total_posts'] += 1
                    
                    # Contar imágenes descargadas
                    if 'images_downloaded' in post_data:
                        scraped_data['total_images_downloaded'] += len(post_data['images_downloaded'])
                    
                    # Pequeña pausa para ser respetuoso con la API
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error procesando post {post.id}: {str(e)}")
                    continue
            
            logger.info(f"Scrape completado: {scraped_data['total_posts']} posts procesados")
            logger.info(f"Imágenes descargadas: {scraped_data['total_images_downloaded']}")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scrapeando subreddit {subreddit_name}: {str(e)}")
            raise
    
    def _extract_post_data(self, post) -> Dict:
        """Extraer todos los datos de un post"""
        try:
            # Datos básicos del post
            post_data = {
                'id': post.id,
                'title': post.title,
                'author': str(post.author) if post.author else '[deleted]',
                'created_utc': post.created_utc,
                'created_date': datetime.fromtimestamp(post.created_utc).isoformat(),
                'score': post.score,
                'upvote_ratio': post.upvote_ratio,
                'num_comments': post.num_comments,
                'url': post.url,
                'permalink': f"https://reddit.com{post.permalink}",
                'is_self': post.is_self,
                'selftext': post.selftext if post.is_self else '',
                'subreddit': str(post.subreddit),
                'flair_text': post.link_flair_text,
                'nsfw': post.over_18,
                'locked': post.locked,
                'stickied': post.stickied,
                'gilded': post.gilded,
                'domain': post.domain,
                'thumbnail': post.thumbnail if hasattr(post, 'thumbnail') else '',
                'preview': getattr(post, 'preview', {}),
                'images_downloaded': [],
                'comments': []
            }
            
            # Extraer y descargar imágenes del post
            if self.download_images:
                post_images = self._extract_images_from_post(post)
                if post_images:
                    downloaded = self.image_downloader.download_images_sync(post_images, post.id)
                    post_data['images_downloaded'] = downloaded
                    post_data['image_urls'] = post_images
            
            # Expandir comentarios si el post no está bloqueado
            if not post.locked and post.num_comments > 0:
                post_data['comments'] = self._extract_comments(post)
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del post {post.id}: {str(e)}")
            return {'id': post.id, 'error': str(e)}
    
    def _extract_images_from_post(self, post) -> List[str]:
        """Extraer URLs de imágenes del post"""
        image_urls = []
        
        try:
            # URL principal del post
            if self.image_downloader.is_image_url(post.url):
                image_urls.append(post.url)
            
            # Thumbnail
            if hasattr(post, 'thumbnail') and post.thumbnail and post.thumbnail != 'self':
                if self.image_downloader.is_image_url(post.thumbnail):
                    image_urls.append(post.thumbnail)
            
            # Preview images
            if hasattr(post, 'preview') and post.preview:
                try:
                    preview_images = post.preview.get('images', [])
                    for preview in preview_images:
                        if 'source' in preview:
                            image_urls.append(preview['source']['url'])
                        if 'resolutions' in preview:
                            for res in preview['resolutions']:
                                image_urls.append(res['url'])
                except Exception as e:
                    logger.error(f"Error extrayendo preview images: {str(e)}")
            
            # Extraer imágenes del texto del post
            if post.is_self and post.selftext:
                text_images = self.image_downloader.extract_images_from_text(post.selftext)
                image_urls.extend(text_images)
            
            # Remover duplicados
            image_urls = list(set(image_urls))
            
        except Exception as e:
            logger.error(f"Error extrayendo imágenes del post {post.id}: {str(e)}")
        
        return image_urls
    
    def _extract_comments(self, post) -> List[Dict]:
        """Extraer comentarios de un post"""
        comments = []
        
        try:
            # Expandir todos los comentarios
            post.comments.replace_more(limit=0)
            
            for comment in post.comments.list()[:self.max_comments_per_post]:
                try:
                    comment_data = {
                        'id': comment.id,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'created_date': datetime.fromtimestamp(comment.created_utc).isoformat(),
                        'parent_id': comment.parent_id,
                        'is_submitter': comment.is_submitter,
                        'stickied': comment.stickied,
                        'gilded': comment.gilded,
                        'controversiality': comment.controversiality,
                        'depth': comment.depth if hasattr(comment, 'depth') else 0,
                        'images_downloaded': []
                    }
                    
                    # Extraer y descargar imágenes del comentario
                    if self.download_images and comment.body:
                        comment_images = self.image_downloader.extract_images_from_text(comment.body)
                        if comment_images:
                            downloaded = self.image_downloader.download_images_sync(
                                comment_images, post.id, comment.id
                            )
                            comment_data['images_downloaded'] = downloaded
                            comment_data['image_urls'] = comment_images
                    
                    comments.append(comment_data)
                    
                except Exception as e:
                    logger.error(f"Error procesando comentario {comment.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extrayendo comentarios del post {post.id}: {str(e)}")
        
        return comments
    
    def save_to_json(self, data: Dict, filename: str = None) -> str:
        """Guardar datos en formato JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{data['subreddit']}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Datos guardados en: {filepath}")
        return str(filepath)
    
    def save_to_text(self, data: Dict, filename: str = None) -> str:
        """Guardar datos en formato texto legible"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{data['subreddit']}_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"SCRAPER DE REDDIT - REPORTE COMPLETO\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Subreddit: r/{data['subreddit']}\n")
            f.write(f"Fecha de scrape: {data['scrape_date']}\n")
            f.write(f"Método de ordenamiento: {data['sort_method']}\n")
            f.write(f"Filtro de tiempo: {data['time_filter']}\n")
            f.write(f"Total de posts: {data['total_posts']}\n")
            f.write(f"Imágenes descargadas: {data.get('total_images_downloaded', 0)}\n")
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
                
                # Información de imágenes
                if post.get('images_downloaded'):
                    f.write(f"Imágenes descargadas: {len(post['images_downloaded'])}\n")
                    for img_path in post['images_downloaded']:
                        f.write(f"  📷 {img_path}\n")
                
                if post['selftext']:
                    f.write(f"\nContenido del post:\n{post['selftext']}\n")
                
                f.write(f"\nCOMENTARIOS ({len(post['comments'])}):\n")
                f.write("-" * 20 + "\n")
                
                for j, comment in enumerate(post['comments'], 1):
                    f.write(f"  Comentario #{j}\n")
                    f.write(f"  Autor: {comment['author']}\n")
                    f.write(f"  Score: {comment['score']}\n")
                    f.write(f"  Fecha: {comment['created_date']}\n")
                    f.write(f"  Contenido: {comment['body']}\n")
                    
                    # Imágenes del comentario
                    if comment.get('images_downloaded'):
                        f.write(f"  Imágenes: {len(comment['images_downloaded'])}\n")
                        for img_path in comment['images_downloaded']:
                            f.write(f"    📷 {img_path}\n")
                    
                    f.write(f"  ---\n")
                
                f.write(f"\n" + "=" * 50 + "\n\n")
        
        logger.info(f"Reporte de texto guardado en: {filepath}")
        return str(filepath)
    
    def scrape_multiple_subreddits(self, subreddits: List[str], sort_by: str = 'hot') -> Dict[str, str]:
        """Scrapear múltiples subreddits"""
        results = {}
        
        for subreddit in subreddits:
            try:
                logger.info(f"Iniciando scrape de r/{subreddit}")
                data = self.scrape_subreddit(subreddit, sort_by)
                
                # Guardar en ambos formatos
                json_file = self.save_to_json(data)
                txt_file = self.save_to_text(data)
                
                results[subreddit] = {
                    'json': json_file,
                    'text': txt_file,
                    'posts_count': data['total_posts'],
                    'images_count': data.get('total_images_downloaded', 0)
                }
                
                logger.info(f"r/{subreddit} completado: {data['total_posts']} posts, {data.get('total_images_downloaded', 0)} imágenes")
                
            except Exception as e:
                logger.error(f"Error scrapeando r/{subreddit}: {str(e)}")
                results[subreddit] = {'error': str(e)}
        
        return results

def main():
    """Función principal para ejecutar el scraper"""
    scraper = RedditScraper()
    
    # Configuración por defecto
    subreddits_to_scrape = ['python', 'MachineLearning', 'datascience']
    
    print("Reddit Scraper con Descarga de Imágenes")
    print("=" * 50)
    
    # Permitir al usuario configurar
    custom_subreddits = input(f"Subreddits a scrapear (separados por coma) [default: {', '.join(subreddits_to_scrape)}]: ").strip()
    if custom_subreddits:
        subreddits_to_scrape = [s.strip() for s in custom_subreddits.split(',')]
    
    sort_method = input("Método de ordenamiento [hot/new/top/rising] [default: hot]: ").strip() or 'hot'
    
    download_images = input("¿Descargar imágenes? [y/n] [default: y]: ").strip().lower()
    if download_images in ['n', 'no']:
        scraper.download_images = False
    
    print(f"\nIniciando scrape de: {', '.join(subreddits_to_scrape)}")
    print(f"Método: {sort_method}")
    print(f"Descarga de imágenes: {'Sí' if scraper.download_images else 'No'}")
    
    # Ejecutar scraping
    results = scraper.scrape_multiple_subreddits(subreddits_to_scrape, sort_method)
    
    # Mostrar resultados
    print("\n" + "=" * 50)
    print("RESULTADOS DEL SCRAPING")
    print("=" * 50)
    
    for subreddit, result in results.items():
        if 'error' in result:
            print(f"❌ r/{subreddit}: Error - {result['error']}")
        else:
            print(f"✅ r/{subreddit}: {result['posts_count']} posts, {result['images_count']} imágenes")
            print(f"   📄 JSON: {result['json']}")
            print(f"   📝 Texto: {result['text']}")
            if result['images_count'] > 0:
                print(f"   📷 Imágenes: {scraper.image_downloader.images_dir}")

if __name__ == "__main__":
    main()
