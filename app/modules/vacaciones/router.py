from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.modules.vacaciones.service import VacacionesService

router = APIRouter(prefix="/vacaciones", tags=["Vacaciones"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def inicio_vacaciones():
    return RedirectResponse(url="/vacaciones/saldos", status_code=302)

@router.get("/saldos", response_class=HTMLResponse)
async def ver_saldos(request: Request):
    resultado = VacacionesService.obtener_resumen_saldos()
    return templates.TemplateResponse(
        request=request,
        name="vacaciones/saldos.html",
        context={
            "stats": resultado["stats"],
            "empleados_stats": resultado["empleados"]
        }
    )

@router.get("/api/saldo")
async def consultar_saldo_api(id_empleado: int, periodo: str = "2025"):
    from app.modules.vacaciones.repository import VacacionesRepository
    return VacacionesRepository.obtener_saldo_personal_periodo(id_empleado=id_empleado, periodo=periodo)

@router.get("/historial", response_class=HTMLResponse)
async def ver_historial_vacaciones(request: Request, id_empleado: int = None):
    from app.modules.vacaciones.repository import VacacionesRepository
    from app.modules.empleados.service import EmpleadoService
    
    historial = VacacionesRepository.get_historial_completo_personal(id_empleado=id_empleado)
    empleados = EmpleadoService.listar_personal()
    
    # Calcular totales
    total_dias = sum(h["dias"] for h in historial)
    
    return templates.TemplateResponse(
        request=request,
        name="vacaciones/historial_personal.html",
        context={
            "historial": historial,
            "empleados": empleados,
            "empleado_seleccionado": id_empleado,
            "total_dias": total_dias,
            "total_registros": len(historial)
        }
    )

@router.get("/desplazados", response_class=HTMLResponse)
async def ver_desplazados(request: Request):
    from app.modules.vacaciones.repository import VacacionesRepository
    desplazados = VacacionesRepository.get_reporte_desplazados()
    return templates.TemplateResponse(
        request=request,
        name="vacaciones/desplazados.html",
        context={
            "desplazados": desplazados,
            "total": len(desplazados)
        }
    )


