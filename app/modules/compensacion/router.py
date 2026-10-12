from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from typing import Optional

from app.modules.compensacion.repository import CompensacionRepository
from app.modules.compensacion.service import CompensacionService

router = APIRouter(prefix="/compensacion", tags=["Compensación 24x48"])
templates = Jinja2Templates(directory="app/templates")

MESES_NOMBRES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Setiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
]

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def ver_modulo_compensacion(
    request: Request,
    anio: int = 2026,
    tab: str = "anexo3",
    mes_anexo2: int = 1,
    mensaje: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Vista central e integral del Módulo de Compensación (Lineamiento LI-001-2023-INPE-OGA):
    - tab=anexo3: Reporte Mensualizado de Días Ganados en el Año Fiscal.
    - tab=anexo2: Control Mensual de Exceso de Trabajo (semanas Lunes a Domingo).
    - tab=saldos: Control de Días Usados y Días Restantes (Goce de Compensación).
    - tab=historial: Historial de Papeletas Manuales (Anexo 01).
    """
    matriz_anexo3 = CompensacionRepository.get_matriz_anexo3(anio)
    saldos = CompensacionRepository.get_control_saldos(anio)
    solicitudes = CompensacionRepository.get_solicitudes(anio)
    
    # Datos para Anexo 02
    datos_anexo2 = None
    if tab == "anexo2":
        datos_anexo2 = CompensacionService.calcular_anexo2_mes(anio, mes_anexo2)

    # Indicadores globales de Anexo 03
    total_servidores = len(matriz_anexo3)
    total_dias_ganados_anual = sum(r["total_ganado"] for r in matriz_anexo3)

    # Indicadores globales de Control de Saldos (Goce)
    total_asignados = sum(s["dias_asignados"] for s in saldos)
    total_usados = sum(s["dias_utilizados"] for s in saldos)
    total_restantes = sum(s["dias_disponibles"] for s in saldos)

    return templates.TemplateResponse(
        request=request,
        name="compensacion/matriz_anexo3.html",
        context={
            "anio": anio,
            "tab": tab,
            "mes_anexo2": mes_anexo2,
            "meses": MESES_NOMBRES,
            "matriz_anexo3": matriz_anexo3,
            "datos_anexo2": datos_anexo2,
            "saldos": saldos,
            "solicitudes": solicitudes,
            "total_servidores": total_servidores,
            "total_dias_ganados_anual": total_dias_ganados_anual,
            "total_asignados": total_asignados,
            "total_usados": total_usados,
            "total_restantes": total_restantes,
            "fecha_hoy": date.today().isoformat(),
            "mensaje": mensaje,
            "error": error
        }
    )

@router.post("/anexo2/calcular")
async def calcular_y_guardar_anexo2(
    anio: int = Form(2026),
    mes: int = Form(...)
):
    """
    Calcula automáticamente el Anexo 02 del mes a partir de la asistencia cerrada
    y lo persiste en la base de datos para alimentar el Anexo 03.
    """
    res = CompensacionService.calcular_anexo2_mes(anio, mes)
    if res.get("empleados"):
        CompensacionService.guardar_anexo2_en_db(anio, mes, res["empleados"])
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&mensaje=Anexo+02+de+{mes:02d}/{anio}+calculado+exitosamente+con+{res['total_exceso_mes']}+días+de+exceso+ganados.",
            status_code=303
        )
    else:
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&error=No+se+encontraron+datos+de+asistencia+para+el+mes+{mes}.",
            status_code=303
        )

@router.post("/registrar-uso")
async def registrar_uso_manual(
    id_empleado: int = Form(...),
    fecha_compensacion: str = Form(...),
    fecha_solicitud: Optional[str] = Form(None),
    numero_solicitud: str = Form(""),
    observaciones: str = Form("")
):
    """
    Registra el goce de un día de 24h presentado en papel/manual (Anexo 01)
    y descuenta 1 día del saldo disponible.
    """
    res = CompensacionService.registrar_goce_manual(
        id_empleado=id_empleado,
        fecha_compensacion=fecha_compensacion,
        fecha_solicitud=fecha_solicitud,
        numero_solicitud=numero_solicitud,
        observaciones=observaciones
    )
    if res["success"]:
        return RedirectResponse(f"/compensacion?tab=saldos&mensaje={res['message']}", status_code=303)
    else:
        return RedirectResponse(f"/compensacion?tab=saldos&error={res['message']}", status_code=303)

@router.post("/eliminar-uso/{id_solicitud}")
async def eliminar_uso(id_solicitud: int):
    """
    Anula o elimina un registro de uso manual y reintegra el día al saldo del servidor.
    """
    res = CompensacionService.eliminar_goce_manual(id_solicitud)
    if res["success"]:
        return RedirectResponse(f"/compensacion?tab=saldos&mensaje={res['message']}", status_code=303)
    else:
        return RedirectResponse(f"/compensacion?tab=saldos&error={res['message']}", status_code=303)

@router.get("/papeleta/{id_solicitud}", response_class=HTMLResponse)
async def ver_papeleta_anexo1(request: Request, id_solicitud: int):
    """
    Papeleta oficial imprimible del Anexo N° 01 (REG-010-URH).
    """
    sol = CompensacionRepository.get_solicitud_detalle(id_solicitud)
    if not sol:
        return HTMLResponse("Solicitud no encontrada", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="compensacion/papeleta_anexo1.html",
        context={"sol": sol}
    )
