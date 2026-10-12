from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from app.modules.compensacion.repository import CompensacionRepository
from app.modules.compensacion.service import CompensacionService

router = APIRouter(prefix="/compensacion", tags=["Compensación 24x48"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def ver_matriz_anexo3(request: Request, anio: int = 2026):
    """
    Vista principal: Anexo 03 - Reporte Mensualizado de Compensación de Jornada 24x48.
    """
    matriz = CompensacionRepository.get_matriz_mensualizada(anio)
    
    total_servidores = len(matriz)
    total_asignados = sum(r["dias_asignados"] for r in matriz)
    total_consumidos = sum(r["total_utilizado"] for r in matriz)
    total_pendientes = sum(r["saldo_disponible"] for r in matriz)

    return templates.TemplateResponse(
        request=request,
        name="compensacion/matriz_anexo3.html",
        context={
            "matriz": matriz,
            "anio": anio,
            "total_servidores": total_servidores,
            "total_asignados": total_asignados,
            "total_consumidos": total_consumidos,
            "total_pendientes": total_pendientes
        }
    )

@router.get("/solicitud", response_class=HTMLResponse)
async def form_solicitud(request: Request):
    """
    Formulario oficial Anexo 01 para solicitar compensación 24x48.
    """
    empleados_24x48 = CompensacionRepository.get_matriz_mensualizada(2026)
    return templates.TemplateResponse(
        request=request,
        name="compensacion/form_solicitud.html",
        context={
            "empleados_24x48": empleados_24x48,
            "fecha_hoy": date.today().isoformat()
        }
    )

@router.post("/solicitud", response_class=HTMLResponse)
async def registrar_solicitud(
    request: Request,
    id_empleado: int = Form(...),
    fecha_solicitud: str = Form(...),
    fecha_compensacion: str = Form(...),
    observaciones: str = Form(""),
    es_regularizacion: bool = Form(False),
    jefe_inmediato: str = Form("AUTORIZADO"),
    especialista_personal: str = Form("CONFORME")
):
    resultado = CompensacionService.validar_y_registrar_solicitud(
        id_empleado=id_empleado,
        fecha_solicitud=fecha_solicitud,
        fecha_compensacion=fecha_compensacion,
        observaciones=observaciones,
        es_regularizacion=es_regularizacion,
        jefe_inmediato=jefe_inmediato,
        especialista_personal=especialista_personal
    )

    empleados_24x48 = CompensacionRepository.get_matriz_mensualizada(2026)

    if not resultado["success"]:
        return templates.TemplateResponse(
            request=request,
            name="compensacion/form_solicitud.html",
            context={
                "empleados_24x48": empleados_24x48,
                "fecha_hoy": fecha_solicitud,
                "error": resultado["message"]
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="compensacion/form_solicitud.html",
        context={
            "empleados_24x48": empleados_24x48,
            "fecha_hoy": fecha_solicitud,
            "success": resultado["message"],
            "id_solicitud": resultado["id_solicitud"]
        }
    )

@router.get("/solicitudes", response_class=HTMLResponse)
async def historial_solicitudes(request: Request, anio: int = 2026):
    """
    Historial de solicitudes tramitadas.
    """
    solicitudes = CompensacionRepository.get_solicitudes(anio)
    return templates.TemplateResponse(
        request=request,
        name="compensacion/historial_solicitudes.html",
        context={
            "solicitudes": solicitudes,
            "anio": anio
        }
    )

@router.get("/papeleta/{id_solicitud}", response_class=HTMLResponse)
async def ver_papeleta_anexo1(request: Request, id_solicitud: int):
    """
    Formato oficial de impresión: Anexo N° 01 Papeleta de Compensación.
    """
    sol = CompensacionRepository.get_solicitud_detalle(id_solicitud)
    if not sol:
        return HTMLResponse("Solicitud no encontrada", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="compensacion/papeleta_anexo1.html",
        context={
            "sol": sol
        }
    )
