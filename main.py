import pygame
import sys
import config # Importamos nuestro archivo de configuración
# from components.grid import Grid # <-- 1. IMPORTAMOS LA CLASE GRID
# Ya no importamos Grid aquí, lo hará la escena que lo necesite
from scenes.menu_scene import MenuScene # Importamos nuestra nueva escena
from scenes.race_scene import RaceScene
from scenes.testing_scene import TestingScene
from scenes.editor_scene import EditorScene
from scenes.map_selection_scene import MapSelectionScene
from scenes.ia_vs_ia_scene import IAvsIAScene
from utils import map_manager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.map_manager = map_manager
        
        # Gestor de escenas
        self.scenes = {
            'menu': MenuScene(self),
            'race': RaceScene(self),
            'testing': TestingScene(self),
            'editor': EditorScene(self),
            'map_selection': MapSelectionScene(self),
            'ia_vs_ia': IAvsIAScene(self) # <-- REGISTRAR
        }
        self.current_scene = self.scenes['menu']
        
        # Variables para gestionar el flujo
        self.selected_map = 'assets/maps/default_map.json'
        self.next_scene_after_map_select = None

    def run(self):
        """El bucle principal ahora delega a la escena activa."""
        while self.running:
            # Pasamos la lista de eventos a la escena para que los maneje
            dt = self.clock.tick(config.FPS) / 1000.0 # <-- CALCULA EL DELTA TIME

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.current_scene.handle_events(events)
            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

        # pygame.quit()
        # sys.exit()
        
    def switch_scene(self, scene_name):
        """Función para cambiar entre escenas."""
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            self.current_scene.on_enter()
        else:
            print(f"Error: La escena '{scene_name}' no existe.")

    # def handle_events(self):
    #     """Maneja los eventos de entrada (teclado, mouse)."""
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             self.running = False

    # def update(self):
    #     """Actualiza la lógica del juego."""
    #     # Por ahora no hace nada
    #     pass

    # def draw(self):
    #     """Dibuja todo en la pantalla."""
    #     self.screen.fill(config.GRAY)
    #     self.grid.draw(self.screen) # <-- 3. DIBUJAMOS LA GRID EN LA PANTALLA
    #     pygame.display.flip() # Actualiza la pantalla completa para mostrar lo dibujado

# --- Punto de entrada del programa ---
if __name__ == '__main__':
    game = Game()
    game.run()