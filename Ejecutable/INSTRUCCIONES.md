# LED Screen Test Generator - Ejecutable Portable

## 📱 Acerca de este programa

**LED Screen Test Generator Portable** es una herramienta para crear imágenes de test personalizadas para montajes de pantallas LED. Este ejecutable es completamente portable y no requiere instalación.

## ✅ Características del ejecutable

- **🚀 Completamente portable**: No requiere instalación ni Python
- **💾 Archivo único**: Un solo .exe de 25MB
- **🖥️ Compatible**: Windows 7, 8, 10, 11 (32 y 64 bits)
- **🔒 Seguro**: Sin modificaciones al registro del sistema
- **📁 Portable**: Funciona desde USB, red compartida, etc.

## 🎯 Cómo usar

1. **Ejecutar**: Simplemente haz doble clic en `LED_Screen_Test_Generator_Portable.exe`
2. **Configurar**: Ajusta los parámetros según tus necesidades:
   - Tamaño total de la imagen (píxeles)
   - Número de columnas y filas
   - Altura individual de cada fila
   - Esquema de colores (test_card recomendado)
3. **Generar**: Usa "Vista Previa" para verificar y "Generar y Guardar" para crear la imagen final

## 🎨 Esquemas de colores disponibles

- **test_card**: Colores vivos tipo carta de ajuste (recomendado)
- **primary_colors**: Solo colores primarios y secundarios
- **rainbow**: Gradiente de arco iris
- **gradient**: Gradiente personalizado

## 🔧 Configuración típica

**Para pantalla LED 2560x1152:**
- Tamaño total: 2560 x 1152 píxeles
- Columnas: 20 (128px cada una)
- Filas: 5
  - Filas 1-4: 256px de alto
  - Fila 5: 128px de alto
- Esquema: test_card
- Mostrar números: ✅ Activado
- Mostrar cuadrícula: ✅ Activado

## 💡 Consejos de uso

- **Primera ejecución**: Puede tardar unos segundos en arrancar
- **Números grandes**: Se dimensionan automáticamente según el tamaño de celda
- **Colores contrastantes**: El texto se adapta automáticamente al fondo
- **Vista previa**: Siempre verifica antes de generar la imagen final
- **Formatos soportados**: PNG (recomendado), JPEG, BMP

## 📋 Casos de uso

- **Calibración de pantallas LED**: Verificar alineación de módulos
- **Test de colores**: Comprobar uniformidad de color
- **Mapeo de píxeles**: Identificar cada sección fácilmente
- **Control de calidad**: Detectar píxeles muertos o módulos defectuosos

## 🔍 Solución de problemas

### El programa tarda en arrancar
- **Normal**: La primera ejecución descomprime archivos internamente
- **Siguientes usos**: Serán más rápidos

### Antivirus bloquea el ejecutable
- **Falso positivo**: Común con ejecutables empaquetados
- **Solución**: Agregar excepción en el antivirus

### Error "No se puede abrir el archivo"
- **Permisos**: Ejecutar como administrador
- **Ubicación**: Mover a una carpeta con permisos de escritura

### Imágenes muy grandes
- **Límite de memoria**: Para imágenes enormes (>10000x10000)
- **Solución**: Reducir tamaño o usar vista previa

## 📄 Información técnica

- **Tamaño**: 25.11 MB
- **Tecnología**: Python empaquetado con PyInstaller
- **Librerías incluidas**: Tkinter, PIL (Pillow), tkinter.ttk
- **Sin dependencias externas**: Todo incluido en el ejecutable

## 📞 Soporte

Este ejecutable fue generado automáticamente. Para problemas o sugerencias:
- Verificar que tu sistema cumple los requisitos mínimos
- Probar en modo administrador si hay errores de permisos
- Comprobar que no hay conflictos con software de seguridad

---

**¡Disfruta creando imágenes de test profesionales para tus pantallas LED!** 🎉
