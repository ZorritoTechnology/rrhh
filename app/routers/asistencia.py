from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.asistencia_service import (
    get_personal_activo,
    registrar_o_obtener_reporte_mensual,
    registrar_novedad,
    obtener_resumen_mes
)
from app.services.vacaciones_service import obtener_saldo_empleado

router = APIRouter(prefix="/asistencia", tags=["Asistencia"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/llenado-2026", response_class=HTMLResponse)
async def ver_llenado_2026(request: Request, mes: int = 1, mensaje: str = None):
    # Asegurar reporte mensual abierto
    rep_id = registrar_o_obtener_reporte_mensual(anio=2026, mes=mes)
    empleados = get_personal_activo()
    resumen = obtener_resumen_mes(anio=2026, mes=mes)
    
    return templates.TemplateResponse(
        request=request,
        name="llenado_2026.html",
        context={
            "mes_seleccionado": mes,
            "empleados": empleados,
            "resumen": resumen,
            "mensaje": mensaje
        }
    )

@router.post("/guardar-novedad")
async def guardar_novedad_2026(
    anio: int = Form(...),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    tipo_novedad: str = Form(...),
    cantidad: int = Form(1),
    fecha_inicio: str = Form(""),
    fecha_termino: str = Form(""),
    observaciones: str = Form("")
):
    rep_id = registrar_o_obtener_reporte_mensual(anio=anio, mes=mes)
    
    datos = {
        "minutos": cantidad,
        "dias": cantidad,
        "fecha_inicio": fecha_inicio,
        "fecha_termino": fecha_termino or fecha_inicio,
        "fechas_detalle": fecha_inicio,
        "observaciones": observaciones,
        "periodo": "2025-2026"
    }
    registrar_novedad(tipo_novedad, rep_id, id_empleado, datos)
    
    return RedirectResponse(url=f"/asistencia/llenado-2026?mes={mes}&mensaje=Novedad+registrada+correctamente+para+el+mes+{mes}/2026", status_code=303)

