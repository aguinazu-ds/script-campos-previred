#!/bin/bash

# Script para compilar con PyInstaller localmente (para testing)
# Genera ejecutable Linux para pruebas

echo "========================================="
echo "  COMPILACIÓN LOCAL CON PYINSTALLER"
echo "========================================="
echo

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 no encontrado"
    echo "Instale Python 3: sudo apt-get install python3 python3-venv"
    exit 1
fi

echo "✅ Python encontrado:"
python3 --version
echo

# Crear ambiente virtual si no existe
if [ ! -d ".venv" ]; then
    echo "� Creando ambiente virtual..."
    python3 -m venv .venv
fi

# Activar ambiente virtual
echo "🔌 Activando ambiente virtual..."
source .venv/bin/activate

# Verificar que estamos en el ambiente virtual
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Ambiente virtual activo: $VIRTUAL_ENV"
else
    echo "❌ ERROR: No se pudo activar el ambiente virtual"
    exit 1
fi

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar PyInstaller si no está instalado
if ! pip show pyinstaller &> /dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip install pyinstaller
else
    echo "✅ PyInstaller ya está instalado"
fi

# Verificar PyInstaller
echo "� Verificando PyInstaller..."
pyinstaller --version

echo

# Limpiar compilaciones anteriores
echo "🧹 Limpiando compilaciones anteriores..."
rm -rf build/ dist/ *.spec
rm -f ProcesadorPrevired

echo

# Verificar archivos necesarios
if [ ! -f "procesar_archivos_windows.py" ]; then
    echo "❌ ERROR: No se encuentra procesar_archivos_windows.py"
    exit 1
fi

echo "✅ Archivo fuente encontrado: procesar_archivos_windows.py"
echo

echo "========================================="
echo "   INICIANDO COMPILACIÓN..."
echo "========================================="
echo

# Opciones de compilación explicadas
echo "📋 Opciones de compilación:"
echo "   • --onefile: Un solo ejecutable"
echo "   • --console: Mantener ventana de consola"
echo "   • --name: Nombre del ejecutable"
echo "   • --add-data: Incluir carpetas de datos"
echo

# Compilar con PyInstaller
echo "⚙️  Compilando con PyInstaller..."
pyinstaller \
    --onefile \
    --console \
    --name ProcesadorPrevired \
    --distpath . \
    --workpath build \
    --specpath build \
    procesar_archivos_windows.py

# Verificar el resultado
if [ $? -eq 0 ] && [ -f "ProcesadorPrevired" ]; then
    echo
    echo "========================================="
    echo "   ✅ COMPILACIÓN EXITOSA"
    echo "========================================="
    echo
    
    # Información del ejecutable
    echo "📄 Ejecutable creado: ProcesadorPrevired"
    
    SIZE=$(stat -c%s "ProcesadorPrevired" 2>/dev/null || echo "Desconocido")
    echo "📊 Tamaño: $SIZE bytes (~$(($SIZE/1024/1024)) MB)"
    
    # Verificar permisos
    chmod +x ProcesadorPrevired
    echo "✅ Permisos de ejecución configurados"
    
    # Verificar tipo de archivo
    echo "🔍 Tipo de archivo:"
    file ProcesadorPrevired
    
    echo
    echo "📋 PRUEBA LOCAL:"
    echo "1. Asegúrese de tener archivos en archivos105espacios/"
    echo "2. Verifique jornadas/jornadasTrabajadores.csv"
    echo "3. Ejecute: ./ProcesadorPrevired"
    echo
    echo "⚠️  NOTA: Este es un ejecutable Linux"
    echo "   Para Windows, use GitHub Actions o compile en Windows"
    
    # Opción de prueba inmediata
    echo
    read -p "¿Desea probar el ejecutable ahora? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Ejecutando prueba..."
        ./ProcesadorPrevired
    fi
    
else
    echo
    echo "========================================="
    echo "   ❌ ERROR EN LA COMPILACIÓN"
    echo "========================================="
    echo
    echo "Posibles causas:"
    echo "1. Errores en el código Python"
    echo "2. Dependencias faltantes"
    echo "3. Problemas con PyInstaller"
    echo
    echo "💡 Soluciones:"
    echo "1. Probar el script: python3 procesar_archivos_windows.py"
    echo "2. Revisar los logs de error arriba"
    echo "3. Reinstalar PyInstaller: pip3 install --upgrade pyinstaller"
    exit 1
fi

# Limpiar archivos temporales
echo
echo "🧹 Limpiando archivos temporales..."
rm -rf build/

echo "✅ Limpieza completada"
echo
