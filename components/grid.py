import pygame
import config
from utils import map_manager # Importamos nuestro gestor de mapas


class Grid:
    def __init__(self, cols=None, rows=None):
        # Calcula el número de columnas y filas basado en el tamaño de la pantalla y de la celda
        if cols and rows:
            self.columnas = cols
            self.filas = rows
        else:
            self.columnas = config.SCREEN_WIDTH // config.CELL_SIZE
            self.filas = config.SCREEN_HEIGHT // config.CELL_SIZE
        
        # El estado se inicializará al limpiar o cargar
        self.estados = []
        self.posicion_inicio = None
        self.posicion_fin = None
        self.limpiar() # Asegura un estado inicial limpio
    
    # Propiedades para compatibilidad con código existente
    @property
    def cols(self):
        return self.columnas
    
    @cols.setter
    def cols(self, valor):
        self.columnas = valor
    
    @property
    def rows(self):
        return self.filas
    
    @rows.setter
    def rows(self, valor):
        self.filas = valor
    
    @property
    def states(self):
        return self.estados
    
    @states.setter
    def states(self, valor):
        self.estados = valor
    
    @property
    def start_pos(self):
        return self.posicion_inicio
    
    @start_pos.setter
    def start_pos(self, valor):
        self.posicion_inicio = valor
    
    @property
    def end_pos(self):
        return self.posicion_fin
    
    @end_pos.setter
    def end_pos(self, valor):
        self.posicion_fin = valor
        
    def cargar_mapa(self, ruta_archivo):
        """Limpia la cuadrícula y carga un nuevo mapa, validando cada elemento."""
        # 1. Empieza con una cuadrícula completamente vacía
        self.estados = [[config.STATE_FREE for _ in range(self.filas)] for _ in range(self.columnas)]
        self.posicion_inicio = None
        self.posicion_fin = None

        datos_mapa = map_manager.load_map_data(ruta_archivo)
        if not datos_mapa:
            self.limpiar() # Si el archivo no existe, carga un mapa por defecto
            return

        # 2. Carga los datos del archivo, validando que quepan en la cuadrícula actual
        datos_posicion_inicio = tuple(datos_mapa["start"])
        if 0 <= datos_posicion_inicio[0] < self.columnas and 0 <= datos_posicion_inicio[1] < self.filas:
            self.posicion_inicio = datos_posicion_inicio
            self.estados[self.posicion_inicio[0]][self.posicion_inicio[1]] = config.STATE_START

        datos_posicion_fin = tuple(datos_mapa["end"])
        if 0 <= datos_posicion_fin[0] < self.columnas and 0 <= datos_posicion_fin[1] < self.filas:
            self.posicion_fin = datos_posicion_fin
            self.estados[self.posicion_fin[0]][self.posicion_fin[1]] = config.STATE_END

        if "obstacles" in datos_mapa:
            for obstaculo in datos_mapa["obstacles"]:
                if 0 <= obstaculo[0] < self.columnas and 0 <= obstaculo[1] < self.filas:
                    self.estados[obstaculo[0]][obstaculo[1]] = config.STATE_OBSTACLE

    # --- NUEVOS MÉTODOS PARA EL EDITOR ---
    def obtener_celda_desde_posicion(self, pos):
        """Convierte coordenadas de píxeles a coordenadas de la cuadrícula."""
        grilla_x = pos[0] // config.CELL_SIZE
        grilla_y = pos[1] // config.CELL_SIZE
        if 0 <= grilla_x < self.columnas and 0 <= grilla_y < self.filas:
            return (grilla_x, grilla_y)
        return None
    
    def alternar_obstaculo(self, posicion_grilla):
        """Cambia el estado de una celda entre libre y obstáculo."""
        x, y = posicion_grilla
        # No se puede poner un obstáculo en el inicio o fin
        if self.estados[x][y] == config.STATE_START or self.estados[x][y] == config.STATE_END:
            return
        
        if self.estados[x][y] == config.STATE_FREE:
            self.estados[x][y] = config.STATE_OBSTACLE
        else:
            self.estados[x][y] = config.STATE_FREE
            
    def mover_punto(self, tipo_punto, nueva_pos):
        """Mueve el punto de inicio o fin a una nueva posición."""
        x, y = nueva_pos
        # No se puede mover a un obstáculo o encima del otro punto
        if self.estados[x][y] == config.STATE_OBSTACLE or nueva_pos == self.posicion_fin or nueva_pos == self.posicion_inicio:
            return

        if tipo_punto == 'start':
            # Borra la posición anterior y actualiza la nueva
            self.estados[self.posicion_inicio[0]][self.posicion_inicio[1]] = config.STATE_FREE
            self.posicion_inicio = nueva_pos
            self.estados[x][y] = config.STATE_START
        elif tipo_punto == 'end':
            self.estados[self.posicion_fin[0]][self.posicion_fin[1]] = config.STATE_FREE
            self.posicion_fin = nueva_pos
            self.estados[x][y] = config.STATE_END
    
    def limpiar(self):
        """Limpia el mapa y coloca los puntos de inicio/fin en posiciones por defecto seguras."""
        self.estados = [[config.STATE_FREE for _ in range(self.filas)] for _ in range(self.columnas)]
        
        # Coloca los puntos de inicio y fin en posiciones por defecto relativas al tamaño actual
        inicio_x = 1
        fin_x = self.columnas - 2
        posicion_y = self.filas // 2

        if 0 <= inicio_x < self.columnas:
            self.posicion_inicio = (inicio_x, posicion_y)
            self.estados[self.posicion_inicio[0]][self.posicion_inicio[1]] = config.STATE_START
        
        if 0 <= fin_x < self.columnas:
            self.posicion_fin = (fin_x, posicion_y)
            self.estados[self.posicion_fin[0]][self.posicion_fin[1]] = config.STATE_END

    def obtener_datos_mapa(self):
        """Exporta el estado actual del mapa a un diccionario."""
        obstaculos = []
        for x in range(self.columnas):
            for y in range(self.filas):
                if self.estados[x][y] == config.STATE_OBSTACLE:
                    obstaculos.append([x, y])
        return {
            "start": list(self.posicion_inicio),
            "end": list(self.posicion_fin),
            "obstacles": obstaculos
        }

    # --------------------------

    def dibujar(self, pantalla, desplazamiento=(0, 0)):
        """Dibuja las celdas y las líneas de la cuadrícula."""
        dx, dy = desplazamiento # Desplazamiento X y Desplazamiento Y
        for x in range(self.columnas):
            for y in range(self.filas):
                # Dibuja el rectángulo de la celda con su color de estado
                estado = self.estados[x][y]
                color = config.STATE_COLORS.get(estado, config.GRAY)
                rectangulo = pygame.Rect(x * config.CELL_SIZE + dx, y * config.CELL_SIZE + dy, config.CELL_SIZE, config.CELL_SIZE)
                pygame.draw.rect(pantalla, color, rectangulo)

        # Dibuja las líneas de la cuadrícula encima
        for linea_x in range(self.columnas + 1):
            # Dibuja líneas verticales
            posicion_inicio = (linea_x * config.CELL_SIZE + dx, dy)
            posicion_fin = (linea_x * config.CELL_SIZE + dx, self.filas * config.CELL_SIZE + dy)
            pygame.draw.line(pantalla, config.BLACK, posicion_inicio, posicion_fin)
        
        for linea_y in range(self.filas + 1):
            # Dibuja líneas horizontales
            posicion_inicio = (dx, linea_y * config.CELL_SIZE + dy)
            posicion_fin = (self.columnas * config.CELL_SIZE + dx, linea_y * config.CELL_SIZE + dy)
            pygame.draw.line(pantalla, config.BLACK, posicion_inicio, posicion_fin)
    
    # Propiedades de compatibilidad para métodos
    @property
    def load_map(self):
        return self.cargar_mapa
    
    @property
    def get_cell_from_pos(self):
        return self.obtener_celda_desde_posicion
    
    @property
    def toggle_obstacle(self):
        return self.alternar_obstaculo
    
    @property
    def move_point(self):
        return self.mover_punto
    
    @property
    def clear(self):
        return self.limpiar
    
    @property
    def get_map_data(self):
        return self.obtener_datos_mapa
    
    @property
    def draw(self):
        return self.dibujar
