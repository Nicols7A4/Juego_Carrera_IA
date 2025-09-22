import pygame
import config
import copy
from scenes.scene_base import SceneBase
from components.grid import Grid
from components.button import Button
from algorithms.a_star import AStarPathfinder
from algorithms.dijkstra import DijkstraPathfinder
from algorithms.greedy import GreedyPathfinder
from algorithms.uniform_cost import UniformCostPathfinder

class TestingScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.grid = Grid()
        self.font_scores = pygame.font.SysFont('B612Mono', 12)  # Más pequeña
        self.font_f_score = pygame.font.SysFont('B612Mono', 16, bold=True)  # Más pequeña

        # Estado del movimiento diagonal
        self.allow_diagonal = False

        # 2. Lógica para manejar múltiples algoritmos
        self.algorithms = {
            "A*": AStarPathfinder(self.grid, self.allow_diagonal),
            "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
            "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
            "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
        }
        self.current_algo_name = "A*"
        self.pathfinder = self.algorithms[self.current_algo_name]

        # 1. Variables para el modo automático
        self.is_auto_running = False
        self.auto_step_speed = 0.05 # 0.1 segundos = 10 pasos por segundo
        self.auto_step_timer = 0.0

        # --- NUEVO: Historial de Pasos ---
        self.history = []
        self.current_step = -1

        # Botones de la UI
        self.back_step_button = Button(config.SCREEN_WIDTH - 220, 20, 95, 50, 'Atras', self.step_back)
        self.next_step_button = Button(config.SCREEN_WIDTH - 115, 20, 95, 50, 'Siguiente', self.step_forward)
        self.switch_algo_button = Button(config.SCREEN_WIDTH - 220, 90, 200, 50, f'Algoritmo: {self.current_algo_name}', self.switch_algorithm)
        self.auto_button = Button(config.SCREEN_WIDTH - 220, 160, 200, 50, 'Auto: OFF', self.toggle_auto_mode)
        self.diagonal_button = Button(config.SCREEN_WIDTH - 220, 230, 200, 40, 'Diagonal: OFF', self.toggle_diagonal)
        self.tree_button = Button(config.SCREEN_WIDTH - 220, 280, 200, 40, 'Visualizar Árbol', self.open_tree_visualizer)

    def on_enter(self):
        """Esta función se llamará cada vez que entremos a la escena."""
        self.grid.load_map(self.game.selected_map)
        self.is_auto_running = False
        self.auto_button.text = "Auto: OFF"
        self.allow_diagonal = False
        self.diagonal_button.text = "Diagonal: OFF"
        
        # Recrear algoritmos con configuración por defecto
        self.algorithms = {
            "A*": AStarPathfinder(self.grid, self.allow_diagonal),
            "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
            "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
            "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
        }
        self.pathfinder = self.algorithms[self.current_algo_name]
        
        self.reset_search()
        
        # En RaceScene, recalcula el camino
        # if self.grid.start_pos and self.grid.end_pos:
        #     self.path = self.pathfinder.find_path(self.grid.start_pos, self.grid.end_pos)
        
        # En TestingScene, reinicia la búsqueda
        # self.pathfinder.initialize_search(self.grid.start_pos, self.grid.end_pos)

    def reset_search(self):
        """Prepara una nueva búsqueda y guarda el estado inicial."""
        self.history = []
        self.current_step = 0
        self.pathfinder.initialize_search(self.grid.start_pos, self.grid.end_pos)
        self.history.append(self.get_current_state_snapshot())

    def get_current_state_snapshot(self):
        """Crea una copia profunda del estado actual del pathfinder."""
        return {
            "open_list": copy.deepcopy(self.pathfinder.open_list),
            "closed_list": copy.deepcopy(self.pathfinder.closed_list),
            "path": copy.deepcopy(self.pathfinder.path),
            "is_finished": self.pathfinder.is_finished
        }

    def step_forward(self):
        """Avanza un paso en el algoritmo."""
        if self.pathfinder.is_finished: return

        # Si retrocedimos y ahora avanzamos, borramos el futuro anterior
        if self.current_step < len(self.history) - 1:
            self.history = self.history[:self.current_step + 1]
        
        self.pathfinder.step()
        self.history.append(self.get_current_state_snapshot())
        self.current_step += 1

    def step_back(self):
        """Retrocede un paso en el historial."""
        if self.current_step > 0:
            self.current_step -= 1
            state = self.history[self.current_step]
            self.pathfinder.open_list = copy.deepcopy(state["open_list"])
            self.pathfinder.closed_list = copy.deepcopy(state["closed_list"])
            self.pathfinder.path = copy.deepcopy(state["path"])
            self.pathfinder.is_finished = state["is_finished"]

    def toggle_diagonal(self):
        """Activa/desactiva el movimiento diagonal."""
        if not self.is_auto_running:
            self.allow_diagonal = not self.allow_diagonal
            self.diagonal_button.text = f'Diagonal: {"ON" if self.allow_diagonal else "OFF"}'
            
            # Recrear algoritmos con la nueva configuración
            self.algorithms = {
                "A*": AStarPathfinder(self.grid, self.allow_diagonal),
                "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
                "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
                "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
            }
            self.pathfinder = self.algorithms[self.current_algo_name]
            
            # Reiniciar la búsqueda
            self.reset_search()

    def toggle_auto_mode(self):
        """Activa o desactiva el modo de ejecución automática."""
        self.is_auto_running = not self.is_auto_running
        self.auto_button.text = f"Auto: {'ON' if self.is_auto_running else 'OFF'}"
        self.auto_step_timer = 0.0 # Reinicia el timer al cambiar de modo

    def switch_algorithm(self):
        """Cambia entre los algoritmos disponibles."""
        algo_names = list(self.algorithms.keys())
        current_index = algo_names.index(self.current_algo_name)
        next_index = (current_index + 1) % len(algo_names)
        self.current_algo_name = algo_names[next_index]
        self.pathfinder = self.algorithms[self.current_algo_name]
        self.switch_algo_button.text = f"Algoritmo: {self.current_algo_name}"
        # Reinicia la búsqueda con el nuevo algoritmo
        self.on_enter()
        self.reset_search()
        
    def step_algorithm(self):
        """Avanza un paso solo si la búsqueda no ha terminado."""
        if not self.pathfinder.is_finished:
            self.pathfinder.step()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.switch_scene('menu')
            
            if not self.is_auto_running:
                self.next_step_button.handle_event(event)
                self.back_step_button.handle_event(event)
                self.diagonal_button.handle_event(event)
            
            self.switch_algo_button.handle_event(event)
            self.auto_button.handle_event(event)
            self.tree_button.handle_event(event)

    def update(self, dt):
        """El corazón del modo automático."""
        if self.is_auto_running and not self.history[self.current_step]["is_finished"]:
            self.auto_step_timer += dt
            if self.auto_step_timer >= self.auto_step_speed:
                self.auto_step_timer = 0
                self.step_forward()
                
        if self.is_auto_running and not self.pathfinder.is_finished:
            self.auto_step_timer += dt
            if self.auto_step_timer >= self.auto_step_speed:
                self.auto_step_timer = 0 # Reinicia el timer
                self.step_algorithm() # Ejecuta un paso
        
        # Si el algoritmo termina mientras está en modo auto, lo desactivamos
        if self.pathfinder.is_finished and self.is_auto_running:
            self.toggle_auto_mode()

    def draw(self, screen):
        screen.fill(config.GRAY)
        self.grid.draw(screen)

        state = self.history[self.current_step]
        # Dibujar lista abierta/cerrada usando state["open_list"] y state["closed_list"]

        # Dibujar lista abierta (amarillo)
        for node in state["open_list"]:
            rect = pygame.Rect(node.position[0] * config.CELL_SIZE, node.position[1] * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
            pygame.draw.rect(screen, (255, 255, 0, 150), rect) # Amarillo semitransparente

        # Dibujar lista cerrada (celeste)
        for node in state["closed_list"]:
            rect = pygame.Rect(node.position[0] * config.CELL_SIZE, node.position[1] * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
            pygame.draw.rect(screen, (0, 191, 255, 150), rect) # Celeste semitransparente
        
        # Dibujar el camino final si se encontró en este estado
        if state["path"]:
            for pos in state["path"]:
                if pos != self.grid.start_pos and pos != self.grid.end_pos:
                    rect = pygame.Rect(pos[0] * config.CELL_SIZE, pos[1] * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
                    pygame.draw.rect(screen, (128, 0, 128), rect)

        # Dibujar los scores G, H y F de todos los nodos evaluados
        all_nodes = state["open_list"] + state["closed_list"]
        for node in all_nodes:
             self._draw_node_scores(screen, node)

        # Dibujar UI
        if not self.is_auto_running:
            self.back_step_button.draw(screen)
            self.next_step_button.draw(screen)
            self.diagonal_button.draw(screen)
        
        self.switch_algo_button.draw(screen)
        self.auto_button.draw(screen)
        self.tree_button.draw(screen)
        
        info_font = pygame.font.SysFont('B612Mono', 24)
        info_text = info_font.render('Presiona ESC para volver al menu', True, config.WHITE)
        screen.blit(info_text, (10, 10))

    def _draw_node_scores(self, screen, node):
        """Función auxiliar para dibujar los textos de G, H y F en un nodo."""
        x, y = node.position
        
        # Formatear números para que sean más cortos y legibles
        def format_number(value):
            if isinstance(value, float):
                if value == int(value):
                    return str(int(value))
                else:
                    return f"{value:.1f}"  # Solo 1 decimal
            return str(value)
        
        g_formatted = format_number(node.g)
        h_formatted = format_number(node.h) 
        f_formatted = format_number(node.f)
        
        # g_score (arriba izquierda)
        g_text = self.font_scores.render(g_formatted, True, config.BLACK)
        screen.blit(g_text, (x * config.CELL_SIZE + 2, y * config.CELL_SIZE + 2))
        
        # h_score (arriba derecha)
        h_text = self.font_scores.render(h_formatted, True, config.BLACK)
        h_x = x * config.CELL_SIZE + config.CELL_SIZE - h_text.get_width() - 2
        screen.blit(h_text, (h_x, y * config.CELL_SIZE + 2))
        
        # f_score (centro abajo) - usar fuente más pequeña si es necesario
        f_text = self.font_scores.render(f_formatted, True, config.BLACK)
        # Verificar si el texto es muy ancho para la celda
        if f_text.get_width() > config.CELL_SIZE - 4:
            # Usar fuente más pequeña para F si no cabe
            small_font = pygame.font.SysFont('B612Mono', 14, bold=True)
            f_text = small_font.render(f_formatted, True, config.BLACK)
        
        f_rect = f_text.get_rect(center=(x * config.CELL_SIZE + config.CELL_SIZE / 2, y * config.CELL_SIZE + config.CELL_SIZE - 10))
        screen.blit(f_text, f_rect)
    
    def open_tree_visualizer(self):
        """Abre el visualizador de árbol en una ventana tkinter independiente."""
        import threading
        from visualizador_arbol import AlgorithmTreeVisualizer
        
        # Crear una función para ejecutar el visualizador en un hilo separado
        def run_visualizer():
            try:
                # Preparar los datos actuales
                current_state = self.history[self.current_step] if self.history and self.current_step >= 0 else None
                
                # Crear y ejecutar el visualizador
                visualizer = AlgorithmTreeVisualizer(
                    grid=self.grid,
                    algorithm_name=self.current_algo_name,
                    history=self.history,
                    current_step=self.current_step,
                    allow_diagonal=self.allow_diagonal
                )
                visualizer.run()
            except Exception as e:
                print(f"Error al abrir visualizador de árbol: {e}")
        
        # Ejecutar en un hilo separado para no bloquear pygame
        thread = threading.Thread(target=run_visualizer, daemon=True)
        thread.start()