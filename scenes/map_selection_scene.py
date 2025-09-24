import pygame
import config
import os
from scenes.scene_base import SceneBase
from components.button import Button

class MapSelectionScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.font_title = pygame.font.SysFont('B612Mono', 50)
        
        # Sistema de scroll
        self.scroll_y = 0  # Desplazamiento vertical
        self.scroll_speed = 30  # Velocidad de scroll
        self.visible_area_top = 150  # Área visible superior
        self.visible_area_bottom = config.SCREEN_HEIGHT - 50  # Área visible inferior
        self.button_height = 50
        self.button_spacing = 70
        self.max_scroll = 0  # Se calculará en load_maps()

    def on_enter(self):
        """Se ejecuta cada vez que entramos, actualizando la lista de mapas."""
        self.load_maps() # <-- LA LÓGICA AHORA VIVE AQUÍ

    def load_maps(self):
        """Escanea la carpeta de mapas y crea botones para cada uno."""
        self.buttons = []
        maps_path = 'assets/maps/'
        try:
            # Ordena los archivos para una visualización consistente
            map_files = sorted([f for f in os.listdir(maps_path) if f.endswith('.json')])
            
            button_width = 400
            center_x = config.SCREEN_WIDTH / 2 - button_width / 2
            start_y = 200

            for i, map_file in enumerate(map_files):
                map_path = os.path.join(maps_path, map_file)
                action = lambda path=map_path: self.select_map_and_proceed(path)
                button_y = start_y + i * self.button_spacing
                button = Button(center_x, button_y, button_width, self.button_height, map_file, action)
                self.buttons.append(button)
            
            # Calcular el scroll máximo necesario
            if len(self.buttons) > 0:
                last_button_bottom = start_y + (len(self.buttons) - 1) * self.button_spacing + self.button_height
                visible_height = self.visible_area_bottom - self.visible_area_top
                self.max_scroll = max(0, last_button_bottom - self.visible_area_bottom + 20)  # +20 para margen
            else:
                self.max_scroll = 0
            
            # Reiniciar scroll al cargar mapas
            self.scroll_y = 0

        except FileNotFoundError:
            print(f"Error: La carpeta '{maps_path}' no fue encontrada.")

    def select_map_and_proceed(self, map_path):
        """Guarda el mapa seleccionado y cambia a la escena que corresponda."""
        self.game.selected_map = map_path
        if self.game.next_scene_after_map_select:
            self.game.switch_scene(self.game.next_scene_after_map_select)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.switch_scene('menu')
                elif event.key == pygame.K_UP:
                    # Scroll hacia arriba
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.key == pygame.K_DOWN:
                    # Scroll hacia abajo
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Rueda del mouse hacia arriba
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.button == 5:  # Rueda del mouse hacia abajo
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
            
            # Manejar eventos en botones (solo los visibles)
            self._handle_button_events(event)

    def _handle_button_events(self, event):
        """Maneja eventos de botones ajustando por el scroll."""
        for button in self.buttons:
            # Calcular posición visible del botón
            button_top = button.rect.y - self.scroll_y
            button_bottom = button_top + button.rect.height
            
            # Verificar si el botón está en el área visible
            if (button_top < self.visible_area_bottom and 
                button_bottom > self.visible_area_top):
                
                # Crear un evento modificado para la posición ajustada
                if event.type == pygame.MOUSEMOTION:
                    # Ajustar posición del mouse para el botón desplazado
                    adjusted_pos = (event.pos[0], event.pos[1] + self.scroll_y - self.visible_area_top)
                    adjusted_event = pygame.event.Event(pygame.MOUSEMOTION, pos=adjusted_pos)
                    button.handle_event(adjusted_event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Verificar si el click está dentro del área visible del botón
                    mouse_x, mouse_y = event.pos
                    if (button.rect.x <= mouse_x <= button.rect.x + button.rect.width and
                        button_top <= mouse_y <= button_bottom and
                        self.visible_area_top <= mouse_y <= self.visible_area_bottom):
                        button.handle_event(event)
            else:
                # Si el botón no está visible, asegurar que no esté en hover
                button.is_hovered = False

    def update(self, dt):
        # Actualizar estado de hover para todos los botones
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            # Calcular posición visible del botón
            button_top = button.rect.y - self.scroll_y
            button_bottom = button_top + button.rect.height
            
            # Solo permitir hover si el botón está visible
            if (button_top < self.visible_area_bottom and 
                button_bottom > self.visible_area_top and
                self.visible_area_top <= mouse_pos[1] <= self.visible_area_bottom):
                
                # Verificar hover en la posición ajustada
                if (button.rect.x <= mouse_pos[0] <= button.rect.x + button.rect.width and
                    button_top <= mouse_pos[1] <= button_bottom):
                    button.is_hovered = True
                else:
                    button.is_hovered = False
            else:
                button.is_hovered = False

    def draw(self, screen):
        screen.fill(config.GRAY)
        
        # Título (siempre visible)
        title_text = self.font_title.render('Selecciona un Mapa', True, config.WHITE)
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH / 2, 100))
        screen.blit(title_text, title_rect)
        
        # Crear superficie de recorte para el área de scroll
        visible_height = self.visible_area_bottom - self.visible_area_top
        scroll_surface = pygame.Surface((config.SCREEN_WIDTH, visible_height))
        scroll_surface.fill(config.GRAY)
        
        # Dibujar botones en la superficie de scroll
        for button in self.buttons:
            button_y_in_scroll = button.rect.y - self.scroll_y - self.visible_area_top
            
            # Solo dibujar si está dentro del área visible
            if (-button.rect.height <= button_y_in_scroll <= visible_height):
                # Crear una copia temporal del botón con posición ajustada
                temp_button = Button(button.rect.x, button_y_in_scroll, button.rect.width, button.rect.height, button.text, button.on_click)
                temp_button.color_normal = button.color_normal
                temp_button.color_text = button.color_text
                temp_button.color_hover = button.color_hover
                temp_button.is_hovered = button.is_hovered  # Copiar estado de hover
                temp_button.draw(scroll_surface)
        
        # Dibujar la superficie de scroll en la pantalla
        screen.blit(scroll_surface, (0, self.visible_area_top))
        
        # Indicadores de scroll si es necesario
        if self.max_scroll > 0:
            # Barra de scroll a la derecha
            scrollbar_x = config.SCREEN_WIDTH - 20
            scrollbar_width = 15
            scrollbar_height = visible_height
            scrollbar_y = self.visible_area_top
            
            # Fondo de la barra de scroll
            pygame.draw.rect(screen, (100, 100, 100), 
                           (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
            
            # Indicador de posición
            indicator_height = max(20, int(scrollbar_height * (visible_height / (visible_height + self.max_scroll))))
            indicator_y = scrollbar_y + int((self.scroll_y / self.max_scroll) * (scrollbar_height - indicator_height))
            pygame.draw.rect(screen, config.WHITE, 
                           (scrollbar_x + 2, indicator_y, scrollbar_width - 4, indicator_height))
            
            # Instrucciones de scroll
            font_small = pygame.font.SysFont('Arial', 16)
            instructions = font_small.render('↑↓ o rueda del mouse para desplazar', True, config.WHITE)
            screen.blit(instructions, (10, config.SCREEN_HEIGHT - 30))