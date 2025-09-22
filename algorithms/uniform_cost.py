import pygame
import config
from algorithms.pathfinder_base import PathfinderBase

class Nodo:
    """Una clase para representar un nodo en la búsqueda por costo uniforme."""
    def __init__(self, padre=None, posicion=None):
        self.padre = padre
        self.posicion = posicion

        self.g = 0  # Costo desde el inicio hasta el nodo actual
        self.h = 0  # No se usa en costo uniforme, pero se mantiene por compatibilidad
        self.f = 0  # En costo uniforme, f = g (solo costo acumulado)

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

class UniformCostPathfinder(PathfinderBase):
    """Implementa el algoritmo de búsqueda por costo uniforme (Uniform Cost Search)."""

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
        
        # En costo uniforme, inicializamos con costo 0
        self.nodo_inicio.g = 0
        self.nodo_inicio.f = 0
        
        self.lista_abierta = [self.nodo_inicio]
        self.lista_cerrada = []
        self.camino = None
        self.terminado = False
    
    def step(self):
        """Ejecuta una sola iteración del algoritmo de costo uniforme."""
        if not self.lista_abierta or self.terminado:
            return False  # No hay más pasos que dar

        # Encontrar el nodo con el menor costo g (costo acumulado)
        nodo_actual = self.lista_abierta[0]
        indice_actual = 0
        for indice, elemento in enumerate(self.lista_abierta):
            if elemento.g < nodo_actual.g:
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

            # Calcular el costo acumulado
            vecino.g = nodo_actual.g + vecino.move_cost
            vecino.h = 0  # No se usa heurística en costo uniforme
            vecino.f = vecino.g  # En costo uniforme, f = g

            # Verificar si ya está en lista_abierta con un costo menor o igual
            nodo_existente = None
            for nodo_abierto in self.lista_abierta:
                if vecino == nodo_abierto:
                    nodo_existente = nodo_abierto
                    break
            
            if nodo_existente:
                # Si encontramos un camino mejor al mismo nodo, actualizar
                if vecino.g < nodo_existente.g:
                    nodo_existente.g = vecino.g
                    nodo_existente.f = vecino.f
                    nodo_existente.padre = vecino.padre
            else:
                # Si no está en lista_abierta, agregarlo
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
    def _process_neighbors(self):
        return self._procesar_vecinos
    
    @property
    def _reconstruct_path(self):
        return self._reconstruir_camino