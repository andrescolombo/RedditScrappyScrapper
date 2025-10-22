# 🚀 Reddit Scraper - Proyecto Completo

Este proyecto contiene **DOS scrapers diferentes** para extraer datos de Reddit:

## 📁 Estructura del Proyecto

```
Reddit Scrapper/
├── reddit_newbie_scrapper/     # 🎨 Scraper con GUI (tkinter)
├── reddit_scrappy/            # ⚡ Scraper Profesional (Scrapy)
├── run_gui.bat               # 🖥️ Ejecutar GUI (tkinter)
├── run_scraper.bat           # 🚀 Ejecutar Scrapy
├── run_scraper_debug.bat     # 🔍 Ejecutar Scrapy con logging
├── run_scrapy_gui.bat        # 🎨 Ejecutar GUI para Scrapy
├── reddit_scrapy_gui.py      # 🖥️ GUI personalizada para Scrapy
├── limpiar_datos.bat         # 🗑️ Limpiar datos (con confirmación)
├── limpiar_rapido.bat        # ⚡ Limpiar datos (rápido)
└── requirements.txt          # 📦 Dependencias
```

## 🎯 ¿Cuál usar?

### 🎨 **reddit_newbie_scrapper** (GUI)
- ✅ **Interfaz gráfica** fácil de usar
- ✅ **Progreso en tiempo real**
- ✅ **Filtros de tiempo** como Reddit
- ✅ **Ideal para principiantes**

### ⚡ **reddit_scrappy** (Profesional)
- ✅ **Framework Scrapy** profesional
- ✅ **Muy rápido** (procesamiento paralelo)
- ✅ **Logging detallado**
- ✅ **Exportación** a JSON y CSV
- ✅ **Ideal para uso intensivo**

## 🚀 Inicio Rápido

### Opción 1: GUI (Fácil)
```bash
# Doble clic en:
run_gui.bat
```

### Opción 2: Scrapy (Profesional)
```bash
# Doble clic en:
run_scrapy_gui.bat       # ← GUI para Scrapy (recomendado)
# O
run_scraper_debug.bat    # ← CON LOGGING
# O
run_scraper.bat          # ← Normal
```

## 🗑️ Limpiar Datos

### Opción 1: Con confirmación (Seguro)
```bash
# Doble clic en:
limpiar_datos.bat
```

### Opción 2: Rápido (Sin confirmación)
```bash
# Doble clic en:
limpiar_rapido.bat
```

**¿Qué borra?**
- ✅ Datos JSON y CSV
- ✅ Imágenes descargadas
- ✅ Logs de Scrapy
- ✅ Carpetas temporales

## 📦 Instalación

```bash
pip install -r requirements.txt
```

## 📊 Datos Extraídos

- ✅ **Posts** (título, contenido, votos, fecha)
- ✅ **Comentarios** (texto, votos, respuestas)
- ✅ **Imágenes** (descarga automática)
- ✅ **Metadatos** (autor, subreddit, enlaces)

## 🎛️ Configuración

### GUI Scraper
- Subreddit personalizable
- Métodos: hot, new, top, rising
- Filtros de tiempo: all, hour, day, week, month, year
- Límites configurables

### Scrapy Scraper
- Parámetros por línea de comandos
- Logging detallado
- Exportación múltiple (JSON, CSV)
- Manejo robusto de errores

## 📁 Archivos Generados

### GUI Scraper
```
reddit_newbie_scrapper/scraped_data/
├── images/              # Imágenes descargadas
├── report.txt          # Reporte completo
└── data.json           # Datos estructurados
```

### Scrapy Scraper
```
reddit_scrappy/scraped_data_scrapy/
├── images/              # Imágenes descargadas
├── *.json              # Datos JSON
└── *.csv               # Datos CSV
```

## 🔧 Tecnologías

- **Python 3.8+**
- **tkinter** (GUI)
- **Scrapy** (Framework profesional)
- **requests** (HTTP)
- **BeautifulSoup** (HTML parsing)
- **aiohttp** (Descarga asíncrona)

## 📝 Notas

- Ambos scrapers son **independientes**
- Puedes usar **cualquiera** según tus necesidades
- El **GUI** es más fácil para principiantes
- El **Scrapy** es más potente para uso profesional

---

**¡Elige el que mejor se adapte a tus necesidades!** 🎯