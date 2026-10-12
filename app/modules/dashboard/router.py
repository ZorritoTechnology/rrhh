from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.modules.empleados.service import EmpleadoService
from app.modules.vacaciones.service import VacacionesService
from app.modules.asistencia.service import AsistenciaService

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    total_empleados = EmpleadoService.contar_empleados()
    saldos = VacacionesService.obtener_resumen_saldos()
    resumen_enero = AsistenciaService.obtener_resumen_mes(anio=2026, mes=1)
    historial = AsistenciaService.obtener_historial_reportes()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_empleados": total_empleados,
            "vacaciones_stats": saldos["stats"],
            "resumen_actual": resumen_enero,
            "historial_reciente": historial[:5]
        }
    )
