@echo off
echo ===============================================
echo    Creador de Ejecutable Portable LED
echo ===============================================
echo.
echo Este script creara un archivo .exe portable
echo que funcionara en cualquier PC Windows sin
echo necesidad de tener Python instalado.
echo.
pause

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Creando ejecutable portable...
pyinstaller --onefile --windowed --name="LED_Screen_Test_Generator" --distpath="./Ejecutable" led_screen_test_generator.py

echo.
if exist "Ejecutable\LED_Screen_Test_Generator.exe" (
    echo ¡EXITO! Ejecutable creado correctamente.
    echo.
    echo Ubicacion: Ejecutable\LED_Screen_Test_Generator.exe
    echo.
    echo Este archivo .exe es completamente portable:
    echo - No requiere instalacion
    echo - No requiere Python
    echo - Funciona en cualquier PC Windows
    echo - Tamaño aproximado: 20-30 MB
    echo.
    echo ¿Deseas abrir la carpeta del ejecutable?
    pause
    explorer "Ejecutable"
) else (
    echo ERROR: No se pudo crear el ejecutable.
    echo Verifica que tengas permisos de escritura.
)

echo.
echo Limpiando archivos temporales...
if exist "build" rmdir /s /q "build"
if exist "LED_Screen_Test_Generator.spec" del "LED_Screen_Test_Generator.spec"

echo.
echo Proceso completado.
pause
