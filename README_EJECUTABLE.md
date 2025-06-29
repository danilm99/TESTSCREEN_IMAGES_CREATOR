# Crear Ejecutable Portable

Este proyecto incluye herramientas para crear un archivo ejecutable (.exe) completamente portable del Generador de Imágenes de Test para Pantallas LED.

## Métodos para crear el ejecutable

### Método 1: Automático (Recomendado)
1. Haz doble clic en `crear_ejecutable.bat`
2. Sigue las instrucciones en pantalla
3. El ejecutable se creará en la carpeta `Ejecutable`

### Método 2: Manual con Python
1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta el creador:
   ```bash
   python create_executable.py
   ```

### Método 3: PyInstaller directo
1. Instala PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Crea el ejecutable:
   ```bash
   pyinstaller --onefile --windowed --name="LED_Screen_Test_Generator" led_screen_test_generator.py
   ```

### Método 4: Con archivo de configuración avanzado
```bash
pyinstaller led_generator.spec
```

## Características del ejecutable

✅ **Completamente portable**: No requiere instalación
✅ **Sin dependencias**: No necesita Python instalado
✅ **Multiplataforma Windows**: Funciona en Windows 7, 8, 10, 11
✅ **Sin consola**: Solo interfaz gráfica
✅ **Tamaño optimizado**: Aproximadamente 25-35 MB
✅ **Arranque rápido**: Primera ejecución descomprime internamente

## Estructura de salida

```
Ejecutable/
└── LED_Screen_Test_Generator.exe    # Archivo ejecutable portable
```

## Distribución

El archivo `.exe` generado es completamente autónomo:

- **Cópialo a cualquier PC Windows**
- **No requiere instalación**
- **No deja rastros en el registro**
- **Funciona desde USB, red, etc.**

## Solución de problemas

### Error: "PyInstaller no encontrado"
```bash
pip install pyinstaller
```

### Error: "No se puede crear el ejecutable"
- Verifica permisos de escritura
- Ejecuta como administrador si es necesario
- Cierra antivirus temporalmente

### Ejecutable muy grande
- El tamaño es normal (25-35 MB)
- Incluye Python y todas las librerías
- No se puede reducir significativamente

### Arranque lento la primera vez
- Es normal en la primera ejecución
- PyInstaller descomprime internamente
- Ejecuciones posteriores son más rápidas

## Archivos incluidos

- `crear_ejecutable.bat` - Script automático (Windows)
- `create_executable.py` - Creador con Python
- `led_generator.spec` - Configuración avanzada
- `version_info.txt` - Información de versión
- `requirements.txt` - Dependencias actualizadas

## Notas técnicas

- **PyInstaller**: Empaqueta Python + librerías en un solo .exe
- **UPX**: Compresión adicional (opcional)
- **Ventana única**: Sin consola de comandos
- **Imports ocultos**: Incluye todas las dependencias automáticamente
