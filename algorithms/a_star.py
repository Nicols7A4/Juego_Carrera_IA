import pygame # Lo necesitamos para dibujar los textos
import config
from algorithms.pathfinder_base import PathfinderBase

class Nodo:
    """Una clase para representar un nodo en la búsqueda A*."""
    def __init__(self, padre=None, posicion=None):
        self.padre = padre      # Nodo desde el cual llegamos (para reconstruir camino)
        self.posicion = posicion # Coordenadas (x, y) del nodo en la grilla

        # Costos fundamentales de A*:
        self.g = 0  # Costo real desde el inicio hasta este nodo
        self.h = 0  # Heurística: estimación del costo desde este nodo al objetivo
        self.f = 0  # Costo total estimado (f = g + h) - usado para seleccionar nodos

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
        # Crear nodos de inicio y objetivo
        self.nodo_inicio = Nodo(None, pos_inicio)
        self.nodo_final = Nodo(None, pos_final)
        
        # Lista abierta: nodos por evaluar (empezamos con el nodo inicial)
        self.lista_abierta = [self.nodo_inicio]
        # Lista cerrada: nodos ya evaluados (inicialmente vacía)
        self.lista_cerrada = []
        self.camino = None
        self.terminado = False
        self.iteraciones = 0  # Reiniciar contador de iteraciones
    
    def paso(self):
        """Ejecuta una sola iteración del algoritmo A*."""
        # Verificar si hay nodos por evaluar o si ya terminamos
        if not self.lista_abierta or self.terminado:
            return False # No hay más pasos que dar

        self.iteraciones += 1  # Incrementar contador de iteraciones

        # PASO 1: Encontrar el nodo con el menor costo f en la lista abierta
        # Este es el nodo más prometedor para expandir
        nodo_actual = self.lista_abierta[0]
        indice_actual = 0
        for indice, elemento in enumerate(self.lista_abierta):
            if elemento.f < nodo_actual.f:
                nodo_actual = elemento
                indice_actual = indice

        # PASO 2: Mover el nodo actual de lista abierta a lista cerrada
        # Esto indica que ya lo hemos evaluado completamente
        self.lista_abierta.pop(indice_actual)
        self.lista_cerrada.append(nodo_actual)

        # PASO 3: Verificar si hemos llegado al objetivo
        if nodo_actual == self.nodo_final:
            self.camino = self._reconstruir_camino(nodo_actual)
            self.terminado = True
            return True

        # PASO 4: Expandir vecinos del nodo actual
        self._procesar_vecinos(nodo_actual)
        return True
    
    def _procesar_vecinos(self, nodo_actual):
        """Procesa los vecinos del nodo actual usando la funcionalidad de la clase base."""
        # Obtener vecinos válidos y sus costos de movimiento desde la clase base
        vecinos_con_costos = self.get_neighbors_and_costs(nodo_actual.posicion)
        vecinos = []
        
        # Crear nodos vecinos con la información de costo
        for pos_vecino, costo_movimiento in vecinos_con_costos:
            vecino = Nodo(nodo_actual, pos_vecino)
            vecino.costo_movimiento = costo_movimiento
            vecinos.append(vecino)

        # Evaluar cada vecino
        for vecino in vecinos:
            # Ignorar vecinos que ya fueron completamente evaluados
            if vecino in self.lista_cerrada:
                continue

            # Calcular costos del vecino
            vecino.g = nodo_actual.g + vecino.costo_movimiento  # Costo real acumulado
            vecino.h = self.calcular_heuristica(vecino.posicion, self.nodo_final.posicion)  # Estimación al objetivo
            vecino.f = vecino.g + vecino.h  # Costo total estimado (f = g + h)

            # Si ya existe un camino mejor a este vecino en lista abierta, ignorarlo
            if any(nodo_abierto for nodo_abierto in self.lista_abierta if vecino == nodo_abierto and vecino.g >= nodo_abierto.g):
                continue
            
            # Agregar vecino a la lista abierta para evaluación futura
            self.lista_abierta.append(vecino)

    def encontrar_camino(self, pos_inicio, pos_final):
        """Ejecuta el algoritmo completo de una vez."""
        # Inicializar la búsqueda con posiciones de inicio y final
        self.inicializar_busqueda(pos_inicio, pos_final)
        
        # Continuar hasta que no haya más nodos que evaluar o encontremos el objetivo
        while self.lista_abierta and not self.terminado:
            self.paso()  # Ejecutar una iteración del algoritmo
        
        return self.camino  # Retornar el camino encontrado (o None si no hay camino)

    def _reconstruir_camino(self, nodo_actual):
        """Reconstruye el camino desde el nodo objetivo hasta el inicio siguiendo los padres."""
        camino = []
        actual = nodo_actual
        
        # Seguir la cadena de padres desde el objetivo hasta el inicio
        while actual is not None:
            camino.append(actual.posicion)
            actual = actual.padre
        
        # Invertir para obtener el camino de inicio a objetivo
        return camino[::-1]

