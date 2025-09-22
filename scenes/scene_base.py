class SceneBase:
    """Clase base para todas las escenas del juego."""
    def __init__(self, juego):
        self.juego = juego
    
    # Propiedades para compatibilidad con código existente
    @property
    def game(self):
        return self.juego
    
    @game.setter
    def game(self, valor):
        self.juego = valor

    def al_entrar(self):
        """Se ejecuta cada vez que la escena se convierte en la activa."""
        pass # Las clases hijas pueden sobreescribir esto

    def manejar_eventos(self, eventos):
        """Procesa todos los eventos de la cola de Pygame."""
        raise NotImplementedError # Obliga a las clases hijas a implementar este método

    def actualizar(self, dt):
        """Actualiza la lógica de la escena."""
        raise NotImplementedError # Obliga a las clases hijas a implementar este método

    def dibujar(self, pantalla):
        """Dibuja la escena en la pantalla."""
        raise NotImplementedError # Obliga a las clases hijas a implementar este método
    
    # Propiedades de compatibilidad para métodos
    @property
    def on_enter(self):
        return self.al_entrar
    
    @property
    def handle_events(self):
        return self.manejar_eventos
    
    @property
    def update(self):
        return self.actualizar
    
    @property
    def draw(self):
        return self.dibujar