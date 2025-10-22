# Reddit Scraper con Scrapy (Profesional)

Este es el scraper **profesional** usando el framework Scrapy. Es más rápido, robusto y escalable.

## 🚀 Características

- ✅ **Framework profesional** Scrapy
- ✅ **Muy rápido** - Procesamiento paralelo
- ✅ **Descarga automática** de imágenes
- ✅ **Manejo robusto** de errores
- ✅ **Escalable** - Miles de posts
- ✅ **Exportación múltiple** - JSON, CSV, imágenes

## 📁 Archivos

- `reddit_scraper/` - Proyecto Scrapy completo
- `run_scraper.py` - Script para ejecutar Scrapy
- `run_scraper_scrapy.bat` - Archivo .bat para Windows

## 🎯 Cómo usar

### Opción 1: Archivo .bat (Recomendado)
```bash
# Doble clic en:
run_scraper_scrapy.bat
```

### Opción 2: Comando directo
```bash
python run_scraper.py --subreddit NMSCoordinateExchange --sort hot --max-posts 50
```

### Opción 3: Modo interactivo
```bash
python run_scraper.py --interactive
```

## ⚙️ Parámetros disponibles

- `--subreddit` - Subreddit a scrapear
- `--sort` - Método (hot, new, top, rising)
- `--time-filter` - Filtro de tiempo (all, hour, day, week, month, year)
- `--max-posts` - Máximo posts
- `--max-comments` - Máximo comentarios por post

## 📊 Ejemplo de uso

```bash
# Scrapear 100 posts más votados de esta semana
python run_scraper.py --subreddit NMSCoordinateExchange --sort top --time-filter week --max-posts 100 --max-comments 15
```

## 📁 Archivos generados

```
scraped_data/
├── images/
│   └── NMSCoordinateExchange/
│       ├── post_id_1/
│       │   ├── image_1.jpg
│       │   └── image_2.jpg
│       └── post_id_2/
│           └── image_1.jpg
├── reddit_2025-10-22T11-49-57+00-00.json
└── reddit_2025-10-22T11-49-57+00-00.csv
```

## 🔧 Requisitos

- Python 3.7+
- Scrapy: `pip install scrapy`

## 🎉 Ventajas sobre el scraper original

| Característica | Scrapy | Original |
|----------------|--------|----------|
| Velocidad | ⚡⚡⚡ | ⚡⚡ |
| Concurrencia | ✅ Paralelo | ❌ Secuencial |
| Robustez | ✅ Profesional | ⚠️ Básico |
| Escalabilidad | ✅ Miles de posts | ⚠️ Limitado |
| Manejo de errores | ✅ Avanzado | ⚠️ Básico |
| Descarga de imágenes | ✅ Automática | ⚠️ Manual |

¡Este es el scraper recomendado para uso profesional!
