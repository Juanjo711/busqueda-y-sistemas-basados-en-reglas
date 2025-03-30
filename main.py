import heapq 
import math

# --- 1. Base de Conocimiento (Representación de Hechos y Reglas Simuladas) ---
knowledge_base = {
    'estaciones': {
        'San Antonio': {'lineas': ['A', 'B', 'T']},
        'Parque Berrio': {'lineas': ['A']},
        'Prado': {'lineas': ['A']},
        'Hospital': {'lineas': ['A']},
        'San Javier': {'lineas': ['B', 'J']},
        'Poblado': {'lineas': ['A']},
        'Industriales': {'lineas': ['A', '1', '2']},
        'Cisneros': {'lineas': ['B']},
        'Buenos Aires': {'lineas': ['T']},
        'Miraflores': {'lineas': ['T', 'M']},
    },
    'conexiones': [
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
        ('San Antonio', 'Buenos Aires', 'T', 10),
        ('Buenos Aires', 'San Antonio', 'T', 10),
        ('Buenos Aires', 'Miraflores', 'T', 5),
        ('Miraflores', 'Buenos Aires', 'T', 5),
    ],
    'trasbordos': {
        ('San Antonio', 'A', 'B'): 5,
        ('San Antonio', 'B', 'A'): 5,
        ('San Antonio', 'A', 'T'): 7,
        ('San Antonio', 'T', 'A'): 7,
        ('San Antonio', 'B', 'T'): 6,
        ('San Antonio', 'T', 'B'): 6,
        ('Industriales', 'A', '1'): 4,
        ('Industriales', '1', 'A'): 4,
    },
    'costos': {
        'Metro': 3200,
        'Metroplus': 3200,
        'Tranvia': 3200,
        'Cable': 3200,
        'Integrado': 500,
    }
}

def es_movimiento_valido(estacion_actual, linea_actual, proxima_estacion, kb):
    """Regla: Verifica si existe una conexión directa."""
    for origen, destino, linea, _ in kb['conexiones']:
        if origen == estacion_actual and destino == proxima_estacion:
            if linea_actual is None or linea in kb['estaciones'][proxima_estacion]['lineas']:
                 return True, linea
    return False, None

def obtener_vecinos(estacion, linea_actual, kb):
    """Regla: Encuentra todas las estaciones alcanzables directamente."""
    vecinos = []
    for origen, destino, linea, _ in kb['conexiones']:
        if origen == estacion:
            if linea_actual is None or linea == linea_actual:
                 vecinos.append((destino, linea))
            elif linea_actual is not None and linea_actual != linea:
                 if linea_actual in kb['estaciones'][estacion]['lineas'] and \
                    linea in kb['estaciones'][estacion]['lineas']:
                     vecinos.append((destino, linea))

    return list(set(vecinos))

def calcular_costo_paso(estacion_actual, linea_actual, proxima_estacion, linea_proxima, kb, criterio='tiempo'):
    """Regla: Calcula el costo (tiempo, trasbordos) de un movimiento."""
    costo = 0
    trasbordo_realizado = False

    tiempo_viaje = 0
    for origen, destino, linea, tiempo in kb['conexiones']:
        if origen == estacion_actual and destino == proxima_estacion and linea == linea_proxima:
            tiempo_viaje = tiempo
            break

    if criterio == 'tiempo':
        costo += tiempo_viaje
        if linea_actual is not None and linea_actual != linea_proxima:
            trasbordo_realizado = True
            llave_trasbordo = (estacion_actual, linea_actual, linea_proxima)
            costo += kb['trasbordos'].get(llave_trasbordo, 5) # Tiempo de trasbordo default 5 min si no está especificado
    elif criterio == 'trasbordos':
        costo += tiempo_viaje * 0.01
        if linea_actual is not None and linea_actual != linea_proxima:
            trasbordo_realizado = True
            costo += 1

    return costo, trasbordo_realizado


# --- 2. Motor de Inferencia (Algoritmo de Búsqueda - Dijkstra/A*) ---

def encontrar_mejor_ruta(inicio, fin, kb, criterio='tiempo'):
    """
    Encuentra la mejor ruta usando un algoritmo tipo Dijkstra.
    'criterio' puede ser 'tiempo' o 'trasbordos'.
    """
    if inicio not in kb['estaciones'] or fin not in kb['estaciones']:
        print("Error: Estación de inicio o fin no encontrada en la base de conocimiento.")
        return None

    pq = [(0, inicio, None, [(inicio, None, 0)])]

    visitados = {}

    while pq:
        costo_actual, estacion_actual, linea_actual, path = heapq.heappop(pq)

        estado_actual_key = (estacion_actual, linea_actual)

        if estado_actual_key in visitados and visitados[estado_actual_key] <= costo_actual:
            continue

        visitados[estado_actual_key] = costo_actual

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
                 print(f"  Trasbordos: {math.floor(costo_total)}")
                 tiempo_real = sum(p[2] - (path[i-1][2] if i > 0 else 0) for i, p in enumerate(path))
                 print(f"  Tiempo estimado: {tiempo_real:.2f} minutos")

            return path # Devolvemos la ruta encontrada

        vecinos = obtener_vecinos(estacion_actual, linea_actual, kb)

        for proxima_estacion, linea_proxima in vecinos:
            costo_paso, _ = calcular_costo_paso(
                estacion_actual, linea_actual, proxima_estacion, linea_proxima, kb, criterio
            )

            nuevo_costo = costo_actual + costo_paso
            nuevo_estado_key = (proxima_estacion, linea_proxima)

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