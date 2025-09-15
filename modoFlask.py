from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Editor de Escenario IA</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f7f7f7; }
        .panel { background: #fff; padding: 16px; margin: 24px auto; border-radius: 8px; box-shadow: 0 2px 8px #0001; max-width: 900px; }
        .controls { margin-bottom: 16px; }
        label { margin-right: 8px; }
        input[type=number] { width: 60px; }
        .grid { display: grid; margin: 0 auto; background: #eee; border-radius: 6px; }
        .cell { width: 32px; height: 32px; border: 1px solid #ccc; box-sizing: border-box; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .obstacle { background: #333; }
        .origin { background: #2e86de; color: #fff; border: 2px solid #145; border-radius: 50%; }
        .dest { background: #e74c3c; color: #fff; border: 2px solid #800; border-radius: 50%; }
        .btn { padding: 6px 16px; margin-right: 8px; border: none; border-radius: 4px; background: #2e86de; color: #fff; cursor: pointer; }
        .btn:active { background: #145; }
        .btn-clear { background: #aaa; }
        .btn-save { background: #27ae60; }
        .status { margin-top: 12px; color: #555; }
    </style>
</head>
<body>
<div class="panel">
    <form class="controls" id="controls" onsubmit="return false;">
        <label>Filas: <input type="number" id="rows" min="2" value="{{ rows }}"></label>
        <label>Columnas: <input type="number" id="cols" min="2" value="{{ cols }}"></label>
        <label><input type="checkbox" id="diagonals" {% if diagonals %}checked{% endif %}> Permitir diagonales</label>
        <button class="btn" onclick="generateGrid()">Generar</button>
        <button class="btn btn-clear" onclick="clearObstacles()">Limpiar</button>
        <button class="btn btn-save" onclick="saveJSON()">Guardar JSON</button>
    </form>
    <div id="grid" class="grid"></div>
    <div class="status" id="status"></div>
</div>
<script>
let rows = {{ rows }};
let cols = {{ cols }};
let diagonals = {{ diagonals|tojson }};
let grid = {{ grid|tojson }};
let origin = {{ origin|tojson }};
let dest = {{ dest|tojson }};
let dragging = null;

function renderGrid() {
    const gridDiv = document.getElementById('grid');
    gridDiv.innerHTML = '';
    gridDiv.style.gridTemplateRows = `repeat(${rows}, 32px)`;
    gridDiv.style.gridTemplateColumns = `repeat(${cols}, 32px)`;
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.r = r;
            cell.dataset.c = c;
            if (grid[r][c] === 1) cell.classList.add('obstacle');
            if (origin[0] === r && origin[1] === c) cell.classList.add('origin');
            if (dest[0] === r && dest[1] === c) cell.classList.add('dest');
            cell.onmousedown = (e) => onCellDown(e, r, c);
            cell.onmouseup = (e) => onCellUp(e, r, c);
            cell.onmousemove = (e) => onCellMove(e, r, c);
            cell.onclick = (e) => onCellClick(e, r, c);
            gridDiv.appendChild(cell);
        }
    }
}

function onCellClick(e, r, c) {
    if ((origin[0] === r && origin[1] === c) || (dest[0] === r && dest[1] === c)) return;
    grid[r][c] = grid[r][c] === 1 ? 0 : 1;
    renderGrid();
}
function onCellDown(e, r, c) {
    if (origin[0] === r && origin[1] === c) dragging = 'origin';
    else if (dest[0] === r && dest[1] === c) dragging = 'dest';
}
function onCellUp(e, r, c) {
    dragging = null;
}
function onCellMove(e, r, c) {
    if (!dragging) return;
    if (dragging === 'origin' && !(dest[0] === r && dest[1] === c)) {
        origin = [r, c];
        renderGrid();
    }
    if (dragging === 'dest' && !(origin[0] === r && origin[1] === c)) {
        dest = [r, c];
        renderGrid();
    }
}
function generateGrid() {
    rows = parseInt(document.getElementById('rows').value);
    cols = parseInt(document.getElementById('cols').value);
    diagonals = document.getElementById('diagonals').checked;
    grid = Array.from({length: rows}, () => Array(cols).fill(0));
    origin = [0,0];
    dest = [rows-1, cols-1];
    renderGrid();
    setStatus('Tablero generado.');
}
function clearObstacles() {
    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            grid[r][c] = 0;
    renderGrid();
    setStatus('Obstáculos eliminados.');
}
function saveJSON() {
    fetch('/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            dimensiones: {n: rows, m: cols},
            diagonales: diagonals,
            origen: origin,
            destino: dest,
            grid: grid
        })
    }).then(r => r.json()).then(data => {
        setStatus(data.status);
    });
}
function setStatus(msg) {
    document.getElementById('status').textContent = msg;
}
window.onload = renderGrid;
</script>
</body>
</html>
'''

JSON_PATH = os.path.join(os.path.dirname(__file__), 'escenario.json')

def load_json():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {
            'rows': data.get('dimensiones', {}).get('n', 10),
            'cols': data.get('dimensiones', {}).get('m', 10),
            'diagonals': data.get('diagonales', False),
            'origin': data.get('origen', [0,0]),
            'dest': data.get('destino', [9,9]),
            'grid': data.get('grid', [[0]*10 for _ in range(10)])
        }
    else:
        return {
            'rows': 10,
            'cols': 10,
            'diagonals': False,
            'origin': [0,0],
            'dest': [9,9],
            'grid': [[0]*10 for _ in range(10)]
        }

@app.route('/')
def index():
    ctx = load_json()
    return render_template_string(TEMPLATE, **ctx)

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    try:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({'status': 'Guardado correctamente en escenario.json'})
    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
