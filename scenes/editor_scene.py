import os
import pygame
import config
from scenes.scene_base import SceneBase
from components.grid import Grid
from components.button import Button
from utils import map_manager

class EditorScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.grid = Grid()
        # self.grid.load_map('assets/maps/default_map.json') # Carga un mapa base

        # Estado del mouse
        self.dragging_start = False
        self.dragging_end = False
        self.painting_obstacles = False  # Para el modo de pintar obstáculos
        self.paint_mode = None  # 'add' para agregar obstáculos, 'remove' para quitar
        self.last_painted_cell = None  # Para evitar pintar la misma celda múltiples veces

        # Botones
        self.buttons = [
            Button(config.SCREEN_WIDTH - 220, 20, 200, 50, 'Guardar Mapa', self.save_map),
            Button(config.SCREEN_WIDTH - 220, 90, 200, 50, 'Limpiar', self.grid.clear),
        ]
        
        # Calcular el área segura para el modo IA vs IA y guardarla
        self.ia_vs_ia_cell_size = 25
        margin_x = 50
        margin_y = 100
        available_width = (config.SCREEN_WIDTH / 2) - margin_x
        available_height = config.SCREEN_HEIGHT - margin_y
        
        cols = int(available_width // self.ia_vs_ia_cell_size)
        rows = int(available_height // self.ia_vs_ia_cell_size)
        
        # Creamos un rectángulo guía (en píxeles)
        self.safe_zone_rect = pygame.Rect(
            0, 0,
            cols * config.CELL_SIZE, # Usamos el CELL_SIZE del editor
            rows * config.CELL_SIZE
        )
        
        # ...
        self.saved_message = ""
        self.message_timer = 0
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.switch_scene('menu')

            for button in self.buttons:
                button.handle_event(event)
            
            # Lógica de edición con el mouse
            grid_pos = self.grid.get_cell_from_pos(pygame.mouse.get_pos())
            if not grid_pos: continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Click izquierdo
                    if grid_pos == self.grid.start_pos:
                        self.dragging_start = True
                    elif grid_pos == self.grid.end_pos:
                        self.dragging_end = True
                    else:
                        # Iniciar modo de pintar obstáculos
                        self.painting_obstacles = True
                        self.last_painted_cell = grid_pos
                        
                        # Determinar si vamos a agregar o quitar obstáculos
                        current_state = self.grid.states[grid_pos[0]][grid_pos[1]]
                        if current_state == config.STATE_OBSTACLE:
                            self.paint_mode = 'remove'  # La celda es obstáculo, vamos a quitar
                        else:
                            self.paint_mode = 'add'     # La celda no es obstáculo, vamos a agregar
                        
                        # Aplicar el cambio inicial
                        self.grid.toggle_obstacle(grid_pos)
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_start = False
                    self.dragging_end = False
                    self.painting_obstacles = False
                    self.paint_mode = None
                    self.last_painted_cell = None
            
            if event.type == pygame.MOUSEMOTION:
                if self.dragging_start:
                    self.grid.move_point('start', grid_pos)
                elif self.dragging_end:
                    self.grid.move_point('end', grid_pos)
                elif self.painting_obstacles and grid_pos != self.last_painted_cell:
                    # Solo pintar si es una celda diferente y no es punto de inicio/fin
                    if grid_pos != self.grid.start_pos and grid_pos != self.grid.end_pos:
                        current_state = self.grid.states[grid_pos[0]][grid_pos[1]]
                        
                        # Aplicar el modo de pintura consistente
                        if self.paint_mode == 'add' and current_state != config.STATE_OBSTACLE:
                            self.grid.set_obstacle(grid_pos, True)
                        elif self.paint_mode == 'remove' and current_state == config.STATE_OBSTACLE:
                            self.grid.set_obstacle(grid_pos, False)
                        
                        self.last_painted_cell = grid_pos

    def update(self, dt):
        # Timer para el mensaje de guardado
        if self.message_timer > 0:
            self.message_timer -= dt
        else:
            self.saved_message = ""

    def draw(self, screen):
        screen.fill(config.GRAY)
        self.grid.draw(screen)

        # --- AÑADIR ESTO ---
        # Dibujar la guía visual para el modo IA vs IA
        # Creamos una superficie temporal para poder dibujarla con transparencia
        safe_zone_surface = pygame.Surface(self.safe_zone_rect.size, pygame.SRCALPHA)
        safe_zone_surface.fill((255, 255, 255, 50)) # Blanco con 50 de opacidad (de 255)
        screen.blit(safe_zone_surface, (0, 0))
        pygame.draw.rect(screen, (255, 255, 255), self.safe_zone_rect, 1) # Borde blanco
        
        for button in self.buttons:
            button.draw(screen)

        info_font = pygame.font.SysFont('B612Mono', 24)
        info_text = info_font.render('Click o arrastra para poner/quitar obstaculos. Arrastra los puntos.', True, config.WHITE)
        screen.blit(info_text, (10, 10))
        
        esc_text = info_font.render('Presiona ESC para volver al menu', True, config.WHITE)
        screen.blit(esc_text, (10, 40))

        # Añade esto al final del método draw para mostrar el mensaje
        if self.saved_message:
            font = pygame.font.SysFont('B612Mono', 24)
            text_surf = font.render(self.saved_message, True, config.GREEN)
            text_rect = text_surf.get_rect(center=(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT - 30))
            screen.blit(text_surf, text_rect)

    def save_map(self):
        map_data = self.grid.get_map_data()
        
        # Lógica para encontrar un nombre de archivo único
        base_name = "custom_map"
        extension = ".json"
        path = "assets/maps/"
        i = 1
        while os.path.exists(os.path.join(path, f"{base_name}_{i}{extension}")):
            i += 1
        
        file_name = f"{base_name}_{i}{extension}"
        full_path = os.path.join(path, file_name)
        
        map_manager.save_map_data(map_data, full_path)
        
        # Muestra un mensaje de confirmación
        self.saved_message = f"¡Guardado como {file_name}!"
        self.message_timer = 3 # Muestra el mensaje por 3 segundos
    
    def on_enter(self):
        """Reinicia la escena del editor al entrar."""
        print("Entrando al editor de mapas.")
        self.grid.load_map('assets/maps/default_map.json')