import pygame
import config
from scenes.scene_base import SceneBase
from components.grid import Grid
from components.agent import Agent
from components.button import Button
from algorithms.a_star import AStarPathfinder
from algorithms.dijkstra import DijkstraPathfinder
from algorithms.greedy import GreedyPathfinder
from algorithms.uniform_cost import UniformCostPathfinder

# Algoritmos disponibles
AVAILABLE_ALGORITHMS = [
    ('a_star', 'A*'),
    ('dijkstra', 'Dijkstra'),
    ('greedy', 'Voraz'),
    ('uniform_cost', 'Costo Uniforme')
]

def get_pathfinder(name, grid, allow_diagonal=False):
    """Función para obtener el pathfinder correspondiente según el nombre del algoritmo."""
    if name == 'a_star':
        return AStarPathfinder(grid, allow_diagonal)
    elif name == 'dijkstra':
        return DijkstraPathfinder(grid, allow_diagonal)
    elif name == 'greedy':
        return GreedyPathfinder(grid, allow_diagonal)
    elif name == 'uniform_cost':
        return UniformCostPathfinder(grid, allow_diagonal)
    else:
        raise ValueError(f"Algoritmo desconocido: {name}")

def get_algorithm_display_name(name):
    """Función para obtener el nombre de visualización del algoritmo."""
    names = {
        'a_star': 'A*',
        'dijkstra': 'Dijkstra',
        'greedy': 'Voraz',
        'uniform_cost': 'Costo Uniforme'
    }
    return names.get(name, name.upper())

class IAvsIAScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        # Reducimos el tamaño de celda para que quepan dos mapas
        self.cell_size = 25
        
        # Calcular dimensiones para que quepan dos mapas
        margin_x = 50
        margin_y = 100 # Espacio para títulos arriba y espacio abajo
        available_width = (config.SCREEN_WIDTH / 2) - margin_x
        available_height = config.SCREEN_HEIGHT - margin_y
        
        cols_per_map = int(available_width // self.cell_size)
        rows_per_map = int(available_height // self.cell_size)

        # Estado de la competencia
        self.race_started = False
        self.race_finished = False
        self.allow_diagonal = False  # Por defecto desactivado
        
        # Algoritmos seleccionados (por defecto)
        self.algo1_name = 'a_star'
        self.algo2_name = 'dijkstra'
        
        # Área de la izquierda para el primer algoritmo
        self.grid1 = Grid(cols=cols_per_map, rows=rows_per_map)
        self.offset1 = (margin_x, 70) # Margen izquierdo con más espacio
        
        # Área de la derecha para el segundo algoritmo
        self.grid2 = Grid(cols=cols_per_map, rows=rows_per_map)
        self.offset2 = (config.SCREEN_WIDTH / 2 + margin_x / 2, 70) # Margen derecho con más espacio

        # Fuentes
        self.font_title = pygame.font.SysFont('B612Mono', 30, bold=True)
        self.font_stats = pygame.font.SysFont('B612Mono', 22)
        self.font_winner = pygame.font.SysFont('B612Mono', 80, bold=True)
        self.font_button = pygame.font.SysFont('B612Mono', 20)
        
        self.winner_text = ""
        
        # Crear botones de selección de algoritmo
        self._create_algorithm_buttons()
        
        # Botón para comenzar la carrera
        self.start_button = Button(
            config.SCREEN_WIDTH // 2 - 75, 
            config.SCREEN_HEIGHT - 60, 
            150, 40, 
            "COMENZAR", 
            self._start_race
        )
        
        # Botón para toggle movimiento diagonal
        self.diagonal_button = Button(
            config.SCREEN_WIDTH // 2 - 100, 
            config.SCREEN_HEIGHT - 110, 
            200, 35, 
            "Movimiento Diagonal: OFF", 
            self._toggle_diagonal
        )
        
        # Variables de la competencia
        self.pathfinder1 = None
        self.pathfinder2 = None
        self.ai1 = None
        self.ai2 = None
        self.ai1_nodes_expanded = 0
        self.ai2_nodes_expanded = 0
        self.ai1_iterations = 0
        self.ai2_iterations = 0
    
    def _create_algorithm_buttons(self):
        """Crea los botones para selección de algoritmos."""
        button_width = 120
        button_height = 30
        button_spacing = 35
        
        # Botones para el algoritmo 1 (lado izquierdo)
        self.algo1_buttons = []
        start_y = 190  # Más espacio desde arriba para las estadísticas
        for i, (algo_id, algo_name) in enumerate(AVAILABLE_ALGORITHMS):
            button = Button(
                self.offset1[0], 
                start_y + i * button_spacing,
                button_width, button_height,
                algo_name,
                lambda algo=algo_id: self._select_algorithm_1(algo)
            )
            self.algo1_buttons.append(button)
        
        # Botones para el algoritmo 2 (lado derecho)
        self.algo2_buttons = []
        for i, (algo_id, algo_name) in enumerate(AVAILABLE_ALGORITHMS):
            button = Button(
                self.offset2[0], 
                start_y + i * button_spacing,
                button_width, button_height,
                algo_name,
                lambda algo=algo_id: self._select_algorithm_2(algo)
            )
            self.algo2_buttons.append(button)
    
    def _select_algorithm_1(self, algorithm):
        """Selecciona el algoritmo para el jugador 1."""
        if algorithm != self.algo2_name and not self.race_started:
            self.algo1_name = algorithm
    
    def _select_algorithm_2(self, algorithm):
        """Selecciona el algoritmo para el jugador 2."""
        if algorithm != self.algo1_name and not self.race_started:
            self.algo2_name = algorithm
    
    def _start_race(self):
        """Inicia la competencia entre los algoritmos seleccionados."""
        if not self.race_started and not self.race_finished:
            self.race_started = True
            self._initialize_algorithms()
    
    def _toggle_diagonal(self):
        """Activa/desactiva el movimiento diagonal."""
        if not self.race_started:
            self.allow_diagonal = not self.allow_diagonal
            self.diagonal_button.text = f"Movimiento Diagonal: {'ON' if self.allow_diagonal else 'OFF'}"
    
    def _initialize_algorithms(self):
        """Inicializa los pathfinders y agentes para la competencia."""
        # Crear pathfinders con la configuración de movimiento diagonal
        self.pathfinder1 = get_pathfinder(self.algo1_name, self.grid1, self.allow_diagonal)
        self.pathfinder2 = get_pathfinder(self.algo2_name, self.grid2, self.allow_diagonal)
        
        # Verificar que el mapa tenga inicio y fin válidos
        if not self.grid1.start_pos or not self.grid1.end_pos:
            self.winner_text = "MAPA INVÁLIDO"
            self.race_finished = True
            return
        
        start = self.grid1.start_pos
        
        # Configurar IA 1 (primer algoritmo)
        self.ai1 = Agent(start, (255, 128, 0)) # Naranja
        self.ai1.path = self.pathfinder1.find_path(start, self.grid1.end_pos)
        self.ai1_nodes_expanded = len(self.pathfinder1.closed_list)
        self.ai1_iterations = self.pathfinder1.iterations
        
        # Configurar IA 2 (segundo algoritmo)
        self.ai2 = Agent(start, (0, 191, 255)) # Celeste
        self.ai2.path = self.pathfinder2.find_path(start, self.grid2.end_pos)
        self.ai2_nodes_expanded = len(self.pathfinder2.closed_list)
        self.ai2_iterations = self.pathfinder2.iterations

        # Control de tiempo para la animación
        self.move_speed = 0.05
        self.move_timer = 0
        self.path_index = 1

    def on_enter(self):
        """Se ejecuta cuando se entra a la escena."""
        # Sobreescribimos config para esta escena
        config.CELL_SIZE = self.cell_size
        
        # Resetear estado
        self.race_started = False
        self.race_finished = False
        self.winner_text = ""
        self.allow_diagonal = False
        self.diagonal_button.text = "Movimiento Diagonal: OFF"
        
        # Cargar el mismo mapa en ambas cuadrículas
        self.grid1.load_map(self.game.selected_map)
        self.grid2.load_map(self.game.selected_map)
        
        # Resetear agentes y pathfinders
        self.pathfinder1 = None
        self.pathfinder2 = None
        self.ai1 = None
        self.ai2 = None
        self.ai1_nodes_expanded = 0
        self.ai2_nodes_expanded = 0
        self.ai1_iterations = 0
        self.ai2_iterations = 0

    def update(self, dt):
        """Actualiza la lógica de la escena."""
        # Solo actualizar si la carrera ha comenzado y no ha terminado
        if not self.race_started or self.race_finished or self.winner_text:
            return
        
        # Verificar que los agentes existan
        if not self.ai1 or not self.ai2:
            return
            
        self.move_timer += dt
        if self.move_timer >= self.move_speed:
            self.move_timer = 0
            
            if self.ai1.path and self.path_index < len(self.ai1.path):
                self.ai1.position = self.ai1.path[self.path_index]
            
            if self.ai2.path and self.path_index < len(self.ai2.path):
                self.ai2.position = self.ai2.path[self.path_index]
            
            self.path_index += 1

            # Comprobar ganador
            p1_finished = self.ai1.position == self.grid1.end_pos
            p2_finished = self.ai2.position == self.grid2.end_pos
            
            if p1_finished or p2_finished:
                self.ai1.finished = True
                self.ai2.finished = True
                self.race_finished = True
                
                algo1_display = get_algorithm_display_name(self.algo1_name)
                algo2_display = get_algorithm_display_name(self.algo2_name)
                
                if p1_finished and p2_finished:
                    # Si empatan en pasos, gana el que exploró menos nodos
                    if self.ai1_nodes_expanded < self.ai2_nodes_expanded:
                        self.winner_text = f"¡GANA {algo1_display} (MÁS EFICIENTE)!"
                    elif self.ai2_nodes_expanded < self.ai1_nodes_expanded:
                        self.winner_text = f"¡GANA {algo2_display} (MÁS EFICIENTE)!"
                    else:
                        self.winner_text = "¡EMPATE PERFECTO!"
                elif p1_finished:
                    self.winner_text = f"¡GANA {algo1_display}!"
                elif p2_finished:
                    self.winner_text = f"¡GANA {algo2_display}!"

    def handle_events(self, events):
        """Maneja los eventos de la escena."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                config.CELL_SIZE = 40 # Restaura el tamaño de celda original
                self.game.switch_scene('menu')
            
            # Manejar eventos de botones solo si la carrera no ha comenzado
            if not self.race_started:
                # Botones de selección de algoritmo 1
                for button in self.algo1_buttons:
                    button.handle_event(event)
                
                # Botones de selección de algoritmo 2
                for button in self.algo2_buttons:
                    button.handle_event(event)
                
                # Botón de comenzar
                self.start_button.handle_event(event)
                
                # Botón de movimiento diagonal
                self.diagonal_button.handle_event(event)

    def draw(self, screen):
        """Dibuja la escena en pantalla."""
        screen.fill(config.GRAY)
        
        # Dibujar ambas cuadrículas
        self.grid1.draw(screen, self.offset1)
        self.grid2.draw(screen, self.offset2)

        # Si la carrera ha comenzado, dibujar agentes y caminos
        if self.race_started and self.ai1 and self.ai2:
            # Si la carrera terminó, dibuja los caminos recorridos
            if self.race_finished:
                # Camino para IA 1 (primer algoritmo)
                if self.ai1.path:
                    for pos in self.ai1.path:
                        if pos != self.grid1.start_pos and pos != self.grid1.end_pos:
                            rect = pygame.Rect(pos[0] * config.CELL_SIZE + self.offset1[0], 
                                              pos[1] * config.CELL_SIZE + self.offset1[1], 
                                              config.CELL_SIZE, config.CELL_SIZE)
                            pygame.draw.rect(screen, (100, 50, 0), rect) # Marrón oscuro

                # Camino para IA 2 (segundo algoritmo)
                if self.ai2.path:
                    for pos in self.ai2.path:
                        if pos != self.grid2.start_pos and pos != self.grid2.end_pos:
                            rect = pygame.Rect(pos[0] * config.CELL_SIZE + self.offset2[0], 
                                              pos[1] * config.CELL_SIZE + self.offset2[1], 
                                              config.CELL_SIZE, config.CELL_SIZE)
                            pygame.draw.rect(screen, (0, 70, 100), rect) # Azul oscuro
            
            # Dibujar los agentes (se dibujarán encima de los caminos)
            self.ai1.draw(screen, self.offset1)
            self.ai2.draw(screen, self.offset2)

            # Dibujar estadísticas cuando la carrera ha comenzado
            stats1_line1 = self.font_stats.render(f"Nodos: {self.ai1_nodes_expanded} | Pasos: {len(self.ai1.path or [])-1}", True, config.WHITE)
            stats1_line2 = self.font_stats.render(f"Iteraciones: {self.ai1_iterations}", True, config.WHITE)
            screen.blit(stats1_line1, (self.offset1[0], 35))
            screen.blit(stats1_line2, (self.offset1[0], 55))

            stats2_line1 = self.font_stats.render(f"Nodos: {self.ai2_nodes_expanded} | Pasos: {len(self.ai2.path or [])-1}", True, config.WHITE)
            stats2_line2 = self.font_stats.render(f"Iteraciones: {self.ai2_iterations}", True, config.WHITE)
            screen.blit(stats2_line1, (self.offset2[0], 35))
            screen.blit(stats2_line2, (self.offset2[0], 55))

        # Dibujar títulos de los algoritmos seleccionados
        algo1_display = get_algorithm_display_name(self.algo1_name)
        algo2_display = get_algorithm_display_name(self.algo2_name)
        
        # Título lado izquierdo
        title1 = self.font_title.render(f"Jugador 1: {algo1_display}", True, config.WHITE)
        screen.blit(title1, (self.offset1[0], 10))
        
        # Título lado derecho
        title2 = self.font_title.render(f"Jugador 2: {algo2_display}", True, config.WHITE)
        screen.blit(title2, (self.offset2[0], 10))

        # Si la carrera no ha comenzado, mostrar interfaz de selección
        if not self.race_started:
            # Instrucciones
            instruction_text = self.font_stats.render("Selecciona los algoritmos y presiona COMENZAR", True, config.WHITE)
            text_rect = instruction_text.get_rect(center=(config.SCREEN_WIDTH // 2, 160))
            screen.blit(instruction_text, text_rect)
            
            # Dibujar botones de selección de algoritmo
            for i, button in enumerate(self.algo1_buttons):
                # Destacar el algoritmo seleccionado
                if AVAILABLE_ALGORITHMS[i][0] == self.algo1_name:
                    button.color_normal = (0, 100, 0)  # Verde para seleccionado
                    button.color_hover = (0, 150, 0)
                else:
                    button.color_normal = config.BLACK
                    button.color_hover = (60, 60, 60)
                button.draw(screen)
            
            for i, button in enumerate(self.algo2_buttons):
                # Destacar el algoritmo seleccionado
                if AVAILABLE_ALGORITHMS[i][0] == self.algo2_name:
                    button.color_normal = (0, 100, 0)  # Verde para seleccionado
                    button.color_hover = (0, 150, 0)
                else:
                    button.color_normal = config.BLACK
                    button.color_hover = (60, 60, 60)
                button.draw(screen)
            
            # Dibujar botón de comenzar
            self.start_button.draw(screen)
            
            # Dibujar botón de movimiento diagonal
            self.diagonal_button.draw(screen)

        # Dibujar texto del ganador si existe
        if self.winner_text:
            text_surf = self.font_winner.render(self.winner_text, True, config.WHITE)
            text_rect = text_surf.get_rect(center=(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2))
            screen.blit(text_surf, text_rect)