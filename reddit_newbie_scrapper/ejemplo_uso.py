#!/usr/bin/env python3
"""
Ejemplo de uso del Reddit Scraper
Este script muestra diferentes formas de usar el scraper
"""

from reddit_scraper import RedditScraper
import json

def ejemplo_basico():
    """Ejemplo básico de uso del scraper"""
    print("=== EJEMPLO BÁSICO ===")
    
    # Crear instancia del scraper
    scraper = RedditScraper()
    
    # Scrapear un subreddit específico
    print("Scrapeando r/python...")
    data = scraper.scrape_subreddit('python', sort_by='hot')
    
    # Mostrar estadísticas
    print(f"Posts procesados: {data['total_posts']}")
    print(f"Imágenes descargadas: {data.get('total_images_downloaded', 0)}")
    
    # Guardar datos
    json_file = scraper.save_to_json(data)
    txt_file = scraper.save_to_text(data)
    
    print(f"Datos guardados en:")
    print(f"  JSON: {json_file}")
    print(f"  Texto: {txt_file}")

def ejemplo_multiple_subreddits():
    """Ejemplo scrapeando múltiples subreddits"""
    print("\n=== EJEMPLO MÚLTIPLES SUBREDDITS ===")
    
    scraper = RedditScraper()
    
    # Lista de subreddits a scrapear
    subreddits = ['python', 'MachineLearning', 'datascience']
    
    print(f"Scrapeando: {', '.join(subreddits)}")
    results = scraper.scrape_multiple_subreddits(subreddits, sort_by='top')
    
    # Mostrar resultados
    for subreddit, result in results.items():
        if 'error' in result:
            print(f"❌ r/{subreddit}: Error - {result['error']}")
        else:
            print(f"✅ r/{subreddit}: {result['posts_count']} posts, {result['images_count']} imágenes")

def ejemplo_solo_datos():
    """Ejemplo sin descarga de imágenes"""
    print("\n=== EJEMPLO SIN IMÁGENES ===")
    
    scraper = RedditScraper()
    scraper.download_images = False  # Deshabilitar descarga de imágenes
    
    print("Scrapeando r/artificial sin imágenes...")
    data = scraper.scrape_subreddit('artificial', sort_by='new')
    
    print(f"Posts procesados: {data['total_posts']}")
    print("Imágenes descargadas: 0 (deshabilitado)")

def ejemplo_filtros_avanzados():
    """Ejemplo con diferentes filtros"""
    print("\n=== EJEMPLO CON FILTROS ===")
    
    scraper = RedditScraper()
    
    # Scrapear posts más votados de la semana
    print("Scrapeando posts más votados de la semana...")
    data = scraper.scrape_subreddit('programming', sort_by='top', time_filter='week')
    
    print(f"Posts procesados: {data['total_posts']}")
    print(f"Imágenes descargadas: {data.get('total_images_downloaded', 0)}")

def ejemplo_analisis_datos():
    """Ejemplo de análisis básico de los datos"""
    print("\n=== EJEMPLO ANÁLISIS DE DATOS ===")
    
    scraper = RedditScraper()
    
    # Scrapear datos
    data = scraper.scrape_subreddit('python', sort_by='hot')
    
    # Análisis básico
    posts = data['posts']
    
    # Estadísticas
    total_score = sum(post['score'] for post in posts)
    avg_score = total_score / len(posts) if posts else 0
    
    nsfw_posts = sum(1 for post in posts if post['nsfw'])
    locked_posts = sum(1 for post in posts if post['locked'])
    
    # Posts con más comentarios
    top_commented = sorted(posts, key=lambda x: x['num_comments'], reverse=True)[:3]
    
    print(f"Análisis de r/{data['subreddit']}:")
    print(f"  Total posts: {len(posts)}")
    print(f"  Score promedio: {avg_score:.1f}")
    print(f"  Posts NSFW: {nsfw_posts}")
    print(f"  Posts bloqueados: {locked_posts}")
    print(f"  Posts con más comentarios:")
    
    for i, post in enumerate(top_commented, 1):
        print(f"    {i}. {post['title'][:50]}... ({post['num_comments']} comentarios)")

def main():
    """Función principal con menú de ejemplos"""
    print("Reddit Scraper - Ejemplos de Uso")
    print("=" * 40)
    
    ejemplos = {
        '1': ('Ejemplo básico', ejemplo_basico),
        '2': ('Múltiples subreddits', ejemplo_multiple_subreddits),
        '3': ('Sin imágenes', ejemplo_solo_datos),
        '4': ('Con filtros', ejemplo_filtros_avanzados),
        '5': ('Análisis de datos', ejemplo_analisis_datos),
        '6': ('Todos los ejemplos', lambda: [func() for _, func in ejemplos.values() if func != lambda: [func() for _, func in ejemplos.values()]])
    }
    
    print("Selecciona un ejemplo:")
    for key, (name, _) in ejemplos.items():
        print(f"  {key}. {name}")
    
    print("  0. Salir")
    
    choice = input("\nOpción: ").strip()
    
    if choice == '0':
        print("¡Hasta luego!")
        return
    
    if choice in ejemplos:
        try:
            ejemplos[choice][1]()
        except Exception as e:
            print(f"Error ejecutando ejemplo: {str(e)}")
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()
