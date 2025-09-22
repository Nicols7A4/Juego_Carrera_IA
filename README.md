# Pathfinding Race AI

Este proyecto es una aplicación interactiva de visualización y competencia de algoritmos de búsqueda de caminos (pathfinding) desarrollada en Python con Pygame.

## Características principales
- **Visualización de algoritmos**: A*, Dijkstra, Voraz (Greedy), Costo Uniforme
- **Modo Carrera**: Compite humano vs IA o IA vs IA
- **Editor de mapas**: Crea y guarda tus propios mapas personalizados
- **Modo de pruebas**: Paso a paso, retroceso y visualización del árbol de búsqueda
- **Soporte para movimiento diagonal**
- **Interfaz en español**

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
- Desarrollado por Adolfo y colaboradores
- Inspirado en proyectos educativos de visualización de algoritmos

## Licencia
Este proyecto es de uso educativo y libre para modificar.
