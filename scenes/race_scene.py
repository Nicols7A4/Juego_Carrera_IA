import pygame
import config
from scenes.scene_base import SceneBase
from components.grid import Grid
from components.agent import Agent
from algorithms.a_star import AStarPathfinder
from algorithms.dijkstra import DijkstraPathfinder
from algorithms.greedy import GreedyPathfinder
from algorithms.uniform_cost import UniformCostPathfinder
from components.button import Button

SP1 = 0.12
SP2 = 0.080

class RaceScene(SceneBase):
    """
    Escena de carrera entre humano e IA.
    
    PROPÓSITO: Permitir al jugador competir directamente contra un algoritmo de IA
    CARACTERÍSTICAS:
    1. Control humano con teclas direccionales (movimiento continuo)
    2. Selección de algoritmo de IA (A*, Dijkstra, Voraz, Costo Uniforme)
    3. Toggle de movimiento diagonal
    4. Medición de tiempos de finalización
    5. Detección de ganador en tiempo real
    """
    def __init__(self, game):
        super().__init__(game)
        
        # CONFIGURACIÓN DE LA CUADRÍCULA Y FUENTES
        self.grid = Grid()
        self.font_winner = pygame.font.SysFont('B612Mono', 80, bold=True)
        self.font_stats = pygame.font.SysFont('B612Mono', 24)
        self.winner_text = ""
        
        # CONFIGURACIÓN DE MOVIMIENTO DIAGONAL
        self.allow_diagonal = False
        
        # CONFIGURACIÓN DE ALGORITMOS DISPONIBLES
        # Diccionario con todos los algoritmos que la IA puede usar
        self.algorithms = {
            "A*": AStarPathfinder(self.grid, self.allow_diagonal),
            "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
            "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
            "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
        }
        self.current_algo_name = "A*"
        self.pathfinder = self.algorithms[self.current_algo_name]

        # CONTROL DE ESTADO DE LA CARRERA
        self.race_started = False
        
        # BOTONES DE INTERFACE DE USUARIO
        self.switch_algo_button = Button(config.SCREEN_WIDTH - 220, 20, 200, 50, 'IA: A*', self.switch_algorithm)
        self.start_race_button = Button(config.SCREEN_WIDTH - 220, 90, 200, 50, 'Carrera: Comenzar', self.toggle_race_state)
        self.diagonal_button = Button(config.SCREEN_WIDTH - 220, 160, 200, 40, 'Diagonal: OFF', self.toggle_diagonal)
        
        # SISTEMA DE MEDICIÓN DE TIEMPO
        # Para determinar quién llega primero y por cuánto margen
        self.race_start_time = 0
        self.player_finish_time = 0
        self.ai_finish_time = 0
        self.race_time = 0
        
        # SISTEMA DE MOVIMIENTO CONTINUO DEL JUGADOR
        # Permite mantener presionada una tecla para movimiento fluido
        self.player_move_speed = SP1  # Velocidad de movimiento del jugador (segundos entre movimientos)
        self.player_move_timer = 0

    def on_enter(self):
        """
        Inicializar la escena cuando se accede a ella.
        
        PROPÓSITO: Configurar el estado inicial de la carrera
        ACCIONES:
        1. Cargar el mapa seleccionado
        2. Crear agentes humano e IA en posición inicial
        3. Configurar velocidades de movimiento
        4. Inicializar algoritmo seleccionado
        """
        # Cargar mapa y obtener posición inicial
        self.grid.load_map(self.game.selected_map) # Carga el JSON como matriz 2D
        start = self.grid.start_pos
        if not start: return

        # CREAR AGENTES
        # Jugador humano (azul) controlado por teclas
        self.player = Agent(start, (0, 150, 255), is_human=True)
        # IA (naranja) controlada por algoritmo
        self.ai = Agent(start, (255, 128, 0))
        
        # CONFIGURAR VELOCIDADES DE MOVIMIENTO
        self.ai_move_speed = 0.15  # IA se mueve cada 0.15 segundos
        self.ai_move_timer = 0
        self.ai_path_index = 1  # Índice del próximo nodo en el camino de la IA
        
        # Inicializar algoritmo sin reiniciar carrera
        self.switch_algorithm(initial_setup=True)

    def toggle_diagonal(self):
        """
        Activar/desactivar movimiento diagonal.
        
        PROPÓSITO: Permitir cambiar reglas de movimiento antes de la carrera
        FUNCIONAMIENTO:
        1. Solo permitir cambios antes de iniciar carrera
        2. Recrear todos los algoritmos con nueva configuración
        3. Recalcular camino de la IA con nuevas reglas
        """
        if not self.race_started:
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
            
            # Recalcular camino de la IA con nuevas reglas de movimiento
            if self.grid.start_pos and self.grid.end_pos:
                self.ai.path = self.pathfinder.find_path(self.grid.start_pos, self.grid.end_pos)

    def switch_algorithm(self, initial_setup=False):
        """
        Cambiar algoritmo de IA disponible.
        
        PROPÓSITO: Permitir al jugador seleccionar contra qué algoritmo competir
        ALGORITMOS DISPONIBLES: A*, Dijkstra, Voraz, Costo Uniforme
        FUNCIONAMIENTO: Ciclar entre algoritmos y recalcular camino
        """
        algo_names = list(self.algorithms.keys())
        current_index = algo_names.index(self.current_algo_name)
        
        # Avanzar al siguiente algoritmo (excepto en configuración inicial)
        if not initial_setup:
            next_index = (current_index + 1) % len(algo_names)
            self.current_algo_name = algo_names[next_index]

        # Actualizar pathfinder activo
        self.pathfinder = self.algorithms[self.current_algo_name]
        # Actualizar texto del botón y calcular camino de la IA
        self.switch_algo_button.text = f"IA: {self.current_algo_name}"

        # Calcular camino óptimo para el algoritmo seleccionado
        if self.grid.start_pos and self.grid.end_pos:
            self.ai.path = self.pathfinder.find_path(self.grid.start_pos, self.grid.end_pos)

        # Reiniciar estado de carrera
        self.reset_race()
        
    def toggle_race_state(self):
        """
        Iniciar o reiniciar la carrera.
        
        PROPÓSITO: Controlar el estado de la competencia
        FUNCIONAMIENTO:
        1. Si no hay carrera: iniciar carrera y temporizador
        2. Si hay carrera: reiniciar todo al estado inicial
        """
        if self.race_started:
            # REINICIAR CARRERA
            # Si la carrera está en marcha, el botón funciona como "Reiniciar"
            self.reset_race()
        else:
            # INICIAR CARRERA
            # Si la carrera está pausada, la inicia
            self.race_started = True
            self.start_race_button.text = "Carrera: Reiniciar"
            # Iniciar medición de tiempo
            self.race_start_time = pygame.time.get_ticks() / 1000.0  # Convertir a segundos

    def reset_race(self):
        """
        Reiniciar el estado de todos los componentes de la carrera.
        
        PROPÓSITO: Volver al estado inicial para nueva competencia
        COMPONENTES REINICIADOS:
        1. Estado de carrera y botones
        2. Posiciones de agentes
        3. Temporizadores y contadores
        4. Caminos recorridos
        """
        # REINICIAR ESTADO DE CARRERA
        self.race_started = False
        self.start_race_button.text = "Carrera: Comenzar"
        self.winner_text = ""
        
        # REINICIAR TEMPORIZADORES
        self.race_start_time = 0
        self.player_finish_time = 0
        self.ai_finish_time = 0
        self.race_time = 0
        self.player_move_timer = 0  # Reiniciar también el temporizador del jugador

        # REINICIAR POSICIONES DE AGENTES
        if self.grid.start_pos:
            self.ai.position = self.grid.start_pos
            self.player.position = self.grid.start_pos
        
        # REINICIAR ESTADO DE LA IA
        self.ai.finished = False
        self.ai.steps = 0
        self.ai_path_index = 1  # Empezar desde el segundo nodo del camino
        
        # REINICIAR ESTADO DEL JUGADOR
        self.player.finished = False
        self.player.path = [self.grid.start_pos]  # Camino recorrido por el jugador
        self.player.steps = 0

    def handle_events(self, events):
        """
        Manejar eventos de entrada del usuario.
        
        PROPÓSITO: Procesar teclas y clics de botones
        EVENTOS MANEJADOS:
        1. Tecla ESC - regresar al menú
        2. Botón de inicio/reinicio de carrera (siempre activo)
        3. Botones de configuración (solo antes de iniciar carrera)
        """
        for event in events:
            # TECLA ESC: Regresar al menú principal
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.switch_scene('menu')

            # BOTÓN DE CARRERA: Siempre activo (iniciar/reiniciar)
            self.start_race_button.handle_event(event)

            # BOTONES DE CONFIGURACIÓN: Solo activos antes de iniciar carrera
            if not self.race_started:
                self.switch_algo_button.handle_event(event)  # Cambiar algoritmo de IA
                self.diagonal_button.handle_event(event)     # Toggle movimiento diagonal

    def update(self, dt):
        """
        Actualizar lógica de la carrera en cada frame.
        
        PROPÓSITO: Gestionar movimiento de agentes y detección de ganador
        COMPONENTES ACTUALIZADOS:
        1. Tiempo transcurrido de carrera
        2. Movimiento continuo del jugador (con teclas presionadas)
        3. Movimiento automático de la IA
        4. Detección de llegada al destino
        """
        # Solo actualizar si la carrera está activa y no hay ganador
        if not self.race_started or self.winner_text: 
            return

        # ACTUALIZACIÓN DE TIEMPO DE CARRERA
        self.race_time = pygame.time.get_ticks() / 1000.0 - self.race_start_time

        # SISTEMA DE MOVIMIENTO CONTINUO DEL JUGADOR
        # Permite mantener presionadas las teclas para movimiento fluido
        if not self.player.finished:
            self.player_move_timer += dt
            if self.player_move_timer >= self.player_move_speed:
                keys = pygame.key.get_pressed()
                moved = False
                
                # Movimientos básicos
                
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.player.move(0, -1, self.grid)
                    moved = True
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.player.move(0, 1, self.grid)
                    moved = True
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.player.move(-1, 0, self.grid)
                    moved = True
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.player.move(1, 0, self.grid)
                    moved = True
                # Movimientos diagonales (si están habilitados)
                elif self.allow_diagonal:
                    self.player_move_speed = SP2
                    if keys[pygame.K_q]:  # Diagonal arriba-izquierda
                        self.player.move(-1, -1, self.grid)
                        moved = True
                    elif keys[pygame.K_e]:  # Diagonal arriba-derecha
                        self.player.move(1, -1, self.grid)
                        moved = True
                    elif keys[pygame.K_z]:  # Diagonal abajo-izquierda
                        self.player.move(-1, 1, self.grid)
                        moved = True
                    elif keys[pygame.K_c]:  # Diagonal abajo-derecha
                        self.player.move(1, 1, self.grid)
                        moved = True
                
                # Solo reiniciar el temporizador si se movió
                if moved:
                    self.player_move_timer = 0

        # Mover la IA
        if not self.ai.finished and self.ai.path:
            self.ai_move_timer += dt
            if self.ai_move_timer >= self.ai_move_speed:
                self.ai_move_timer = 0
                if self.ai_path_index < len(self.ai.path):
                    self.ai.position = self.ai.path[self.ai_path_index]
                    self.ai.steps += 1
                    self.ai_path_index += 1

        # Comprobar si el jugador llegó al objetivo
        if not self.player.finished and self.player.position == self.grid.end_pos:
            self.player.finished = True
            self.player_finish_time = self.race_time
            
        # Comprobar si la IA llegó al objetivo
        if not self.ai.finished and self.ai.position == self.grid.end_pos:
            self.ai.finished = True
            self.ai_finish_time = self.race_time

        # Comprobar ganador
        if self.player.finished or self.ai.finished:
            self.race_started = False
            self.start_race_button.text = "Carrera: Reiniciar"
            
            # Determinar ganador basado en quién terminó primero
            if self.player.finished and self.ai.finished:
                # Ambos terminaron, el que terminó primero gana
                if self.player_finish_time < self.ai_finish_time:
                    self.winner_text = "¡GANASTE!"
                elif self.ai_finish_time < self.player_finish_time:
                    self.winner_text = "GANA LA IA"
                else:
                    self.winner_text = "¡EMPATE!"
            elif self.player.finished:
                self.winner_text = "¡GANASTE!"
            elif self.ai.finished:
                self.winner_text = "GANA LA IA"

    def draw(self, screen):
        screen.fill(config.GRAY)
        self.grid.draw(screen)

        if self.winner_text:
            # Dibujar el camino del jugador (primero)
            if self.player.path:
                for pos in self.player.path:
                    if pos != self.grid.start_pos and pos != self.grid.end_pos:
                        rect = pygame.Rect(pos[0] * config.CELL_SIZE, pos[1] * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
                        pygame.draw.rect(screen, (0, 60, 100), rect) # Azul oscuro

            # Dibujar camino de la IA (después)
            if self.ai.path:
                for pos in self.ai.path:
                    if pos != self.grid.start_pos and pos != self.grid.end_pos:
                        rect = pygame.Rect(pos[0] * config.CELL_SIZE, pos[1] * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
                        pygame.draw.rect(screen, (80, 40, 0), rect) # Marrón oscuro

        self.player.draw(screen)
        self.ai.draw(screen)

        info_font = pygame.font.SysFont('B612Mono', 20)
        instructions = [
            'Presiona ESC para volver al menu',
            'Flechas: Mover'
        ]
        if self.allow_diagonal:
            instructions.append('Q/E/Z/C: Mover diagonal')
            
        for i, instruction in enumerate(instructions):
            info_text = info_font.render(instruction, True, config.WHITE)
            screen.blit(info_text, (10, 10 + i * 25))

        # Dibujar los botones
        self.switch_algo_button.draw(screen)
        self.start_race_button.draw(screen)
        self.diagonal_button.draw(screen)
        
        # Mostrar tiempo actual durante la carrera
        if self.race_started and not self.winner_text:
            time_text = f"Tiempo: {self.race_time:.1f}s"
            time_surface = self.font_stats.render(time_text, True, config.WHITE)
            screen.blit(time_surface, (config.SCREEN_WIDTH - 220, 230))

        if self.winner_text:
            # Dibujar las estadísticas finales
            center_x = config.SCREEN_WIDTH / 2
            center_y = config.SCREEN_HEIGHT / 2
            
            # Estadísticas del jugador
            player_stats = f"Tus pasos: {self.player.steps}"
            player_time = f"Tu tiempo: {self.player_finish_time:.2f}s" if self.player.finished else "Tu tiempo: --"
            
            # Estadísticas de la IA
            ai_stats = f"Pasos IA: {self.ai.steps}"
            ai_time = f"Tiempo IA: {self.ai_finish_time:.2f}s" if self.ai.finished else "Tiempo IA: --"
            
            # Renderizar textos
            player_stats_text = self.font_stats.render(player_stats, True, config.WHITE)
            player_time_text = self.font_stats.render(player_time, True, config.WHITE)
            ai_stats_text = self.font_stats.render(ai_stats, True, config.WHITE)
            ai_time_text = self.font_stats.render(ai_time, True, config.WHITE)
            
            # Posicionar textos
            screen.blit(player_stats_text, player_stats_text.get_rect(center=(center_x, center_y + 80)))
            screen.blit(player_time_text, player_time_text.get_rect(center=(center_x, center_y + 105)))
            screen.blit(ai_stats_text, ai_stats_text.get_rect(center=(center_x, center_y + 135)))
            screen.blit(ai_time_text, ai_time_text.get_rect(center=(center_x, center_y + 160)))
            
            # Dibujar texto de ganador
            text_surf = self.font_winner.render(self.winner_text, True, config.WHITE)
            text_rect = text_surf.get_rect(center=(center_x, center_y))
            screen.blit(text_surf, text_rect)
    
    