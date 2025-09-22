import pygame
import math
import config

class TreeVisualizerWindow:
    """Visualizador de árbol de búsqueda en una ventana separada."""
    
    def __init__(self, width=1000, height=700):
        self.width = width
        self.height = height
        self.is_open = False
        self.screen = None
        self.clock = pygame.time.Clock()
        
        # Configuración visual
        self.node_radius = 25
        self.font_small = pygame.font.SysFont('B612Mono', 10)
        self.font_medium = pygame.font.SysFont('B612Mono', 12, bold=True)
        
        # Colores
        self.colors = {
            'background': (240, 240, 240),
            'open_node': (255, 255, 100),      # Amarillo para nodos abiertos
            'closed_node': (100, 200, 255),    # Azul para nodos cerrados  
            'path_node': (255, 100, 255),      # Magenta para nodos en el camino
            'start_node': (100, 255, 100),     # Verde para inicio
            'goal_node': (255, 100, 100),      # Rojo para objetivo
            'line': (80, 80, 80),              # Gris para líneas
            'text': (0, 0, 0)                  # Negro para texto
        }
        
        # Estado del árbol
        self.tree_layout = {}  # Posiciones de los nodos
        self.node_levels = {}  # Nivel de cada nodo en el árbol
        
        # Control de cámara
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        
    def open_window(self):
        """Abre la ventana del visualizador."""
        if not self.is_open:
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Visualizador de Árbol de Búsqueda")
            self.is_open = True
            
    def close_window(self):
        """Cierra la ventana del visualizador."""
        if self.is_open:
            pygame.display.quit()
            self.is_open = False
            self.screen = None
            
    def toggle_window(self):
        """Alterna entre abrir y cerrar la ventana."""
        if self.is_open:
            self.close_window()
        else:
            self.open_window()
            
    def calculate_tree_layout(self, all_nodes, start_pos, goal_pos):
        """Calcula las posiciones de los nodos en el árbol."""
        if not all_nodes:
            return
            
        # Crear un mapa de posición a nodo para búsqueda rápida
        pos_to_node = {node.position: node for node in all_nodes}
        
        # Encontrar el nodo raíz (start)
        root_node = pos_to_node.get(start_pos)
        if not root_node:
            return
            
        # Calcular niveles usando BFS
        self.node_levels = {}
        self.tree_layout = {}
        
        # BFS para calcular niveles
        queue = [(root_node, 0)]
        visited = {root_node.position}
        level_nodes = {}  # level -> [nodes]
        
        while queue:
            current_node, level = queue.pop(0)
            self.node_levels[current_node.position] = level
            
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(current_node)
            
            # Buscar hijos (nodos que tienen este como padre)
            for node in all_nodes:
                if (node.parent and 
                    node.parent.position == current_node.position and 
                    node.position not in visited):
                    queue.append((node, level + 1))
                    visited.add(node.position)
        
        # Calcular posiciones
        max_level = max(level_nodes.keys()) if level_nodes else 0
        level_height = 80
        
        for level, nodes in level_nodes.items():
            y = 50 + level * level_height
            node_count = len(nodes)
            
            if node_count == 1:
                x = self.width // 2
                self.tree_layout[nodes[0].position] = (x, y)
            else:
                # Distribuir horizontalmente
                total_width = self.width - 100
                spacing = total_width / (node_count + 1)
                
                for i, node in enumerate(nodes):
                    x = 50 + spacing * (i + 1)
                    self.tree_layout[node.position] = (x, y)
    
    def draw_tree(self, open_list, closed_list, path, start_pos, goal_pos):
        """Dibuja el árbol de búsqueda."""
        if not self.is_open or not self.screen:
            return
            
        # Limpiar pantalla
        self.screen.fill(self.colors['background'])
        
        # Combinar todos los nodos
        all_nodes = open_list + closed_list
        
        if not all_nodes:
            pygame.display.flip()
            return
            
        # Calcular layout del árbol
        self.calculate_tree_layout(all_nodes, start_pos, goal_pos)
        
        # Dibujar líneas de conexión primero
        self._draw_connections(all_nodes)
        
        # Dibujar nodos
        self._draw_nodes(open_list, closed_list, path, start_pos, goal_pos)
        
        # Dibujar instrucciones
        self._draw_instructions()
        
        pygame.display.flip()
        
    def _draw_connections(self, all_nodes):
        """Dibuja las líneas de conexión entre nodos padre-hijo."""
        for node in all_nodes:
            if node.parent and node.position in self.tree_layout and node.parent.position in self.tree_layout:
                start_pos = self.tree_layout[node.parent.position]
                end_pos = self.tree_layout[node.position]
                
                pygame.draw.line(self.screen, self.colors['line'], start_pos, end_pos, 2)
                
    def _draw_nodes(self, open_list, closed_list, path, start_pos, goal_pos):
        """Dibuja los nodos del árbol."""
        # Crear sets para búsqueda rápida
        open_positions = {node.position for node in open_list}
        closed_positions = {node.position for node in closed_list}
        path_positions = set(path) if path else set()
        
        # Dibujar todos los nodos
        all_nodes = open_list + closed_list
        
        for node in all_nodes:
            if node.position not in self.tree_layout:
                continue
                
            x, y = self.tree_layout[node.position]
            
            # Determinar color del nodo
            if node.position == start_pos:
                color = self.colors['start_node']
            elif node.position == goal_pos:
                color = self.colors['goal_node']
            elif node.position in path_positions:
                color = self.colors['path_node']
            elif node.position in closed_positions:
                color = self.colors['closed_node']
            else:  # open_list
                color = self.colors['open_node']
            
            # Dibujar círculo del nodo
            pygame.draw.circle(self.screen, color, (int(x), int(y)), self.node_radius)
            pygame.draw.circle(self.screen, self.colors['text'], (int(x), int(y)), self.node_radius, 2)
            
            # Dibujar texto del nodo
            self._draw_node_text(node, x, y)
            
    def _draw_node_text(self, node, x, y):
        """Dibuja el texto de información del nodo."""
        # Posición del nodo
        pos_text = f"{node.position}"
        pos_surface = self.font_small.render(pos_text, True, self.colors['text'])
        pos_rect = pos_surface.get_rect(center=(x, y - 8))
        self.screen.blit(pos_surface, pos_rect)
        
        # Valores G, H, F
        def format_value(val):
            if isinstance(val, float):
                return f"{val:.1f}" if val != int(val) else str(int(val))
            return str(val)
            
        g_text = f"G:{format_value(node.g)}"
        h_text = f"H:{format_value(node.h)}"
        f_text = f"F:{format_value(node.f)}"
        
        # Dibujar G
        g_surface = self.font_small.render(g_text, True, self.colors['text'])
        self.screen.blit(g_surface, (x - self.node_radius + 2, y + 2))
        
        # Dibujar H
        h_surface = self.font_small.render(h_text, True, self.colors['text'])
        h_rect = h_surface.get_rect()
        self.screen.blit(h_surface, (x + self.node_radius - h_rect.width - 2, y + 2))
        
        # Dibujar F (centrado abajo)
        f_surface = self.font_medium.render(f_text, True, self.colors['text'])
        f_rect = f_surface.get_rect(center=(x, y + self.node_radius - 8))
        self.screen.blit(f_surface, f_rect)
        
    def _draw_instructions(self):
        """Dibuja las instrucciones de uso."""
        instructions = [
            "Visualizador de Árbol de Búsqueda",
            "Verde: Nodo inicial | Rojo: Nodo objetivo",
            "Amarillo: Lista abierta | Azul: Lista cerrada",
            "Magenta: Camino encontrado"
        ]
        
        y_offset = 10
        for instruction in instructions:
            text_surface = self.font_medium.render(instruction, True, self.colors['text'])
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
            
    def handle_events(self):
        """Maneja los eventos de la ventana del árbol."""
        if not self.is_open:
            return True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_window()
                return False
                
        return True
        
    def update(self):
        """Actualiza la ventana del árbol."""
        if self.is_open:
            self.clock.tick(60)  # 60 FPS