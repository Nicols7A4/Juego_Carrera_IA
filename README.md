# Juego Carrera IA (Python)

Este repositorio contiene la base para un proyecto de Python. Incluye una estructura mínima, un script de ejemplo y archivos estándar para compartir dependencias sin subir el entorno virtual.

## Requisitos
- Python 3.10+ instalado y en el PATH
- PowerShell (Windows)

## Configurar entorno local
Ejecuta estos comandos en PowerShell dentro de la carpeta del proyecto:

```powershell
# 1) Crear entorno virtual local
python -m venv .venv

# 2) Activar el entorno (PowerShell)
. .\.venv\Scripts\Activate.ps1

# 3) Actualizar pip y herramientas
python -m pip install --upgrade pip

# 4) Instalar dependencias del proyecto
pip install -r requirements.txt

# 5) Instalar el paquete en modo editable (recomendado)
pip install -e .
```

## Ejecutar el ejemplo
```powershell
# Con el entorno activado
python -m carrera_ia
```

## Añadir nuevas dependencias
Instala la librería y congela versiones en `requirements.txt`:
```powershell
pip install <paquete>
pip freeze > requirements.txt
```

Recomendación: en desarrollo puedes usar `pip install -U <paquete>` para actualizar un paquete específico y luego actualizar el `requirements.txt`.

## Estructura del proyecto
```
.
├─ src/
│  └─ carrera_ia/
│     ├─ __init__.py
│     ├─ __main__.py
│     └─ main.py
├─ tests/
│  └─ test_smoke.py
├─ pyproject.toml
├─ requirements.txt
├─ README.md
└─ .gitignore
```

## Notas importantes
- No subas el entorno virtual (`.venv/`) al repositorio. Usa `requirements.txt` para compartir dependencias.
- Si clones este repo en otra máquina, repite los pasos de “Configurar entorno local”.
- Si prefieres `pip-tools` o `poetry`, se pueden agregar más adelante.

## Ejecutar pruebas (opcional)
Si añades pytest:
```powershell
pip install pytest
pytest -q
```

## Publicación
- Confirma que `requirements.txt` y el código en `src/` compilan/ejecutan correctamente.
- Crea un repositorio en GitHub y empuja este proyecto.
