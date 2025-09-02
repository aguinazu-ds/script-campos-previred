import random

def extraer_ruts_del_archivo():
    """
    Extrae todos los RUTs únicos del archivo de datos y los formatea correctamente.
    """
    ruts_procesados = set()
    
    with open('archivos105espacios/077120142202508.TXT', 'r', encoding='utf-8', errors='replace') as f:
        for linea in f:
            if len(linea) >= 12:
                # Extraer los primeros 12 caracteres
                rut_completo = linea[0:12]
                
                # El RUT son los primeros 11 caracteres, el 12vo es el dígito verificador
                rut_numeros = rut_completo[0:11]
                digito_verificador = rut_completo[11]
                
                # Quitar ceros a la izquierda de los números
                rut_sin_ceros = rut_numeros.lstrip('0')
                
                # Si queda vacío después de quitar ceros, significa que era "00000000000"
                if not rut_sin_ceros:
                    rut_sin_ceros = "0"
                
                # Formatear como RUT chileno: números-dígito_verificador
                rut_formateado = f"{rut_sin_ceros}-{digito_verificador}"
                
                ruts_procesados.add(rut_formateado)
    
    return sorted(list(ruts_procesados))

def generar_archivo_jornadas():
    """
    Genera el archivo jornadasTrabajadores.csv con los RUTs y jornadas aleatorias.
    """
    ruts = extraer_ruts_del_archivo()
    
    # Crear el archivo CSV
    with open('jornadas/jornadasTrabajadores.csv', 'w', encoding='utf-8') as f:
        # Escribir header (opcional)
        f.write("rut;jornada\n")
        
        for rut in ruts:
            # Generar jornada aleatoria: 1 = completa, 2 = parcial
            # Hacemos que la mayoría sean jornada completa (80%)
            jornada = 1 if random.random() < 0.8 else 2
            f.write(f"{rut};{jornada}\n")
    
    print(f"Archivo generado: jornadas/jornadasTrabajadores.csv")
    print(f"Total de trabajadores: {len(ruts)}")
    
    # Mostrar algunos ejemplos
    print("\nEjemplos generados:")
    with open('jornadas/jornadasTrabajadores.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[1:11]):  # Mostrar los primeros 10 (sin header)
            print(f"  {line.strip()}")

if __name__ == "__main__":
    generar_archivo_jornadas()
