#!/bin/bash
# -*- coding: utf-8 -*-
"""
Script de automatización para releases con versionado automático
"""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🚀 SISTEMA DE VERSIONADO AUTOMÁTICO${NC}"
    echo ""
    echo "Uso: $0 [TIPO] [MENSAJE]"
    echo ""
    echo "TIPOS de incremento:"
    echo "  patch   - Incrementa versión PATCH (1.2.0 → 1.2.1) para bugs y pequeños cambios"
    echo "  minor   - Incrementa versión MINOR (1.2.0 → 1.3.0) para nuevas características"
    echo "  major   - Incrementa versión MAJOR (1.2.0 → 2.0.0) para cambios importantes"
    echo ""
    echo "MENSAJE: Descripción del cambio (opcional)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 patch \"Corregido error en cálculo de cotización\""
    echo "  $0 minor \"Agregado sistema de versionado automático\""
    echo "  $0 major \"Refactorización completa del sistema\""
    echo ""
    echo "El script automáticamente:"
    echo "  ✅ Incrementa la versión apropiada"
    echo "  ✅ Actualiza los archivos con la nueva versión"
    echo "  ✅ Hace commit con mensaje estándar + emoji"
    echo "  ✅ Crea tag de la versión"
    echo "  ✅ Hace push con tags"
}

# Función para obtener versión actual
get_current_version() {
    python3 version.py --show | grep "Versión:" | cut -d' ' -f2
}

# Función para emojis según tipo de cambio
get_emoji() {
    case $1 in
        "patch") echo "🔧" ;;
        "minor") echo "✨" ;;
        "major") echo "🚀" ;;
        *) echo "📦" ;;
    esac
}

# Verificar argumentos
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

TIPO="$1"
MENSAJE="${2:-Actualización automática}"

# Verificar que el tipo sea válido
if [[ ! "$TIPO" =~ ^(patch|minor|major)$ ]]; then
    echo -e "${RED}❌ Error: Tipo de versión inválido. Debe ser patch, minor o major${NC}"
    show_help
    exit 1
fi

# Verificar que estemos en un repositorio git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: No se encontró repositorio git en el directorio actual${NC}"
    exit 1
fi

# Verificar que no haya cambios pendientes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️ Hay cambios pendientes. Agregándolos automáticamente...${NC}"
    git add .
fi

# Obtener versión actual
CURRENT_VERSION=$(get_current_version)
echo -e "${BLUE}📋 Versión actual: $CURRENT_VERSION${NC}"

# Incrementar versión
echo -e "${BLUE}🔄 Incrementando versión $TIPO...${NC}"
python3 version.py --$TIPO

# Obtener nueva versión
NEW_VERSION=$(get_current_version)
echo -e "${GREEN}✅ Nueva versión: $NEW_VERSION${NC}"

# Obtener emoji para el commit
EMOJI=$(get_emoji $TIPO)

# Crear mensaje de commit
COMMIT_MESSAGE="$EMOJI v$NEW_VERSION: $MENSAJE"

# Hacer commit
echo -e "${BLUE}💾 Haciendo commit...${NC}"
git add .
git commit -m "$COMMIT_MESSAGE"

# Crear tag
echo -e "${BLUE}🏷️ Creando tag v$NEW_VERSION...${NC}"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION: $MENSAJE"

# Push con tags
echo -e "${BLUE}🚀 Subiendo cambios y tags a repositorio...${NC}"
git push origin main
git push origin --tags

echo ""
echo -e "${GREEN}🎉 ¡Release completado exitosamente!${NC}"
echo -e "${GREEN}   Versión: $CURRENT_VERSION → $NEW_VERSION${NC}"
echo -e "${GREEN}   Tag: v$NEW_VERSION${NC}"
echo -e "${GREEN}   Commit: $COMMIT_MESSAGE${NC}"
echo ""
echo -e "${BLUE}🔗 Para ver el release en GitHub:${NC}"
echo -e "   https://github.com/aguinazu-ds/script-campos-previred/releases/tag/v$NEW_VERSION"
