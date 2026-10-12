import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.modules.dashboard.router import router as dashboard_router
from app.modules.asistencia.router import router as asistencia_router
from app.modules.vacaciones.router import router as vacaciones_router
from app.modules.empleados.router import router as empleados_router
from app.modules.reportes.router import router as reportes_router
from app.modules.compensacion.router import router as compensacion_router
from app.modules.desplazamientos.router import router as desplazamientos_router

app = FastAPI(
    title="Sistema RRHH & Control de Asistencia",
    description="Sistema modular de gestión de personal, control de asistencia mensual, vacaciones y compensación 24x48",
    version="2.1.0"
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registrar Routers Modulares
app.include_router(dashboard_router)
app.include_router(asistencia_router)
app.include_router(vacaciones_router)
app.include_router(compensacion_router)
app.include_router(desplazamientos_router)
app.include_router(empleados_router)
app.include_router(reportes_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
