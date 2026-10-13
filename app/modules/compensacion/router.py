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
    mes_reporte: int = 1,
    mensaje: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Vista central e integral del Módulo de Compensación (LI-001-2023-INPE-OGA):
    - tab=anexo3: Matriz Oficial Anexo 03 (Días Ganados en el Año Fiscal)
    - tab=anexo2: Control Semanal Anexo 02 (Grupos 1, 2, 3 con Alcaides y Rotaciones)
    - tab=solicitudes: Solicitudes de Compensación (Control de Saldo Inicial, Días Solicitados y Saldo Restante)
    - tab=reporte_gastos: Reporte Mensual de Gastos y Saldos Restantes para la Oficina Regional
    - tab=historial: Historial de Papeletas y Anexo 01
    """
    matriz_anexo3 = CompensacionRepository.get_matriz_anexo3(anio)
    grupos_guardia = CompensacionRepository.get_grupos_guardia()
    saldos = CompensacionRepository.get_control_saldos(anio)
    solicitudes = CompensacionRepository.get_solicitudes(anio)
    
    # Anexo 02 (por grupos con alcaides)
    datos_anexo2 = None
    rotaciones_mes = []
    if tab == "anexo2":
        datos_anexo2 = CompensacionService.calcular_anexo2_mes(anio, mes_anexo2)
        rotaciones_mes = CompensacionRepository.get_rotaciones_mes(anio, mes_anexo2)

    # Reporte mensual de gastos y saldos restantes
    reporte_gastos = []
    if tab == "reporte_gastos":
        reporte_gastos = CompensacionRepository.get_reporte_mensual_gastos(anio, mes_reporte)

    # Indicadores globales
    total_servidores = len(matriz_anexo3)
    total_dias_ganados_anual = sum(r["total_ganado"] for r in matriz_anexo3)

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
            "mes_reporte": mes_reporte,
            "meses": MESES_NOMBRES,
            "matriz_anexo3": matriz_anexo3,
            "grupos_guardia": grupos_guardia,
            "datos_anexo2": datos_anexo2,
            "rotaciones_mes": rotaciones_mes,
            "saldos": saldos,
            "solicitudes": solicitudes,
            "reporte_gastos": reporte_gastos,
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
    Calcula el Anexo 02 del mes por grupos y persiste los días de exceso ganados en el Anexo 03.
    """
    res = CompensacionService.calcular_anexo2_mes(anio, mes)
    if res.get("grupos"):
        CompensacionService.guardar_anexo2_en_db(anio, mes, res["grupos"])
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&mensaje=Anexo+02+de+{mes:02d}/{anio}+calculado+exitosamente+con+{res['total_exceso_mes']}+días+de+exceso+ganados.",
            status_code=303
        )
    else:
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&error=No+se+encontraron+datos+de+asistencia+para+el+mes+{mes}.",
            status_code=303
        )

@router.post("/rotacion/registrar")
async def registrar_rotacion_grupo(
    id_empleado: int = Form(...),
    anio: int = Form(2026),
    mes: int = Form(...),
    grupo_origen: str = Form(...),
    grupo_destino: str = Form(...),
    fecha_rotacion: str = Form(...),
    numero_memorando: str = Form(...),
    modalidad_dia_cambio: str = Form("24_HORAS"),
    observaciones: str = Form("")
):
    """
    Registra la rotación oficial de grupo mediante Memorando y actualiza el Anexo 02.
    """
    try:
        CompensacionRepository.registrar_rotacion_grupo(
            id_empleado=id_empleado,
            anio=anio,
            mes=mes,
            grupo_origen=grupo_origen,
            grupo_destino=grupo_destino,
            fecha_rotacion=fecha_rotacion,
            numero_memorando=numero_memorando,
            modalidad_dia_cambio=modalidad_dia_cambio,
            observaciones=observaciones
        )
        # Recalcular inmediatamente el Anexo 02 de ese mes
        res = CompensacionService.calcular_anexo2_mes(anio, mes)
        if res.get("grupos"):
            CompensacionService.guardar_anexo2_en_db(anio, mes, res["grupos"])

        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&mensaje=Rotación+registrada+correctamente+según+{numero_memorando}.+Historial+actualizado.",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&error={str(e)}",
            status_code=303
        )

@router.post("/rotacion/eliminar/{id_rotacion}")
async def eliminar_rotacion_grupo(
    id_rotacion: int,
    anio: int = Form(2026),
    mes: int = Form(...)
):
    """
    Anula una rotación y recalcula el rol preservando la historia previa.
    """
    try:
        CompensacionRepository.eliminar_rotacion_grupo(id_rotacion)
        res = CompensacionService.calcular_anexo2_mes(anio, mes)
        if res.get("grupos"):
            CompensacionService.guardar_anexo2_en_db(anio, mes, res["grupos"])

        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&mensaje=Rotación+revertida+correctamente.+Rol+restaurado.",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&error={str(e)}",
            status_code=303
        )

@router.post("/alcaide/asignar")
async def asignar_alcaide_grupo(
    id_grupo: int = Form(...),
    id_alcaide: int = Form(...),
    anio: int = Form(2026),
    mes: int = Form(1)
):
    """
    Asigna o actualiza el Alcaide / Responsable de un Grupo de Guardia,
    trasladándolo automáticamente a su nuevo grupo.
    """
    try:
        CompensacionRepository.asignar_alcaide_grupo(id_grupo, id_alcaide)
        res = CompensacionService.calcular_anexo2_mes(anio, mes)
        if res.get("grupos"):
            CompensacionService.guardar_anexo2_en_db(anio, mes, res["grupos"])

        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&mensaje=Alcaide+del+Grupo+{id_grupo}+asignado+correctamente+y+trasladado+a+su+grupo.",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&error={str(e)}",
            status_code=303
        )

@router.post("/empleado/cambiar-grupo")
async def cambiar_grupo_empleado(
    id_empleado: int = Form(...),
    id_grupo: int = Form(...),
    anio: int = Form(2026),
    mes: int = Form(1)
):
    """
    Traslada a un servidor directamente a otro grupo para acomodar los grupos iniciales.
    """
    try:
        CompensacionRepository.cambiar_grupo_empleado(id_empleado, id_grupo, anio, mes)
        res = CompensacionService.calcular_anexo2_mes(anio, mes)
        if res.get("grupos"):
            CompensacionService.guardar_anexo2_en_db(anio, mes, res["grupos"])

        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&mensaje=Servidor+trasladado+al+Grupo+{id_grupo}+correctamente.",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            f"/compensacion?tab=anexo2&mes_anexo2={mes}&anio={anio}&error={str(e)}",
            status_code=303
        )

@router.post("/solicitud/registrar")
async def registrar_solicitud_compensacion(
    id_empleado: int = Form(...),
    anio_goce: int = Form(2026),
    mes: int = Form(...),
    fecha_solicitud: str = Form(...),
    fecha_compensacion: str = Form(...),
    dias_solicitados: int = Form(...),
    fechas_compensacion_detalle: str = Form(""),
    numero_solicitud: str = Form(""),
    observaciones: str = Form("")
):
    """
    Registra la Solicitud de Compensación formal (1 o múltiples días/turnos)
    descontando del saldo disponible y registrando saldo anterior y restante.
    """
    res = CompensacionService.registrar_solicitud_compensacion(
        id_empleado=id_empleado,
        anio_goce=anio_goce,
        mes=mes,
        fecha_solicitud=fecha_solicitud,
        fecha_compensacion=fecha_compensacion,
        dias_solicitados=dias_solicitados,
        fechas_compensacion_detalle=fechas_compensacion_detalle,
        numero_solicitud=numero_solicitud,
        observaciones=observaciones
    )
    if res["success"]:
        return RedirectResponse(f"/compensacion?tab=solicitudes&mensaje={res['message']}", status_code=303)
    else:
        return RedirectResponse(f"/compensacion?tab=solicitudes&error={res['message']}", status_code=303)

@router.post("/solicitud/eliminar/{id_solicitud}")
async def eliminar_solicitud(id_solicitud: int):
    """
    Elimina una solicitud de compensación y reintegra los días solicitados al saldo del servidor.
    """
    res = CompensacionRepository.eliminar_solicitud_compensacion(id_solicitud)
    if res["success"]:
        return RedirectResponse(f"/compensacion?tab=solicitudes&mensaje={res['message']}", status_code=303)
    else:
        return RedirectResponse(f"/compensacion?tab=solicitudes&error={res['message']}", status_code=303)

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


@router.get("/solicitudes")
@router.get("/solicitud")
async def redirigir_a_tab_solicitudes():
    """
    Redirige al apartado oficial de Solicitudes de Compensacion (Control de Saldos).
    """
    return RedirectResponse("/compensacion?tab=solicitudes", status_code=303)
