import math

class PathfinderBase:
    """
    Clase base para todos los algoritmos de búsqueda de caminos.
    Define la interfaz que deben seguir.
    """
    def __init__(self, grid, allow_diagonal=False):
        self.grid = grid
        self.allow_diagonal = allow_diagonal

    def get_neighbors_and_costs(self, position):
        """
        Obtiene los vecinos válidos de una posición y sus costos.
        Retorna una lista de tuplas (nueva_posicion, costo).
        """
        neighbors = []
        x, y = position
        
        # Movimientos básicos (4 direcciones)
        basic_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        # Movimientos diagonales (4 direcciones adicionales)
        diagonal_moves = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        # Combinar movimientos según la configuración
        moves = basic_moves
        if self.allow_diagonal:
            moves.extend(diagonal_moves)
        
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy
            
            # Verificar límites del grid
            if not (0 <= new_x < self.grid.cols and 0 <= new_y < self.grid.rows):
                continue
            
            # Verificar obstáculos
            if self.grid.states[new_x][new_y] == self._get_obstacle_state():
                continue
            
            # Calcular costo del movimiento
            if abs(dx) + abs(dy) == 2:  # Movimiento diagonal
                cost = math.sqrt(2)  # ≈ 1.414
            else:  # Movimiento básico
                cost = 1.0
            
            neighbors.append(((new_x, new_y), cost))
        
        return neighbors
    
    def _get_obstacle_state(self):
        """Obtiene el estado que representa un obstáculo."""
        # Importamos config aquí para evitar dependencias circulares
        import config
        return config.STATE_OBSTACLE

    def find_path(self, start_pos, end_pos):
        """
        Encuentra el camino desde un punto de inicio a un punto final.
        Este método debe ser implementado por las clases hijas.
        """
        raise NotImplementedError