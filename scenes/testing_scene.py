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
    """
    Escena de testing para visualización paso a paso de algoritmos.
    
    PROPÓSITO: Permitir análisis detallado del funcionamiento interno de algoritmos
    CARACTERÍSTICAS:
    1. Visualización paso a paso de la exploración de nodos
    2. Historial navegable (avanzar/retroceder pasos)
    3. Modo automático con velocidad controlable
    4. Intercambio entre algoritmos en tiempo real
    5. Visualización de costos y heurísticas en cada nodo
    6. Toggle de movimiento diagonal
    """
    def __init__(self, game):
        super().__init__(game)
        
        # CONFIGURACIÓN DE CUADRÍCULA Y FUENTES
        self.grid = Grid()
        self.font_scores = pygame.font.SysFont('B612Mono', 12)  # Para mostrar costos en nodos
        self.font_f_score = pygame.font.SysFont('B612Mono', 16, bold=True)  # Para destacar F-score

        # CONFIGURACIÓN DE MOVIMIENTO DIAGONAL
        self.allow_diagonal = False

        # CONFIGURACIÓN DE ALGORITMOS DISPONIBLES
        # Diccionario con todos los algoritmos que se pueden visualizar
        self.algorithms = {
            "A*": AStarPathfinder(self.grid, self.allow_diagonal),
            "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
            "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
            "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
        }
        self.current_algo_name = "A*"
        self.pathfinder = self.algorithms[self.current_algo_name]

        # SISTEMA DE EJECUCIÓN AUTOMÁTICA
        # Para observar el algoritmo ejecutándose automáticamente
        self.is_auto_running = False
        self.auto_step_speed = 0.05  # 0.05 segundos = 20 pasos por segundo
        self.auto_step_timer = 0.0

        # SISTEMA DE HISTORIAL DE PASOS
        # Permite navegar hacia adelante y atrás en la ejecución
        self.history = []        # Lista de estados del algoritmo
        self.current_step = -1   # Índice del paso actual en el historial

        # BOTONES DE CONTROL DE LA INTERFAZ
        self.back_step_button = Button(config.SCREEN_WIDTH - 220, 20, 95, 50, 'Atras', self.step_back)
        self.next_step_button = Button(config.SCREEN_WIDTH - 115, 20, 95, 50, 'Siguiente', self.step_forward)
        self.switch_algo_button = Button(config.SCREEN_WIDTH - 220, 90, 200, 50, f'Algoritmo: {self.current_algo_name}', self.switch_algorithm)
        self.auto_button = Button(config.SCREEN_WIDTH - 220, 160, 200, 50, 'Auto: OFF', self.toggle_auto_mode)
        self.diagonal_button = Button(config.SCREEN_WIDTH - 220, 230, 200, 40, 'Diagonal: OFF', self.toggle_diagonal)
        self.tree_button = Button(config.SCREEN_WIDTH - 220, 280, 200, 40, 'Visualizar Árbol', self.open_tree_visualizer)

    def on_enter(self):
        """
        Inicializar la escena cuando se accede a ella.
        
        PROPÓSITO: Configurar estado inicial para visualización de algoritmos
        ACCIONES:
        1. Cargar mapa seleccionado
        2. Reiniciar configuraciones a valores por defecto
        3. Recrear algoritmos con configuración actual
        4. Preparar sistema de historial para navegación
        """
        # Cargar mapa seleccionado
        self.grid.load_map(self.game.selected_map)
        
        # REINICIAR CONFIGURACIONES POR DEFECTO
        self.is_auto_running = False
        self.auto_button.text = "Auto: OFF"
        self.allow_diagonal = False
        self.diagonal_button.text = "Diagonal: OFF"
        
        # RECREAR ALGORITMOS con configuración actual
        # Necesario porque el tipo de movimiento afecta las heurísticas
        self.algorithms = {
            "A*": AStarPathfinder(self.grid, self.allow_diagonal),
            "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
            "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
            "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
        }
        self.pathfinder = self.algorithms[self.current_algo_name]
        
        # INICIALIZAR SISTEMA DE BÚSQUEDA Y HISTORIAL
        self.reset_search()

    def reset_search(self):
        """
        Preparar nueva búsqueda y capturar estado inicial.
        
        PROPÓSITO: Inicializar algoritmo y sistema de historial
        FUNCIONAMIENTO:
        1. Limpiar historial de pasos previos
        2. Inicializar algoritmo seleccionado
        3. Capturar estado inicial para navegación
        """
        # Limpiar historial de pasos previos
        self.history = []
        self.current_step = 0
        
        # Inicializar algoritmo en posiciones de inicio y destino
        self.pathfinder.initialize_search(self.grid.start_pos, self.grid.end_pos)
        
        # Capturar estado inicial (antes de explorar cualquier nodo)
        self.history.append(self.get_current_state_snapshot())

    def get_current_state_snapshot(self):
        """
        Crear copia del estado actual del algoritmo.
        
        PROPÓSITO: Capturar estado para navegación en historial
        ESTADO CAPTURADO:
        1. Lista abierta (nodos por explorar)
        2. Lista cerrada (nodos ya explorados)
        3. Camino actual encontrado
        4. Estado de finalización del algoritmo
        """
        return {
            "open_list": copy.deepcopy(self.pathfinder.open_list),
            "closed_list": copy.deepcopy(self.pathfinder.closed_list),
            "path": copy.deepcopy(self.pathfinder.path),
            "is_finished": self.pathfinder.is_finished
        }

    def step_forward(self):
        """
        Avanzar un paso en la ejecución del algoritmo.
        
        PROPÓSITO: Ejecutar una iteración del algoritmo y guardar estado
        FUNCIONAMIENTO:
        1. Verificar que el algoritmo no haya terminado
        2. Si navegamos desde historial, limpiar pasos futuros
        3. Ejecutar un paso del algoritmo
        4. Capturar nuevo estado en historial
        """
        # No avanzar si el algoritmo ya terminó
        if self.pathfinder.is_finished: 
            return

        # GESTIÓN DE HISTORIAL
        # Si retrocedimos y ahora avanzamos, borramos el futuro anterior
        if self.current_step < len(self.history) - 1:
            self.history = self.history[:self.current_step + 1]
        
        # EJECUTAR PASO DEL ALGORITMO
        self.pathfinder.step()
        
        # GUARDAR ESTADO ACTUAL
        self.history.append(self.get_current_state_snapshot())
        self.current_step += 1

    def step_back(self):
        """
        Retroceder un paso en la ejecución del algoritmo.
        
        PROPÓSITO: Navegar hacia atrás en el historial de ejecución
        FUNCIONAMIENTO:
        1. Verificar que hay pasos previos disponibles
        2. Decrementar índice de paso actual
        3. Restaurar estado desde historial
        """
        # Solo retroceder si hay pasos previos
        if self.current_step > 0:
            self.current_step -= 1
            
            # RESTAURAR ESTADO desde historial
            state = self.history[self.current_step]
            self.pathfinder.open_list = copy.deepcopy(state["open_list"])
            self.pathfinder.closed_list = copy.deepcopy(state["closed_list"])
            self.pathfinder.path = copy.deepcopy(state["path"])
            self.pathfinder.is_finished = state["is_finished"]

    def toggle_diagonal(self):
        """
        Activar/desactivar movimiento diagonal.
        
        PROPÓSITO: Cambiar reglas de movimiento durante análisis
        RESTRICCIÓN: Solo permitir cambios cuando no hay ejecución automática
        EFECTO: Recrear algoritmos y reiniciar búsqueda con nuevas reglas
        """
        # Solo permitir cambios cuando no hay ejecución automática
        if not self.is_auto_running:
            # Cambiar estado diagonal
            self.allow_diagonal = not self.allow_diagonal
            self.diagonal_button.text = f'Diagonal: {"ON" if self.allow_diagonal else "OFF"}'
            
            # RECREAR ALGORITMOS con nueva configuración de movimiento
            # Esto es necesario porque el tipo de movimiento afecta las heurísticas
            self.algorithms = {
                "A*": AStarPathfinder(self.grid, self.allow_diagonal),
                "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
                "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
                "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
            }
            self.pathfinder = self.algorithms[self.current_algo_name]
            
            # Reiniciar búsqueda con nuevas reglas
            self.reset_search()

    def toggle_auto_mode(self):
        """
        Activar/desactivar modo de ejecución automática.
        
        PROPÓSITO: Permitir observar algoritmo ejecutándose automáticamente
        FUNCIONAMIENTO:
        1. Alternar estado de ejecución automática
        2. Actualizar texto del botón
        3. Reiniciar temporizador de pasos automáticos
        """
        self.is_auto_running = not self.is_auto_running
        self.auto_button.text = f"Auto: {'ON' if self.is_auto_running else 'OFF'}"
        self.auto_step_timer = 0.0  # Reiniciar temporizador al cambiar modo

    def switch_algorithm(self):
        """
        Cambiar entre algoritmos disponibles.
        
        PROPÓSITO: Permitir comparar diferentes algoritmos en el mismo mapa
        ALGORITMOS: A*, Dijkstra, Voraz, Costo Uniforme
        EFECTO: Reiniciar búsqueda con algoritmo seleccionado
        """
        # Ciclar al siguiente algoritmo en la lista
        algo_names = list(self.algorithms.keys())
        current_index = algo_names.index(self.current_algo_name)
        next_index = (current_index + 1) % len(algo_names)
        self.current_algo_name = algo_names[next_index]
        
        # Actualizar pathfinder y botón
        self.pathfinder = self.algorithms[self.current_algo_name]
        self.switch_algo_button.text = f"Algoritmo: {self.current_algo_name}"
        
        # Reiniciar búsqueda con nuevo algoritmo
        self.reset_search()

    def handle_events(self, events):
        """
        Manejar eventos de entrada del usuario.
        
        PROPÓSITO: Procesar teclas y clics de botones
        EVENTOS MANEJADOS:
        1. Tecla ESC - regresar al menú
        2. Botones de navegación (solo si no hay auto-ejecución)
        3. Botones de configuración (siempre disponibles)
        """
        for event in events:
            # TECLA ESC: Regresar al menú principal
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.switch_scene('menu')
            
            # BOTONES DE NAVEGACIÓN: Solo activos si no hay auto-ejecución
            if not self.is_auto_running:
                self.next_step_button.handle_event(event)    # Avanzar paso
                self.back_step_button.handle_event(event)    # Retroceder paso
                self.diagonal_button.handle_event(event)     # Toggle diagonal
            
            # BOTONES SIEMPRE ACTIVOS
            self.switch_algo_button.handle_event(event)      # Cambiar algoritmo
            self.auto_button.handle_event(event)             # Toggle auto-mode
            self.tree_button.handle_event(event)             # Visualizador de árbol

    def update(self, dt):
        """
        Actualizar lógica de ejecución automática.
        
        PROPÓSITO: Gestionar progreso automático del algoritmo
        FUNCIONAMIENTO:
        1. Acumular tiempo transcurrido
        2. Si es tiempo de dar paso automático y algoritmo no terminó
        3. Ejecutar siguiente paso del algoritmo
        4. Reiniciar temporizador para próximo paso
        """
        # MODO AUTOMÁTICO: Solo si está activado y algoritmo no terminó
        if self.is_auto_running and not self.history[self.current_step]["is_finished"]:
            # Acumular tiempo para controlar velocidad
            self.auto_step_timer += dt
            
            # Si es tiempo de dar el siguiente paso
            if self.auto_step_timer >= self.auto_step_speed:
                self.auto_step_timer = 0  # Reiniciar temporizador
                self.step_forward()       # Ejecutar siguiente paso
        
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