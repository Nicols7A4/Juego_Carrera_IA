import pygame
import config
from algorithms.pathfinder_base import PathfinderBase

class Nodo:
    """Una clase para representar un nodo en la búsqueda Voraz."""
    def __init__(self, padre=None, posicion=None):
        self.padre = padre
        self.posicion = posicion

        self.g = 0  # Costo desde el inicio hasta el nodo actual (no se usa en voraz)
        self.h = 0  # Heurística: costo estimado desde el nodo actual hasta el final
        self.f = 0  # En voraz, f = h (solo heurística)

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

class GreedyPathfinder(PathfinderBase):
    """Implementa el algoritmo de búsqueda voraz (greedy) basado solo en heurística."""

    def __init__(self, grid, allow_diagonal=False):
        super().__init__(grid, allow_diagonal)
        self.lista_abierta = []
        self.lista_cerrada = []
        self.nodo_inicio = None
        self.nodo_fin = None
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
    def start_node(self):
        return self.nodo_inicio
    
    @start_node.setter
    def start_node(self, valor):
        self.nodo_inicio = valor
    
    @property
    def end_node(self):
        return self.nodo_fin
    
    @end_node.setter
    def end_node(self, valor):
        self.nodo_fin = valor
    
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
        """Prepara el algoritmo para una nueva búsqueda."""
        self.nodo_inicio = Nodo(None, start_pos)
        self.nodo_fin = Nodo(None, end_pos)
        
        # Calcular heurística inicial
        self.nodo_inicio.h = self._calcular_heuristica(self.nodo_inicio.posicion, end_pos)
        self.nodo_inicio.f = self.nodo_inicio.h  # En voraz, f = h
        
        self.lista_abierta = [self.nodo_inicio]
        self.lista_cerrada = []
        self.camino = None
        self.terminado = False
        self.iteraciones = 0  # Reiniciar contador de iteraciones
    
    def step(self):
        """Ejecuta una sola iteración del algoritmo Voraz."""
        if not self.lista_abierta or self.terminado:
            return False  # No hay más pasos que dar

        self.iteraciones += 1  # Incrementar contador de iteraciones

        # Encontrar el nodo con la menor heurística (f = h)
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
        if nodo_actual == self.nodo_fin:
            self.camino = self._reconstruir_camino(nodo_actual)
            self.terminado = True
            return True

        # Generar y procesar vecinos
        self._procesar_vecinos(nodo_actual)
        return True
    
    def _calcular_heuristica(self, pos1, pos2):
        """Calcula la distancia euclidiana como heurística."""
        return ((pos1[0] - pos2[0]) ** 2) + ((pos1[1] - pos2[1]) ** 2)
    
    def _procesar_vecinos(self, nodo_actual):
        """Procesa los vecinos del nodo actual usando la funcionalidad de la clase base."""
        vecinos_con_costos = self.get_neighbors_and_costs(nodo_actual.posicion)
        vecinos = []
        
        for posicion_vecino, costo_movimiento in vecinos_con_costos:
            vecino = Nodo(nodo_actual, posicion_vecino)
            vecino.move_cost = costo_movimiento
            vecinos.append(vecino)

        for vecino in vecinos:
            # Si ya está en la lista cerrada, ignorar
            if vecino in self.lista_cerrada:
                continue

            # Calcular solo la heurística (característica del algoritmo voraz)
            vecino.h = self._calcular_heuristica(vecino.posicion, self.nodo_fin.posicion)
            vecino.f = vecino.h  # En voraz, f = h (solo heurística)
            vecino.g = nodo_actual.g + vecino.move_cost  # Mantener registro del costo real para reconstrucción

            # Si ya está en lista_abierta con mejor heurística, ignorar
            if any(nodo_abierto for nodo_abierto in self.lista_abierta 
                   if vecino == nodo_abierto and vecino.f >= nodo_abierto.f):
                continue
            
            self.lista_abierta.append(vecino)

    def buscar_camino(self, posicion_inicio, posicion_fin):
        """Ejecuta el algoritmo completo de una vez."""
        self.initialize_search(posicion_inicio, posicion_fin)
        while self.lista_abierta and not self.terminado:
            if not self.step():
                break
        return self.camino

    def _reconstruir_camino(self, nodo_actual):
        """Reconstruye el camino desde el nodo final hasta el inicial."""
        camino = []
        actual = nodo_actual
        while actual is not None:
            camino.append(actual.posicion)
            actual = actual.padre
        return camino[::-1]  # Invertir para obtener el camino desde inicio a fin
    
    # Propiedades de compatibilidad para métodos
    @property
    def find_path(self):
        return self.buscar_camino
    
    @property
    def _calculate_heuristic(self):
        return self._calcular_heuristica
    
    @property
    def _process_neighbors(self):
        return self._procesar_vecinos
    
    @property
    def _reconstruct_path(self):
        return self._reconstruir_camino