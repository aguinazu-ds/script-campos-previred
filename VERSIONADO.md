# 🚀 Sistema de Versionado Automático

Este proyecto incluye un sistema de versionado automático que incrementa las versiones y crea releases automáticamente.

## 📋 Tipos de Versión

El sistema usa **versionado semántico** (SemVer):

- **MAJOR** (ej: 1.0.0 → 2.0.0): Cambios importantes que rompen compatibilidad
- **MINOR** (ej: 1.2.0 → 1.3.0): Nuevas características sin romper compatibilidad
- **PATCH** (ej: 1.2.0 → 1.2.1): Corrección de bugs y cambios menores

## 🛠️ Cómo Usar

### Opción 1: Script Automático (Recomendado)

```bash
# Para cambios menores (bugs, correcciones)
./release.sh patch "Corregido error en cálculo de cotización"

# Para nuevas características
./release.sh minor "Agregado sistema de versionado automático"

# Para cambios importantes
./release.sh major "Refactorización completa del sistema"
```

### Opción 2: Manual

```bash
# 1. Incrementar versión
python3 version.py --patch   # o --minor o --major

# 2. Hacer commit
git add .
git commit -m "🔧 v1.2.1: Descripción del cambio"

# 3. Crear tag
git tag -a "v1.2.1" -m "Release v1.2.1"

# 4. Subir cambios
git push origin main --tags
```

## 🤖 Automatización

### GitHub Actions

El workflow se ejecuta automáticamente cuando:
- Se crea un **tag** que empieza con `v` (ej: `v1.2.1`)
- Se ejecuta manualmente desde GitHub

### Compilación Windows

El sistema automáticamente:
1. ✅ Detecta la versión del tag
2. ✅ Compila el ejecutable Windows
3. ✅ Crea paquete con nombre versionado
4. ✅ Sube artefactos con versión
5. ✅ Crea release en GitHub con archivos

## 📁 Archivos del Sistema

```
proyecto/
├── version.py              # Sistema de versionado
├── release.sh              # Script de release automático
├── procesar_archivos.py    # Script principal (Linux)
├── procesar_archivos_windows.py  # Script principal (Windows)
└── .github/workflows/
    └── build-windows.yml   # Workflow de compilación
```

## 🔍 Ver Información de Versión

```bash
# Ver versión actual
python3 version.py --show

# Ver solo número de versión
python3 version.py
```

## 📝 Convenciones de Commit

El script automático usa emojis estándar:

- 🔧 `patch`: Correcciones y cambios menores
- ✨ `minor`: Nuevas características
- 🚀 `major`: Cambios importantes

## 🎯 Ejemplos Prácticos

### Caso 1: Corrección de Bug
```bash
./release.sh patch "Corregido error de encoding en archivos con caracteres especiales"
```
**Resultado**: `1.2.0 → 1.2.1`

### Caso 2: Nueva Característica
```bash
./release.sh minor "Agregado soporte para validación de RUTs en tiempo real"
```
**Resultado**: `1.2.1 → 1.3.0`

### Caso 3: Cambio Mayor
```bash
./release.sh major "Refactorización completa: nuevo motor de procesamiento"
```
**Resultado**: `1.3.0 → 2.0.0`

## ✅ Ventajas del Sistema

1. **Consistencia**: Todos los releases siguen el mismo patrón
2. **Automatización**: Un solo comando hace todo el proceso
3. **Trazabilidad**: Cada versión tiene tag, commit y release
4. **GitHub Integration**: Releases automáticos con archivos compilados
5. **Versionado en Ejecutables**: Los archivos incluyen número de versión

## 🔗 Enlaces Útiles

- [Versionado Semántico](https://semver.org/lang/es/)
- [Convenciones de Commit](https://www.conventionalcommits.org/es/v1.0.0/)
- [GitHub Releases](https://docs.github.com/es/repositories/releasing-projects-on-github/about-releases)
