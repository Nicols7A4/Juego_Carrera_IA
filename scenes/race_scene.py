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

class RaceScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.grid = Grid()
        self.font_winner = pygame.font.SysFont('B612Mono', 80, bold=True)
        self.font_stats = pygame.font.SysFont('B612Mono', 24)
        self.winner_text = ""
        
        # Estado del movimiento diagonal
        self.allow_diagonal = False
        
        self.algorithms = {
            "A*": AStarPathfinder(self.grid, self.allow_diagonal),
            "Dijkstra": DijkstraPathfinder(self.grid, self.allow_diagonal),
            "Voraz": GreedyPathfinder(self.grid, self.allow_diagonal),
            "Costo U": UniformCostPathfinder(self.grid, self.allow_diagonal)
        }
        self.current_algo_name = "A*"
        self.pathfinder = self.algorithms[self.current_algo_name]

        # --- NUEVO: Lógica de botones y estado de carrera ---
        self.race_started = False
        self.switch_algo_button = Button(config.SCREEN_WIDTH - 220, 20, 200, 50, 'IA: A*', self.switch_algorithm)
        self.start_race_button = Button(config.SCREEN_WIDTH - 220, 90, 200, 50, 'Carrera: Comenzar', self.toggle_race_state)
        self.diagonal_button = Button(config.SCREEN_WIDTH - 220, 160, 200, 40, 'Diagonal: OFF', self.toggle_diagonal)
        
        # --- NUEVO: Variables del temporizador ---
        self.race_start_time = 0
        self.player_finish_time = 0
        self.ai_finish_time = 0
        self.race_time = 0

    def on_enter(self):
        self.grid.load_map(self.game.selected_map)
        start = self.grid.start_pos
        if not start: return

        self.player = Agent(start, (0, 150, 255), is_human=True)
        self.ai = Agent(start, (255, 128, 0))
        
        self.ai_move_speed = 0.15
        self.ai_move_timer = 0
        
        self.switch_algorithm(initial_setup=True) # Configura el estado inicial sin reiniciar

    def toggle_diagonal(self):
        """Activa/desactiva el movimiento diagonal."""
        if not self.race_started:
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
            
            # Recalcular el camino de la IA
            if self.grid.start_pos and self.grid.end_pos:
                self.ai.path = self.pathfinder.find_path(self.grid.start_pos, self.grid.end_pos)

    def switch_algorithm(self, initial_setup=False):
        algo_names = list(self.algorithms.keys())
        current_index = algo_names.index(self.current_algo_name)
        if not initial_setup:
            next_index = (current_index + 1) % len(algo_names)
            self.current_algo_name = algo_names[next_index]

        self.pathfinder = self.algorithms[self.current_algo_name]
        self.switch_algo_button.text = f"IA: {self.current_algo_name}"

        if self.grid.start_pos and self.grid.end_pos:
            self.ai.path = self.pathfinder.find_path(self.grid.start_pos, self.grid.end_pos)

        self.reset_race()
        
    def toggle_race_state(self):
        """Inicia o reinicia la carrera."""
        if self.race_started:
            # Si la carrera está en marcha, el botón funciona como "Reiniciar"
            self.reset_race()
        else:
            # Si la carrera está pausada, la inicia
            self.race_started = True
            self.start_race_button.text = "Carrera: Reiniciar"
            # Iniciar el temporizador
            self.race_start_time = pygame.time.get_ticks() / 1000.0  # Convertir a segundos

    def reset_race(self):
        """Función auxiliar para reiniciar el estado de los agentes."""
        self.race_started = False
        self.start_race_button.text = "Carrera: Comenzar"
        self.winner_text = ""
        
        # Reiniciar temporizadores
        self.race_start_time = 0
        self.player_finish_time = 0
        self.ai_finish_time = 0
        self.race_time = 0

        if self.grid.start_pos:
            self.ai.position = self.grid.start_pos
            self.player.position = self.grid.start_pos
        
        self.ai.finished = False
        self.ai.steps = 0
        self.ai_path_index = 1
        
        self.player.finished = False
        self.player.path = [self.grid.start_pos]
        self.player.steps = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.switch_scene('menu')

            # El botón de comenzar/reiniciar siempre debe estar activo
            self.start_race_button.handle_event(event)

            # El botón de cambiar IA solo está activo si la carrera no ha comenzado
            # (lo que también es cierto cuando la carrera termina)
            if not self.race_started:
                self.switch_algo_button.handle_event(event)
                self.diagonal_button.handle_event(event)

            # El jugador solo se puede mover si la carrera ha empezado y no hay ganador
            if self.race_started and not self.winner_text:
                if event.type == pygame.KEYDOWN:
                    # Movimientos básicos
                    if event.key == pygame.K_UP:
                        self.player.move(0, -1, self.grid)
                    elif event.key == pygame.K_DOWN:
                        self.player.move(0, 1, self.grid)
                    elif event.key == pygame.K_LEFT:
                        self.player.move(-1, 0, self.grid)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(1, 0, self.grid)
                    # Movimientos diagonales (si están habilitados)
                    elif self.allow_diagonal:
                        if event.key == pygame.K_q:  # Diagonal arriba-izquierda
                            self.player.move(-1, -1, self.grid)
                        elif event.key == pygame.K_e:  # Diagonal arriba-derecha
                            self.player.move(1, -1, self.grid)
                        elif event.key == pygame.K_z:  # Diagonal abajo-izquierda
                            self.player.move(-1, 1, self.grid)
                        elif event.key == pygame.K_c:  # Diagonal abajo-derecha
                            self.player.move(1, 1, self.grid)

    def update(self, dt):
        """Mueve la IA y comprueba si hay un ganador."""
        if not self.race_started or self.winner_text: return

        # Actualizar tiempo de carrera
        self.race_time = pygame.time.get_ticks() / 1000.0 - self.race_start_time

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
    
    