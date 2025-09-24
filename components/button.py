import pygame
import config

class Button:
    def __init__(self, x, y, width, height, text, on_click):
        self.rectangulo = pygame.Rect(x, y, width, height)
        self.texto = text
        self.al_hacer_clic = on_click
        self.fuente = pygame.font.SysFont('B612Mono', 30)
        self.esta_sobre = False

        # Colores
        self.color_normal = config.BLACK
        self.color_sobre = (60, 60, 60) # Gris más claro
        self.color_texto = config.WHITE
    
    # Propiedades para compatibilidad con código existente
    @property
    def rect(self):
        return self.rectangulo
    
    @rect.setter
    def rect(self, valor):
        self.rectangulo = valor
    
    @property
    def text(self):
        return self.texto
    
    @text.setter
    def text(self, valor):
        self.texto = valor
    
    @property
    def on_click(self):
        return self.al_hacer_clic
    
    @on_click.setter
    def on_click(self, valor):
        self.al_hacer_clic = valor
    
    @property
    def font(self):
        return self.fuente
    
    @font.setter
    def font(self, valor):
        self.fuente = valor
    
    @property
    def is_hovered(self):
        return self.esta_sobre
    
    @is_hovered.setter
    def is_hovered(self, valor):
        self.esta_sobre = valor
    
    @property
    def color_hover(self):
        return self.color_sobre
    
    @color_hover.setter
    def color_hover(self, valor):
        self.color_sobre = valor
    
    @property
    def color_text(self):
        return self.color_texto
    
    @color_text.setter
    def color_text(self, valor):
        self.color_texto = valor
    
    # Propiedades adicionales para compatibilidad con el sistema de scroll
    @property
    def x(self):
        return self.rectangulo.x
    
    @x.setter
    def x(self, valor):
        self.rectangulo.x = valor
    
    @property
    def y(self):
        return self.rectangulo.y
    
    @y.setter
    def y(self, valor):
        self.rectangulo.y = valor
    
    @property
    def width(self):
        return self.rectangulo.width
    
    @property
    def height(self):
        return self.rectangulo.height
    
    @property
    def action(self):
        return self.al_hacer_clic
    
    @action.setter
    def action(self, valor):
        self.al_hacer_clic = valor
    
    @property
    def color(self):
        return self.color_normal
    
    @color.setter
    def color(self, valor):
        self.color_normal = valor

    def manejar_evento(self, evento):
        """Maneja un evento individual (mouse)."""
        if evento.type == pygame.MOUSEMOTION:
            self.esta_sobre = self.rectangulo.collidepoint(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if self.esta_sobre and evento.button == 1: # Botón izquierdo del mouse
                self.al_hacer_clic()

    def dibujar(self, pantalla):
        """Dibuja el botón en la pantalla."""
        # Elige el color basado en si el mouse está encima o no
        color = self.color_sobre if self.esta_sobre else self.color_normal
        pygame.draw.rect(pantalla, color, self.rectangulo, border_radius=10)

        # Dibuja el texto centrado en el botón
        superficie_texto = self.fuente.render(self.texto, True, self.color_texto)
        rectangulo_texto = superficie_texto.get_rect(center=self.rectangulo.center)
        pantalla.blit(superficie_texto, rectangulo_texto)
    
    # Propiedades de compatibilidad para métodos
    @property
    def handle_event(self):
        return self.manejar_evento
    
    @property
    def draw(self):
        return self.dibujar