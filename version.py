#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de versionado automático para el procesador de archivos Previred
"""

import os
import sys
from datetime import datetime

# Versión actual del software
VERSION_MAJOR = 1
VERSION_MINOR = 6
VERSION_PATCH = 0

def get_version():
    """
    Retorna la versión actual en formato semántico.
    
    Returns:
        String con la versión en formato MAJOR.MINOR.PATCH
    """
    return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

def get_version_info():
    """
    Retorna información completa de la versión incluyendo fecha de compilación.
    
    Returns:
        Diccionario con información de versión
    """
    return {
        'version': get_version(),
        'major': VERSION_MAJOR,
        'minor': VERSION_MINOR,
        'patch': VERSION_PATCH,
        'build_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': sys.version.split()[0]
    }

def increment_patch_version():
    """
    Incrementa la versión PATCH en 1.
    Útil para pequeños cambios y correcciones de bugs.
    """
    global VERSION_PATCH
    VERSION_PATCH += 1
    update_version_file()

def increment_minor_version():
    """
    Incrementa la versión MINOR en 1 y resetea PATCH a 0.
    Útil para nuevas características.
    """
    global VERSION_MINOR, VERSION_PATCH
    VERSION_MINOR += 1
    VERSION_PATCH = 0
    update_version_file()

def increment_major_version():
    """
    Incrementa la versión MAJOR en 1 y resetea MINOR y PATCH a 0.
    Útil para cambios importantes que rompen compatibilidad.
    """
    global VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH
    VERSION_MAJOR += 1
    VERSION_MINOR = 0
    VERSION_PATCH = 0
    update_version_file()

def update_version_file():
    """
    Actualiza este archivo con las nuevas versiones.
    """
    script_path = os.path.abspath(__file__)
    
    # Leer el archivo actual
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar las líneas de versión
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('VERSION_MAJOR = '):
            lines[i] = f'VERSION_MAJOR = {VERSION_MAJOR}'
        elif line.startswith('VERSION_MINOR = '):
            lines[i] = f'VERSION_MINOR = {VERSION_MINOR}'
        elif line.startswith('VERSION_PATCH = '):
            lines[i] = f'VERSION_PATCH = {VERSION_PATCH}'
    
    # Escribir el archivo actualizado
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    # Permitir incrementar versión desde línea de comandos
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de versionado')
    parser.add_argument('--patch', action='store_true', help='Incrementar versión PATCH')
    parser.add_argument('--minor', action='store_true', help='Incrementar versión MINOR')
    parser.add_argument('--major', action='store_true', help='Incrementar versión MAJOR')
    parser.add_argument('--show', action='store_true', help='Mostrar versión actual')
    
    args = parser.parse_args()
    
    if args.patch:
        old_version = get_version()
        increment_patch_version()
        print(f"Versión incrementada: {old_version} → {get_version()}")
    elif args.minor:
        old_version = get_version()
        increment_minor_version()
        print(f"Versión incrementada: {old_version} → {get_version()}")
    elif args.major:
        old_version = get_version()
        increment_major_version()
        print(f"Versión incrementada: {old_version} → {get_version()}")
    elif args.show:
        info = get_version_info()
        print(f"Versión: {info['version']}")
        print(f"Python: {info['python_version']}")
        print(f"Fecha: {info['build_date']}")
    else:
        print(f"Versión actual: {get_version()}")
        print("Uso: python version.py [--patch|--minor|--major|--show]")
