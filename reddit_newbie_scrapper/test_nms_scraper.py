#!/usr/bin/env python3
"""
Script de prueba del Reddit Scraper para r/NMSCoordinateExchange
Este script funciona sin credenciales de Reddit usando solo lectura pública
"""

import praw
import os
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
    """Probar el scraper con r/NMSCoordinateExchange"""
    
    print("Reddit Scraper - Prueba con r/NMSCoordinateExchange")
    print("=" * 60)
    
    try:
        # Configurar Reddit con credenciales mínimas (solo lectura)
        reddit = praw.Reddit(
            client_id="dummy_client_id",  # No necesario para lectura pública
            client_secret="dummy_secret",  # No necesario para lectura pública
            user_agent="RedditScraper/1.0 by AndresColombo"
        )
        
        # Acceder al subreddit
        subreddit_name = "NMSCoordinateExchange"
        subreddit = reddit.subreddit(subreddit_name)
        
        print(f"Accediendo a r/{subreddit_name}...")
        print(f"Descripción: {subreddit.description[:100]}...")
        print(f"Suscriptores: {subreddit.subscribers:,}")
        print(f"Posts activos: {subreddit.active_user_count}")
        
        # Crear directorio de salida
        output_dir = Path("scraped_data")
        output_dir.mkdir(exist_ok=True)
        
        # Configurar límites para la prueba
        max_posts = 10  # Solo 10 posts para la prueba
        max_comments = 5  # Solo 5 comentarios por post
        
        print(f"\nExtrayendo {max_posts} posts con máximo {max_comments} comentarios cada uno...")
        
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
        posts_processed = 0
        for post in subreddit.hot(limit=max_posts):
            try:
                print(f"\nProcesando post {posts_processed + 1}: {post.title[:50]}...")
                
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
                    'domain': post.domain,
                    'comments': []
                }
                
                # Extraer comentarios si no está bloqueado
                if not post.locked and post.num_comments > 0:
                    print(f"  Extrayendo comentarios...")
                    
                    # Expandir comentarios
                    post.comments.replace_more(limit=0)
                    
                    comments_count = 0
                    for comment in post.comments.list()[:max_comments]:
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
                                'depth': comment.depth if hasattr(comment, 'depth') else 0
                            }
                            post_data['comments'].append(comment_data)
                            comments_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error procesando comentario: {str(e)}")
                            continue
                    
                    print(f"  Comentarios extraídos: {comments_count}")
                    scraped_data['total_comments'] += comments_count
                
                scraped_data['posts'].append(post_data)
                scraped_data['total_posts'] += 1
                posts_processed += 1
                
                # Pausa para ser respetuoso con la API
                time.sleep(0.5)
                
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
        print(f"✅ Subreddit: r/{subreddit_name}")
        print(f"📊 Posts procesados: {scraped_data['total_posts']}")
        print(f"💬 Comentarios extraídos: {scraped_data['total_comments']}")
        print(f"📄 Archivo JSON: {json_file}")
        print(f"📝 Archivo texto: {txt_file}")
        
        # Mostrar algunos ejemplos
        print(f"\nEJEMPLOS DE POSTS EXTRAÍDOS:")
        print("-" * 40)
        for i, post in enumerate(scraped_data['posts'][:3], 1):
            print(f"{i}. {post['title'][:60]}...")
            print(f"   Score: {post['score']}, Comentarios: {len(post['comments'])}")
            if post['flair_text']:
                print(f"   Flair: {post['flair_text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el scraping: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_reddit_scraper()
    if success:
        print(f"\n🎉 ¡Prueba completada exitosamente!")
        print(f"Los archivos están guardados en la carpeta 'scraped_data'")
    else:
        print(f"\n❌ La prueba falló. Revisa los errores arriba.")
