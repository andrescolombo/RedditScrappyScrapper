#!/usr/bin/env python3
"""
Script de prueba del Reddit Scraper para r/NMSCoordinateExchange
Usando requests directamente para evitar problemas de autenticación
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_reddit_scraper():
    """Probar el scraper con r/NMSCoordinateExchange usando requests"""
    
    print("Reddit Scraper - Prueba con r/NMSCoordinateExchange")
    print("=" * 60)
    
    try:
        # URL del subreddit en formato JSON
        subreddit_name = "NMSCoordinateExchange"
        url = f"https://www.reddit.com/r/{subreddit_name}/hot.json?limit=10"
        
        headers = {
            'User-Agent': 'RedditScraper/1.0 by AndresColombo'
        }
        
        print(f"Accediendo a r/{subreddit_name}...")
        print(f"URL: {url}")
        
        # Crear directorio de salida
        output_dir = Path("scraped_data")
        output_dir.mkdir(exist_ok=True)
        
        # Hacer request a Reddit
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            return False
        
        data = response.json()
        
        if 'data' not in data or 'children' not in data['data']:
            print("Error: Estructura de datos inesperada")
            print(f"Datos recibidos: {json.dumps(data, indent=2)[:500]}")
            return False
        
        posts = data['data']['children']
        print(f"Posts encontrados: {len(posts)}")
        
        # Datos del scrape
        scraped_data = {
            'subreddit': subreddit_name,
            'scrape_date': datetime.now().isoformat(),
            'sort_method': 'hot',
            'total_posts': 0,
            'total_comments': 0,
            'posts': []
        }
        
        # Procesar posts
        for i, post_wrapper in enumerate(posts):
            try:
                post_data_raw = post_wrapper['data']
                
                print(f"\nProcesando post {i + 1}: {post_data_raw['title'][:50]}...")
                
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
                    'comments': []
                }
                
                # Intentar obtener comentarios
                if post_data['num_comments'] > 0 and not post_data['locked']:
                    print(f"  Intentando extraer comentarios...")
                    
                    # URL para obtener comentarios
                    comments_url = f"https://www.reddit.com{post_data_raw['permalink']}.json"
                    
                    try:
                        comments_response = requests.get(comments_url, headers=headers)
                        if comments_response.status_code == 200:
                            comments_data = comments_response.json()
                            
                            # Los comentarios están en el segundo elemento del array
                            if len(comments_data) > 1:
                                comments_list = comments_data[1]['data']['children']
                                
                                comments_count = 0
                                for comment_wrapper in comments_list[:5]:  # Solo 5 comentarios
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
                                        logger.error(f"Error procesando comentario: {str(e)}")
                                        continue
                                
                                print(f"  Comentarios extraídos: {comments_count}")
                                scraped_data['total_comments'] += comments_count
                        
                    except Exception as e:
                        logger.error(f"Error obteniendo comentarios: {str(e)}")
                
                scraped_data['posts'].append(post_data)
                scraped_data['total_posts'] += 1
                
                # Pausa para ser respetuoso con la API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error procesando post: {str(e)}")
                continue
        
        # Guardar datos en JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = output_dir / f"{subreddit_name}_{timestamp}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        
        # Guardar datos en texto
        txt_file = output_dir / f"{subreddit_name}_{timestamp}.txt"
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"SCRAPER DE REDDIT - REPORTE COMPLETO\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Subreddit: r/{scraped_data['subreddit']}\n")
            f.write(f"Fecha de scrape: {scraped_data['scrape_date']}\n")
            f.write(f"Método de ordenamiento: {scraped_data['sort_method']}\n")
            f.write(f"Total de posts: {scraped_data['total_posts']}\n")
            f.write(f"Total de comentarios: {scraped_data['total_comments']}\n")
            f.write(f"\n" + "=" * 50 + "\n\n")
            
            for i, post in enumerate(scraped_data['posts'], 1):
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
        
        # Mostrar resultados
        print(f"\n" + "=" * 60)
        print("RESULTADOS DEL SCRAPING")
        print("=" * 60)
        print(f"Subreddit: r/{subreddit_name}")
        print(f"Posts procesados: {scraped_data['total_posts']}")
        print(f"Comentarios extraídos: {scraped_data['total_comments']}")
        print(f"Archivo JSON: {json_file}")
        print(f"Archivo texto: {txt_file}")
        
        # Mostrar algunos ejemplos
        print(f"\nEJEMPLOS DE POSTS EXTRAIDOS:")
        print("-" * 40)
        for i, post in enumerate(scraped_data['posts'][:3], 1):
            print(f"{i}. {post['title'][:60]}...")
            print(f"   Score: {post['score']}, Comentarios: {len(post['comments'])}")
            if post['flair_text']:
                print(f"   Flair: {post['flair_text']}")
        
        return True
        
    except Exception as e:
        print(f"Error durante el scraping: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_reddit_scraper()
    if success:
        print(f"\nPrueba completada exitosamente!")
        print(f"Los archivos estan guardados en la carpeta 'scraped_data'")
    else:
        print(f"\nLa prueba fallo. Revisa los errores arriba.")
