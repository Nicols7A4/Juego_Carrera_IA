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
        # La carga de mapas ya no se hace aquí

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
            button_height = 50
            center_x = config.SCREEN_WIDTH / 2 - button_width / 2
            start_y = 200

            for i, map_file in enumerate(map_files):
                map_path = os.path.join(maps_path, map_file)
                action = lambda path=map_path: self.select_map_and_proceed(path)
                button = Button(center_x, start_y + i * 70, button_width, button_height, map_file, action)
                self.buttons.append(button)

        except FileNotFoundError:
            print(f"Error: La carpeta '{maps_path}' no fue encontrada.")

    def select_map_and_proceed(self, map_path):
        """Guarda el mapa seleccionado y cambia a la escena que corresponda."""
        self.game.selected_map = map_path
        if self.game.next_scene_after_map_select:
            self.game.switch_scene(self.game.next_scene_after_map_select)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.switch_scene('menu')
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(config.GRAY)
        
        title_text = self.font_title.render('Selecciona un Mapa', True, config.WHITE)
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH / 2, 100))
        screen.blit(title_text, title_rect)
        
        for button in self.buttons:
            button.draw(screen)