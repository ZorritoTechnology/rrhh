from typing import Optional
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.modules.empleados.service import EmpleadoService
from app.modules.empleados.models import EmpleadoCreate

router = APIRouter(prefix="/empleados", tags=["Empleados"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def padron_empleados(request: Request, mensaje: str = None, error: str = None):
    personal = EmpleadoService.listar_personal()
    total = len(personal)
    total_seg = sum(1 for p in personal if p.get("area_clasificacion") == "SEG")
    total_adm = sum(1 for p in personal if p.get("area_clasificacion") == "ADM")
    total_tra = sum(1 for p in personal if p.get("area_clasificacion") == "TRA")
    total_desp = sum(1 for p in personal if p.get("estado_laboral") == "DESPLAZADO")
    total_lic = sum(1 for p in personal if "LICENCIA" in str(p.get("estado_laboral", "")))
    total_cesados = sum(1 for p in personal if p.get("estado_laboral") == "CESADO")

    return templates.TemplateResponse(
        request=request,
        name="empleados/padron.html",
        context={
            "personal": personal,
            "total": total,
            "total_seg": total_seg,
            "total_adm": total_adm,
            "total_tra": total_tra,
            "total_desp": total_desp,
            "total_lic": total_lic,
            "total_cesados": total_cesados,
            "mensaje": mensaje,
            "error": error
        }
    )

@router.get("/{id_empleado}")
async def obtener_detalle_empleado(id_empleado: int):
    emp = EmpleadoService.obtener_empleado(id_empleado)
    if not emp:
        return JSONResponse(status_code=404, content={"error": "Servidor no encontrado"})
    return JSONResponse(content=emp)

@router.post("/editar/{id_empleado}")
async def editar_empleado(
    id_empleado: int,
    codigo_servidor: str = Form(...),
    dni: str = Form(""),
    apellidos_nombres: str = Form(...),
    sexo: str = Form("M"),
    fecha_nacimiento: Optional[str] = Form(None),
    correo: Optional[str] = Form(""),
    regimen_nombre: Optional[str] = Form("Ley N° 29709"),
    nivel: Optional[str] = Form("T1"),
    cargo_estructural: Optional[str] = Form(""),
    cargo_funcion: Optional[str] = Form(""),
    area_clasificacion: Optional[str] = Form("SEG"),
    horario_laboral: Optional[str] = Form("24 x 48"),
    estado_laboral: Optional[str] = Form("ACTIVO"),
    modalidad_laboral: Optional[str] = Form("PRESENCIAL"),
    direccion_oficina: Optional[str] = Form(""),
    jefatura_area: Optional[str] = Form(""),
    fecha_ingreso_inpe: Optional[str] = Form(None),
    fecha_ingreso_eepp: Optional[str] = Form(None),
    resolucion_documento: Optional[str] = Form(""),
    observaciones: Optional[str] = Form("")
):
    try:
        # Determinar id_regimen
        id_reg = 1
        if "276" in str(regimen_nombre):
            id_reg = 2
        elif "1057" in str(regimen_nombre) or "CAS" in str(regimen_nombre).upper():
            id_reg = 3

        datos = {
            "codigo_servidor": codigo_servidor.strip(),
            "dni": dni.strip() if dni else None,
            "apellidos_nombres": apellidos_nombres.strip().upper(),
            "sexo": sexo.strip().upper() if sexo else "M",
            "fecha_nacimiento": fecha_nacimiento if fecha_nacimiento else None,
            "correo": correo.strip().lower() if correo else "",
            "id_regimen": id_reg,
            "regimen_nombre": regimen_nombre.strip(),
            "nivel": nivel.strip() if nivel else "T1",
            "cargo_estructural": cargo_estructural.strip() if cargo_estructural else "",
            "cargo_funcion": cargo_funcion.strip() if cargo_funcion else "",
            "area_clasificacion": area_clasificacion.strip() if area_clasificacion else "SEG",
            "horario_laboral": horario_laboral.strip() if horario_laboral else "24 x 48",
            "estado_laboral": estado_laboral.strip() if estado_laboral else "ACTIVO",
            "modalidad_laboral": modalidad_laboral.strip() if modalidad_laboral else "PRESENCIAL",
            "direccion_oficina": direccion_oficina.strip() if direccion_oficina else "",
            "jefatura_area": jefatura_area.strip() if jefatura_area else "",
            "fecha_ingreso_inpe": fecha_ingreso_inpe if fecha_ingreso_inpe else None,
            "fecha_ingreso_eepp": fecha_ingreso_eepp if fecha_ingreso_eepp else None,
            "resolucion_documento": resolucion_documento.strip() if resolucion_documento else "",
            "observaciones": observaciones.strip() if observaciones else ""
        }

        EmpleadoService.actualizar_empleado(id_empleado, datos)
        if request.headers.get("referer") and "legajo" in request.headers.get("referer"):
            return RedirectResponse(
                url=f"/empleados/legajo/{id_empleado}?mensaje=Legajo+actualizado+correctamente",
                status_code=303
            )
        return RedirectResponse(
            url=f"/empleados?mensaje=Legajo+de+{apellidos_nombres}+actualizado+correctamente",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(url=f"/empleados?error={str(e)}", status_code=303)

@router.get("/legajo/{id_empleado}", response_class=HTMLResponse)
async def ver_legajo_expediente(request: Request, id_empleado: int, mensaje: str = None, error: str = None):
    expediente = EmpleadoService.obtener_expediente(id_empleado)
    if not expediente or not expediente.get("empleado"):
        return RedirectResponse(url="/empleados?error=Servidor+no+encontrado", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="empleados/legajo_detalle.html",
        context={
            "exp": expediente,
            "emp": expediente["empleado"],
            "historial": expediente["historial_laboral"],
            "sanciones": expediente["sanciones"],
            "vacaciones_gozadas": expediente["vacaciones_gozadas"],
            "compensacion_saldo": expediente["compensacion_saldo"],
            "compensacion_solicitudes": expediente["compensacion_solicitudes"],
            "licencias": expediente["licencias"],
            "desplazamientos": expediente["desplazamientos"],
            "vac_info": expediente["empleado"].get("vacaciones_info", {}),
            "record_laboral": expediente.get("record_laboral"),
            "mensaje": mensaje,
            "error": error
        }
    )

@router.post("/legajo/{id_empleado}/historial")
async def agregar_hito_carrera(
    id_empleado: int,
    tipo_evento: str = Form(...),
    fecha_evento: str = Form(...),
    regimen_laboral: Optional[str] = Form(None),
    nivel_cargo: Optional[str] = Form(None),
    cargo_funcion: Optional[str] = Form(None),
    resolucion_documento: Optional[str] = Form(""),
    detalles: Optional[str] = Form("")
):
    try:
        datos = {
            "tipo_evento": tipo_evento.strip().upper(),
            "fecha_evento": fecha_evento.strip(),
            "regimen_laboral": regimen_laboral.strip() if regimen_laboral else None,
            "nivel_cargo": nivel_cargo.strip().upper() if nivel_cargo else None,
            "cargo_funcion": cargo_funcion.strip().upper() if cargo_funcion else None,
            "resolucion_documento": resolucion_documento.strip() if resolucion_documento else "S/N",
            "detalles": detalles.strip() if detalles else ""
        }
        EmpleadoService.registrar_hito_carrera(id_empleado, datos)
        return RedirectResponse(
            url=f"/empleados/legajo/{id_empleado}?mensaje=Hito+de+carrera+registrado+con+%C3%A9xito",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/empleados/legajo/{id_empleado}?error={str(e)}",
            status_code=303
        )

@router.post("/legajo/{id_empleado}/sancion")
async def registrar_sancion_legajo(
    id_empleado: int,
    tipo_sancion: str = Form(...),
    documento_resolucion: str = Form(...),
    fecha_resolucion: Optional[str] = Form(None),
    fecha_inicio: Optional[str] = Form(None),
    fecha_fin: Optional[str] = Form(None),
    dias_sancion: int = Form(0),
    motivo_falta: Optional[str] = Form(""),
    tiempo_que_resuelve: Optional[str] = Form("EN DIAS"),
    observaciones: Optional[str] = Form("")
):
    try:
        datos = {
            "tipo_sancion": tipo_sancion.strip().upper(),
            "documento_resolucion": documento_resolucion.strip(),
            "fecha_resolucion": fecha_resolucion if fecha_resolucion else None,
            "fecha_inicio": fecha_inicio if fecha_inicio else None,
            "fecha_fin": fecha_fin if fecha_fin else None,
            "dias_sancion": dias_sancion,
            "motivo_falta": motivo_falta.strip() if motivo_falta else "",
            "tiempo_que_resuelve": tiempo_que_resuelve.strip() if tiempo_que_resuelve else "EN DIAS",
            "observaciones": observaciones.strip() if observaciones else "",
            "estado_sancion": "EJECUTADA"
        }
        EmpleadoService.registrar_sancion(id_empleado, datos)
        return RedirectResponse(
            url=f"/empleados/legajo/{id_empleado}?mensaje=Sanci%C3%B3n+disciplinaria+incorporada+al+expediente",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/empleados/legajo/{id_empleado}?error={str(e)}",
            status_code=303
        )

@router.post("/nuevo")
async def nuevo_empleado(
    codigo_servidor: str = Form(...),
    dni: str = Form(""),
    apellidos_nombres: str = Form(...)
):
    try:
        nuevo = EmpleadoCreate(
            codigo_servidor=codigo_servidor,
            dni=dni if dni.strip() else None,
            apellidos_nombres=apellidos_nombres
        )
        EmpleadoService.registrar_empleado(nuevo)
        return RedirectResponse(url="/empleados?mensaje=Servidor+registrado+exitosamente", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/empleados?error={str(e)}", status_code=303)

@router.get("/record-laboral/{id_empleado}", response_class=HTMLResponse)
async def ver_formulario_record_laboral(request: Request, id_empleado: int, mensaje: str = None, error: str = None):
    emp = EmpleadoService.obtener_empleado(id_empleado)
    if not emp:
        return RedirectResponse(url="/empleados?error=Servidor+no+encontrado", status_code=303)

    record = EmpleadoService.obtener_record_laboral(id_empleado)
    # Valores predeterminados si no existe
    if not record:
        record = {
            "id_empleado": id_empleado,
            "tipo_proceso": "LIQUIDACION_CAS",
            "regimen_laboral": emp.get("regimen_nombre", "D.L. Nº 1057 CAS"),
            "cargo_funcion": emp.get("cargo_funcion", emp.get("cargo_estructural", "")),
            "dependencia_region": "EP MUJERES IQUITOS",
            "numero_celular": "",
            "fecha_ingreso_entidad": emp.get("fecha_ingreso_eepp") or emp.get("fecha_ingreso_inpe") or "",
            "ultimo_dia_laborado": "2025-12-31",
            "fecha_cese_laboral": "2025-12-31",
            "motivo_cese": "EXTINCIÓN DE CONTRATO Carta N° D001999-2025-INPE-URH",
            "documento_sustento": "Carta N° D001999-2025-INPE-URH",
            "vacaciones_periodo_1_anio": "2024",
            "vacaciones_periodo_1_ini": "x",
            "vacaciones_periodo_1_fin": "x",
            "vacaciones_periodo_1_gozadas": 0,
            "vacaciones_periodo_1_pendientes": 0,
            "vacaciones_periodo_2_anio": "2025",
            "vacaciones_periodo_2_ini": "30/09/2025",
            "vacaciones_periodo_2_fin": "31/12/2025",
            "vacaciones_periodo_2_gozadas": 0,
            "vacaciones_periodo_2_pendientes": 7.66,
            "vacaciones_no_gozadas_truncas": 8,
            "asistencia_rango_periodo": "01/12/2025 al 31/12/2025",
            "inasistencias_dias_minutos": "-",
            "inasistencias_fechas": "",
            "tardanzas_dias_minutos": "-",
            "tardanzas_fechas": "",
            "particulares_dias_minutos": "-",
            "particulares_fechas": "",
            "horas_compensar_total": "0",
            "horas_compensar_detalle": "",
            "observaciones": "NINGUNA",
            "responsable_rrhh": "Jefe de Recursos Humanos y/o Responsable de Control de Personal"
        }

    return templates.TemplateResponse(
        request=request,
        name="empleados/record_laboral_form.html",
        context={
            "emp": emp,
            "rec": record,
            "mensaje": mensaje,
            "error": error
        }
    )

@router.post("/record-laboral/{id_empleado}")
async def guardar_record_laboral(
    id_empleado: int,
    tipo_proceso: str = Form("LIQUIDACION_CAS"),
    regimen_laboral: str = Form("D.L. Nº 1057 CAS"),
    cargo_funcion: str = Form(""),
    dependencia_region: str = Form("EP MUJERES IQUITOS"),
    numero_celular: Optional[str] = Form(""),
    fecha_ingreso_entidad: Optional[str] = Form(None),
    ultimo_dia_laborado: Optional[str] = Form(None),
    fecha_cese_laboral: Optional[str] = Form(None),
    motivo_cese: str = Form(""),
    documento_sustento: Optional[str] = Form(""),
    vacaciones_periodo_1_anio: Optional[str] = Form("2024"),
    vacaciones_periodo_1_ini: Optional[str] = Form("x"),
    vacaciones_periodo_1_fin: Optional[str] = Form("x"),
    vacaciones_periodo_1_gozadas: float = Form(0),
    vacaciones_periodo_1_pendientes: float = Form(0),
    vacaciones_periodo_2_anio: Optional[str] = Form("2025"),
    vacaciones_periodo_2_ini: Optional[str] = Form(""),
    vacaciones_periodo_2_fin: Optional[str] = Form(""),
    vacaciones_periodo_2_gozadas: float = Form(0),
    vacaciones_periodo_2_pendientes: float = Form(0),
    vacaciones_no_gozadas_truncas: int = Form(0),
    asistencia_rango_periodo: Optional[str] = Form(""),
    inasistencias_dias_minutos: Optional[str] = Form("-"),
    inasistencias_fechas: Optional[str] = Form(""),
    tardanzas_dias_minutos: Optional[str] = Form("-"),
    tardanzas_fechas: Optional[str] = Form(""),
    particulares_dias_minutos: Optional[str] = Form("-"),
    particulares_fechas: Optional[str] = Form(""),
    horas_compensar_total: Optional[str] = Form("0"),
    horas_compensar_detalle: Optional[str] = Form(""),
    observaciones: Optional[str] = Form("NINGUNA"),
    responsable_rrhh: Optional[str] = Form("Jefe de Recursos Humanos y/o Responsable de Control de Personal")
):
    try:
        datos = {
            "tipo_proceso": tipo_proceso.strip(),
            "regimen_laboral": regimen_laboral.strip(),
            "cargo_funcion": cargo_funcion.strip(),
            "dependencia_region": dependencia_region.strip(),
            "numero_celular": numero_celular.strip() if numero_celular else "",
            "fecha_ingreso_entidad": fecha_ingreso_entidad if fecha_ingreso_entidad else None,
            "ultimo_dia_laborado": ultimo_dia_laborado if ultimo_dia_laborado else None,
            "fecha_cese_laboral": fecha_cese_laboral if fecha_cese_laboral else None,
            "motivo_cese": motivo_cese.strip(),
            "documento_sustento": documento_sustento.strip() if documento_sustento else "",
            "vacaciones_periodo_1_anio": vacaciones_periodo_1_anio,
            "vacaciones_periodo_1_ini": vacaciones_periodo_1_ini,
            "vacaciones_periodo_1_fin": vacaciones_periodo_1_fin,
            "vacaciones_periodo_1_gozadas": vacaciones_periodo_1_gozadas,
            "vacaciones_periodo_1_pendientes": vacaciones_periodo_1_pendientes,
            "vacaciones_periodo_2_anio": vacaciones_periodo_2_anio,
            "vacaciones_periodo_2_ini": vacaciones_periodo_2_ini,
            "vacaciones_periodo_2_fin": vacaciones_periodo_2_fin,
            "vacaciones_periodo_2_gozadas": vacaciones_periodo_2_gozadas,
            "vacaciones_periodo_2_pendientes": vacaciones_periodo_2_pendientes,
            "vacaciones_no_gozadas_truncas": vacaciones_no_gozadas_truncas,
            "asistencia_rango_periodo": asistencia_rango_periodo,
            "inasistencias_dias_minutos": inasistencias_dias_minutos,
            "inasistencias_fechas": inasistencias_fechas,
            "tardanzas_dias_minutos": tardanzas_dias_minutos,
            "tardanzas_fechas": tardanzas_fechas,
            "particulares_dias_minutos": particulares_dias_minutos,
            "particulares_fechas": particulares_fechas,
            "horas_compensar_total": horas_compensar_total,
            "horas_compensar_detalle": horas_compensar_detalle,
            "observaciones": observaciones if observaciones else "NINGUNA",
            "responsable_rrhh": responsable_rrhh
        }

        EmpleadoService.guardar_record_laboral(id_empleado, datos)
        return RedirectResponse(
            url=f"/empleados/record-laboral/{id_empleado}?mensaje=R%C3%A9cord+laboral+de+liquidaci%C3%B3n+guardado+correctamente",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/empleados/record-laboral/{id_empleado}?error={str(e)}",
            status_code=303
        )

@router.get("/record-laboral/{id_empleado}/imprimir", response_class=HTMLResponse)
async def imprimir_record_laboral(request: Request, id_empleado: int):
    emp = EmpleadoService.obtener_empleado(id_empleado)
    if not emp:
        return RedirectResponse(url="/empleados?error=Servidor+no+encontrado", status_code=303)

    record = EmpleadoService.obtener_record_laboral(id_empleado)
    if not record:
        return RedirectResponse(url=f"/empleados/record-laboral/{id_empleado}?error=A%C3%BAn+no+se+ha+generado+el+r%C3%A9cord+laboral", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="empleados/record_laboral_imprimir.html",
        context={
            "emp": emp,
            "rec": record
        }
    )


