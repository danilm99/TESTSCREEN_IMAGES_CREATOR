# Generador de Ejecutable Portable
# Este script crea un archivo .exe que no requiere Python instalado

# Instalar PyInstaller
# pip install pyinstaller

# Crear ejecutable
# pyinstaller --onefile --windowed --name="LED_Screen_Test_Generator" led_screen_test_generator.py

# Opciones:
# --onefile: Crea un solo archivo ejecutable
# --windowed: No muestra consola (solo interfaz gráfica)
# --name: Nombre del ejecutable
# --icon: Icono del ejecutable (opcional)

import subprocess
import sys
import os

def install_pyinstaller():
    """Instala PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("PyInstaller ya está instalado.")
        return True
    except ImportError:
        print("Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller instalado correctamente.")
            return True
        except subprocess.CalledProcessError:
            print("Error al instalar PyInstaller.")
            return False

def create_executable():
    """Crea el ejecutable portable"""
    if not install_pyinstaller():
        return False
    
    print("Creando ejecutable portable...")
    
    # Comando para crear el ejecutable
    cmd = [
        "pyinstaller",
        "--onefile",           # Un solo archivo
        "--windowed",          # Sin consola
        "--name=LED_Screen_Test_Generator",  # Nombre del ejecutable
        "--distpath=./dist",   # Carpeta de salida
        "--workpath=./build",  # Carpeta temporal
        "--specpath=./",       # Archivo spec
        "led_screen_test_generator.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n¡Ejecutable creado exitosamente!")
        print("Ubicación: ./dist/LED_Screen_Test_Generator.exe")
        print("\nEste archivo .exe es portable y puede ejecutarse en cualquier")
        print("sistema Windows sin necesidad de tener Python instalado.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al crear ejecutable: {e}")
        return False
    except FileNotFoundError:
        print("PyInstaller no encontrado. Instalando...")
        if install_pyinstaller():
            return create_executable()
        return False

if __name__ == "__main__":
    print("=== Generador de Ejecutable Portable ===")
    print("Este script creará un archivo .exe portable del generador de imágenes LED")
    print()
    
    success = create_executable()
    
    if success:
        print("\n=== INSTRUCCIONES DE USO ===")
        print("1. El archivo ejecutable está en la carpeta 'dist'")
        print("2. Puedes copiar LED_Screen_Test_Generator.exe a cualquier PC")
        print("3. No necesita instalación ni Python")
        print("4. Simplemente haz doble clic para ejecutar")
        print("\nNota: El primer arranque puede ser más lento mientras se")
        print("descomprime internamente.")
    else:
        print("\nError: No se pudo crear el ejecutable.")
        print("Verifica que tengas permisos de escritura en la carpeta.")
