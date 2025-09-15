import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


class GridEditor(tk.Tk):
    def __init__(self, json_path: str):
        super().__init__()
        self.title("Editor de Escenario")

        self.json_path = json_path

        # Estado
        self.rows = 10
        self.cols = 10
        self.allow_diagonals = False
        self.grid_data = []  # 0 libre, 1 obstáculo
        self.origin = None  # (r, c)
        self.dest = None  # (r, c)

        # Interacción
        self.dragging = None  # 'origin' | 'dest' | None

        # UI
        self._build_ui()
        self._new_grid()

    def _build_ui(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        ttk.Label(control_frame, text="Filas:").grid(row=0, column=0, sticky="w")
        self.rows_var = tk.StringVar(value=str(self.rows))
        ttk.Entry(control_frame, textvariable=self.rows_var, width=6).grid(row=0, column=1, padx=(4, 10))

        ttk.Label(control_frame, text="Columnas:").grid(row=0, column=2, sticky="w")
        self.cols_var = tk.StringVar(value=str(self.cols))
        ttk.Entry(control_frame, textvariable=self.cols_var, width=6).grid(row=0, column=3, padx=(4, 10))

        self.diag_var = tk.BooleanVar(value=self.allow_diagonals)
        ttk.Checkbutton(control_frame, text="Permitir diagonales", variable=self.diag_var).grid(row=0, column=4, padx=(4, 10))

        ttk.Button(control_frame, text="Generar", command=self._on_generate).grid(row=0, column=5, padx=(4, 10))
        ttk.Button(control_frame, text="Limpiar", command=self._on_clear_obstacles).grid(row=0, column=6, padx=(4, 10))
        ttk.Button(control_frame, text="Guardar JSON", command=self._on_save).grid(row=0, column=7)

        # Lienzo para la grilla
        self.canvas_size = 640
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg="#ffffff")
        self.canvas.pack(side=tk.TOP, padx=10, pady=(0, 10))

        # Eventos del canvas
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Info
        self.status_var = tk.StringVar(value="Click: obstáculo ON/OFF. Arrastrar círculos para mover origen/destino.")
        ttk.Label(self, textvariable=self.status_var).pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))

    def _parse_dimensions(self):
        try:
            r = int(self.rows_var.get())
            c = int(self.cols_var.get())
            if r <= 0 or c <= 0:
                raise ValueError
            return r, c
        except Exception:
            messagebox.showerror("Dimensiones inválidas", "Ingrese números enteros positivos para filas y columnas.")
            return None

    def _new_grid(self):
        self.grid_data = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.origin = (0, 0)
        self.dest = (self.rows - 1, self.cols - 1)
        self.allow_diagonals = self.diag_var.get()
        self._redraw()

    def _on_generate(self):
        dims = self._parse_dimensions()
        if dims is None:
            return
        self.rows, self.cols = dims
        self.allow_diagonals = self.diag_var.get()
        self._new_grid()

    def _on_clear_obstacles(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid_data[r][c] = 0
        self._redraw()

    def _cell_from_xy(self, x, y):
        cell_w = self.canvas_size / self.cols
        cell_h = self.canvas_size / self.rows
        c = int(x // cell_w)
        r = int(y // cell_h)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None

    def _on_left_click(self, event):
        pos = self._cell_from_xy(event.x, event.y)
        if not pos:
            return
        r, c = pos
        if self.origin == (r, c):
            self.dragging = 'origin'
            return
        if self.dest == (r, c):
            self.dragging = 'dest'
            return
        # Toggle obstáculo
        if (r, c) != self.origin and (r, c) != self.dest:
            self.grid_data[r][c] = 0 if self.grid_data[r][c] == 1 else 1
            self._draw_cell(r, c)

    def _on_drag(self, event):
        if not self.dragging:
            return
        pos = self._cell_from_xy(event.x, event.y)
        if not pos:
            return
        r, c = pos
        if self.dragging == 'origin' and (r, c) != self.dest:
            self.origin = (r, c)
            self._redraw()
        elif self.dragging == 'dest' and (r, c) != self.origin:
            self.dest = (r, c)
            self._redraw()

    def _on_release(self, _event):
        self.dragging = None

    def _draw_cell(self, r, c):
        cell_w = self.canvas_size / self.cols
        cell_h = self.canvas_size / self.rows
        x0 = c * cell_w
        y0 = r * cell_h
        x1 = x0 + cell_w
        y1 = y0 + cell_h

        fill = "#ffffff" if self.grid_data[r][c] == 0 else "#333333"
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#cccccc")

    def _redraw(self):
        self.canvas.delete("all")
        # celdas
        for r in range(self.rows):
            for c in range(self.cols):
                self._draw_cell(r, c)
        # origen y destino
        self._draw_endpoints()

    def _draw_endpoints(self):
        cell_w = self.canvas_size / self.cols
        cell_h = self.canvas_size / self.rows

        def draw_circle(rc, color):
            if rc is None:
                return
            r, c = rc
            x0 = c * cell_w
            y0 = r * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h
            padding = min(cell_w, cell_h) * 0.18
            self.canvas.create_oval(x0 + padding, y0 + padding, x1 - padding, y1 - padding, fill=color, outline="")

        draw_circle(self.origin, "#2e86de")  # Azul: origen
        draw_circle(self.dest, "#e74c3c")    # Rojo: destino

    def _on_save(self):
        data = {
            "dimensiones": {"n": self.rows, "m": self.cols},
            "diagonales": bool(self.diag_var.get()),
            "origen": [int(self.origin[0]), int(self.origin[1])] if self.origin else None,
            "destino": [int(self.dest[0]), int(self.dest[1])] if self.dest else None,
            "grid": [[int(v) for v in row] for row in self.grid_data],
        }
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"Guardado en {os.path.basename(self.json_path)}")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "escenario.json")
    app = GridEditor(json_path)
    app.mainloop()

if __name__ == "__main__":
    main()