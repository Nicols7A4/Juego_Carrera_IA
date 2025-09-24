# --- CONFIGURACIONES DE LA VENTANA ---
SCREEN_WIDTH = 1280 # /40 = 32
SCREEN_HEIGHT = 720 # /40 = 18
FPS = 60
TITLE = "Pathfinding Race AI"

# --- TAMAÑO DE LA CUADRÍCULA ---
CELL_SIZE = 40
# Estas se calcularán después, pero las dejamos aquí para referencia
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# --- COLORES (en formato RGB) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# GRAY = (40, 40, 40)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- ESTADOS DE LAS CELDAS ---
STATE_FREE = 0
STATE_OBSTACLE = 1
STATE_START = 2
STATE_END = 3

# Mapeo de estados a colores para el dibujado
STATE_COLORS = {
    STATE_FREE: GRAY,
    STATE_OBSTACLE: BLACK,
    STATE_START: (0, 150, 0), # Verde oscuro
    STATE_END: (150, 0, 0)   # Rojo oscuro
}