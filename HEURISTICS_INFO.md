# Heurísticas Implementadas en los Algoritmos

## Antes vs Después

### Implementación ANTERIOR (problemática):
```python
# Distancia Euclidiana al cuadrado - NO ADMISIBLE
h = (x1 - x2)² + (y1 - y2)²
```

### Implementación ACTUAL (mejorada):

#### Para movimiento SIN diagonal (4-direccional):
```python
# Distancia Manhattan - ADMISIBLE y ÓPTIMA
h = |x1 - x2| + |y1 - y2|
```

#### Para movimiento CON diagonal (8-direccional):
```python
# Distancia Diagonal (Chebyshev modificada) - ADMISIBLE y ÓPTIMA
dx = |x1 - x2|
dy = |y1 - y2|
h = max(dx, dy) + (√2 - 1) × min(dx, dy)
```

## Ventajas de las nuevas heurísticas:

### 1. **Admisibilidad garantizada**
- Nunca sobrestiman el costo real
- A* garantiza encontrar el camino óptimo

### 2. **Consistencia mejorada**
- Satisfacen la desigualdad triangular
- Búsqueda más estable y predecible

### 3. **Eficiencia mejorada**
- Menos nodos explorados
- Convergencia más rápida al objetivo

### 4. **Adaptabilidad**
- Se ajusta automáticamente según el tipo de movimiento permitido
- Heurística óptima para cada configuración

## Impacto en los algoritmos:

### A* (AStarPathfinder):
- Mantiene optimalidad garantizada
- Reduce significativamente los nodos explorados
- Mejor rendimiento especialmente en mapas complejos

### Greedy (GreedyPathfinder):
- Comportamiento más directo hacia el objetivo
- Menos zigzagueo innecesario
- Mejor calidad de caminos (aunque no garantiza optimalidad)

## Resultado esperado:
- **Menos iteraciones** en promedio
- **Menos nodos explorados**
- **Caminos más directos**
- **Mejor rendimiento computacional**