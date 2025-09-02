#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de procesamiento de archivos Previred - Versión Windows con Nuitka
Procesa archivos de ancho fijo y aplica transformaciones según jornadas de trabajadores.
"""

import os
import glob
import math

def cargar_jornadas_trabajadores():
    """
    Carga las jornadas de los trabajadores desde el archivo CSV.
    
    Returns:
        Diccionario con RUT como clave y jornada como valor
    """
    jornadas = {}
    # Para Windows, usar ruta relativa desde el directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    archivo_jornadas = os.path.join(script_dir, "jornadas", "jornadasTrabajadores.csv")
    
    if not os.path.exists(archivo_jornadas):
        print(f"⚠️ Archivo de jornadas no encontrado: {archivo_jornadas}")
        print("Se usará jornada completa (1) por defecto para todos los trabajadores")
        return jornadas
    
    try:
        with open(archivo_jornadas, 'r', encoding='utf-8') as f:
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
                        f"   Todos los RUTs del archivo de datos deben estar presentes en jornadas\\jornadasTrabajadores.csv\n"
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

def calcular_cotizacion_afp_actualizada(renta_imponible_afp, cotizacion_afp):
    """
    Calcula la cotización AFP actualizada según la fórmula:
    (rentaImponibleAfp * 0.001) + cotizacionAfp, aproximado al entero más cercano
    
    Args:
        renta_imponible_afp: Renta imponible AFP (entero)
        cotizacion_afp: Cotización AFP original (entero)
    
    Returns:
        Valor entero aproximado al más cercano
    """
    if renta_imponible_afp is None or cotizacion_afp is None:
        return 0
    
    # Calcular: (rentaImponibleAfp * 0.001) + cotizacionAfp
    resultado = (renta_imponible_afp * 0.001) + cotizacion_afp
    
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
    if len(linea) < 190:
        return linea
    
    # Reemplazar posición 182, largo 8 (índices 182-189)
    linea_modificada = linea[:182] + nueva_cotizacion_str + linea[190:]
    return linea_modificada

def calcular_cotizacion_expectativa_vida(imponible_seguro_cesantia):
    """
    Calcula la cotización expectativa de vida (imponibleSeguroCesantia * 0.009) redondeada.
    
    Args:
        imponible_seguro_cesantia: Imponible seguro cesantía (entero)
    
    Returns:
        Cotización expectativa de vida (entero redondeado)
    """
    cotizacion = imponible_seguro_cesantia * 0.009
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta_salida = os.path.join(script_dir, "archivos_modificados")
    
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Carpeta creada: {carpeta_salida}")
    else:
        print(f"Usando carpeta existente: {carpeta_salida}")
    
    return carpeta_salida

def procesar_archivos():
    # Cargar jornadas de trabajadores al inicio
    print("=== CARGANDO JORNADAS DE TRABAJADORES ===")
    jornadas_trabajadores = cargar_jornadas_trabajadores()
    
    # Buscar archivos .txt en la carpeta archivos105espacios (relativa al script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta = os.path.join(script_dir, "archivos105espacios")
    
    if not os.path.exists(carpeta):
        print(f"❌ ERROR: No se encontró la carpeta {carpeta}")
        print("Asegúrese de que la carpeta 'archivos105espacios' esté en el mismo directorio que el ejecutable.")
        return None
    
    patron = os.path.join(carpeta, "*.txt")
    archivos = glob.glob(patron)
    
    # También buscar archivos .TXT (mayúsculas)
    patron_mayus = os.path.join(carpeta, "*.TXT")
    archivos.extend(glob.glob(patron_mayus))
    
    if not archivos:
        print(f"No se encontraron archivos .txt en la carpeta {carpeta}")
        print("Coloque los archivos .txt o .TXT en la carpeta 'archivos105espacios'")
        return None
    
    print(f"\nArchivos encontrados: {[os.path.basename(a) for a in archivos]}")
    
    # Crear carpeta de salida
    carpeta_salida = crear_carpeta_salida()
    
    # Map para agrupar por el campo posición 0, largo 11
    grupos = {}
    archivos_modificados = {}  # Para almacenar las líneas modificadas por archivo
    
    for archivo in archivos:
        print(f"\nProcesando archivo: {os.path.basename(archivo)}")
        nombre_archivo = os.path.basename(archivo)
        archivos_modificados[nombre_archivo] = []
        
        with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
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
                        print(f"📄 Archivo: {os.path.basename(archivo)}")
                        print(f"📋 Línea: {numero_linea}")
                        print(f"🔍 RUT extraído: {rutFormateado}")
                        print(f"\n💡 SOLUCIÓN: Agregue el RUT '{rutFormateado}' al archivo jornadas\\jornadasTrabajadores.csv")
                        print("   o verifique que el formato del RUT sea correcto.")
                        print("\n🛑 PROCESAMIENTO DETENIDO")
                        print("\nPresione Enter para cerrar...")
                        input()
                        return None  # Detener completamente la ejecución
                    
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
                        cotizacionAfpActualizada = calcular_cotizacion_afp_actualizada(rentaImponibleAfp, cotizacionAfp)
                        cotizacionAfpActualizadaStr = convertir_a_string_8_ceros(cotizacionAfpActualizada)
                        
                        # Calcular cotización expectativa de vida
                        cotizacionExpectativaVida = calcular_cotizacion_expectativa_vida(imponibleSeguroCesantia)
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
                        print(f"    Cotización AFP: {cotizacionAfp:,} → {cotizacionAfpActualizada:,}")
                        print(f"    Campo 740 (ImponibleSegCes): {'REEMPLAZADO' if tieneSubsidio else 'SIN CAMBIOS'} ({'tiene subsidio' if tieneSubsidio else 'no tiene subsidio'})")
                        print(f"    Campo 748 (Jornada): REEMPLAZADO con {jornada_string} ({'completa' if jornada_numero == 1 else 'parcial'})")
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
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            for linea in lineas:
                f.write(linea + '\n')
        print(f"Archivo guardado: {os.path.basename(ruta_salida)}")
    
    return grupos, archivos_modificados

def main():
    """Función principal con manejo de errores para Windows"""
    print("=" * 60)
    print("  PROCESADOR DE ARCHIVOS PREVIRED - VERSIÓN WINDOWS")
    print("  Compilado con Nuitka para máximo rendimiento")
    print("=" * 60)
    print()
    
    try:
        resultado = procesar_archivos()
        if resultado is None:
            # El procesamiento se detuvo por un error crítico
            return 1
        
        grupos, archivos_modificados = resultado
        
        # Mostrar resultados resumidos
        print(f"\n=== RESUMEN DEL PROCESAMIENTO ===")
        print(f"Total de trabajadores: {len(grupos)}")
        
        # Contar trabajadores con subsidio
        trabajadores_con_subsidio = 0
        lineas_principales = 0
        
        for rut, filas in grupos.items():
            for fila in filas:
                if fila['esLineaPrincipal']:
                    lineas_principales += 1
                    if fila['tieneSubsidio']:
                        trabajadores_con_subsidio += 1
                        break  # Solo contar una vez por trabajador
        
        print(f"Trabajadores con subsidio: {trabajadores_con_subsidio}")
        print(f"Líneas principales modificadas: {lineas_principales}")
        print(f"Archivos generados: {len(archivos_modificados)}")
        
        # Mostrar algunos ejemplos de las modificaciones
        print(f"\n=== EJEMPLOS DE MODIFICACIONES ===")
        ejemplo_count = 0
        
        for rut, filas in grupos.items():
            for fila in filas:
                if fila['esLineaPrincipal'] and ejemplo_count < 3:
                    print(f"RUT {fila['rutFormateado']} (línea {fila['linea']}):")
                    print(f"  Cotización original: {fila['cotizacionAfp']:,}")
                    print(f"  Cotización actualizada: {fila['cotizacionAfpActualizada']:,}")
                    print(f"  String reemplazo: '{fila['cotizacionAfpActualizadaStr']}'")
                    ejemplo_count += 1
                
                if ejemplo_count >= 3:
                    break
            
            if ejemplo_count >= 3:
                break
        
        print(f"\n✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print(f"Los archivos modificados están en la carpeta: archivos_modificados\\")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")
        print("\nPresione Enter para cerrar...")
        input()
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        print("\nPresione Enter para cerrar...")
        input()
    exit(exit_code)
