from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.modules.asistencia.service import AsistenciaService
from app.modules.asistencia.repository import AsistenciaRepository
from app.modules.empleados.service import EmpleadoService

router = APIRouter(prefix="/asistencia", tags=["Asistencia"])
templates = Jinja2Templates(directory="app/templates")

MESES_NOMBRES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Setiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
]

@router.get("/llenado-2026", response_class=HTMLResponse)
async def ver_llenado_2026(request: Request, mes: int = 1, tab: str = "personal", mensaje: str = None, error: str = None):
    datos_mes = AsistenciaService.obtener_libro_mes(anio=2026, mes=mes)
    empleados = EmpleadoService.listar_personal()
    
    return templates.TemplateResponse(
        request=request,
        name="asistencia/libro_mensual_2026.html",
        context={
            "mes_seleccionado": mes,
            "tab_activa": tab,
            "meses": MESES_NOMBRES,
            "empleados": empleados,
            "datos_mes": datos_mes,
            "libro": datos_mes["libro"],
            "counts": datos_mes["counts"],
            "catalogos": datos_mes["catalogos"],
            "mensaje": mensaje,
            "error": error
        }
    )

# Endpoints modulares para registrar cada tipo de registro oficial

@router.post("/guardar-personal-mes")
async def guardar_personal_mes(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    id_regimen: int = Form(...),
    nivel: str = Form(""),
    cargo_estructural: str = Form(""),
    estado_laboral: str = Form("ACTIVO"),
    modalidad_laboral: str = Form("PRESENCIAL"),
    direccion_oficina: str = Form(""),
    jefatura_area: str = Form(""),
    cargo_funcion: str = Form(""),
    area_clasificacion: str = Form("SEG"),
    horario_laboral: str = Form("24 x 48"),
    fecha_ingreso_eepp: str = Form(""),
    resolucion_documento: str = Form(""),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_personal_mes(
            id_reporte=rep_id, id_empleado=id_empleado, id_regimen=id_regimen, nivel=nivel,
            cargo_estructural=cargo_estructural, estado_laboral=estado_laboral, modalidad_laboral=modalidad_laboral,
            direccion_oficina=direccion_oficina, jefatura_area=jefatura_area, cargo_funcion=cargo_funcion,
            area_clasificacion=area_clasificacion, horario_laboral=horario_laboral,
            fecha_ingreso_eepp=fecha_ingreso_eepp, resolucion_documento=resolucion_documento, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=personal&mensaje=Servidor+agregado+a+la+plantilla+del+mes", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=personal&error={str(e)}", status_code=303)

@router.post("/guardar-funcionario")
async def guardar_funcionario(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    cargo_funcion: str = Form("DIRECTORA"),
    nivel: str = Form("S4"),
    fecha_inicio_funciones: str = Form(""),
    resolucion_documento: str = Form(""),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_funcionario(
            id_reporte=rep_id, id_empleado=id_empleado, cargo_funcion=cargo_funcion,
            nivel=nivel, fecha_inicio_funciones=fecha_inicio_funciones,
            resolucion_documento=resolucion_documento, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=funcionarios&mensaje=Funcionario+registrado+correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=funcionarios&error={str(e)}", status_code=303)

@router.post("/guardar-sancion")
async def guardar_sancion(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    tipo_sancion: str = Form(...),
    fecha_inicio: str = Form(""),
    fecha_termino: str = Form(""),
    dias: int = Form(0),
    tiempo_que_resuelve: str = Form(""),
    resolucion_documento: str = Form(""),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_sancion(
            id_reporte=rep_id, id_empleado=id_empleado, tipo_sancion=tipo_sancion,
            fecha_inicio=fecha_inicio, fecha_termino=fecha_termino, dias=dias,
            tiempo_que_resuelve=tiempo_que_resuelve, resolucion_documento=resolucion_documento, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=sanciones&mensaje=Sanción+registrada+correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=sanciones&error={str(e)}", status_code=303)

@router.post("/guardar-renuncia")
async def guardar_renuncia(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    a_partir_del: str = Form(""),
    carta_fecha: str = Form(""),
    fecha_recepcion: str = Form(""),
    motivos: str = Form(""),
    ultimo_dia_laborado: str = Form(""),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_renuncia(
            id_reporte=rep_id, id_empleado=id_empleado, a_partir_del=a_partir_del,
            carta_fecha=carta_fecha, fecha_recepcion=fecha_recepcion, motivos=motivos,
            ultimo_dia_laborado=ultimo_dia_laborado, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=renuncias&mensaje=Renuncia+registrada+correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=renuncias&error={str(e)}", status_code=303)

@router.post("/guardar-reincorporacion")
async def guardar_reincorporacion(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    fecha_inicio_inactividad: str = Form(""),
    motivo_inactividad: str = Form(""),
    fecha_reincorporacion: str = Form(""),
    motivo_reincorporacion: str = Form(""),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_reincorporacion(
            id_reporte=rep_id, id_empleado=id_empleado, fecha_inicio_inactividad=fecha_inicio_inactividad,
            motivo_inactividad=motivo_inactividad, fecha_reincorporacion=fecha_reincorporacion,
            motivo_reincorporacion=motivo_reincorporacion, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=reincorporaciones&mensaje=Reincorporación+registrada", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=reincorporaciones&error={str(e)}", status_code=303)

@router.post("/guardar-desplazamiento")
async def guardar_desplazamiento(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    area: str = Form(""),
    cargo_funcion: str = Form(""),
    fecha: str = Form(""),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_desplazamiento(
            id_reporte=rep_id, id_empleado=id_empleado, area=area,
            cargo_funcion=cargo_funcion, fecha=fecha, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=desplazamientos&mensaje=Desplazamiento+guardado", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=desplazamientos&error={str(e)}", status_code=303)

@router.post("/guardar-licencia")
async def guardar_licencia(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    tipo: str = Form("ENFERMEDAD"),
    entidad: str = Form("ESSALUD"),
    fecha_inicio: str = Form(...),
    fecha_termino: str = Form(...),
    dias: int = Form(1),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_licencia(
            id_reporte=rep_id, id_empleado=id_empleado, tipo=tipo, entidad=entidad,
            fecha_inicio=fecha_inicio, fecha_termino=fecha_termino, dias=dias, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=licencias&mensaje=Licencia+registrada+correctamente", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=licencias&error={str(e)}", status_code=303)

@router.post("/guardar-vacacion")
async def guardar_vacacion(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    periodo: str = Form("2025"),
    fecha_inicio: str = Form(...),
    fecha_termino: str = Form(...),
    dias: int = Form(1),
    observaciones: str = Form("")
):
    try:
        from app.modules.vacaciones.repository import VacacionesRepository
        from app.core.database import get_connection

        # 1. Validación de orden de fechas
        if fecha_termino < fecha_inicio:
            raise ValueError(f"La fecha de término ({fecha_termino}) no puede ser anterior a la fecha de inicio ({fecha_inicio}).")

        # 2. Validación de Cruce / Solapamiento de fechas con otras vacaciones ya registradas para el empleado
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT v.id_vacacion, v.fecha_inicio, v.fecha_termino, v.periodo, r.mes, r.anio
                FROM reporte_vacaciones v
                JOIN reportes_cierre_mensual r ON v.id_reporte = r.id_reporte
                WHERE v.id_empleado = ?
                  AND NOT (v.fecha_termino < ? OR v.fecha_inicio > ?)
            """, (id_empleado, fecha_inicio, fecha_termino))
            cruce = cur.fetchone()
            if cruce:
                raise ValueError(
                    f"Cruce de fechas detectado: El servidor ya tiene vacaciones programadas del {cruce['fecha_inicio']} al {cruce['fecha_termino']} (Período {cruce['periodo']} - Reporte {cruce['mes']}/{cruce['anio']})."
                )

        # 3. Validación de Saldo Máximo (30 días por período anual)
        saldo_info = VacacionesRepository.obtener_saldo_personal_periodo(id_empleado=id_empleado, periodo=periodo)
        saldo_disponible = saldo_info["saldo_restante"]

        if dias > saldo_disponible:
            raise ValueError(
                f"Exceso de vacaciones: Solo dispone de {saldo_disponible} días de saldo para el período {periodo} (ya gozó {saldo_info['dias_gozados']} de {saldo_info['dias_derecho']} días). No se pueden registrar {dias} días."
            )

        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_vacacion(
            id_reporte=rep_id, id_empleado=id_empleado, periodo=periodo,
            fecha_inicio=fecha_inicio, fecha_termino=fecha_termino, dias=dias, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=vacaciones&mensaje=Vacaciones+registradas+correctamente+(Saldo+restante:+{saldo_disponible - dias}+días)", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=vacaciones&error={str(e)}", status_code=303)


@router.post("/guardar-tardanza")
async def guardar_tardanza(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    minutos: int = Form(...),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_tardanza(
            id_reporte=rep_id, id_empleado=id_empleado, minutos=minutos, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=tardanzas&mensaje=Tardanza+registrada", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=tardanzas&error={str(e)}", status_code=303)

@router.post("/guardar-permiso")
async def guardar_permiso(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    minutos: int = Form(...),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_permiso(
            id_reporte=rep_id, id_empleado=id_empleado, minutos=minutos, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=permisos&mensaje=Permiso+particular+registrado", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=permisos&error={str(e)}", status_code=303)

@router.post("/guardar-inasistencia")
async def guardar_inasistencia(
    anio: int = Form(2026),
    mes: int = Form(...),
    id_empleado: int = Form(...),
    dias: int = Form(1),
    fechas_detalle: str = Form(""),
    observaciones: str = Form("")
):
    try:
        rep_id = AsistenciaService.asegurar_reporte_mes(anio, mes)
        AsistenciaRepository.insert_inasistencia(
            id_reporte=rep_id, id_empleado=id_empleado, dias=dias,
            fechas_detalle=fechas_detalle, observaciones=observaciones
        )
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=inasistencias&mensaje=Inasistencia+registrada", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab=inasistencias&error={str(e)}", status_code=303)

@router.post("/eliminar-registro")
async def eliminar_registro(
    tabla: str = Form(...),
    pk_col: str = Form(...),
    id_valor: int = Form(...),
    mes: int = Form(...),
    tab: str = Form("personal")
):
    try:
        AsistenciaService.eliminar_registro(tabla=tabla, pk_col=pk_col, id_valor=id_valor)
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab={tab}&mensaje=Registro+eliminado+exitosamente", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&tab={tab}&error={str(e)}", status_code=303)

@router.post("/cerrar-mes")
async def cerrar_mes(anio: int = Form(2026), mes: int = Form(...)):
    try:
        AsistenciaService.cerrar_mes(anio=anio, mes=mes)
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&mensaje=Mes+{mes}%2F{anio}+CERRADO+oficialmente.+Los+registros+quedan+validados+y+protegidos.", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&error={str(e)}", status_code=303)

@router.post("/reabrir-mes")
async def reabrir_mes(anio: int = Form(2026), mes: int = Form(...)):
    try:
        AsistenciaService.reabrir_mes(anio=anio, mes=mes)
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&mensaje=Mes+{mes}%2F{anio}+REABIERTO+para+edici%C3%B3n+y+ajustes.", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&error={str(e)}", status_code=303)

@router.post("/clonar-mes-anterior")
async def clonar_mes_anterior(anio: int = Form(2026), mes: int = Form(...)):
    try:
        total = AsistenciaService.clonar_plantilla_mes_anterior(anio=anio, mes=mes)
        if total > 0:
            return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&mensaje=Se+traspasaron+exitosamente+{total}+servidores+del+mes+anterior+como+plantilla+continua.", status_code=303)
        else:
            return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&error=No+se+encontraron+registros+en+el+mes+anterior+para+traspasar.", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/asistencia/llenado-2026?mes={mes}&error={str(e)}", status_code=303)

@router.get("/reportes", response_class=HTMLResponse)
async def historial_reportes(request: Request):
    historial = AsistenciaService.obtener_historial_reportes()
    return templates.TemplateResponse(
        request=request,
        name="asistencia/historial.html",
        context={"historial": historial}
    )

