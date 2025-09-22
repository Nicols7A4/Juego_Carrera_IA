# visualizer.py
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from collections import deque
from maps_data.map_repository import MAPS
from algorithms import ALGORITHMS

class GraphVisualizer:
    def __init__(self, ventana_principal):
        self.ventana_principal = ventana_principal
        self.ventana_principal.title("Visualizador de Algoritmos de Búsqueda")
        self.ventana_principal.geometry("1600x900")

        marco_principal = tk.Frame(self.ventana_principal)
        marco_principal.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        marco_inferior = tk.Frame(self.ventana_principal)
        marco_inferior.pack(side=tk.BOTTOM, fill=tk.X)
        self.marco_controles = tk.Frame(marco_inferior, pady=5)
        self.marco_controles.pack(side=tk.TOP, fill=tk.X)
        self.marco_estadisticas = tk.Frame(marco_inferior, pady=5)
        self.marco_estadisticas.pack(side=tk.TOP, fill=tk.X)

        self.fig = Figure(figsize=(16, 8))
        # Ajuste de márgenes para toda la figura
        self.fig.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.05)
        self.ax_map = self.fig.add_subplot(1, 2, 1)
        self.ax_tree = self.fig.add_subplot(1, 2, 2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=marco_principal)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.mapa_var = tk.StringVar(self.ventana_principal)
        self.mapa_var.set("Peru")  # Cambiar mapa por defecto a Peru
        menu_mapa = tk.OptionMenu(self.marco_controles, self.mapa_var, *MAPS.keys(), command=lambda _: self.reset_simulation())
        menu_mapa.pack(side=tk.LEFT, padx=10)

        self.algoritmo_var = tk.StringVar(self.ventana_principal)
        self.algoritmo_var.set(list(ALGORITHMS.keys())[0])
        menu_algoritmo = tk.OptionMenu(self.marco_controles, self.algoritmo_var, *ALGORITHMS.keys(), command=lambda _: self.reset_simulation())
        menu_algoritmo.pack(side=tk.LEFT, padx=10)
        
        self.boton_paso_anterior = tk.Button(self.marco_controles, text="< Retroceder Paso", command=self.prev_step)
        self.boton_paso_anterior.pack(side=tk.LEFT, padx=10)

        self.boton_siguiente_paso = tk.Button(self.marco_controles, text="Siguiente Paso >", command=self.next_step)
        self.boton_siguiente_paso.pack(side=tk.LEFT, padx=10)
        
        self.boton_reiniciar = tk.Button(self.marco_controles, text="Reiniciar", command=self.reset_simulation)
        self.boton_reiniciar.pack(side=tk.LEFT, padx=10)

        self.etiquetas_estadisticas = {}
        stats_to_show = ["Iteración", "Nodos Abiertos", "Nodos Cerrados", "Costo del Camino"]
        for stat in stats_to_show:
            frame = tk.Frame(self.marco_estadisticas)
            frame.pack(side=tk.LEFT, padx=15)
            tk.Label(frame, text=f"{stat}:", font=("Arial", 10, "bold")).pack()
            self.etiquetas_estadisticas[stat] = tk.Label(frame, text="N/A", font=("Arial", 10))
            self.etiquetas_estadisticas[stat].pack()

        self.historial = []
        self.indice_paso_actual = -1
        self.reset_simulation()

    def _calculate_tree_layout(self, G, root):
        pos, levels = {}, {}
        if not G.nodes(): return {}
        q = deque([(root, 0)]); visited = {root}; levels[root] = 0
        while q:
            node, level = q.popleft()
            for child in list(G.successors(node)):
                if child not in visited: visited.add(child); levels[child] = level + 1; q.append((child, level + 1))
        level_widths = {level: list(levels.values()).count(level) for level in set(levels.values())}
        level_x_offsets = {}
        for node in sorted(levels.keys(), key=lambda n: (levels[n], n)):
            level = levels[node]; width = level_widths[level]
            current_x = level_x_offsets.get(level, -(width - 1) / 2.0)
            pos[node] = (current_x, -level)
            level_x_offsets[level] = current_x + 1.0
        return pos
    
    def _get_node_label(self, nodo, estado):
        algo_name = self.algoritmo_var.get()
        if algo_name in ["Breadth-First Search (BFS)", "Depth-First Search (DFS)"]: return ""
        g = estado.get("g_score", {}).get(nodo)
        h = self.heuristicas.get(nodo)
        f = estado.get("f_score", {}).get(nodo)
        if algo_name == "A*":
            if f is not None: return f"g={g}\nh={h}\nf={f}"
        elif algo_name == "Greedy BFS":
            h_val = f if f is not None else h
            if h_val is not None: return f"h={h_val}"
        elif algo_name == "Uniform-Cost Search (UCS)":
            if g is not None: return f"g={g}"
        return ""

    def reset_simulation(self):
        selected_map_name = self.mapa_var.get()
        map_data = MAPS[selected_map_name]
        self.grafo = map_data["graph"]; self.posiciones = map_data["positions"]; self.heuristicas = map_data["heuristics"]
        self.nodo_inicio = map_data["start_node"]; self.nodo_objetivo = map_data["goal_node"]
        self.G_map = nx.Graph()
        for node, neighbors in self.grafo.items():
            for neighbor, weight in neighbors.items(): self.G_map.add_edge(node, neighbor, weight=weight)
        selected_algo_name = self.algoritmo_var.get()
        algorithm_func = ALGORITHMS[selected_algo_name]
        self.generador_algoritmo = algorithm_func(self.grafo, self.heuristicas, self.nodo_inicio, self.nodo_objetivo)
        self.historial = []; self.indice_paso_actual = -1
        self.update_visuals(None)
        self._update_button_states()

    def next_step(self):
        self.indice_paso_actual += 1
        if self.indice_paso_actual >= len(self.historial):
            try:
                estado = next(self.generador_algoritmo)
                self.historial.append(estado)
            except StopIteration: self.indice_paso_actual -= 1; return
        estado = self.historial[self.indice_paso_actual]
        self.update_visuals(estado)
        self._update_button_states()

    def prev_step(self):
        if self.indice_paso_actual > -1:
            self.indice_paso_actual -= 1
            estado = self.historial[self.indice_paso_actual] if self.indice_paso_actual > -1 else None
            self.update_visuals(estado)
            self._update_button_states()
    
    def _update_button_states(self):
        self.boton_paso_anterior.config(state=tk.NORMAL if self.indice_paso_actual > -1 else tk.DISABLED)
        is_last_step_a_solution = self.historial and self.historial[-1].get("final_path")
        self.boton_siguiente_paso.config(state=tk.DISABLED if self.indice_paso_actual >= len(self.historial) - 1 and is_last_step_a_solution else tk.NORMAL)

    def _update_stats(self, estado):
        if estado is None:
            self.etiquetas_estadisticas["Iteración"].config(text="0"); self.etiquetas_estadisticas["Nodos Abiertos"].config(text="0")
            self.etiquetas_estadisticas["Nodos Cerrados"].config(text="0"); self.etiquetas_estadisticas["Costo del Camino"].config(text="N/A")
            return
        self.etiquetas_estadisticas["Iteración"].config(text=str(self.indice_paso_actual + 1))
        self.etiquetas_estadisticas["Nodos Abiertos"].config(text=str(len(estado.get("open_set", []))))
        self.etiquetas_estadisticas["Nodos Cerrados"].config(text=str(len(estado.get("closed_set", []))))
        cost = "Calculando..."
        path = estado.get("final_path")
        if path:
            cost_val = estado.get("g_score", {}).get(self.nodo_objetivo)
            if cost_val is None:
                cost_val = 0
                for i in range(len(path) - 1): cost_val += self.grafo[path[i]][path[i+1]]
            cost = str(cost_val)
        self.etiquetas_estadisticas["Costo del Camino"].config(text=cost)

    def update_visuals(self, estado):
        self._update_stats(estado)
        self.update_map_view(estado)
        self.update_search_tree_view(estado)
        self.canvas.draw()
    
    def update_map_view(self, estado):
        self.ax_map.clear()
        edge_labels = {(u, v): d['weight'] for u, v, d in self.G_map.edges(data=True)}
        
        if estado is None:
            nx.draw(self.G_map, pos=self.posiciones, with_labels=True, node_size=500, node_color='lightblue', font_size=8, ax=self.ax_map)
        else:
            mapa_colores = []
            for nodo in self.G_map:
                if nodo == estado.get("current_node"): mapa_colores.append('orange')
                elif nodo in estado.get("final_path", []): mapa_colores.append('lightgreen')
                elif nodo in estado.get("open_set", []): mapa_colores.append('skyblue')
                elif nodo in estado.get("closed_set", []): mapa_colores.append('gray')
                else: mapa_colores.append('lightgray')
            nx.draw(self.G_map, pos=self.posiciones, node_color=mapa_colores, with_labels=True, node_size=500, font_size=8, ax=self.ax_map)
        
        nx.draw_networkx_edge_labels(self.G_map, self.posiciones, edge_labels=edge_labels, font_size=7, ax=self.ax_map)
        if estado:
            etiquetas = {nodo: self._get_node_label(nodo, estado) for nodo in self.G_map.nodes()}
            label_pos = {k: (v[0], v[1] - 25) for k, v in self.posiciones.items()}
            nx.draw_networkx_labels(self.G_map, pos=label_pos, labels={k: v for k, v in etiquetas.items() if v}, font_size=7, ax=self.ax_map, bbox=dict(facecolor='white', alpha=0.4, edgecolor='none'))
            self.ax_map.set_title(f"{self.algoritmo_var.get()} - {estado.get('status', 'Inicio')}")
        else: self.ax_map.set_title(f"Mapa: {self.mapa_var.get()}")
        x_coords, y_coords = zip(*self.posiciones.values()); margin_x = (max(x_coords) - min(x_coords)) * 0.1; margin_y = (max(y_coords) - min(y_coords)) * 0.1
        self.ax_map.set_xlim(min(x_coords) - margin_x, max(x_coords) + margin_x); self.ax_map.set_ylim(min(y_coords) - margin_y, max(y_coords) + margin_y)

    def update_search_tree_view(self, estado):
        self.ax_tree.clear()
        self.ax_tree.set_title("Árbol de Búsqueda")
        if estado is None:
            self.ax_tree.text(0.5, 0.5, "El árbol se construirá aquí...", ha='center', va='center', transform=self.ax_tree.transAxes); return
        G_tree = nx.DiGraph(); G_tree.add_node(self.nodo_inicio)
        aristas = estado.get("search_tree_edges", []); 
        if aristas: G_tree.add_edges_from(aristas)
        pos_tree = self._calculate_tree_layout(G_tree, self.nodo_inicio)
        if not pos_tree: return
        mapa_colores = []
        for nodo in G_tree:
            if nodo == estado.get("current_node"): mapa_colores.append('orange')
            elif nodo in estado.get("final_path", []): mapa_colores.append('lightgreen')
            elif nodo in estado.get("open_set", []): mapa_colores.append('skyblue')
            elif nodo in estado.get("closed_set", []): mapa_colores.append('gray')
            else: mapa_colores.append('lightgray')
        nx.draw(G_tree, pos=pos_tree, with_labels=True, node_color=mapa_colores, node_size=500, font_size=7, ax=self.ax_tree, arrows=True)
        tree_edge_labels = {edge: self.grafo[edge[0]][edge[1]] for edge in G_tree.edges()}
        nx.draw_networkx_edge_labels(G_tree, pos=pos_tree, edge_labels=tree_edge_labels, font_size=7, ax=self.ax_tree, label_pos=0.3)
        etiquetas = {nodo: self._get_node_label(nodo, estado) for nodo in G_tree.nodes()}
        label_pos = {k: (v[0], v[1] - 0.22) for k, v in pos_tree.items()}
        nx.draw_networkx_labels(G_tree, pos=label_pos, labels={k: v for k, v in etiquetas.items() if v}, font_size=6, ax=self.ax_tree, bbox=dict(facecolor='white', alpha=0.4, edgecolor='none'))
        if pos_tree:
            x_coords, y_coords = zip(*pos_tree.values()); margin_x = max((max(x_coords) - min(x_coords)) * 0.1, 0.5); margin_y = max((max(y_coords) - min(y_coords)) * 0.1, 0.5)
            self.ax_tree.set_xlim(min(x_coords) - margin_x, max(x_coords) + margin_x); self.ax_tree.set_ylim(min(y_coords) - margin_y, max(y_coords) + margin_y)