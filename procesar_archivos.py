#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de procesamiento de archivos Previred - Versión Linux
Procesa archivos de ancho fijo y aplica transformaciones según jornadas de trabajadores.
"""

import os
import glob
import math
import sys

# Importar sistema de versionado
try:
    from version import get_version_info
except ImportError:
    # Fallback si no existe el archivo de versión
    def get_version_info():
        return {
            'version': '1.2.0',
            'build_date': 'N/A',
            'python_version': sys.version.split()[0]
        }

def solicitar_tope_imponible_afp():
    """
    Solicita al usuario el tope imponible AFP del mes en pesos.
    
    Returns:
        int: Tope imponible AFP en pesos (número entero)
    """
    while True:
        try:
            print("📊 CONFIGURACIÓN INICIAL")
            print("=" * 50)
            tope_str = input("Ingrese el tope imponible AFP del mes en pesos (número entero): ")
            
            # Remover separadores de miles si los hay (comas, puntos)
            tope_str = tope_str.replace(',', '').replace('.', '')
            
            tope_imponible = int(tope_str)
            
            if tope_imponible <= 0:
                print("❌ Error: El tope debe ser un número positivo mayor a 0")
                continue
            
            # Confirmar el valor ingresado
            print(f"✅ Tope imponible AFP configurado: ${tope_imponible:,} pesos")
            print()
            return tope_imponible
            
        except ValueError:
            print("❌ Error: Debe ingresar un número entero válido")
            print("   Ejemplo: 2460000 o 2,460,000")
            continue
        except KeyboardInterrupt:
            print("\n\n🛑 Operación cancelada por el usuario")
            sys.exit(0)

def detectar_codificacion(archivo_path):
    """
    Detecta la codificación de un archivo probando varias opciones comunes.
    
    Args:
        archivo_path: Ruta al archivo
    
    Returns:
        String con la codificación detectada
    """
    codificaciones = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in codificaciones:
        try:
            with open(archivo_path, 'r', encoding=encoding) as f:
                # Leer una muestra del archivo para verificar
                muestra = f.read(1024)
                # Si llegamos aquí sin excepción, la codificación es válida
                return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # Si ninguna funciona, usar utf-8 con errors='replace'
    print(f"⚠️ No se pudo detectar la codificación de {archivo_path}, usando utf-8 con reemplazo de caracteres")
    return 'utf-8'

def cargar_jornadas_trabajadores():
    """
    Carga las jornadas de los trabajadores desde el archivo CSV.
    
    Returns:
        Diccionario con RUT como clave y jornada como valor
    """
    jornadas = {}
    archivo_jornadas = "jornadas/jornadasTrabajadores.csv"
    
    if not os.path.exists(archivo_jornadas):
        print(f"⚠️ Archivo de jornadas no encontrado: {archivo_jornadas}")
        print("Se usará jornada completa (1) por defecto para todos los trabajadores")
        return jornadas
    
    try:
        # Detectar codificación del archivo de jornadas
        encoding_jornadas = detectar_codificacion(archivo_jornadas)
        print(f"📄 Codificación detectada para jornadas: {encoding_jornadas}")
        
        with open(archivo_jornadas, 'r', encoding=encoding_jornadas) as f:
            lines = f.readlines()
            
            # Saltar header si existe
            start_line = 1 if lines and 'rut' in lines[0].lower() else 0
            
            for i, line in enumerate(lines[start_line:], start_line + 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    rut, jornada = line.split(';')
                    jornadas[rut.strip()] = int(jornada.strip())
                except ValueError as e:
                    print(f"⚠️ Error procesando línea {i} del archivo de jornadas: {line}")
                    continue
        
        print(f"✅ Jornadas cargadas: {len(jornadas)} trabajadores")
        return jornadas
        
    except Exception as e:
        print(f"❌ Error leyendo archivo de jornadas: {e}")
        print("Se usará jornada completa (1) por defecto para todos los trabajadores")
        return {}

def extraer_rut_formateado(linea):
    """
    Extrae el RUT de una línea y lo formatea como en el archivo de jornadas.
    
    Args:
        linea: Línea del archivo de datos
    
    Returns:
        RUT formateado como 'numero-digito_verificador' o None si hay error
    """
    if len(linea) < 12:
        return None
    
    try:
        # Extraer los primeros 12 caracteres (11 números + 1 dígito verificador)
        rut_completo = linea[0:12]
        
        # Separar números y dígito verificador
        rut_numeros = rut_completo[0:11]
        digito_verificador = rut_completo[11]
        
        # Quitar ceros a la izquierda de los números
        rut_sin_ceros = rut_numeros.lstrip('0')
        
        # Si queda vacío después de quitar ceros, usar "0"
        if not rut_sin_ceros:
            rut_sin_ceros = "0"
        
        # Formatear como RUT chileno: números-dígito_verificador
        rut_formateado = f"{rut_sin_ceros}-{digito_verificador}"
        
        return rut_formateado
        
    except Exception:
        return None

def obtener_jornada_trabajador(rut_formateado, jornadas_dict):
    """
    Obtiene la jornada de un trabajador desde el diccionario de jornadas.
    
    Args:
        rut_formateado: RUT en formato 'numero-digito_verificador'
        jornadas_dict: Diccionario con las jornadas
    
    Returns:
        Tupla (jornada_numero, jornada_string_8_digitos)
        - jornada_numero: 1 (completa) o 2 (parcial)
        - jornada_string_8_digitos: "00000001" o "00000002"
    
    Raises:
        ValueError: Si el RUT no se encuentra en el archivo de jornadas
    """
    # Verificar si el RUT existe en el diccionario
    if rut_formateado not in jornadas_dict:
        raise ValueError(f"❌ ERROR CRÍTICO: RUT '{rut_formateado}' no encontrado en archivo de jornadas.\n"
                        f"   Todos los RUTs del archivo de datos deben estar presentes en jornadas/jornadasTrabajadores.csv\n"
                        f"   RUTs disponibles en jornadas: {sorted(list(jornadas_dict.keys()))}")
    
    # Obtener jornada del diccionario
    jornada_numero = jornadas_dict[rut_formateado]
    
    # Convertir a string de 8 dígitos
    jornada_string = f"{jornada_numero:08d}"
    
    return jornada_numero, jornada_string

def convertir_a_string_8_ceros(valor):
    """
    Convierte un valor entero a string de largo 8 con ceros a la izquierda.
    
    Args:
        valor: Valor entero a convertir
    
    Returns:
        String de 8 caracteres con ceros a la izquierda
    """
    return str(valor).zfill(8)

def calcular_cotizacion_afp_actualizada(renta_imponible_afp, cotizacion_afp, tope_imponible_afp):
    """
    Calcula la cotización AFP actualizada según la fórmula:
    (rentaImponibleAfp * 0.001) + cotizacionAfp, aproximado al entero más cercano
    
    Si rentaImponibleAfp es mayor al tope, se usa el tope en el cálculo.
    
    Args:
        renta_imponible_afp: Renta imponible AFP (entero)
        cotizacion_afp: Cotización AFP original (entero)
        tope_imponible_afp: Tope imponible AFP del mes (entero)
    
    Returns:
        Valor entero aproximado al más cercano
    """
    if renta_imponible_afp is None or cotizacion_afp is None:
        return 0
    
    # Aplicar tope si la renta imponible AFP lo excede
    renta_efectiva = min(renta_imponible_afp, tope_imponible_afp)
    
    # Calcular: (rentaImponibleAfp efectiva * 0.001) + cotizacionAfp
    resultado = (renta_efectiva * 0.001) + cotizacion_afp
    
    # Aproximar al entero más cercano (redondeo normal)
    return round(resultado)

def reemplazar_cotizacion_en_linea(linea, nueva_cotizacion_str):
    """
    Reemplaza la cotización AFP en una línea (posición 182, largo 8).
    
    Args:
        linea: Línea original
        nueva_cotizacion_str: Nueva cotización como string de 8 caracteres
    
    Returns:
        Línea con la cotización reemplazada
    """
    if len(linea) < 190:  # Verificar que la línea sea suficientemente larga
        return linea
    
    # Reemplazar posición 182, largo 8 (índices 182-189)
    linea_modificada = linea[:182] + nueva_cotizacion_str + linea[190:]
    return linea_modificada

def calcular_cotizacion_expectativa_vida(imponible_seguro_cesantia, tope_imponible_afp, tiene_subsidio=False, renta_imponible_afp=0):
    """
    Calcula la cotización expectativa de vida:
    - Sin subsidio: (imponibleSeguroCesantia * 0.009) redondeada
    - Con subsidio: ((rentaImponibleAfp + imponibleSeguroCesantia) * 0.009) redondeada
    
    Si algún valor excede el tope imponible, se usa el tope en el cálculo.
    
    Args:
        imponible_seguro_cesantia: Imponible seguro cesantía (entero)
        tope_imponible_afp: Tope imponible AFP del mes (entero)
        tiene_subsidio: True si el trabajador tiene subsidio
        renta_imponible_afp: Renta imponible AFP (entero), usado solo si tiene subsidio
    
    Returns:
        Cotización expectativa de vida (entero redondeado)
    """
    # Aplicar tope a los valores si los exceden
    imponible_cesantia_efectivo = min(imponible_seguro_cesantia, tope_imponible_afp)
    renta_afp_efectiva = min(renta_imponible_afp, tope_imponible_afp)
    
    if tiene_subsidio:
        # Con subsidio: usar tanto rentaImponibleAfp como imponibleSeguroCesantia (con topes aplicados)
        cotizacion = (renta_afp_efectiva + imponible_cesantia_efectivo) * 0.009
    else:
        # Sin subsidio: solo imponibleSeguroCesantia (con tope aplicado)
        cotizacion = imponible_cesantia_efectivo * 0.009
    
    return round(cotizacion)

def reemplazar_campo_740_imponible_cesantia(linea, imponible_cesantia_str, tiene_subsidio=False):
    """
    Reemplaza el campo 740 con el imponible cesantía solo si tiene subsidio.
    
    Args:
        linea: Línea original
        imponible_cesantia_str: Imponible cesantía como string de 8 dígitos con ceros a la izquierda
        tiene_subsidio: True si el trabajador tiene subsidio
    
    Returns:
        Línea con el campo 740 reemplazado (solo si tiene subsidio)
    """
    if len(linea) < 748 or not tiene_subsidio:  # Solo modificar si tiene subsidio
        return linea
    
    # Reemplazar posición 740, largo 8 (índices 740-747)
    linea_modificada = linea[:740] + imponible_cesantia_str + linea[748:]
    return linea_modificada

def reemplazar_campo_748_jornada(linea, jornada_str="00000001"):
    """
    Reemplaza el campo 748 con la jornada laboral (siempre).
    
    Args:
        linea: Línea original
        jornada_str: Jornada como string (00000001=completa, 00000002=parcial)
    
    Returns:
        Línea con el campo 748 reemplazado
    """
    if len(linea) < 756:  # Verificar que la línea sea suficientemente larga
        return linea
    
    # Reemplazar posición 748, largo 8 (índices 748-755)
    linea_modificada = linea[:748] + jornada_str + linea[756:]
    return linea_modificada

def reemplazar_campo_756_cotizacion_expectativa(linea, cotizacion_expectativa_str):
    """
    Reemplaza el campo 756 con la cotización expectativa de vida (siempre).
    
    Args:
        linea: Línea original
        cotizacion_expectativa_str: Cotización expectativa como string de 8 dígitos con ceros a la izquierda
    
    Returns:
        Línea con el campo 756 reemplazado
    """
    if len(linea) < 764:  # Verificar que la línea sea suficientemente larga
        return linea
    
    # Reemplazar posición 756, largo 8 (índices 756-763)
    linea_modificada = linea[:756] + cotizacion_expectativa_str + linea[764:]
    return linea_modificada

def crear_carpeta_salida():
    """
    Crea la carpeta de salida para los archivos modificados.
    
    Returns:
        Nombre de la carpeta de salida
    """
    carpeta_salida = "archivos_modificados"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Carpeta creada: {carpeta_salida}")
    else:
        print(f"Usando carpeta existente: {carpeta_salida}")
    
    return carpeta_salida

def procesar_archivos(tope_imponible_afp):
    # Cargar jornadas de trabajadores al inicio
    print("=== CARGANDO JORNADAS DE TRABAJADORES ===")
    jornadas_trabajadores = cargar_jornadas_trabajadores()
    
    print(f"📊 Tope imponible AFP del mes: ${tope_imponible_afp:,} pesos")
    print()
    
    # Buscar archivos .txt en la carpeta archivos105espacios
    carpeta = "archivos105espacios"
    patron = os.path.join(carpeta, "*.txt")
    archivos = glob.glob(patron)
    
    # También buscar archivos .TXT (mayúsculas)
    patron_mayus = os.path.join(carpeta, "*.TXT")
    archivos.extend(glob.glob(patron_mayus))
    
    if not archivos:
        print(f"No se encontraron archivos .txt en la carpeta {carpeta}")
        return
    
    print(f"\nArchivos encontrados: {archivos}")
    
    # Crear carpeta de salida
    carpeta_salida = crear_carpeta_salida()
    
    # Map para agrupar por el campo posición 0, largo 11
    grupos = {}
    archivos_modificados = {}  # Para almacenar las líneas modificadas por archivo
    codificaciones_archivos = {}  # Para almacenar la codificación detectada de cada archivo
    
    for archivo in archivos:
        print(f"\nProcesando archivo: {archivo}")
        nombre_archivo = os.path.basename(archivo)
        archivos_modificados[nombre_archivo] = []
        
        # Detectar codificación del archivo de datos
        encoding_archivo = detectar_codificacion(archivo)
        print(f"📄 Codificación detectada para {nombre_archivo}: {encoding_archivo}")
        
        # Almacenar la codificación para usar al guardar
        codificaciones_archivos[nombre_archivo] = encoding_archivo
        
        with open(archivo, 'r', encoding=encoding_archivo) as f:
            for numero_linea, linea in enumerate(f, 1):
                linea_original = linea.rstrip('\n\r')
                linea_modificada = linea_original  # Por defecto, no modificar
                
                if len(linea_original) >= 813:  # Necesitamos al menos hasta posición 812 (805+8)
                    # Extraer rutTrabajador: posición 0, largo 11 (solo para compatibilidad con código existente)
                    rutTrabajador = linea_original[0:11]
                    
                    # Extraer RUT formateado completo (incluyendo dígito verificador)
                    rutFormateado = extraer_rut_formateado(linea_original)
                    
                    # Obtener jornada del trabajador con validación estricta
                    try:
                        jornada_numero, jornada_string = obtener_jornada_trabajador(rutFormateado, jornadas_trabajadores)
                    except ValueError as e:
                        print(f"\n{str(e)}")
                        print(f"📄 Archivo: {archivo}")
                        print(f"📋 Línea: {numero_linea}")
                        print(f"🔍 RUT extraído: {rutFormateado}")
                        print(f"\n💡 SOLUCIÓN: Agregue el RUT '{rutFormateado}' al archivo jornadas/jornadasTrabajadores.csv")
                        print("   o verifique que el formato del RUT sea correcto.")
                        print("\n🛑 PROCESAMIENTO DETENIDO")
                        return  # Detener completamente la ejecución
                    
                    # Extraer codigoMovimientoPersonal: posición 126, largo 2
                    codigoMovimientoPersonal = linea_original[126:128]

                    # Extraer indicador de línea principal: posición 124, largo 2
                    indicadorLineaPrincipal = linea_original[124:126]
                    esLineaPrincipal = indicadorLineaPrincipal == "00"
                    
                    # Verificar si tieneSubsidio (código 03 o 06)
                    tieneSubsidio = codigoMovimientoPersonal in ['03', '06']
                    
                    # Extraer campos adicionales de la línea principal
                    rentaImponibleAfp = None
                    cotizacionAfp = None
                    imponibleSeguroCesantia = None
                    cotizacionAfpActualizada = None
                    cotizacionAfpActualizadaStr = None
                    cotizacionExpectativaVida = None
                    cotizacionExpectativaVidaStr = None
                    
                    # Inicializar variables por defecto para líneas no principales
                    if rutFormateado is None:
                        rutFormateado = "DESCONOCIDO"
                        jornada_numero = 1
                        jornada_string = "00000001"
                    
                    if esLineaPrincipal:
                        try:
                            # Campo 174, largo 8 - rentaImponibleAfp
                            rentaImponibleAfp = int(linea_original[174:182])
                        except (ValueError, IndexError):
                            rentaImponibleAfp = 0
                        
                        try:
                            # Campo 182, largo 8 - cotizacionAfp
                            cotizacionAfp = int(linea_original[182:190])
                        except (ValueError, IndexError):
                            cotizacionAfp = 0
                        
                        try:
                            # Campo 805, largo 8 - imponibleSeguroCesantia
                            imponibleSeguroCesantia = int(linea_original[805:813])
                        except (ValueError, IndexError):
                            imponibleSeguroCesantia = 0
                        
                        # Calcular cotizaciónAfpActualizada
                        cotizacionAfpActualizada = calcular_cotizacion_afp_actualizada(rentaImponibleAfp, cotizacionAfp, tope_imponible_afp)
                        cotizacionAfpActualizadaStr = convertir_a_string_8_ceros(cotizacionAfpActualizada)
                        
                        # Calcular cotización expectativa de vida
                        cotizacionExpectativaVida = calcular_cotizacion_expectativa_vida(
                            imponibleSeguroCesantia, 
                            tope_imponible_afp,
                            tiene_subsidio=tieneSubsidio, 
                            renta_imponible_afp=rentaImponibleAfp
                        )
                        cotizacionExpectativaVidaStr = convertir_a_string_8_ceros(cotizacionExpectativaVida)
                        
                        # Aplicar todas las modificaciones a la línea
                        # 1. Reemplazar cotización AFP (siempre)
                        linea_modificada = reemplazar_cotizacion_en_linea(linea_original, cotizacionAfpActualizadaStr)
                        
                        # 2. Reemplazar campo 740 con imponible cesantía (solo si tiene subsidio)
                        if imponibleSeguroCesantia > 0:
                            imponibleSeguroCesantiaStr = convertir_a_string_8_ceros(imponibleSeguroCesantia)
                            linea_modificada = reemplazar_campo_740_imponible_cesantia(linea_modificada, imponibleSeguroCesantiaStr, tieneSubsidio)
                        
                        # 3. Reemplazar campo 748 con jornada según CSV
                        linea_modificada = reemplazar_campo_748_jornada(linea_modificada, jornada_string)
                        
                        # 4. Reemplazar campo 756 con cotización expectativa de vida (siempre)
                        linea_modificada = reemplazar_campo_756_cotizacion_expectativa(linea_modificada, cotizacionExpectativaVidaStr)
                        
                        print(f"  Línea {numero_linea} (PRINCIPAL) - RUT {rutFormateado}:")
                        
                        # Mostrar cotización AFP con información de tope si aplica
                        renta_efectiva_afp = min(rentaImponibleAfp, tope_imponible_afp)
                        if rentaImponibleAfp > tope_imponible_afp:
                            print(f"    Cotización AFP: {cotizacionAfp:,} → {cotizacionAfpActualizada:,} (Renta AFP: {rentaImponibleAfp:,} → {renta_efectiva_afp:,} por tope)")
                        else:
                            print(f"    Cotización AFP: {cotizacionAfp:,} → {cotizacionAfpActualizada:,}")
                        
                        print(f"    Campo 740 (ImponibleSegCes): {'REEMPLAZADO' if tieneSubsidio else 'SIN CAMBIOS'} ({'tiene subsidio' if tieneSubsidio else 'no tiene subsidio'})")
                        print(f"    Campo 748 (Jornada): REEMPLAZADO con {jornada_string} ({'completa' if jornada_numero == 1 else 'parcial'})")
                        
                        # Mostrar cotización expectativa de vida con información de tope si aplica
                        imponible_cesantia_efectivo = min(imponibleSeguroCesantia, tope_imponible_afp)
                        
                        if tieneSubsidio:
                            # Verificar si se aplicaron topes
                            tope_aplicado_afp = rentaImponibleAfp > tope_imponible_afp
                            tope_aplicado_cesantia = imponibleSeguroCesantia > tope_imponible_afp
                            
                            if tope_aplicado_afp or tope_aplicado_cesantia:
                                mensaje_tope = []
                                if tope_aplicado_afp:
                                    mensaje_tope.append(f"AFP: {rentaImponibleAfp:,}→{renta_efectiva_afp:,}")
                                if tope_aplicado_cesantia:
                                    mensaje_tope.append(f"Cesantía: {imponibleSeguroCesantia:,}→{imponible_cesantia_efectivo:,}")
                                
                                print(f"    Campo 756 (CotizExpVida): ({renta_efectiva_afp:,} + {imponible_cesantia_efectivo:,}) × 0.009 = {cotizacionExpectativaVida:,} → {cotizacionExpectativaVidaStr} (CON SUBSIDIO) [TOPE: {', '.join(mensaje_tope)}]")
                            else:
                                print(f"    Campo 756 (CotizExpVida): ({rentaImponibleAfp:,} + {imponibleSeguroCesantia:,}) × 0.009 = {cotizacionExpectativaVida:,} → {cotizacionExpectativaVidaStr} (CON SUBSIDIO)")
                        else:
                            if imponibleSeguroCesantia > tope_imponible_afp:
                                print(f"    Campo 756 (CotizExpVida): {imponible_cesantia_efectivo:,} × 0.009 = {cotizacionExpectativaVida:,} → {cotizacionExpectativaVidaStr} [TOPE: Cesantía {imponibleSeguroCesantia:,}→{imponible_cesantia_efectivo:,}]")
                            else:
                                print(f"    Campo 756 (CotizExpVida): {imponibleSeguroCesantia:,} × 0.009 = {cotizacionExpectativaVida:,} → {cotizacionExpectativaVidaStr}")
                    
                    else:
                        linea_modificada = linea_original  # No modificar líneas no principales
                    
                    # Si no existe el grupo, crearlo
                    if rutTrabajador not in grupos:
                        grupos[rutTrabajador] = []
                    
                    # Agregar la fila completa al grupo
                    grupos[rutTrabajador].append({
                        'archivo': nombre_archivo,
                        'linea': numero_linea,
                        'rutTrabajador': rutTrabajador,
                        'rutFormateado': rutFormateado,
                        'jornada_numero': jornada_numero,
                        'jornada_string': jornada_string,
                        'codigoMovimientoPersonal': codigoMovimientoPersonal,
                        'tieneSubsidio': tieneSubsidio,
                        'indicadorLineaPrincipal': indicadorLineaPrincipal,
                        'esLineaPrincipal': esLineaPrincipal,
                        'rentaImponibleAfp': rentaImponibleAfp,
                        'cotizacionAfp': cotizacionAfp,
                        'imponibleSeguroCesantia': imponibleSeguroCesantia,
                        'cotizacionAfpActualizada': cotizacionAfpActualizada,
                        'cotizacionAfpActualizadaStr': cotizacionAfpActualizadaStr,
                        'cotizacionExpectativaVida': cotizacionExpectativaVida,
                        'cotizacionExpectativaVidaStr': cotizacionExpectativaVidaStr,
                        'linea_original': linea_original,
                        'linea_modificada': linea_modificada
                    })
                
                # Agregar línea al archivo modificado (con o sin cambios)
                archivos_modificados[nombre_archivo].append(linea_modificada)
    
    # Guardar archivos modificados
    print(f"\n=== GUARDANDO ARCHIVOS MODIFICADOS ===")
    for nombre_archivo, lineas in archivos_modificados.items():
        ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
        # Usar la misma codificación que el archivo original
        encoding_salida = codificaciones_archivos.get(nombre_archivo, 'utf-8')
        print(f"💾 Guardando {nombre_archivo} con codificación: {encoding_salida}")
        
        with open(ruta_salida, 'w', encoding=encoding_salida) as f:
            for linea in lineas:
                f.write(linea + '\n')
        print(f"Archivo guardado: {ruta_salida}")
    
    return grupos, archivos_modificados

if __name__ == "__main__":
    version_info = get_version_info()
    
    print("=" * 70)
    print("  PROCESADOR DE ARCHIVOS PREVIRED - VERSIÓN LINUX")
    print(f"  Versión: {version_info['version']} | Python: {version_info['python_version']}")
    print(f"  Compilado: {version_info['build_date']}")
    print("=" * 70)
    print()
    
    try:
        # Solicitar tope imponible AFP al usuario
        tope_imponible_afp = solicitar_tope_imponible_afp()
        
        resultado = procesar_archivos(tope_imponible_afp)
        if resultado is None:
            # El procesamiento se detuvo por un error crítico
            exit(1)
        
        grupos, archivos_modificados = resultado
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")
        exit(1)
    
    # Mostrar resultados resumidos
    print(f"\n=== RESUMEN DEL PROCESAMIENTO ===")
    print(f"Total de trabajadores: {len(grupos)}")
    
    # Contar trabajadores con subsidio y líneas principales modificadas
    trabajadores_con_subsidio = 0
    lineas_principales_modificadas = 0
    
    for rutTrabajador, filas in grupos.items():
        # Verificar si ALGUNA línea del trabajador tiene subsidio
        trabajador_tiene_subsidio = any(fila['tieneSubsidio'] for fila in filas)
        
        if trabajador_tiene_subsidio:
            trabajadores_con_subsidio += 1
        
        # Contar líneas principales modificadas
        for fila in filas:
            if fila['esLineaPrincipal']:
                lineas_principales_modificadas += 1
    
    print(f"Trabajadores con subsidio: {trabajadores_con_subsidio}")
    print(f"Líneas principales modificadas: {lineas_principales_modificadas}")
    print(f"Archivos generados: {len(archivos_modificados)}")
    
    # Mostrar algunos ejemplos de modificaciones
    print(f"\n=== EJEMPLOS DE MODIFICACIONES ===")
    ejemplos_mostrados = 0
    for rutTrabajador, filas in grupos.items():
        if ejemplos_mostrados >= 3:
            break
            
        for fila in filas:
            if fila['esLineaPrincipal'] and ejemplos_mostrados < 3:
                print(f"RUT {fila['rutTrabajador']} (línea {fila['linea']}):")
                print(f"  Cotización original: {fila['cotizacionAfp']:,}")
                print(f"  Cotización actualizada: {fila['cotizacionAfpActualizada']:,}")
                print(f"  String reemplazo: '{fila['cotizacionAfpActualizadaStr']}'")
                ejemplos_mostrados += 1
