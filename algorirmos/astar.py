class Node:
    def __init__(self, position=(0,0), parent=None, tipo='Normal'):
        self.position = position  # Corregido el nombre del atributo
        self.parent = parent      # Añadido para rastrear el camino
        self.g = 0               # Costo desde el inicio hasta este nodo
        self.h = 0               # Heurística estimada hasta el final
        self.f = 0               # Costo total (g + h)
        self.tipo = tipo         # Tipo de nodo (Normal, Obstáculo, etc.)
        
    def update_scores(self, g, h):
        """Actualiza los valores g, h y f del nodo"""
        self.g = g
        self.h = h
        self.f = g + h
    
    def get_neighbors(self, grid, allow_diagonal=True):
        """Obtiene los nodos vecinos válidos"""
        x, y = self.position
        neighbors = []
        
        # Movimientos posibles: [dx, dy, costo]
        movements = [
            (-1, 0, 10),  # Arriba
            (1, 0, 10),   # Abajo
            (0, -1, 10),  # Izquierda
            (0, 1, 10)    # Derecha
        ]
        
        if allow_diagonal:
            movements.extend([
                (-1, -1, 14),  # Diagonal superior izquierda
                (-1, 1, 14),   # Diagonal superior derecha
                (1, -1, 14),   # Diagonal inferior izquierda
                (1, 1, 14)     # Diagonal inferior derecha
            ])
        
        for dx, dy, cost in movements:
            new_x, new_y = x + dx, y + dy
            
            # Verificar si la posición está dentro de la cuadrícula
            if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]):
                # Verificar que no sea un obstáculo
                if grid[new_x][new_y] != 'Obstaculo':
                    neighbor = Node((new_x, new_y))
                    neighbor.movement_cost = cost
                    neighbors.append(neighbor)
        
        return neighbors
    

def heuristic(a, b, allow_diagonal=True):
    """Calcula la heurística (distancia) entre dos puntos"""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    
    if allow_diagonal:
        # Distancia diagonal (permite movimientos en 8 direcciones)
        return 10 * (dx + dy) + (14 - 2 * 10) * min(dx, dy)
    else:
        # Distancia Manhattan (solo permite movimientos en 4 direcciones)
        return 10 * (dx + dy)


def astar(start_pos, end_pos, grid, allow_diagonal=True):
    """Implementación del algoritmo A*"""
    # Crear nodos inicial y final
    start_node = Node(start_pos)
    end_node = Node(end_pos)
    
    # Inicializar listas abierta y cerrada
    open_list = []
    closed_list = []
    
    # Agregar nodo inicial a la lista abierta
    open_list.append(start_node)
    
    while open_list:
        # Encontrar el nodo con menor f en la lista abierta
        current_node = min(open_list, key=lambda x: x.f)
        
        # Mover el nodo actual de la lista abierta a la cerrada
        open_list.remove(current_node)
        closed_list.append(current_node)
        
        # Si llegamos al destino, reconstruir y devolver el camino
        if current_node.position == end_node.position:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Devolver el camino invertido
        
        # Obtener vecinos del nodo actual
        neighbors = current_node.get_neighbors(grid, allow_diagonal)
        
        for neighbor in neighbors:
            # Saltar si el vecino ya está en la lista cerrada
            if any(closed_node.position == neighbor.position for closed_node in closed_list):
                continue
            
            # Calcular el nuevo costo g
            tentative_g = current_node.g + neighbor.movement_cost
            
            # Verificar si el vecino ya está en la lista abierta
            in_open_list = False
            for open_node in open_list:
                if open_node.position == neighbor.position:
                    if tentative_g >= open_node.g:
                        # Este camino no es mejor que el existente
                        in_open_list = True
                        break
                    else:
                        # Este camino es mejor, actualizar el nodo
                        open_list.remove(open_node)
                        break
            
            if not in_open_list:
                # Añadir el vecino a la lista abierta
                neighbor.parent = current_node
                neighbor.update_scores(
                    g=tentative_g,
                    h=heuristic(neighbor.position, end_pos, allow_diagonal)
                )
                open_list.append(neighbor)
    
    # No se encontró un camino
    return None


# # Ejemplo de uso:
# if __name__ == "__main__":
#     # Ejemplo de cuadrícula (0 = libre, 1 = obstáculo)
#     grid = [
#         [0, 0, 0, 1, 0],
#         [1, 1, 0, 1, 0],
#         [0, 0, 0, 0, 0],
#         [0, 1, 1, 1, 0],
#         [0, 0, 0, 1, 0]
#     ]
    
#     # Convertir números a tipos de nodo
#     grid = [['Obstaculo' if cell == 1 else 'Normal' for cell in row] for row in grid]
    
#     start = (0, 0)
#     end = (4, 4)
    
#     path = astar(start, end, grid, False)
#     if path:
#         print("Camino encontrado:", path)
#     else:
#         print("No se encontró un camino")