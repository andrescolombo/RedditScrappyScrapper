#!/usr/bin/env python3
"""
Script de instalación y configuración del Reddit Scraper
"""

import os
import sys
import subprocess
from pathlib import Path

def instalar_dependencias():
    """Instalar las dependencias del proyecto"""
    print("Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def crear_archivo_env():
    """Crear archivo .env con configuración básica"""
    env_file = Path(".env")
    example_file = Path("config.env.example")
    
    if env_file.exists():
        print("⚠️  El archivo .env ya existe")
        overwrite = input("¿Sobrescribir? (y/n): ").lower()
        if overwrite != 'y':
            return True
    
    if not example_file.exists():
        print("❌ Archivo config.env.example no encontrado")
        return False
    
    try:
        # Copiar contenido del ejemplo
        with open(example_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Archivo .env creado")
        print("📝 Edita el archivo .env con tus credenciales de Reddit")
        return True
        
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False

def verificar_credenciales():
    """Verificar si las credenciales están configuradas"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'tu_client_id_aqui' in content or 'tu_client_secret_aqui' in content:
            print("⚠️  Las credenciales de Reddit no están configuradas")
            print("📝 Edita el archivo .env con tus credenciales reales")
            return False
        
        print("✅ Credenciales configuradas")
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo archivo .env: {e}")
        return False

def crear_directorios():
    """Crear directorios necesarios"""
    directories = ['scraped_data', 'scraped_data/images']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directorios creados")

def mostrar_instrucciones_reddit():
    """Mostrar instrucciones para obtener credenciales de Reddit"""
    print("\n" + "="*60)
    print("INSTRUCCIONES PARA OBTENER CREDENCIALES DE REDDIT")
    print("="*60)
    print("1. Ve a https://www.reddit.com/prefs/apps")
    print("2. Haz clic en 'Create App' o 'Create Another App'")
    print("3. Completa el formulario:")
    print("   - Name: RedditScraper (o cualquier nombre)")
    print("   - App type: Script")
    print("   - Description: Scraper personal")
    print("   - About URL: (dejar vacío)")
    print("   - Redirect URI: http://localhost:8080")
    print("4. Haz clic en 'Create app'")
    print("5. Copia el 'client ID' y 'client secret'")
    print("6. Edita el archivo .env con estos valores")
    print("="*60)

def test_conexion():
    """Probar la conexión con Reddit"""
    print("\nProbando conexión con Reddit...")
    
    try:
        from reddit_scraper import RedditScraper
        scraper = RedditScraper()
        
        # Intentar acceder a un subreddit público
        subreddit = scraper.reddit.subreddit('test')
        print(f"✅ Conexión exitosa! Subreddit de prueba: r/{subreddit.display_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("Verifica tus credenciales en el archivo .env")
        return False

def main():
    """Función principal de instalación"""
    print("Reddit Scraper - Instalador")
    print("=" * 40)
    
    # Verificar Python
    if sys.version_info < (3, 7):
        print("❌ Se requiere Python 3.7 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Instalar dependencias
    if not instalar_dependencias():
        sys.exit(1)
    
    # Crear directorios
    crear_directorios()
    
    # Crear archivo .env
    if not crear_archivo_env():
        sys.exit(1)
    
    # Verificar credenciales
    if not verificar_credenciales():
        mostrar_instrucciones_reddit()
        print("\n⚠️  Configura tus credenciales y ejecuta este script nuevamente")
        return
    
    # Probar conexión
    if test_conexion():
        print("\n🎉 ¡Instalación completada exitosamente!")
        print("\nPuedes ejecutar el scraper con:")
        print("  python reddit_scraper.py")
        print("  python ejemplo_uso.py")
    else:
        print("\n⚠️  Instalación completada pero hay problemas de conexión")
        print("Verifica tus credenciales de Reddit")

if __name__ == "__main__":
    main()
