import os
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = Path(__file__).resolve().parent.parent

# Base de datos SQLite central
DB_PATH = BASE_DIR / "rrhh_control.db"

# Parámetros por defecto
DEFAULT_ESTABLECIMIENTO_ID = 722
DEFAULT_ESTABLECIMIENTO_NOMBRE = "EP. MUJERES IQUITOS"
DEFAULT_OFICINA_REGIONAL = "OFICINA REGIONAL NOR ORIENTE"
CURRENT_ANIO_FISCAL = 2026
