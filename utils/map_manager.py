import json

def load_map_data(file_path):
    """Carga los datos de un mapa desde un archivo JSON."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f"Mapa '{file_path}' cargado correctamente.")
            return data
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de mapa en '{file_path}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: El archivo '{file_path}' no es un JSON válido.")
        return None

def save_map_data(data, file_path):
    """Guarda los datos de un mapa en un archivo JSON."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4) # indent=4 para que el JSON sea legible
            print(f"Mapa guardado correctamente en '{file_path}'")
    except IOError as e:
        print(f"Error al guardar el mapa en '{file_path}': {e}")