# Procesador de Archivos Previred

Script para procesar archivos de ancho fijo de Previred, aplicando transformaciones según jornadas de trabajadores y detectando subsidios.

## 🚀 Compilación Automática con GitHub Actions

La forma más fácil de obtener el ejecutable Windows es usar GitHub Actions con PyInstaller:

### 1. Subir a GitHub
```bash
# Inicializar repositorio Git
git init
git add .
git commit -m "Procesador Previred inicial"

# Subir a GitHub (crear repositorio primero en github.com)
git remote add origin https://github.com/tu-usuario/procesador-previred.git
git push -u origin main
```

### 2. Ejecutar Compilación
- Ve a tu repositorio en GitHub
- Click en "Actions"
- Click en "Compilar Ejecutable Windows"
- Click en "Run workflow"
- Espera ~2-3 minutos

### 3. Descargar Ejecutable
- En "Actions", click en el workflow completado
- Descarga "ProcesadorPrevired-Windows"
- Obtienes `ProcesadorPrevired.exe` compilado con PyInstaller

## 🛠️ Compilación Local (Alternativas)

### Opción 1: PyInstaller Local (Para Pruebas)
```bash
./compilar_local_pyinstaller.sh
```
- Compila ejecutable Linux para testing
- Rápido y confiable
- Ideal para probar el script localmente

### Opción 2: Script Alternativo
```bash
./compilar_alternativo.sh
```
- GUI intuitiva con auto-py-to-exe
- PyInstaller directo
- Opciones Docker

### Opción 3: Wine + Nuitka (Experimental)
```bash
# Instalar dependencias en Wine
./instalar_python_wine.sh

# Compilar (puede tener problemas)
./compilar_con_wine.sh
```

## 📁 Estructura del Proyecto

```
procesador-previred/
├── procesar_archivos_windows.py    # Script principal para Windows
├── procesar_archivos.py            # Script original para Linux
├── generar_jornadas.py             # Generador de archivo de jornadas
├── compilar_local_pyinstaller.sh     # Compilador PyInstaller local (testing)
├── compilar_alternativo.sh         # Compilador con múltiples opciones
├── compilar_con_wine.sh            # Compilador con Wine (experimental)
├── instalar_python_wine.sh         # Instalador de Python en Wine
├── .github/workflows/              # GitHub Actions para compilación automática
├── archivos105espacios/            # Carpeta para archivos .txt de entrada
├── jornadas/                       # Carpeta con jornadasTrabajadores.csv
├── archivos_modificados/           # Carpeta de salida (se crea automáticamente)
└── README*.md                      # Documentación
```

## 📋 Uso del Script

### Preparación
1. Coloque archivos .txt/.TXT en `archivos105espacios/`
2. Asegúrese de tener `jornadas/jornadasTrabajadores.csv` con formato:
   ```csv
   rut;jornada
   12345678-9;1
   98765432-1;2
   ```

### Ejecución
```bash
# Linux
python3 procesar_archivos.py

# Windows (ejecutable)
ProcesadorPrevired.exe
```

### Salida
- Archivos procesados en `archivos_modificados/`
- Los archivos originales NO se modifican
- Validación estricta: se detiene si falta algún RUT

## 📖 Instrucciones Completas para Windows

### REQUISITOS:
- Windows 10/11
- NO requiere Python instalado

### PREPARACIÓN:
1. Descargue el paquete `ProcesadorPrevired_v1.0.zip` desde GitHub Actions
2. Extraiga en su computadora
3. Coloque sus archivos .txt o .TXT en la carpeta `archivos105espacios`
4. Verifique que el archivo `jornadas\jornadasTrabajadores.csv` contenga todos los RUTs

### FORMATO DEL ARCHIVO DE JORNADAS:
```csv
rut;jornada
12345678-9;1
98765432-1;2
```

**Valores de jornada:**
- `1` = Jornada completa
- `2` = Jornada parcial

### USO:
1. Ejecute `ProcesadorPrevired.exe`
2. El programa procesará automáticamente todos los archivos
3. Los resultados aparecerán en la carpeta `archivos_modificados`

### IMPORTANTE:
- **TODOS** los RUTs en los archivos de datos deben estar en `jornadasTrabajadores.csv`
- Si falta algún RUT, el programa se detendrá con un mensaje de error
- Los archivos originales **NUNCA** se modifican

### ESTRUCTURA DE CARPETAS REQUERIDA:
```
ProcesadorPrevired_v1.0/
├── ProcesadorPrevired.exe           # Ejecutable principal
├── archivos105espacios/             # Coloque aquí sus archivos .txt
├── jornadas/                        # Archivo de jornadas
│   └── jornadasTrabajadores.csv
├── archivos_modificados/            # Se crea automáticamente
└── README.md                        # Este archivo
```

## ⚙️ Características

### Procesamiento de Campos
- **Campo 174**: Renta imponible AFP
- **Campo 182**: Cotización AFP (actualizada con fórmula)
- **Campo 740**: Imponible cesantía (solo con subsidio)
- **Campo 748**: Jornada laboral (según CSV)
- **Campo 756**: Cotización expectativa de vida
- **Campo 805**: Imponible seguro cesantía

### Detección de Subsidio
- Códigos de movimiento: `03`, `06`
- Posición 126-128 en archivo
- Afecta procesamiento del campo 740

### Validación de RUTs
- Extracción con dígito verificador
- Formato: `12345678-9`
- Validación contra archivo de jornadas
- Error si falta algún RUT

## 🔧 Resolución de Problemas

### Error: "RUT no encontrado en jornadas"
```
❌ ERROR CRÍTICO: RUT '12345678-9' no encontrado en archivo de jornadas
```
**Solución**: Agregue el RUT al archivo `jornadas/jornadasTrabajadores.csv`

### Error: "Archivo de jornadas no encontrado"
**Solución**: Cree el archivo `jornadas/jornadasTrabajadores.csv` con formato correcto

### Error: "No se encontraron archivos .txt"
**Solución**: Coloque archivos .txt o .TXT en la carpeta `archivos105espacios/`

### Problemas con Wine
```bash
# Reconfigurar Wine
winecfg

# Reinstalar Python en Wine
rm -rf ~/.wine-nuitka
./instalar_python_wine.sh
```

## 📊 Rendimiento

### PyInstaller vs Nuitka
| Aspecto | PyInstaller | Nuitka |
|---------|-------------|--------|
| **Velocidad** | Velocidad Python | 2-4x más rápido |
| **Tamaño** | 15-25 MB | 8-15 MB |
| **Compatibilidad** | Excelente | Muy buena |
| **Tiempo compilación** | 2-3 min | 5-10 min |
| **Facilidad uso** | Muy fácil | Moderada |
| **Confiabilidad** | Alta | Alta |

### Estadísticas Típicas
- **Archivos procesados**: 1000+ registros/segundo
- **Memoria**: ~50 MB durante ejecución
- **Tiempo**: Proporcional al tamaño del archivo
- **Compatibilidad**: Windows 10/11, Linux (según compilación)

## 🤝 Contribución

1. Fork el repositorio
2. Cree una rama para su feature
3. Haga commit de sus cambios
4. Push a la rama
5. Abra un Pull Request

## 📄 Licencia

Este proyecto es de uso interno para procesamiento de archivos Previred.

## 📞 Soporte

Para problemas o preguntas:
1. Revise esta documentación
2. Verifique los logs de error
3. Consulte los archivos README específicos
4. Abra un issue en GitHub

---

**Versión**: 1.0  
**Última actualización**: Septiembre 2024  
**Compilado con**: PyInstaller para máxima compatibilidad
