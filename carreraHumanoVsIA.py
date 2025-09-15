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
cell_size = min(40, 700 // max(rows, cols))
margin = 40
width = cols * cell_size * 2 + margin * 3
height = rows * cell_size + margin * 2
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Carrera Humano vs IA - A*")

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
    'human': (39, 174, 96),
    'ia': (241, 196, 15),
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

# Inicializar nodos visuales para ambos mapas
def make_grid_vis():
    grid_vis = [[VisNode((r, c)) for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 'Obstaculo':
                grid_vis[r][c].state = 'obstacle'
    grid_vis[origin[0]][origin[1]].state = 'origin'
    grid_vis[dest[0]][dest[1]].state = 'dest'
    return grid_vis

grid_vis_ia = make_grid_vis()
grid_vis_humano = make_grid_vis()
# Calcular ruta IA antes de la carrera (scope global)
ia_path = astar_mod.astar(origin, dest, grid, allow_diagonal)
ia_index = 0
ia_finished = False

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

    def step_forward(self):
        if self.finished:
            return
        if not self.open_list:
            self.finished = True
            self.path = None
            return
        # Seleccionar nodo con menor f
        self.current = min(self.open_list, key=lambda x: x.f)
        self.open_list.remove(self.current)
        self.closed_list.append(self.current)
        # Si llegamos al destino
        if self.current.position == self.end:
            self.finished = True
            self.path = self._reconstruct_path(self.current)
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

    def _reconstruct_path(self, node):
        path = []
        while node:
            path.append(node.position)
            node = node.parent
        return path[::-1]

    def get_visual_state(self, grid_vis):
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


    # Calcular ruta IA antes de la carrera (scope global)
    ia_path = astar_mod.astar(origin, dest, grid, allow_diagonal)
    ia_index = 0
    ia_finished = False

# Humano
class Humano:
    def __init__(self, start, end, grid, allow_diagonal):
        self.pos = start
        self.end = end
        self.grid = grid
        self.allow_diagonal = allow_diagonal
        self.finished = False
        self.path = [start]

    def move(self, dx, dy):
        if self.finished:
            return
        r, c = self.pos
        nr, nc = r + dx, c + dy
        if 0 <= nr < rows and 0 <= nc < cols and self.grid[nr][nc] != 'Obstaculo':
            self.pos = (nr, nc)
            self.path.append(self.pos)
            if self.pos == self.end:
                self.finished = True
                # Marcar recorrido en el grid visual
                for pos in self.path:
                    if pos != self.end and pos != self.pos:
                        grid_vis_humano[pos[0]][pos[1]].state = 'path'

humano = Humano(origin, dest, grid, allow_diagonal)

# Dibujo de mapas
def draw_grid(grid_vis, offset_x, offset_y, actor_pos=None, actor_color=None):
    for r in range(rows):
        for c in range(cols):
            v = grid_vis[r][c]
            x = offset_x + c * cell_size
            y = offset_y + r * cell_size
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
    # Actor
    if actor_pos:
        x = offset_x + actor_pos[1] * cell_size
        y = offset_y + actor_pos[0] * cell_size
        pygame.draw.ellipse(win, actor_color, (x+6, y+6, cell_size-12, cell_size-12))

# UI
speed = 0.20  # segundos por iteración
auto_run = True
last_step_time = time.time()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if not humano.finished:
                if event.key == pygame.K_UP:
                    humano.move(-1,0)
                if event.key == pygame.K_DOWN:
                    humano.move(1,0)
                if event.key == pygame.K_LEFT:
                    humano.move(0,-1)
                if event.key == pygame.K_RIGHT:
                    humano.move(0,1)
                # Diagonales
                if allow_diagonal:
                    if event.key == pygame.K_q:  # Arriba-Izquierda
                        humano.move(-1,-1)
                    if event.key == pygame.K_e:  # Arriba-Derecha
                        humano.move(-1,1)
                    if event.key == pygame.K_z:  # Abajo-Izquierda
                        humano.move(1,-1)
                    if event.key == pygame.K_c:  # Abajo-Derecha
                        humano.move(1,1)
            if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                speed = max(0.01, speed - 0.01)
            if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                speed = min(2.0, speed + 0.01)
            if event.key == pygame.K_a:
                auto_run = not auto_run
    # IA avanza automáticamente por su ruta calculada
    if auto_run and not ia_finished and ia_path and time.time() - last_step_time > speed:
        if ia_index < len(ia_path):
            pos = ia_path[ia_index]
            # Marcar recorrido en el grid visual IA
            if pos != dest and pos != origin:
                grid_vis_ia[pos[0]][pos[1]].state = 'path'
            ia_index += 1
            last_step_time = time.time()
        else:
            ia_finished = True
    # Dibujo
    win.fill((255,255,255))
    # IA
    ia_actor_pos = ia_path[ia_index-1] if ia_path and ia_index > 0 else origin
    draw_grid(grid_vis_ia, margin, margin, actor_pos=ia_actor_pos, actor_color=COLORS['ia'])
    win.blit(font_ui.render("IA (A*)", True, COLORS['ia']), (margin, 8))
    # Humano
    draw_grid(grid_vis_humano, margin*2+cols*cell_size, margin, actor_pos=humano.pos, actor_color=COLORS['human'])
    win.blit(font_ui.render("Humano", True, COLORS['human']), (margin*2+cols*cell_size, 8))
    # Info
    win.blit(font_ui.render(f"[Flechas] Mover Humano", True, (0,0,0)), (width//2-120, height-32))
    if allow_diagonal:
        win.blit(font_ui.render(f"[Q/E/Z/C] Diagonales", True, (0,0,0)), (width//2-120, height-60))
        win.blit(font_ui.render(f"[A] Auto IA: {'ON' if auto_run else 'OFF'}", True, (0,0,0)), (width//2-120, height-88))
        win.blit(font_ui.render(f"[+/-] Velocidad: {speed:.2f}s", True, (0,0,0)), (width//2-120, height-116))
    else:
        win.blit(font_ui.render(f"[A] Auto IA: {'ON' if auto_run else 'OFF'}", True, (0,0,0)), (width//2-120, height-60))
        win.blit(font_ui.render(f"[+/-] Velocidad: {speed:.2f}s", True, (0,0,0)), (width//2-120, height-88))
    # Resultados
    if ia_finished:
        if ia_path:
            win.blit(font_ui.render(f"IA pasos: {len(ia_path)-1}", True, COLORS['ia']), (margin, height-32))
        else:
            win.blit(font_ui.render(f"IA sin camino", True, (120,0,0)), (margin, height-32))
    if humano.finished:
        win.blit(font_ui.render(f"Humano pasos: {len(humano.path)-1}", True, COLORS['human']), (margin*2+cols*cell_size, height-32))
    pygame.display.flip()
