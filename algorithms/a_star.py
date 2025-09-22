import pygame # Lo necesitamos para dibujar los textos
import config
from algorithms.pathfinder_base import PathfinderBase

class Nodo:
    """Una clase para representar un nodo en la búsqueda A*."""
    def __init__(self, padre=None, posicion=None):
        self.padre = padre
        self.posicion = posicion

        self.g = 0  # Costo desde el inicio hasta el nodo actual
        self.h = 0  # Heurística: costo estimado desde el nodo actual hasta el final
        self.f = 0  # Costo total (g + h)

    def __eq__(self, otro):
        return self.posicion == otro.posicion
    
    # Propiedades para compatibilidad con código existente
    @property
    def parent(self):
        return self.padre
    
    @parent.setter
    def parent(self, valor):
        self.padre = valor
    
    @property
    def position(self):
        return self.posicion
    
    @position.setter
    def position(self, valor):
        self.posicion = valor

class AStarPathfinder(PathfinderBase):
    """Implementa el algoritmo de búsqueda de caminos A*."""

    def __init__(self, cuadricula, permitir_diagonal=False):
        super().__init__(cuadricula, permitir_diagonal)
        self.lista_abierta = []
        self.lista_cerrada = []
        self.nodo_inicio = None
        self.nodo_final = None
        self.camino = None
        self.terminado = False
    
    # Propiedades para compatibilidad con código existente
    @property
    def open_list(self):
        return self.lista_abierta
    
    @open_list.setter
    def open_list(self, valor):
        self.lista_abierta = valor
    
    @property
    def closed_list(self):
        return self.lista_cerrada
    
    @closed_list.setter
    def closed_list(self, valor):
        self.lista_cerrada = valor
    
    @property
    def path(self):
        return self.camino
    
    @path.setter
    def path(self, valor):
        self.camino = valor
    
    @property
    def is_finished(self):
        return self.terminado
    
    @is_finished.setter
    def is_finished(self, valor):
        self.terminado = valor
    
    def initialize_search(self, start_pos, end_pos):
        """Método de compatibilidad - llama a inicializar_busqueda."""
        return self.inicializar_busqueda(start_pos, end_pos)
    
    def step(self):
        """Método de compatibilidad - llama a paso."""
        return self.paso()
    
    def find_path(self, start_pos, end_pos):
        """Método de compatibilidad - llama a encontrar_camino."""
        return self.encontrar_camino(start_pos, end_pos)
    
    def inicializar_busqueda(self, pos_inicio, pos_final):
        """Prepara el algoritmo para una nueva búsqueda."""
        self.nodo_inicio = Nodo(None, pos_inicio)
        self.nodo_final = Nodo(None, pos_final)
        
        self.lista_abierta = [self.nodo_inicio]
        self.lista_cerrada = []
        self.camino = None
        self.terminado = False
        self.iteraciones = 0  # Reiniciar contador de iteraciones
    
    def paso(self):
        """Ejecuta una sola iteración del algoritmo A*."""
        if not self.lista_abierta or self.terminado:
            return False # No hay más pasos que dar

        self.iteraciones += 1  # Incrementar contador de iteraciones

        # Encontrar el nodo con el menor costo f
        nodo_actual = self.lista_abierta[0]
        indice_actual = 0
        for indice, elemento in enumerate(self.lista_abierta):
            if elemento.f < nodo_actual.f:
                nodo_actual = elemento
                indice_actual = indice

        # Mover a la lista cerrada
        self.lista_abierta.pop(indice_actual)
        self.lista_cerrada.append(nodo_actual)

        # Meta encontrada
        if nodo_actual == self.nodo_final:
            self.camino = self._reconstruir_camino(nodo_actual)
            self.terminado = True
            return True

        # Generar y procesar vecinos
        self._procesar_vecinos(nodo_actual)
        return True
    
    def _procesar_vecinos(self, nodo_actual):
        """Procesa los vecinos del nodo actual usando la funcionalidad de la clase base."""
        vecinos_con_costos = self.get_neighbors_and_costs(nodo_actual.posicion)
        vecinos = []
        
        for pos_vecino, costo_movimiento in vecinos_con_costos:
            vecino = Nodo(nodo_actual, pos_vecino)
            vecino.costo_movimiento = costo_movimiento
            vecinos.append(vecino)

        for vecino in vecinos:
            if vecino in self.lista_cerrada:
                continue

            vecino.g = nodo_actual.g + vecino.costo_movimiento
            vecino.h = ((vecino.posicion[0] - self.nodo_final.posicion[0]) ** 2) + \
                       ((vecino.posicion[1] - self.nodo_final.posicion[1]) ** 2)
            vecino.f = vecino.g + vecino.h

            if any(nodo_abierto for nodo_abierto in self.lista_abierta if vecino == nodo_abierto and vecino.g >= nodo_abierto.g):
                continue
            
            self.lista_abierta.append(vecino)

    def encontrar_camino(self, pos_inicio, pos_final):
        """Ejecuta el algoritmo completo de una vez."""
        self.inicializar_busqueda(pos_inicio, pos_final)
        while self.lista_abierta and not self.terminado:
            self.paso()
        return self.camino

    def _reconstruir_camino(self, nodo_actual):
        # ... (Este método no cambia)
        camino = []
        actual = nodo_actual
        while actual is not None:
            camino.append(actual.posicion)
            actual = actual.padre
        return camino[::-1]

