# Reddit Scraper Original (tkinter)

Este es el scraper **original** con interfaz gráfica usando tkinter. Es más fácil de usar para principiantes.

## 🎨 Características

- ✅ **Interfaz gráfica** con tkinter
- ✅ **Barra de progreso** en tiempo real
- ✅ **Estadísticas en vivo** durante el scraping
- ✅ **Controles visuales** fáciles de usar
- ✅ **Log de actividad** detallado
- ✅ **Configuración visual** de parámetros

## 📁 Archivos

- `reddit_scraper.py` - Scraper principal
- `reddit_scraper_gui.py` - Interfaz gráfica
- `test_nms_simple.py` - Versión simple de consola
- `ejemplo_uso.py` - Ejemplos de uso
- `run_gui_original.bat` - Archivo .bat para Windows

## 🎯 Cómo usar

### Opción 1: Interfaz gráfica (Recomendado)
```bash
# Doble clic en:
run_gui_original.bat
```

### Opción 2: Comando directo
```bash
python reddit_scraper_gui.py
```

### Opción 3: Versión simple
```bash
python test_nms_simple.py
```

## 🖥️ Interfaz gráfica

La interfaz incluye:

- **Configuración visual**: Subreddit, método, límites
- **Barra de progreso**: Avance en tiempo real
- **Estadísticas en vivo**: Posts, comentarios, imágenes
- **Log de actividad**: Mensajes detallados
- **Controles**: Iniciar, detener, abrir carpeta

## ⚙️ Configuración

- **Subreddit**: Campo de texto para ingresar subreddit
- **Método**: Dropdown (hot, new, top, rising)
- **Filtro de tiempo**: Dropdown (all, hour, day, week, month, year)
- **Límites**: Spinboxes para posts y comentarios
- **Opciones**: Checkboxes para imágenes, JSON, texto

## 📊 Ejemplo de uso

1. Ejecuta `run_gui_original.bat`
2. Configura el subreddit (ej: NMSCoordinateExchange)
3. Selecciona método (ej: hot)
4. Establece límites (ej: 50 posts, 10 comentarios)
5. Haz clic en "Iniciar Scraping"
6. Observa el progreso en tiempo real

## 📁 Archivos generados

```
scraped_data/
├── images/
│   └── post_id_1/
│       ├── image_1.jpg
│       └── image_2.jpg
├── subreddit_20251022_120000.json
└── subreddit_20251022_120000.txt
```

## 🔧 Requisitos

- Python 3.7+
- tkinter: `pip install tk` (generalmente incluido)
- requests: `pip install requests`

## 🎉 Ventajas

- **Fácil de usar**: Interfaz visual intuitiva
- **Progreso visual**: Barras de progreso y estadísticas
- **Configuración simple**: Controles gráficos
- **Log detallado**: Mensajes en tiempo real
- **Ideal para principiantes**: No requiere comandos

## ⚠️ Limitaciones

- **Menos rápido** que Scrapy
- **Procesamiento secuencial** (no paralelo)
- **Manejo de errores básico**
- **Limitado a cientos de posts**

¡Perfecto para usuarios que prefieren interfaces gráficas!
