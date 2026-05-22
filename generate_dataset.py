import subprocess
import sys
from pathlib import Path

# Configuración
SCRIPTS_DIR = Path("scripts")
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

SCRIPTS = [
    "personal.py",
    "academics.py",
    "financial.py",
    "socioeconomic.py",
    "demographic.py",
    "well-being.py",
    "additional.py",
]

def run_script(script_name: str) -> bool:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Error: No se encuentra el script {script_path}")
        return False

    print(f"Ejecutando {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_name}:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"Error inesperado con {script_name}: {e}")
        return False

def generate_dataset():
    # Crear directorios necesarios
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Ejecutar cada script de generación
    success = True
    for script in SCRIPTS:
        if not run_script(script):
            success = False
            break

    if not success:
        print("\nLa generación de datos se detuvo por errores previos.")
        return

    print("\nTodos los scripts se ejecutaron correctamente.")

if __name__ == "__main__":
    generate_dataset()