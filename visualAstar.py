import pygame
import sys
import os
import json
import importlib.util
import time

# Cargar algoritmo astar.py dinámicamente
ASTAR_PATH = os.path.join(os.path.dirname(__file__), 'algorirmos', 'astar.py')
spec = importlib.util.spec_from_file_location("astar", ASTAR_PATH)
astar_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(astar_mod)

# Cargar escenario.json
JSON_PATH = os.path.join(os.path.dirname(__file__), 'escenario.json')
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    escenario = json.load(f)

rows = escenario['dimensiones']['n']
cols = escenario['dimensiones']['m']
grid_raw = escenario['grid']
allow_diagonal = escenario.get('diagonales', False)
origin = tuple(escenario['origen'])
dest = tuple(escenario['destino'])

# Convertir grid a formato del algoritmo
# 0 = libre, 1 = obstáculo
grid = [['Obstaculo' if cell == 1 else 'Normal' for cell in row] for row in grid_raw]

# Pygame setup
pygame.init()
cell_size = min(48, 800 // max(rows, cols))
width = cols * cell_size + 200
height = rows * cell_size + 40
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Visualización A* Carrera IA")

# Colores
COLORS = {
    'free': (255, 255, 255),
    'obstacle': (30, 30, 30),
    'origin': (46, 134, 222),
    'dest': (231, 76, 60),
    'open': (255, 255, 0),
    'closed': (173, 216, 230),
    'path': (209, 125, 212),
    'border': (120, 120, 120),
}

font_f = pygame.font.SysFont(None, int(cell_size * 0.7))
font_gh = pygame.font.SysFont(None, int(cell_size * 0.35))
font_ui = pygame.font.SysFont(None, 28)

# Estados para visualización
class VisNode:
    def __init__(self, pos):
        self.pos = pos
        self.g = None
        self.h = None
        self.f = None
        self.state = 'free'  # free, obstacle, origin, dest, open, closed, path
        self.parent = None

# Inicializar nodos visuales
grid_vis = [[VisNode((r, c)) for c in range(cols)] for r in range(rows)]
for r in range(rows):
    for c in range(cols):
        if grid[r][c] == 'Obstaculo':
            grid_vis[r][c].state = 'obstacle'

grid_vis[origin[0]][origin[1]].state = 'origin'
grid_vis[dest[0]][dest[1]].state = 'dest'

# Algoritmo A* paso a paso
class AStarStepper:
    def __init__(self, start, end, grid, allow_diagonal):
        self.start = start
        self.end = end
        self.grid = grid
        self.allow_diagonal = allow_diagonal
        self.reset()

    def reset(self):
        self.open_list = []
        self.closed_list = []
        self.steps = []  # Cada paso: (open_list, closed_list, current, grid_vis snapshot)
        self.finished = False
        self.path = None
        self._init_nodes()
        self._step_init()

    def _init_nodes(self):
        self.nodes = {}
        for r in range(rows):
            for c in range(cols):
                self.nodes[(r, c)] = astar_mod.Node((r, c))
                if self.grid[r][c] == 'Obstaculo':
                    self.nodes[(r, c)].tipo = 'Obstaculo'

    def _step_init(self):
        self.open_list = [self.nodes[self.start]]
        self.closed_list = []
        self.nodes[self.start].update_scores(0, astar_mod.heuristic(self.start, self.end, self.allow_diagonal))
        self.nodes[self.start].parent = None
        self.current = None
        self.finished = False
        self.path = None
        self.steps = []
        self._snapshot()

    def _snapshot(self):
        # Copia el estado actual para visualización
        snap = {
            'open': [n.position for n in self.open_list],
            'closed': [n.position for n in self.closed_list],
            'current': self.current.position if self.current else None,
            'g': {pos: self.nodes[pos].g for pos in self.nodes},
            'h': {pos: self.nodes[pos].h for pos in self.nodes},
            'f': {pos: self.nodes[pos].f for pos in self.nodes},
            'parent': {pos: self.nodes[pos].parent.position if self.nodes[pos].parent else None for pos in self.nodes},
        }
        self.steps.append(snap)

    def step_forward(self):
        if self.finished:
            return
        if not self.open_list:
            self.finished = True
            self.path = None
            self._snapshot()
            return
        # Seleccionar nodo con menor f
        self.current = min(self.open_list, key=lambda x: x.f)
        self.open_list.remove(self.current)
        self.closed_list.append(self.current)
        # Si llegamos al destino
        if self.current.position == self.end:
            self.finished = True
            self.path = self._reconstruct_path(self.current)
            self._snapshot()
            return
        # Vecinos
        neighbors = self.current.get_neighbors(self.grid, self.allow_diagonal)
        for neighbor in neighbors:
            pos = neighbor.position
            if any(n.position == pos for n in self.closed_list):
                continue
            tentative_g = self.current.g + neighbor.movement_cost
            node = self.nodes[pos]
            if node.tipo == 'Obstaculo':
                continue
            if node not in self.open_list:
                node.parent = self.current
                node.update_scores(tentative_g, astar_mod.heuristic(pos, self.end, self.allow_diagonal))
                self.open_list.append(node)
            else:
                if tentative_g < node.g:
                    node.parent = self.current
                    node.update_scores(tentative_g, astar_mod.heuristic(pos, self.end, self.allow_diagonal))
        self._snapshot()

    def step_back(self):
        if len(self.steps) > 1:
            self.steps.pop()
            snap = self.steps[-1]
            self._restore_snapshot(snap)

    def _restore_snapshot(self, snap):
        # Restaurar estado desde snapshot
        self.open_list = [self.nodes[pos] for pos in snap['open']]
        self.closed_list = [self.nodes[pos] for pos in snap['closed']]
        self.current = self.nodes[snap['current']] if snap['current'] else None
        for pos in self.nodes:
            self.nodes[pos].g = snap['g'][pos]
            self.nodes[pos].h = snap['h'][pos]
            self.nodes[pos].f = snap['f'][pos]
            parent_pos = snap['parent'][pos]
            self.nodes[pos].parent = self.nodes[parent_pos] if parent_pos else None

    def _reconstruct_path(self, node):
        path = []
        while node:
            path.append(node.position)
            node = node.parent
        return path[::-1]

    def get_visual_state(self):
        # Actualiza grid_vis según el estado actual
        for r in range(rows):
            for c in range(cols):
                v = grid_vis[r][c]
                v.g = self.nodes[(r, c)].g
                v.h = self.nodes[(r, c)].h
                v.f = self.nodes[(r, c)].f
                v.parent = self.nodes[(r, c)].parent.position if self.nodes[(r, c)].parent else None
                if v.state == 'obstacle':
                    continue
                if (r, c) == origin:
                    v.state = 'origin'
                elif (r, c) == dest:
                    v.state = 'dest'
                elif self.finished and self.path and (r, c) in self.path:
                    v.state = 'path'
                elif (r, c) in [n.position for n in self.open_list]:
                    v.state = 'open'
                elif (r, c) in [n.position for n in self.closed_list]:
                    v.state = 'closed'
                else:
                    v.state = 'free'

stepper = AStarStepper(origin, dest, grid, allow_diagonal)

# UI
speed = 1.0  # segundos por iteración
auto_run = False
step_count = 0

# Botones
def draw_ui():
    pygame.draw.rect(win, (220,220,220), (cols*cell_size,0,200,height))
    y = 20
    win.blit(font_ui.render(f"Velocidad: {speed:.2f}s", True, (0,0,0)), (cols*cell_size+20, y))
    y += 40
    win.blit(font_ui.render("[+/-] Cambiar velocidad", True, (0,0,0)), (cols*cell_size+20, y))
    y += 40
    win.blit(font_ui.render("[Espacio] Avanzar", True, (0,0,0)), (cols*cell_size+20, y))
    y += 40
    win.blit(font_ui.render("[B] Retroceder", True, (0,0,0)), (cols*cell_size+20, y))
    y += 40
    win.blit(font_ui.render("[A] Auto", True, (0,0,0)), (cols*cell_size+20, y))
    y += 40
    win.blit(font_ui.render(f"Iteración: {len(stepper.steps)-1}", True, (0,0,0)), (cols*cell_size+20, y))
    y += 40
    if stepper.finished:
        if stepper.path:
            win.blit(font_ui.render(f"¡Camino encontrado!", True, (0,120,0)), (cols*cell_size+20, y))
            y += 30
            win.blit(font_ui.render(f"Pasos: {len(stepper.path)-1}", True, (0,120,0)), (cols*cell_size+20, y))
        else:
            win.blit(font_ui.render(f"Sin camino", True, (120,0,0)), (cols*cell_size+20, y))

def draw_grid():
    for r in range(rows):
        for c in range(cols):
            v = grid_vis[r][c]
            x = c * cell_size
            y = r * cell_size
            color = COLORS[v.state]
            pygame.draw.rect(win, color, (x, y, cell_size, cell_size))
            pygame.draw.rect(win, COLORS['border'], (x, y, cell_size, cell_size), 1)
            # Texto F grande
            if v.state in ['open','closed','path','dest'] and v.f is not None:
                f_text = font_f.render(str(int(v.f)), True, (0,0,0))
                win.blit(f_text, (x+cell_size//2-f_text.get_width()//2, y+cell_size//2-f_text.get_height()//2))
            # Texto G/H pequeños
            if v.state in ['open','closed','path','dest'] and v.g is not None and v.h is not None:
                g_text = font_gh.render(f"G:{int(v.g)}", True, (60,60,60))
                h_text = font_gh.render(f"H:{int(v.h)}", True, (60,60,60))
                win.blit(g_text, (x+4, y+4))
                win.blit(h_text, (x+cell_size-h_text.get_width()-4, y+4))

# Main loop
last_step_time = time.time()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                stepper.step_forward()
                stepper.get_visual_state()
            if event.key == pygame.K_b:
                stepper.step_back()
                stepper.get_visual_state()
            if event.key == pygame.K_a:
                auto_run = not auto_run
            if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                speed = max(0.1, speed - 0.1)
            if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                speed = min(5.0, speed + 0.1)
    if auto_run and not stepper.finished:
        if time.time() - last_step_time > speed:
            stepper.step_forward()
            stepper.get_visual_state()
            last_step_time = time.time()
    win.fill((255,255,255))
    draw_grid()
    draw_ui()
    pygame.display.flip()
