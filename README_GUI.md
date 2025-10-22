# Reddit Scrapy GUI - Documentación

## 📋 Descripción

GUI personalizada para el scraper de Reddit usando el framework Scrapy. Proporciona una interfaz gráfica fácil de usar para configurar y ejecutar scraping de subreddits.

## 🚀 Instalación

### Dependencias
```bash
pip install -r requirements.txt
```

### Dependencias principales:
- `scrapy==2.11.0` - Framework de scraping
- `tkinter` - GUI (incluido con Python)
- `requests==2.31.0` - HTTP requests
- `beautifulsoup4==4.12.2` - Parsing HTML
- `lxml==4.9.3` - Parser XML/HTML
- `pandas==2.0.3` - Manipulación de datos

## 🎯 Uso

### Ejecución básica
```bash
python reddit_scrapy_gui_simple.py
```

### Ejecución con batch file
```bash
# Doble clic en:
run_scrapy_gui.bat
```

## ⚙️ Configuración

### Parámetros disponibles:
- **Subreddit**: Nombre del subreddit (ej: `NMSCoordinateExchange`)
- **Método**: `hot`, `new`, `top`, `rising`
- **Filtro de tiempo**: `all`, `hour`, `day`, `week`, `month`, `year`
- **Máximo Posts**: Número de posts a scrapear
- **Máximo Comentarios**: Comentarios por post

### Ejemplo de configuración:
```
Subreddit: NMSCoordinateExchange
Método: hot
Filtro: all
Posts: 10
Comentarios: 5
```

## 📁 Estructura de archivos

```
reddit_scrappy/
├── reddit_scraper/
│   ├── spiders/
│   │   └── reddit_spider.py
│   ├── pipelines.py
│   └── settings.py
├── run_scraper.py
└── scraped_data_scrapy/  # Resultados
    ├── *.json
    ├── *.csv
    └── images/
```

## 🧪 Testing

### Tests unitarios
```bash
python test_scrapy_gui.py
```

### Tests de integración
```bash
python test_scrapy_integration.py
```

### Test funcional simple
```bash
python test_gui_simple.py
```

### Test de captura de salida
```bash
python test_gui_output.py
```

### Test final
```bash
python test_final.py
```

## 📊 Resultados

### Archivos generados:
- **JSON**: Datos estructurados de posts y comentarios
- **CSV**: Datos en formato tabla
- **Imágenes**: Imágenes descargadas de los posts

### Ubicación:
```
reddit_scrappy/scraped_data_scrapy/
├── reddit_YYYY-MM-DDTHH-MM-SS.json
├── reddit_YYYY-MM-DDTHH-MM-SS.csv
└── images/
    └── subreddit/
        └── post_id/
            └── image.jpg
```

## 🔧 Variables de entorno

No se requieren variables de entorno. El scraper funciona con acceso público a Reddit.

## 🐛 Solución de problemas

### Error: "No se encuentra el archivo"
- Verificar que estás en el directorio correcto
- Ejecutar desde la raíz del proyecto

### Error: "No se captura la salida"
- Verificar que Scrapy está instalado
- Revisar logs en la consola

### Error: "No se generan archivos"
- Verificar permisos de escritura
- Revisar que el subreddit existe

## 📝 Logs

Los logs se muestran en tiempo real en la GUI con formato:
```
[HH:MM:SS] Mensaje de log
```

## 🚀 Ejemplo de ejecución

1. Abrir `reddit_scrapy_gui_simple.py`
2. Configurar parámetros:
   - Subreddit: `NMSCoordinateExchange`
   - Posts: `5`
   - Comentarios: `3`
3. Hacer clic en "Iniciar Scraping"
4. Observar progreso en el log
5. Revisar resultados en `scraped_data_scrapy/`

## 📈 Rendimiento

- **Velocidad**: ~1-2 posts por segundo
- **Memoria**: ~50MB para 100 posts
- **Almacenamiento**: ~1MB por post (incluyendo imágenes)

## 🔒 Seguridad

- No requiere API keys
- Solo acceso de lectura
- Respeta robots.txt de Reddit
- Rate limiting automático
