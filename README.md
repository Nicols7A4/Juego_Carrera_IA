# Pathfinding Race AI

Este proyecto es una aplicación interactiva de visualización y competencia de algoritmos de búsqueda de caminos (pathfinding) desarrollada en Python con Pygame.

## Características principales
- **Visualización de algoritmos**: A*, Dijkstra, Voraz (Greedy), Costo Uniforme
- **Modo Carrera**: Compite humano vs IA o IA vs IA
- **Editor de mapas**: Crea y guarda tus propios mapas personalizados
- **Modo de pruebas**: Paso a paso, retroceso y visualización del árbol de búsqueda
- **Soporte para movimiento diagonal**
- **Interfaz en español**

## Funcionamiento de los algoritmos

### Estructura de nodos
Cada algoritmo utiliza nodos que contienen:
- **Posición**: Coordenadas (x, y) en la grilla
- **Padre**: Nodo anterior para reconstruir el camino
- **Costos**: g (costo real), h (heurística), f (costo total)

### Heurísticas implementadas
- **Sin diagonal**: Distancia Manhattan (`|x1-x2| + |y1-y2|`)
- **Con diagonal**: Distancia diagonal (`max(dx,dy) + (√2-1)*min(dx,dy)`)

### Proceso de ejecución
1. **Inicialización**: `initialize_search(start, end)` prepara listas abiertas/cerradas
2. **Iteración**: `step()` procesa un nodo y expande vecinos
3. **Finalización**: `find_path()` ejecuta hasta encontrar el objetivo

### Carga y selección de mapas
- Los mapas se almacenan en formato JSON en `assets/maps/`
- `map_manager.load_map_data()` lee obstáculos, inicio y fin
- `grid.load_map()` aplica los datos a la grilla visual

### Tipos de movimiento
- **IA**: Calcula camino completo, luego se mueve automáticamente paso a paso
- **Humano**: Movimiento continuo con teclas presionadas (flechas + QEZC diagonal)
- **Ambos**: Validación de obstáculos y límites en tiempo real

## Estructura del proyecto
- `algorithms/` — Implementaciones de los algoritmos de búsqueda
- `components/` — Componentes reutilizables (agente, botón, grilla)
- `scenes/` — Escenas del juego (menú, carrera, editor, pruebas, etc.)
- `assets/` — Recursos como mapas y fuentes
- `main.py` — Punto de entrada principal
- `config.py` — Configuración global de la aplicación

## Requisitos
- Python 3.8+
- pygame
- matplotlib (para el visualizador de árbol)
- networkx (para el visualizador de árbol)

Instala las dependencias con:
```bash
pip install -r requirements.txt
```

## Ejecución
Desde la raíz del proyecto:
```bash
python main.py
```

## Créditos
- Inspirado en proyectos educativos de visualización de algoritmos

## Licencia
Este proyecto es de uso educativo y libre para modificar.
