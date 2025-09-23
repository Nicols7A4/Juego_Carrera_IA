import pygame
import config
from algorithms.pathfinder_base import PathfinderBase

class Nodo:
    """Una clase para representar un nodo en el algoritmo de Dijkstra."""
    def __init__(self, padre=None, posicion=None):
        self.padre = padre      # Nodo desde el cual llegamos (para reconstruir camino)
        self.posicion = posicion # Coordenadas (x, y) del nodo en la grilla
        
        # Costos en Dijkstra:
        self.g = 0  # Costo real acumulado desde el inicio (PRINCIPAL en Dijkstra)
        self.h = 0  # No se usa heurística en Dijkstra (siempre 0)
        self.f = 0  # En Dijkstra, f = g (solo costo real, sin estimación)
        
    def __eq__(self, otro):
        """Dos nodos son iguales si tienen la misma posición."""
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

class DijkstraPathfinder(PathfinderBase):
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
        """Prepara el algoritmo Dijkstra para una nueva búsqueda."""
        # Crear nodos de inicio y objetivo
        self.nodo_inicio = Nodo(None, start_pos)
        self.nodo_fin = Nodo(None, end_pos)
        
        # Lista abierta: nodos por evaluar (empezamos con el nodo inicial)
        self.lista_abierta = [self.nodo_inicio]
        # Lista cerrada: nodos con distancia mínima ya calculada
        self.lista_cerrada = []
        self.camino = None
        self.terminado = False
        self.iteraciones = 0  # Reiniciar contador de iteraciones
    
    def step(self):
        """Ejecuta una sola iteración del algoritmo Dijkstra."""
        # Verificar si hay nodos por evaluar o si ya terminamos
        if not self.lista_abierta or self.terminado:
            return False # No hay más pasos que dar

        self.iteraciones += 1  # Incrementar contador de iteraciones

        # PASO 1: Encontrar el nodo con menor distancia acumulada (costo g)
        # En Dijkstra seleccionamos siempre el nodo con menor costo real
        nodo_actual = self.lista_abierta[0]
        indice_actual = 0
        for indice, elemento in enumerate(self.lista_abierta):
            if elemento.f < nodo_actual.f:  # f = g en Dijkstra (sin heurística)
                nodo_actual = elemento
                indice_actual = indice

        # PASO 2: Mover nodo a lista cerrada (distancia mínima confirmada)
        self.lista_abierta.pop(indice_actual)
        self.lista_cerrada.append(nodo_actual)

        # PASO 3: Verificar si hemos llegado al objetivo
        if nodo_actual == self.nodo_fin:
            self.camino = self._reconstruir_camino(nodo_actual)
            self.terminado = True
            self.camino = self._reconstruir_camino(nodo_actual)
            self.terminado = True
            return True

        # PASO 4: Expandir vecinos y actualizar distancias
        self._procesar_vecinos(nodo_actual)
        return True

    def _procesar_vecinos(self, nodo_actual):
        """Procesa los vecinos del nodo actual - Algoritmo de relajación de Dijkstra."""
        # Obtener vecinos válidos y sus costos de movimiento
        vecinos_con_costos = self.get_neighbors_and_costs(nodo_actual.posicion)
        vecinos = []
        
        # Crear nodos vecinos con información de costo
        for posicion_vecino, costo_movimiento in vecinos_con_costos:
            vecino = Nodo(nodo_actual, posicion_vecino)
            vecino.move_cost = costo_movimiento
            vecinos.append(vecino)
        
        # Evaluar cada vecino (proceso de relajación)
        for vecino in vecinos:
            # Ignorar vecinos que ya tienen su distancia mínima calculada
            if vecino in self.lista_cerrada:
                continue

            # Calcular nueva distancia a través del nodo actual
            vecino.g = nodo_actual.g + vecino.move_cost  # Distancia acumulada
            vecino.h = 0  # Dijkstra NO usa heurística (búsqueda ciega)
            vecino.f = vecino.g + vecino.h  # f = g en Dijkstra

            # Si ya existe un camino más corto a este vecino, ignorarlo
            if any(nodo_abierto for nodo_abierto in self.lista_abierta if vecino == nodo_abierto and vecino.g >= nodo_abierto.g):
                continue
            
            # Agregar vecino para evaluación futura
            self.lista_abierta.append(vecino)
    
    # Propiedades de compatibilidad para métodos
    @property
    def _process_neighbors(self):
        return self._procesar_vecinos
    
    @property
    def _reconstruct_path(self):
        return self._reconstruir_camino
    
    # ... (el resto de la clase es idéntico a A*)
    def buscar_camino(self, posicion_inicio, posicion_fin):
        """Ejecuta el algoritmo completo de una vez."""
        self.initialize_search(posicion_inicio, posicion_fin)
        while self.lista_abierta and not self.terminado:
            self.step()
        return self.camino

    def _reconstruir_camino(self, nodo_actual):
        camino = []
        actual = nodo_actual
        while actual is not None:
            camino.append(actual.posicion)
            actual = actual.padre
        return camino[::-1]
    
    # Propiedades de compatibilidad para métodos
    @property
    def find_path(self):
        return self.buscar_camino