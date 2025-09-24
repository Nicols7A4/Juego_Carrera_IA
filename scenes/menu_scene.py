import pygame
import config
from scenes.scene_base import SceneBase
from components.button import Button # Importamos el componente Button


class MenuScene(SceneBase):
    
    def establecer_siguiente_escena_y_cambiar(self, siguiente_escena):
        self.juego.next_scene_after_map_select = siguiente_escena
        self.juego.switch_scene('map_selection')
    
    def __init__(self, juego):
        super().__init__(juego)
        self.fuente = pygame.font.SysFont('B612Mono', 60) # Usa una fuente que tengas o SysFont
        
        # Centrar botones
        ancho_boton = 300
        alto_boton = 50
        centro_x = config.SCREEN_WIDTH / 2 - ancho_boton / 2

        # Creamos los botones y les asignamos una acción
        self.botones = [
            Button(centro_x, 220, ancho_boton, alto_boton, 'IA vs Humano', 
                   lambda: self.establecer_siguiente_escena_y_cambiar('race')),
            Button(centro_x, 290, ancho_boton, alto_boton, 'IA vs IA', 
                   lambda: self.establecer_siguiente_escena_y_cambiar('ia_vs_ia')), # <-- NUEVO BOTÓN
            Button(centro_x, 360, ancho_boton, alto_boton, 'Modo de Pruebas', 
                   lambda: self.establecer_siguiente_escena_y_cambiar('testing')),
            Button(centro_x, 430, ancho_boton, alto_boton, 'Editor de Mapas', 
                   lambda: self.juego.switch_scene('editor')),
            Button(centro_x, 500, ancho_boton, alto_boton, 'Salir',
                   lambda: setattr(self.juego, 'running', False))
        ]
    
    # Propiedades para compatibilidad con código existente
    @property
    def font(self):
        return self.fuente
    
    @font.setter
    def font(self, valor):
        self.fuente = valor
    
    @property
    def buttons(self):
        return self.botones
    
    @buttons.setter
    def buttons(self, valor):
        self.botones = valor
    
    @property
    def set_next_scene_and_switch(self):
        return self.establecer_siguiente_escena_y_cambiar

    def manejar_eventos(self, eventos):
        for evento in eventos:
            # Pasamos cada evento a cada botón para que lo procese
            for boton in self.botones:
                boton.handle_event(evento)

    def actualizar(self, dt):
        # El menú no tiene lógica que actualizar por sí mismo.
        pass

    def dibujar(self, pantalla):
        pantalla.fill(config.GRAY)
        
        # titulo_texto = self.fuente.render('Pathfinding Race AI', True, config.WHITE)
        titulo_texto = self.fuente.render('PRAI: PathFinding Race AI', True, config.WHITE)
        rectangulo_texto = titulo_texto.get_rect(center=(config.SCREEN_WIDTH / 2, 120))
        pantalla.blit(titulo_texto, rectangulo_texto)

        # Dibujamos cada botón
        for boton in self.botones:
            boton.draw(pantalla)