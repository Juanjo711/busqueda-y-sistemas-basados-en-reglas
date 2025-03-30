# Sistema Inteligente de Rutas de Transporte Público (SITVA Medellín)

Este proyecto implementa un sistema inteligente en Python capaz de determinar la ruta óptima entre dos puntos (estaciones) dentro del sistema de transporte masivo local del Valle de Aburrá (SITVA). El sistema utiliza una base de conocimiento con hechos (estaciones, conexiones, tiempos) y reglas lógicas (simuladas en Python) para encontrar la mejor ruta según criterios como el tiempo estimado de viaje o el número mínimo de trasbordos.

## Características Principales

* **Cálculo de Rutas:** Encuentra una secuencia de estaciones y líneas para ir de un punto A a un punto B.
* **Base de Conocimiento:** Modela la red de transporte (estaciones, líneas, conexiones, tiempos de viaje, tiempos de trasbordo).
    * Actualmente modela Líneas A y B del Metro, Tranvía T.
* **Optimización Basada en Criterios:** Permite buscar la ruta:
    * Más rápida (menor tiempo total estimado).
    * Con menos trasbordos.
* **Motor de Inferencia Simple:** Utiliza algoritmos de búsqueda (como Dijkstra) y funciones Python que simulan reglas lógicas para explorar y evaluar rutas.

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.12.3
* **Bibliotecas Principales:**
    * `heapq` (para la cola de prioridad en el algoritmo de búsqueda)
* **Gestor de Paquetes:** `pip`

## Instalación y Configuración

Sigue estos pasos para configurar el entorno de desarrollo local:

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://www.atlassian.com/es/git/tutorials/setting-up-a-repository](https://www.atlassian.com/es/git/tutorials/setting-up-a-repository)
    cd [Nombre de la carpeta del repositorio]
    ```
    
## Uso

Para encontrar una ruta, ejecuta el script principal `main.py` desde la terminal.

**Ejemplo:**

```bash
python main.py --inicio "Nombre Estacion Inicio" --fin "Nombre Estacion Fin" --criterio [tiempo|trasbordos]

python main.py --inicio "Parque Berrio" --fin "San Javier" --criterio tiempo