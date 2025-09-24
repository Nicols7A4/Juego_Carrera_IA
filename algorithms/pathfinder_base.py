import math

class PathfinderBase:
    """
    Clase base para todos los algoritmos de búsqueda de caminos.
    Define la interfaz que deben seguir.
    """
    def __init__(self, grid, allow_diagonal=False):
        self.grid = grid
        self.allow_diagonal = allow_diagonal
        self.iteraciones = 0  # Contador de iteraciones

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
    
    def calcular_heuristica(self, pos1, pos2):
        """
        Calcula la heurística apropiada según el tipo de movimiento permitido.
        - Si permite diagonal: usa distancia diagonal
        - Si no permite diagonal: usa distancia Manhattan
        """
        import math
        
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        
        if self.allow_diagonal:
            # Distancia diagonal: combina movimientos diagonales y rectos
            # Costo diagonal = sqrt(2), costo recto = 1
            # Fórmula: max(dx, dy) + (sqrt(2) - 1) * min(dx, dy)
            return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)
        else:
            # Distancia Manhattan para movimiento solo ortogonal
            return dx + dy
    
    # Propiedades para compatibilidad con código existente
    @property
    def iterations(self):
        return self.iteraciones
    
    @iterations.setter
    def iterations(self, valor):
        self.iteraciones = valor
    
    @property
    def calculate_heuristic(self):
        return self.calcular_heuristica

    def find_path(self, start_pos, end_pos):
        """
        Encuentra el camino desde un punto de inicio a un punto final.
        Este método debe ser implementado por las clases hijas.
        """
        raise NotImplementedError