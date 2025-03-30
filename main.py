import heapq 
import math

# --- 1. Base de Conocimiento (Representación de Hechos y Reglas Simuladas) ---

# Hechos: Estaciones, Conexiones, Tiempos, Líneas
# Usaremos diccionarios para simplificar. Una implementación real podría usar clases.
# Ejemplo para Medellín (simplificado)
knowledge_base = {
    'estaciones': {
        'San Antonio': {'lineas': ['A', 'B', 'T']},
        'Parque Berrio': {'lineas': ['A']},
        'Prado': {'lineas': ['A']},
        'Hospital': {'lineas': ['A']},
        'San Javier': {'lineas': ['B', 'J']},
        'Poblado': {'lineas': ['A']},
        'Industriales': {'lineas': ['A', '1', '2']}, # Metro A, Metroplus 1 y 2
        'Cisneros': {'lineas': ['B']},
        'Buenos Aires': {'lineas': ['T']}, # Tranvía
        'Miraflores': {'lineas': ['T', 'M']}, # Tranvía y Metrocable M
    },
    'conexiones': [
        # (origen, destino, linea, tiempo_viaje_minutos)
        ('Parque Berrio', 'San Antonio', 'A', 2),
        ('San Antonio', 'Parque Berrio', 'A', 2),
        ('San Antonio', 'Prado', 'A', 3),
        ('Prado', 'San Antonio', 'A', 3),
        ('Prado', 'Hospital', 'A', 2),
        ('Hospital', 'Prado', 'A', 2),
        ('San Antonio', 'Cisneros', 'B', 3),
        ('Cisneros', 'San Antonio', 'B', 3),
        ('Cisneros', 'San Javier', 'B', 8),
        ('San Javier', 'Cisneros', 'B', 8),
        ('San Antonio', 'Industriales', 'A', 4),
        ('Industriales', 'San Antonio', 'A', 4),
        ('Industriales', 'Poblado', 'A', 5),
        ('Poblado', 'Industriales', 'A', 5),
        ('San Antonio', 'Buenos Aires', 'T', 10), # Conexión Tranvía
        ('Buenos Aires', 'San Antonio', 'T', 10),
        ('Buenos Aires', 'Miraflores', 'T', 5),
        ('Miraflores', 'Buenos Aires', 'T', 5),
        # ... añadir todas las conexiones relevantes del sistema de Medellín
    ],
    'trasbordos': {
        # (estacion, linea_origen, linea_destino): tiempo_trasbordo_minutos
        ('San Antonio', 'A', 'B'): 5,
        ('San Antonio', 'B', 'A'): 5,
        ('San Antonio', 'A', 'T'): 7,
        ('San Antonio', 'T', 'A'): 7,
        ('San Antonio', 'B', 'T'): 6,
        ('San Antonio', 'T', 'B'): 6,
        ('Industriales', 'A', '1'): 4,
        ('Industriales', '1', 'A'): 4,
        # ... otros trasbordos
    },
    'costos': { # Podría ser costo por viaje, por línea, etc. (Simplificado)
        'Metro': 3200,
        'Metroplus': 3200,
        'Tranvia': 3200,
        'Cable': 3200,
        'Integrado': 500, # Costo adicional por trasbordo a bus integrado
    }
    # Podríamos añadir heurísticas aquí si usamos A* (distancia geográfica, etc.)
}

# Reglas Lógicas (Simuladas como funciones Python)

def es_movimiento_valido(estacion_actual, linea_actual, proxima_estacion, kb):
    """Regla: Verifica si existe una conexión directa."""
    for origen, destino, linea, _ in kb['conexiones']:
        if origen == estacion_actual and destino == proxima_estacion:
            # Verifica si la proxima estación pertenece a la línea esperada o si es un inicio de ruta
            if linea_actual is None or linea in kb['estaciones'][proxima_estacion]['lineas']:
                 return True, linea # Devuelve True y la línea usada
    return False, None

def calcular_costo_paso(estacion_actual, linea_actual, proxima_estacion, linea_proxima, kb, criterio='tiempo'):
    """Regla: Calcula el costo (tiempo, trasbordos) de un movimiento."""
    costo = 0
    trasbordo_realizado = False

    # Costo del viaje entre estaciones
    tiempo_viaje = 0
    for origen, destino, linea, tiempo in kb['conexiones']:
        if origen == estacion_actual and destino == proxima_estacion and linea == linea_proxima:
            tiempo_viaje = tiempo
            break

    if criterio == 'tiempo':
        costo += tiempo_viaje
        # Costo del trasbordo si cambiamos de línea
        if linea_actual is not None and linea_actual != linea_proxima:
            trasbordo_realizado = True
            llave_trasbordo = (estacion_actual, linea_actual, linea_proxima)
            costo += kb['trasbordos'].get(llave_trasbordo, 5) # Tiempo de trasbordo default 5 min si no está especificado
    elif criterio == 'trasbordos':
        # El costo principal es 1 si hay trasbordo, 0 si no.
        # Añadimos tiempo de viaje como coste secundario muy pequeño para desempatar
        costo += tiempo_viaje * 0.01
        if linea_actual is not None and linea_actual != linea_proxima:
            trasbordo_realizado = True
            costo += 1 # Suma 1 por cada trasbordo

    # Podrían añadirse otros criterios (costo monetario, etc.)

    return costo, trasbordo_realizado

def obtener_vecinos(estacion, linea_actual, kb):
    """Regla: Encuentra todas las estaciones alcanzables directamente."""
    vecinos = []
    # Buscar conexiones directas en la misma línea o iniciando
    for origen, destino, linea, _ in kb['conexiones']:
        if origen == estacion:
             # Permitir iniciar en cualquier línea de la estación o continuar en la misma
            if linea_actual is None or linea == linea_actual:
                 vecinos.append((destino, linea)) # (estacion_vecina, linea_usada)
            # Permitir trasbordos en la estación actual
            elif linea_actual is not None and linea_actual != linea:
                 # Verificar si hay trasbordo definido (implícito en que la estación tiene ambas líneas)
                 if linea_actual in kb['estaciones'][estacion]['lineas'] and \
                    linea in kb['estaciones'][estacion]['lineas']:
                     vecinos.append((destino, linea)) # Se asume que el trasbordo es posible aquí

    # Eliminar duplicados si una estación es alcanzable por varias vías desde el mismo origen
    # (ej: si hubiera dos líneas directas entre A y B) - aunque no suele pasar en el modelo simple
    return list(set(vecinos))


# --- 2. Motor de Inferencia (Algoritmo de Búsqueda - Dijkstra/A*) ---

def encontrar_mejor_ruta(inicio, fin, kb, criterio='tiempo'):
    """
    Encuentra la mejor ruta usando un algoritmo tipo Dijkstra.
    'criterio' puede ser 'tiempo' o 'trasbordos'.
    """
    if inicio not in kb['estaciones'] or fin not in kb['estaciones']:
        print("Error: Estación de inicio o fin no encontrada en la base de conocimiento.")
        return None

    # Cola de prioridad: (costo_acumulado, estacion_actual, linea_actual, path)
    # path es una lista de tuplas: [(estacion, linea_usada, costo_acumulado_hasta_aqui)]
    pq = [(0, inicio, None, [(inicio, None, 0)])] # Costo inicial 0, sin línea inicial

    # Registro de visitados: { (estacion, linea_entrante) : costo_minimo }
    # Se necesita la línea para diferenciar costos si llegamos a la misma estación por diferentes líneas
    visitados = {}

    while pq:
        costo_actual, estacion_actual, linea_actual, path = heapq.heappop(pq)

        # Clave para el diccionario de visitados
        estado_actual_key = (estacion_actual, linea_actual)

        # Optimización: Si ya encontramos un camino mejor a este estado, lo ignoramos
        if estado_actual_key in visitados and visitados[estado_actual_key] <= costo_actual:
            continue

        # Marcamos como visitado con su costo
        visitados[estado_actual_key] = costo_actual

        # Objetivo alcanzado?
        if estacion_actual == fin:
            print(f"Ruta encontrada con criterio '{criterio}':")
            costo_total = costo_actual
            num_trasbordos = sum(1 for i in range(len(path) - 1) if path[i][1] and path[i+1][1] and path[i][1] != path[i+1][1] )
            
            ruta_str = " -> ".join([f"{est}({lin if lin else 'Inicio'})" for est, lin, _ in path])
            print(f"  Ruta: {ruta_str}")
            if criterio == 'tiempo':
                 print(f"  Tiempo estimado: {costo_total:.2f} minutos")
                 print(f"  Trasbordos: {num_trasbordos}")
            elif criterio == 'trasbordos':
                 # El costo principal eran los trasbordos, el tiempo era secundario
                 print(f"  Trasbordos: {math.floor(costo_total)}") # Redondear hacia abajo para quitar la parte decimal del tiempo
                 tiempo_real = sum(p[2] - (path[i-1][2] if i > 0 else 0) for i, p in enumerate(path)) # Recalcular tiempo real
                 print(f"  Tiempo estimado: {tiempo_real:.2f} minutos") # Esto es una aproximación

            return path # Devolvemos la ruta encontrada

        # Explorar vecinos (Aplicar reglas para encontrar siguientes pasos)
        vecinos = obtener_vecinos(estacion_actual, linea_actual, kb)

        for proxima_estacion, linea_proxima in vecinos:
            # Aplicar regla para calcular el costo del paso
            costo_paso, _ = calcular_costo_paso(
                estacion_actual, linea_actual, proxima_estacion, linea_proxima, kb, criterio
            )

            nuevo_costo = costo_actual + costo_paso
            nuevo_estado_key = (proxima_estacion, linea_proxima)

            # Si no hemos visitado este estado (estacion, linea_llegada) o encontramos un camino más corto
            if nuevo_estado_key not in visitados or nuevo_costo < visitados[nuevo_estado_key]:
                nuevo_path = path + [(proxima_estacion, linea_proxima, nuevo_costo)]
                heapq.heappush(pq, (nuevo_costo, proxima_estacion, linea_proxima, nuevo_path))

    print(f"No se encontró una ruta desde {inicio} hasta {fin}.")
    return None

# --- 3. Ejecución ---

# Definir puntos de inicio y fin
estacion_inicio = 'Parque Berrio'
estacion_fin = 'San Javier'

# Buscar la ruta más rápida
print("--- Buscando ruta más rápida (tiempo) ---")
ruta_tiempo = encontrar_mejor_ruta(estacion_inicio, estacion_fin, knowledge_base, criterio='tiempo')

print("\n--- Buscando ruta con menos trasbordos ---")
# Buscar la ruta con menos trasbordos
ruta_trasbordos = encontrar_mejor_ruta(estacion_inicio, estacion_fin, knowledge_base, criterio='trasbordos')

# Ejemplo con trasbordo explícito necesario
print("\n--- Ejemplo Prado a Miraflores (Requiere trasbordo) ---")
ruta_prado_miraflores_t = encontrar_mejor_ruta('Prado', 'Miraflores', knowledge_base, criterio='tiempo')
ruta_prado_miraflores_tr = encontrar_mejor_ruta('Prado', 'Miraflores', knowledge_base, criterio='trasbordos')