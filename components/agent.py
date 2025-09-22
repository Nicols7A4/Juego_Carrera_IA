import pygame
import config

class Agent:
    def __init__(self, start_pos, color, is_human=False):
        self.posicion = start_pos
        self.color = color
        self.es_humano = is_human
        self.camino = [start_pos] # Para la IA, será el camino de A*. Para el humano, su rastro.
        self.pasos = 0
        self.terminado = False
    
    # Propiedades para compatibilidad con código existente
    @property
    def position(self):
        return self.posicion
    
    @position.setter
    def position(self, valor):
        self.posicion = valor
    
    @property
    def is_human(self):
        return self.es_humano
    
    @is_human.setter
    def is_human(self, valor):
        self.es_humano = valor
    
    @property
    def path(self):
        return self.camino
    
    @path.setter
    def path(self, valor):
        self.camino = valor
    
    @property
    def steps(self):
        return self.pasos
    
    @steps.setter
    def steps(self, valor):
        self.pasos = valor
    
    @property
    def finished(self):
        return self.terminado
    
    @finished.setter
    def finished(self, valor):
        self.terminado = valor

    def dibujar(self, pantalla, desplazamiento=(0, 0)):
        """Dibuja el agente en la cuadrícula."""
        dx, dy = desplazamiento
        x, y = self.posicion
        # rect = pygame.Rect(x * config.CELL_SIZE, y * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
        # Dibuja un círculo dentro de la celda para diferenciarlo
        centro_x = x * config.CELL_SIZE + config.CELL_SIZE // 2 + dx
        centro_y = y * config.CELL_SIZE + config.CELL_SIZE // 2 + dy
        pygame.draw.circle(pantalla, self.color, (centro_x, centro_y), config.CELL_SIZE // 2 - 5)

    def mover(self, dx, dy, grilla):
        """Mueve al agente (usado por el jugador) y valida la posición."""
        if self.terminado: return

        nueva_x = self.posicion[0] + dx
        nueva_y = self.posicion[1] + dy

        # Validar que el movimiento está dentro de los límites y no es un obstáculo
        if 0 <= nueva_x < grilla.cols and 0 <= nueva_y < grilla.rows:
            if grilla.states[nueva_x][nueva_y] != config.STATE_OBSTACLE:
                self.posicion = (nueva_x, nueva_y)
                self.pasos += 1
                self.camino.append(self.posicion)
    
    # Propiedades de compatibilidad para métodos
    @property
    def draw(self):
        return self.dibujar
    
    @property
    def move(self):
        return self.mover