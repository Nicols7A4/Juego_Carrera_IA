import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from collections import deque
import math
import config

class AlgorithmTreeVisualizer:
    """Visualizador de árbol de algoritmos de búsqueda usando tkinter y matplotlib."""
    
    def __init__(self, grid, algorithm_name, history, current_step, allow_diagonal):
        self.grid = grid
        self.algorithm_name = algorithm_name
        self.history = history if history else []
        self.current_step = current_step if current_step >= 0 else 0
        self.allow_diagonal = allow_diagonal
        
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title(f"Visualizador de Árbol - {algorithm_name}")
        self.root.geometry("1400x800")
        
        # Configurar layout principal
        self.setup_ui()
        
        # Variables de control
        self.step_index = max(0, min(current_step, len(self.history) - 1)) if self.history else 0
        
        # Actualizar visualización inicial
        self.update_visualization()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Botones de navegación
        tk.Button(controls_frame, text="⏮ Inicio", command=self.go_to_start).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="◀ Anterior", command=self.prev_step).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="▶ Siguiente", command=self.next_step).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="⏭ Final", command=self.go_to_end).pack(side=tk.LEFT, padx=5)
        
        # Separador
        tk.Label(controls_frame, text="|").pack(side=tk.LEFT, padx=10)
        
        # Información del paso actual
        self.step_label = tk.Label(controls_frame, text="Paso: 0/0", font=("Arial", 12, "bold"))
        self.step_label.pack(side=tk.LEFT, padx=10)
        
        # Información del algoritmo
        algo_info = tk.Label(controls_frame, text=f"Algoritmo: {self.algorithm_name}", font=("Arial", 10))
        algo_info.pack(side=tk.RIGHT, padx=10)
        
        # Frame para estadísticas
        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.stats_labels = {}
        stats_names = ["Nodos Abiertos", "Nodos Cerrados", "Nodos en Camino", "Costo Total"]
        for i, stat in enumerate(stats_names):
            frame = tk.Frame(stats_frame)
            frame.pack(side=tk.LEFT, padx=20)
            
            tk.Label(frame, text=stat, font=("Arial", 9, "bold")).pack()
            self.stats_labels[stat] = tk.Label(frame, text="0", font=("Arial", 12))
            self.stats_labels[stat].pack()
        
        # Frame para la visualización
        viz_frame = tk.Frame(main_frame)
        viz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear figura de matplotlib
        self.fig = Figure(figsize=(14, 7))
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        # Subplots: mapa (izquierda) y árbol (derecha)
        self.ax_map = self.fig.add_subplot(1, 2, 1)
        self.ax_tree = self.fig.add_subplot(1, 2, 2)
        
        # Canvas para matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def update_visualization(self):
        """Actualiza la visualización completa."""
        self.update_step_info()
        self.update_statistics()
        self.draw_grid_state()
        self.draw_search_tree()
        self.canvas.draw()
        
    def update_step_info(self):
        """Actualiza la información del paso actual."""
        total_steps = len(self.history)
        current = self.step_index + 1 if self.history else 0
        self.step_label.config(text=f"Paso: {current}/{total_steps}")
        
    def update_statistics(self):
        """Actualiza las estadísticas mostradas."""
        if not self.history or self.step_index >= len(self.history):
            for label in self.stats_labels.values():
                label.config(text="0")
            return
            
        state = self.history[self.step_index]
        if not state:
            for label in self.stats_labels.values():
                label.config(text="0")
            return
        
        open_list = state.get("open_list", [])
        closed_list = state.get("closed_list", [])
        path = state.get("path", [])
        
        open_count = len(open_list) if open_list else 0
        closed_count = len(closed_list) if closed_list else 0
        path_count = len(path) if path else 0
        
        # Calcular costo total si hay camino
        total_cost = 0
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                current_pos = path[i]
                next_pos = path[i + 1]
                
                # Calcular costo del movimiento
                dx = abs(next_pos[0] - current_pos[0])
                dy = abs(next_pos[1] - current_pos[1])
                
                if dx == 1 and dy == 1 and self.allow_diagonal:
                    total_cost += math.sqrt(2)  # Diagonal
                else:
                    total_cost += 1  # Movimiento ortogonal
        
        self.stats_labels["Nodos Abiertos"].config(text=str(open_count))
        self.stats_labels["Nodos Cerrados"].config(text=str(closed_count))
        self.stats_labels["Nodos en Camino"].config(text=str(path_count))
        self.stats_labels["Costo Total"].config(text=f"{total_cost:.1f}" if total_cost > 0 else "N/A")
        
    def draw_grid_state(self):
        """Dibuja el estado actual de la grilla."""
        self.ax_map.clear()
        self.ax_map.set_title(f"Estado del Mapa - {self.algorithm_name}")
        
        if not self.history or self.step_index >= len(self.history):
            self.ax_map.text(0.5, 0.5, "No hay datos para mostrar", 
                           ha='center', va='center', transform=self.ax_map.transAxes)
            return
            
        state = self.history[self.step_index]
        if not state:
            self.ax_map.text(0.5, 0.5, "Estado vacío", 
                           ha='center', va='center', transform=self.ax_map.transAxes)
            return
        
        # Obtener dimensiones de la grilla
        rows, cols = self.grid.rows, self.grid.cols
        
        # Obtener listas de nodos (manejar casos None)
        open_list = state.get("open_list", []) or []
        closed_list = state.get("closed_list", []) or []
        path = state.get("path", []) or []
        
        # Crear matriz de colores
        color_map = []
        for row in range(rows):
            color_row = []
            for col in range(cols):
                pos = (col, row)  # x, y
                
                # Acceder al estado usando la estructura correcta de Grid
                cell_state = self.grid.states[col][row] if col < self.grid.cols and row < self.grid.rows else config.STATE_FREE
                
                if cell_state == config.STATE_OBSTACLE:  # Obstáculo
                    color_row.append(0.2)  # Gris oscuro
                elif pos == self.grid.start_pos:
                    color_row.append(0.9)  # Verde claro
                elif pos == self.grid.end_pos:
                    color_row.append(0.8)  # Rojo claro
                elif pos in [node.position for node in open_list]:
                    color_row.append(0.7)  # Amarillo
                elif pos in [node.position for node in closed_list]:
                    color_row.append(0.5)  # Azul
                elif path and pos in path:
                    color_row.append(0.6)  # Magenta
                else:
                    color_row.append(1.0)  # Blanco
                    
            color_map.append(color_row)
        
        # Dibujar el mapa
        im = self.ax_map.imshow(color_map, cmap='viridis', origin='upper')
        
        # Agregar grilla
        self.ax_map.set_xticks(range(cols))
        self.ax_map.set_yticks(range(rows))
        self.ax_map.grid(True, color='white', linewidth=0.5)
        
        # Agregar etiquetas a nodos relevantes
        all_nodes = open_list + closed_list
        for node in all_nodes:
            x, y = node.position
            
            # Formatear valores
            def format_val(val):
                return f"{val:.1f}" if isinstance(val, float) and val != int(val) else str(int(val))
            
            if self.algorithm_name == "A*":
                text = f"G:{format_val(node.g)}\nH:{format_val(node.h)}\nF:{format_val(node.f)}"
            elif self.algorithm_name == "Dijkstra":
                text = f"G:{format_val(node.g)}"
            elif self.algorithm_name == "Voraz":
                text = f"H:{format_val(node.h)}"
            elif self.algorithm_name == "Costo U":
                text = f"G:{format_val(node.g)}"
            else:
                text = f"F:{format_val(node.f)}"
                
            self.ax_map.text(x, y, text, ha='center', va='center', 
                           fontsize=6, color='white', weight='bold',
                           bbox=dict(boxstyle="round,pad=0.1", facecolor='black', alpha=0.7))
        
        self.ax_map.set_xlim(-0.5, cols-0.5)
        self.ax_map.set_ylim(rows-0.5, -0.5)
        
    def draw_search_tree(self):
        """Dibuja el árbol de búsqueda."""
        self.ax_tree.clear()
        self.ax_tree.set_title("Árbol de Búsqueda")
        
        if not self.history or self.step_index >= len(self.history):
            self.ax_tree.text(0.5, 0.5, "No hay datos del árbol", 
                            ha='center', va='center', transform=self.ax_tree.transAxes)
            return
            
        state = self.history[self.step_index]
        if not state:
            self.ax_tree.text(0.5, 0.5, "Estado vacío", 
                            ha='center', va='center', transform=self.ax_tree.transAxes)
            return
        
        # Obtener listas de nodos (manejar casos None)
        open_list = state.get("open_list", []) or []
        closed_list = state.get("closed_list", []) or []
        path = state.get("path", []) or []
        
        all_nodes = open_list + closed_list
        
        if not all_nodes:
            self.ax_tree.text(0.5, 0.5, "Árbol vacío", 
                            ha='center', va='center', transform=self.ax_tree.transAxes)
            return
        
        # Crear grafo dirigido para el árbol
        G = nx.DiGraph()
        
        # Agregar nodos y aristas
        for node in all_nodes:
            G.add_node(node.position)
            if node.parent:
                G.add_edge(node.parent.position, node.position)
        
        # Calcular layout del árbol
        try:
            # Intentar layout jerárquico
            pos = self._calculate_tree_layout(G, self.grid.start_pos)
        except:
            # Fallback a layout spring
            pos = nx.spring_layout(G, k=2, iterations=50)
        
        if not pos:
            self.ax_tree.text(0.5, 0.5, "Error en layout del árbol", 
                            ha='center', va='center', transform=self.ax_tree.transAxes)
            return
        
        # Determinar colores de nodos
        node_colors = []
        for node_pos in G.nodes():
            if node_pos == self.grid.start_pos:
                node_colors.append('lightgreen')
            elif node_pos == self.grid.end_pos:
                node_colors.append('lightcoral')
            elif path and node_pos in path:
                node_colors.append('magenta')
            elif node_pos in [node.position for node in open_list]:
                node_colors.append('yellow')
            elif node_pos in [node.position for node in closed_list]:
                node_colors.append('lightblue')
            else:
                node_colors.append('lightgray')
        
        # Dibujar el árbol
        nx.draw(G, pos, 
               node_color=node_colors,
               node_size=600,
               with_labels=True,
               labels={pos: f"({pos[0]},{pos[1]})" for pos in G.nodes()},
               font_size=8,
               font_weight='bold',
               arrows=True,
               arrowsize=20,
               edge_color='gray',
               ax=self.ax_tree)
        
        # Agregar información de nodos
        node_dict = {node.position: node for node in all_nodes}
        for node_pos, (x, y) in pos.items():
            if node_pos in node_dict:
                node = node_dict[node_pos]
                
                def format_val(val):
                    return f"{val:.1f}" if isinstance(val, float) and val != int(val) else str(int(val))
                
                if self.algorithm_name == "A*":
                    info = f"G:{format_val(node.g)} H:{format_val(node.h)} F:{format_val(node.f)}"
                elif self.algorithm_name == "Dijkstra":
                    info = f"G:{format_val(node.g)}"
                elif self.algorithm_name == "Voraz":
                    info = f"H:{format_val(node.h)}"
                elif self.algorithm_name == "Costo U":
                    info = f"G:{format_val(node.g)}"
                else:
                    info = f"F:{format_val(node.f)}"
                    
                self.ax_tree.text(x, y-0.15, info, ha='center', va='center',
                                fontsize=7, 
                                bbox=dict(boxstyle="round,pad=0.1", facecolor='white', alpha=0.8))
        
    def _calculate_tree_layout(self, G, root):
        """Calcula el layout jerárquico del árbol."""
        if not G.nodes():
            return {}
            
        # BFS para calcular niveles
        levels = {}
        queue = deque([(root, 0)])
        visited = {root}
        levels[root] = 0
        
        while queue:
            node, level = queue.popleft()
            for child in G.successors(node):
                if child not in visited:
                    visited.add(child)
                    levels[child] = level + 1
                    queue.append((child, level + 1))
        
        # Agrupar nodos por nivel
        level_nodes = {}
        for node, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)
        
        # Calcular posiciones
        pos = {}
        max_width = max(len(nodes) for nodes in level_nodes.values()) if level_nodes else 1
        
        for level, nodes in level_nodes.items():
            y = -level  # Niveles hacia abajo
            node_count = len(nodes)
            
            if node_count == 1:
                pos[nodes[0]] = (0, y)
            else:
                # Distribuir horizontalmente
                spacing = max_width / (node_count + 1)
                start_x = -max_width / 2
                
                for i, node in enumerate(nodes):
                    x = start_x + spacing * (i + 1)
                    pos[node] = (x, y)
        
        return pos
    
    # Métodos de navegación
    def go_to_start(self):
        """Va al primer paso."""
        self.step_index = 0
        self.update_visualization()
        
    def prev_step(self):
        """Va al paso anterior."""
        if self.step_index > 0:
            self.step_index -= 1
            self.update_visualization()
            
    def next_step(self):
        """Va al paso siguiente."""
        if self.step_index < len(self.history) - 1:
            self.step_index += 1
            self.update_visualization()
            
    def go_to_end(self):
        """Va al último paso."""
        if self.history:
            self.step_index = len(self.history) - 1
            self.update_visualization()
    
    def run(self):
        """Ejecuta el visualizador."""
        self.root.mainloop()

if __name__ == "__main__":
    # Este archivo debe ser importado, no ejecutado directamente
    print("Este visualizador debe ser llamado desde la aplicación principal.")