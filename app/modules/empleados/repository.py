from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.core.database import get_connection, get_db_cursor
from app.modules.empleados.models import EmpleadoCreate, EmpleadoOut

def calcular_tiempo_servicio(fecha_str: Optional[str]) -> Dict[str, Any]:
    if not fecha_str:
        return {"texto": "Sin registro", "anios": 0, "meses": 0, "dias": 0}
    try:
        f_ing = datetime.strptime(str(fecha_str)[:10], "%Y-%m-%d").date()
        hoy = date.today()
        if f_ing > hoy:
            return {"texto": "Fecha futura", "anios": 0, "meses": 0, "dias": 0}

        anios = hoy.year - f_ing.year
        meses = hoy.month - f_ing.month
        dias = hoy.day - f_ing.day

        if dias < 0:
            meses -= 1
            dias += 30
        if meses < 0:
            anios -= 1
            meses += 12

        partes = []
        if anios > 0:
            partes.append(f"{anios} año{'s' if anios != 1 else ''}")
        if meses > 0:
            partes.append(f"{meses} mes{'es' if meses != 1 else ''}")
        if not partes:
            partes.append(f"{max(0, dias)} días")

        return {
            "texto": ", ".join(partes),
            "anios": anios,
            "meses": meses,
            "dias": dias
        }
    except Exception:
        return {"texto": "No calculable", "anios": 0, "meses": 0, "dias": 0}

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def calcular_ciclo_vacacional(fecha_str: Optional[str]) -> Dict[str, Any]:
    """
    Calcula el derecho y la fecha exacta en que el servidor genera sus vacaciones
    a partir de su fecha de ingreso al INPE (Art. 36 Ley 29709 / D.L. 276 / D.L. 1057).
    """
    if not fecha_str:
        return {
            "periodo": "No asignado",
            "dia_generacion_texto": "Sin registro",
            "dia": 0,
            "mes_nombre": "",
            "proximo_ciclo": "-",
            "dias_faltantes": 0,
            "dias_derecho": 30,
            "ya_generado_este_anio": False,
            "estado_generacion": "Fecha de ingreso al INPE no registrada",
            "badge_clase": "badge-neutral"
        }
    try:
        f_ing = datetime.strptime(str(fecha_str)[:10], "%Y-%m-%d").date()
        hoy = date.today()
        dia = f_ing.day
        mes = f_ing.month
        dia_texto = f"Cada {dia:02d} de {MESES_ES.get(mes, '')}"

        # Aniversario en el año actual (2026)
        try:
            aniv_actual = date(hoy.year, mes, dia)
        except ValueError:
            aniv_actual = date(hoy.year, mes, 28)

        if aniv_actual <= hoy:
            # Ya cumplió ciclo en el año actual
            ciclo = f"{hoy.year - 1} - {hoy.year}"
            try:
                proximo = date(hoy.year + 1, mes, dia)
            except ValueError:
                proximo = date(hoy.year + 1, mes, 28)
            faltan = (proximo - hoy).days
            estado = f"Ciclo {ciclo} GENERADO el {aniv_actual.strftime('%d/%m/%Y')} (Disponible)"
            badge_clase = "badge-success"
            ya_generado = True
        else:
            # Aún no cumple su fecha aniversario este año
            ciclo = f"{hoy.year - 1} - {hoy.year}"
            proximo = aniv_actual
            faltan = (aniv_actual - hoy).days
            estado = f"Genera Ciclo {ciclo} en {faltan} días (el {aniv_actual.strftime('%d/%m/%Y')})"
            badge_clase = "badge-warning"
            ya_generado = False

        return {
            "periodo": ciclo,
            "dia_generacion_texto": dia_texto,
            "dia": dia,
            "mes_nombre": MESES_ES.get(mes, ""),
            "proximo_ciclo": proximo.strftime("%d/%m/%Y"),
            "proxima_fecha_iso": proximo.isoformat(),
            "dias_faltantes": faltan,
            "dias_derecho": 30,
            "ya_generado_este_anio": ya_generado,
            "estado_generacion": estado,
            "badge_clase": badge_clase
        }
    except Exception:
        return {
            "periodo": "2025 - 2026",
            "dia_generacion_texto": "No calculable",
            "dia": 0,
            "mes_nombre": "",
            "proximo_ciclo": "-",
            "dias_faltantes": 0,
            "dias_derecho": 30,
            "ya_generado_este_anio": False,
            "estado_generacion": "Error en formato de fecha",
            "badge_clase": "badge-neutral"
        }


class EmpleadoRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    id_empleado, codigo_servidor, dni, apellidos_nombres,
                    sexo, fecha_nacimiento, correo, id_regimen, regimen_nombre,
                    nivel, cargo_estructural, estado_laboral, modalidad_laboral,
                    direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                    horario_laboral, fecha_ingreso_eepp, resolucion_documento,
                    observaciones, fecha_ingreso_inpe, grupo_guardia_default, created_at
                FROM empleados 
                ORDER BY apellidos_nombres ASC
            """)
            filas = [dict(row) for row in cur.fetchall()]

            # Mapear desplazamientos para sincronizar estado real
            cur.execute("""
                SELECT id_empleado, tipo_movimiento, fecha_desplazamiento, fecha_presentacion_eepp,
                       nombre_origen_ext, nombre_destino_ext, documento_oficial,
                       numero_constancia_oficial, vacaciones_saldo_origen, comp_saldo_origen, observaciones
                FROM desplazamientos_personal
                ORDER BY fecha_desplazamiento ASC
            """)
            desps = [dict(r) for r in cur.fetchall()]
            desp_map = {}
            for d in desps:
                desp_map.setdefault(d["id_empleado"], []).append(d)

            for emp in filas:
                e_id = emp["id_empleado"]
                emp["tiempo_servicio"] = calcular_tiempo_servicio(emp.get("fecha_ingreso_inpe"))
                emp["vacaciones_info"] = calcular_ciclo_vacacional(emp.get("fecha_ingreso_inpe"))

                # Mapear movimientos de desplazamiento
                e_desps = desp_map.get(e_id, [])
                emp["desplazamientos"] = e_desps
                emp["es_desplazado"] = False
                emp["desplazamiento_texto"] = ""

                for dp in e_desps:
                    if dp["tipo_movimiento"] == "BAJA_SALIDA":
                        emp["es_desplazado"] = True
                        emp["estado_laboral"] = "DESPLAZADO"
                        emp["desplazamiento_destino"] = dp["nombre_destino_ext"]
                        emp["desplazamiento_fecha"] = dp["fecha_desplazamiento"]
                        emp["desplazamiento_doc"] = dp["documento_oficial"]
                        emp["desplazamiento_constancia"] = dp.get("numero_constancia_oficial", "")
                        emp["desplazamiento_texto"] = f"Desplazado a {dp['nombre_destino_ext']} desde {dp['fecha_desplazamiento']}"
                    elif dp["tipo_movimiento"] == "ALTA_RECEPCION":
                        emp["es_alta"] = True
                        emp["alta_origen"] = dp["nombre_origen_ext"]
                        emp["alta_fecha"] = dp["fecha_presentacion_eepp"]
                        emp["alta_texto"] = f"Llegó de {dp['nombre_origen_ext']} el {dp['fecha_presentacion_eepp']}"

            return filas

    @staticmethod
    def get_by_id(id_empleado: int) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    id_empleado, codigo_servidor, dni, apellidos_nombres,
                    sexo, fecha_nacimiento, correo, id_regimen, regimen_nombre,
                    nivel, cargo_estructural, estado_laboral, modalidad_laboral,
                    direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                    horario_laboral, fecha_ingreso_eepp, resolucion_documento,
                    observaciones, fecha_ingreso_inpe, grupo_guardia_default, created_at
                FROM empleados 
                WHERE id_empleado = ?
            """, (id_empleado,))
            row = cur.fetchone()
            if not row:
                return None
            emp = dict(row)
            emp["tiempo_servicio"] = calcular_tiempo_servicio(emp.get("fecha_ingreso_inpe"))
            emp["vacaciones_info"] = calcular_ciclo_vacacional(emp.get("fecha_ingreso_inpe"))

            # Movimientos de desplazamiento
            cur.execute("""
                SELECT id_empleado, tipo_movimiento, fecha_desplazamiento, fecha_presentacion_eepp,
                       nombre_origen_ext, nombre_destino_ext, documento_oficial,
                       numero_constancia_oficial, vacaciones_saldo_origen, comp_saldo_origen, observaciones
                FROM desplazamientos_personal
                WHERE id_empleado = ?
                ORDER BY fecha_desplazamiento ASC
            """, (id_empleado,))
            e_desps = [dict(r) for r in cur.fetchall()]
            emp["desplazamientos"] = e_desps
            emp["es_desplazado"] = False
            emp["desplazamiento_texto"] = ""

            for dp in e_desps:
                if dp["tipo_movimiento"] == "BAJA_SALIDA":
                    emp["es_desplazado"] = True
                    emp["estado_laboral"] = "DESPLAZADO"
                    emp["desplazamiento_destino"] = dp["nombre_destino_ext"]
                    emp["desplazamiento_fecha"] = dp["fecha_desplazamiento"]
                    emp["desplazamiento_doc"] = dp["documento_oficial"]
                    emp["desplazamiento_constancia"] = dp.get("numero_constancia_oficial", "")
                    emp["desplazamiento_texto"] = f"Desplazado a {dp['nombre_destino_ext']} desde {dp['fecha_desplazamiento']}"
                elif dp["tipo_movimiento"] == "ALTA_RECEPCION":
                    emp["es_alta"] = True
                    emp["alta_origen"] = dp["nombre_origen_ext"]
                    emp["alta_fecha"] = dp["fecha_presentacion_eepp"]
                    emp["alta_texto"] = f"Llegó de {dp['nombre_origen_ext']} el {dp['fecha_presentacion_eepp']}"

            return emp

    @staticmethod
    def get_by_codigo(codigo_servidor: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_empleado, codigo_servidor, dni, apellidos_nombres, created_at 
                FROM empleados 
                WHERE codigo_servidor = ?
            """, (codigo_servidor,))
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(empleado: EmpleadoCreate) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO empleados (codigo_servidor, dni, apellidos_nombres)
                VALUES (?, ?, ?)
            """, (empleado.codigo_servidor.strip(), empleado.dni.strip() if empleado.dni else None, empleado.apellidos_nombres.strip().upper()))
            return cur.lastrowid

    @staticmethod
    def update(id_empleado: int, datos: Dict[str, Any]) -> bool:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE empleados SET
                    codigo_servidor = COALESCE(?, codigo_servidor),
                    dni = COALESCE(?, dni),
                    apellidos_nombres = COALESCE(?, apellidos_nombres),
                    sexo = COALESCE(?, sexo),
                    fecha_nacimiento = COALESCE(?, fecha_nacimiento),
                    correo = COALESCE(?, correo),
                    id_regimen = COALESCE(?, id_regimen),
                    regimen_nombre = COALESCE(?, regimen_nombre),
                    nivel = COALESCE(?, nivel),
                    cargo_estructural = COALESCE(?, cargo_estructural),
                    estado_laboral = COALESCE(?, estado_laboral),
                    modalidad_laboral = COALESCE(?, modalidad_laboral),
                    direccion_oficina = COALESCE(?, direccion_oficina),
                    jefatura_area = COALESCE(?, jefatura_area),
                    cargo_funcion = COALESCE(?, cargo_funcion),
                    area_clasificacion = COALESCE(?, area_clasificacion),
                    horario_laboral = COALESCE(?, horario_laboral),
                    fecha_ingreso_eepp = COALESCE(?, fecha_ingreso_eepp),
                    resolucion_documento = COALESCE(?, resolucion_documento),
                    observaciones = COALESCE(?, observaciones),
                    fecha_ingreso_inpe = COALESCE(?, fecha_ingreso_inpe)
                WHERE id_empleado = ?
            """, (
                datos.get("codigo_servidor"),
                datos.get("dni"),
                datos.get("apellidos_nombres"),
                datos.get("sexo"),
                datos.get("fecha_nacimiento"),
                datos.get("correo"),
                datos.get("id_regimen"),
                datos.get("regimen_nombre"),
                datos.get("nivel"),
                datos.get("cargo_estructural"),
                datos.get("estado_laboral"),
                datos.get("modalidad_laboral"),
                datos.get("direccion_oficina"),
                datos.get("jefatura_area"),
                datos.get("cargo_funcion"),
                datos.get("area_clasificacion"),
                datos.get("horario_laboral"),
                datos.get("fecha_ingreso_eepp"),
                datos.get("resolucion_documento"),
                datos.get("observaciones"),
                datos.get("fecha_ingreso_inpe"),
                id_empleado
            ))
            conn.commit()
            return True

    @staticmethod
    def count_total() -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM empleados")
            return cur.fetchone()[0]

    @staticmethod
    def get_historial_laboral(id_empleado: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_historial, id_empleado, tipo_evento, fecha_evento,
                       regimen_laboral, nivel_cargo, cargo_funcion,
                       resolucion_documento, detalles, created_at
                FROM empleados_historial_laboral
                WHERE id_empleado = ?
                ORDER BY fecha_evento ASC, id_historial ASC
            """, (id_empleado,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def registrar_evento_historial(id_empleado: int, datos: Dict[str, Any]) -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO empleados_historial_laboral (
                    id_empleado, tipo_evento, fecha_evento, regimen_laboral,
                    nivel_cargo, cargo_funcion, resolucion_documento, detalles
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_empleado,
                datos.get("tipo_evento", "EVENTO_LABORAL"),
                datos.get("fecha_evento"),
                datos.get("regimen_laboral"),
                datos.get("nivel_cargo"),
                datos.get("cargo_funcion"),
                datos.get("resolucion_documento"),
                datos.get("detalles")
            ))
            # Si se actualizó régimen, cargo o nivel, reflejarlo en la ficha del empleado
            if datos.get("regimen_laboral") or datos.get("nivel_cargo") or datos.get("cargo_funcion"):
                cur.execute("""
                    UPDATE empleados 
                    SET regimen_nombre = COALESCE(?, regimen_nombre),
                        nivel = COALESCE(?, nivel),
                        cargo_funcion = COALESCE(?, cargo_funcion)
                    WHERE id_empleado = ?
                """, (
                    datos.get("regimen_laboral") if datos.get("regimen_laboral") else None,
                    datos.get("nivel_cargo") if datos.get("nivel_cargo") else None,
                    datos.get("cargo_funcion") if datos.get("cargo_funcion") else None,
                    id_empleado
                ))
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def get_sanciones(id_empleado: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_sancion_legajo, id_empleado, tipo_sancion, documento_resolucion,
                       fecha_resolucion, fecha_inicio, fecha_fin, dias_sancion,
                       motivo_falta, estado_sancion, tiempo_que_resuelve, observaciones, created_at
                FROM empleados_sanciones
                WHERE id_empleado = ?
                ORDER BY fecha_inicio DESC, id_sancion_legajo DESC
            """, (id_empleado,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def registrar_sancion(id_empleado: int, datos: Dict[str, Any]) -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO empleados_sanciones (
                    id_empleado, tipo_sancion, documento_resolucion,
                    fecha_resolucion, fecha_inicio, fecha_fin, dias_sancion,
                    motivo_falta, estado_sancion, tiempo_que_resuelve, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_empleado,
                datos.get("tipo_sancion", "AMONESTACION"),
                datos.get("documento_resolucion", "S/N"),
                datos.get("fecha_resolucion"),
                datos.get("fecha_inicio"),
                datos.get("fecha_fin"),
                int(datos.get("dias_sancion") or 0),
                datos.get("motivo_falta"),
                datos.get("estado_sancion", "EJECUTADA"),
                datos.get("tiempo_que_resuelve", "EN DIAS"),
                datos.get("observaciones")
            ))
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def get_expediente_completo(id_empleado: int) -> Optional[Dict[str, Any]]:
        empleado = EmpleadoRepository.get_by_id(id_empleado)
        if not empleado:
            return None

        historial = EmpleadoRepository.get_historial_laboral(id_empleado)
        sanciones = EmpleadoRepository.get_sanciones(id_empleado)

        with get_connection() as conn:
            cur = conn.cursor()

            # Vacaciones registradas en el libro oficial
            cur.execute("""
                SELECT rv.id_vacacion, rv.id_reporte, rv.periodo,
                       rv.fecha_inicio, rv.fecha_termino, rv.dias,
                       rv.observaciones, rm.mes, rm.anio
                FROM reporte_vacaciones rv
                LEFT JOIN reportes_cierre_mensual rm ON rv.id_reporte = rm.id_reporte
                WHERE rv.id_empleado = ?
                ORDER BY rv.fecha_inicio DESC
            """, (id_empleado,))
            vacaciones_gozadas = [dict(r) for r in cur.fetchall()]

            # Compensaciones 24x48 (saldo y solicitudes)
            # REGLA OBLIGATORIA (Lineamiento LI-001-2023-INPE-OGA y RD N° 037-2026-INPE/ORNOSM):
            # El personal de Tratamiento (TRA) y Administrativo (ADM) con horario ordinario (08:00 a 17:00)
            # NO genera 24x48, NO tiene saldo de compensación y NO realiza compensación de días.
            es_seguridad_24x48 = (
                empleado.get("area_clasificacion") == "SEG"
                and "24" in str(empleado.get("horario_laboral") or "")
            )

            if es_seguridad_24x48:
                cur.execute("""
                    SELECT id_saldo, anio_goce, dias_asignados, dias_utilizados, dias_disponibles, observaciones
                    FROM saldos_compensacion
                    WHERE id_empleado = ? AND anio_goce = 2026
                """, (id_empleado,))
                saldo_row = cur.fetchone()
                if saldo_row:
                    saldo_comp = dict(saldo_row)
                    saldo_comp["aplica"] = True
                else:
                    saldo_comp = {
                        "aplica": True,
                        "dias_asignados": 0,
                        "dias_utilizados": 0,
                        "dias_disponibles": 0,
                        "observaciones": "Sin asignación en RD N° 037-2026"
                    }

                cur.execute("""
                    SELECT id_solicitud, fecha_solicitud, 
                           COALESCE(dias_compensados, dias_solicitados, 1) AS dias_solicitados,
                           fecha_compensacion AS fecha_inicio, estado, observaciones AS justificacion, 
                           numero_solicitud AS codigo_papeleta
                    FROM solicitudes_compensacion
                    WHERE id_empleado = ?
                    ORDER BY fecha_solicitud DESC
                """, (id_empleado,))
                solicitudes_comp = [dict(r) for r in cur.fetchall()]
            else:
                saldo_comp = {
                    "aplica": False,
                    "dias_asignados": 0,
                    "dias_utilizados": 0,
                    "dias_disponibles": 0,
                    "observaciones": "No aplica: Personal de Tratamiento o Administrativo con jornada ordinaria (08:00 - 17:00)"
                }
                solicitudes_comp = []

            # Licencias registradas en el libro oficial
            cur.execute("""
                SELECT rl.id_licencia, rl.tipo AS tipo_licencia, rl.fecha_inicio, rl.fecha_termino,
                       rl.dias, rl.entidad, rl.observaciones, rm.mes, rm.anio
                FROM reporte_licencias rl
                LEFT JOIN reportes_cierre_mensual rm ON rl.id_reporte = rm.id_reporte
                WHERE rl.id_empleado = ?
                ORDER BY rl.fecha_inicio DESC
            """, (id_empleado,))
            licencias = [dict(r) for r in cur.fetchall()]

            # Récord Laboral para Liquidación CAS / Cese si existe
            cur.execute("""
                SELECT * FROM empleados_records_laborales
                WHERE id_empleado = ?
                ORDER BY id_record DESC LIMIT 1
            """, (id_empleado,))
            record_row = cur.fetchone()
            record_laboral = dict(record_row) if record_row else None

        return {
            "empleado": empleado,
            "historial_laboral": historial,
            "sanciones": sanciones,
            "vacaciones_gozadas": vacaciones_gozadas,
            "compensacion_saldo": saldo_comp,
            "compensacion_solicitudes": solicitudes_comp,
            "licencias": licencias,
            "desplazamientos": empleado.get("desplazamientos", []),
            "record_laboral": record_laboral
        }

    @staticmethod
    def get_record_laboral(id_empleado: int) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM empleados_records_laborales
                WHERE id_empleado = ?
                ORDER BY id_record DESC LIMIT 1
            """, (id_empleado,))
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def guardar_record_laboral(id_empleado: int, datos: Dict[str, Any]) -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_record FROM empleados_records_laborales WHERE id_empleado = ?", (id_empleado,))
            existente = cur.fetchone()

            if existente:
                id_rec = existente[0]
                cur.execute("""
                    UPDATE empleados_records_laborales SET
                        tipo_proceso = ?,
                        regimen_laboral = ?,
                        cargo_funcion = ?,
                        dependencia_region = ?,
                        numero_celular = ?,
                        fecha_ingreso_entidad = ?,
                        ultimo_dia_laborado = ?,
                        fecha_cese_laboral = ?,
                        motivo_cese = ?,
                        documento_sustento = ?,
                        vacaciones_periodo_1_anio = ?,
                        vacaciones_periodo_1_ini = ?,
                        vacaciones_periodo_1_fin = ?,
                        vacaciones_periodo_1_gozadas = ?,
                        vacaciones_periodo_1_pendientes = ?,
                        vacaciones_periodo_2_anio = ?,
                        vacaciones_periodo_2_ini = ?,
                        vacaciones_periodo_2_fin = ?,
                        vacaciones_periodo_2_gozadas = ?,
                        vacaciones_periodo_2_pendientes = ?,
                        vacaciones_no_gozadas_truncas = ?,
                        asistencia_rango_periodo = ?,
                        inasistencias_dias_minutos = ?,
                        inasistencias_fechas = ?,
                        tardanzas_dias_minutos = ?,
                        tardanzas_fechas = ?,
                        particulares_dias_minutos = ?,
                        particulares_fechas = ?,
                        horas_compensar_total = ?,
                        horas_compensar_detalle = ?,
                        observaciones = ?,
                        responsable_rrhh = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id_record = ?
                """, (
                    datos.get("tipo_proceso", "LIQUIDACION_CAS"),
                    datos.get("regimen_laboral", "DL Nº 1057 CAS"),
                    datos.get("cargo_funcion", ""),
                    datos.get("dependencia_region", "EP MUJERES IQUITOS"),
                    datos.get("numero_celular", ""),
                    datos.get("fecha_ingreso_entidad"),
                    datos.get("ultimo_dia_laborado"),
                    datos.get("fecha_cese_laboral"),
                    datos.get("motivo_cese", ""),
                    datos.get("documento_sustento", ""),
                    datos.get("vacaciones_periodo_1_anio", "2024"),
                    datos.get("vacaciones_periodo_1_ini", "x"),
                    datos.get("vacaciones_periodo_1_fin", "x"),
                    float(datos.get("vacaciones_periodo_1_gozadas") or 0),
                    float(datos.get("vacaciones_periodo_1_pendientes") or 0),
                    datos.get("vacaciones_periodo_2_anio", "2025"),
                    datos.get("vacaciones_periodo_2_ini", ""),
                    datos.get("vacaciones_periodo_2_fin", ""),
                    float(datos.get("vacaciones_periodo_2_gozadas") or 0),
                    float(datos.get("vacaciones_periodo_2_pendientes") or 0),
                    int(datos.get("vacaciones_no_gozadas_truncas") or 0),
                    datos.get("asistencia_rango_periodo", ""),
                    datos.get("inasistencias_dias_minutos", "-"),
                    datos.get("inasistencias_fechas", ""),
                    datos.get("tardanzas_dias_minutos", "-"),
                    datos.get("tardanzas_fechas", ""),
                    datos.get("particulares_dias_minutos", "-"),
                    datos.get("particulares_fechas", ""),
                    datos.get("horas_compensar_total", "0"),
                    datos.get("horas_compensar_detalle", ""),
                    datos.get("observaciones", "NINGUNA"),
                    datos.get("responsable_rrhh", "Jefe de Recursos Humanos y/o Responsable de Control de Personal"),
                    id_rec
                ))
            else:
                cur.execute("""
                    INSERT INTO empleados_records_laborales (
                        id_empleado, tipo_proceso, regimen_laboral, cargo_funcion, dependencia_region,
                        numero_celular, fecha_ingreso_entidad, ultimo_dia_laborado, fecha_cese_laboral,
                        motivo_cese, documento_sustento,
                        vacaciones_periodo_1_anio, vacaciones_periodo_1_ini, vacaciones_periodo_1_fin,
                        vacaciones_periodo_1_gozadas, vacaciones_periodo_1_pendientes,
                        vacaciones_periodo_2_anio, vacaciones_periodo_2_ini, vacaciones_periodo_2_fin,
                        vacaciones_periodo_2_gozadas, vacaciones_periodo_2_pendientes,
                        vacaciones_no_gozadas_truncas,
                        asistencia_rango_periodo,
                        inasistencias_dias_minutos, inasistencias_fechas,
                        tardanzas_dias_minutos, tardanzas_fechas,
                        particulares_dias_minutos, particulares_fechas,
                        horas_compensar_total, horas_compensar_detalle,
                        observaciones, responsable_rrhh
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?,
                        ?, ?, ?,
                        ?, ?,
                        ?, ?, ?,
                        ?, ?,
                        ?,
                        ?,
                        ?, ?,
                        ?, ?,
                        ?, ?,
                        ?, ?,
                        ?, ?
                    )
                """, (
                    id_empleado,
                    datos.get("tipo_proceso", "LIQUIDACION_CAS"),
                    datos.get("regimen_laboral", "DL Nº 1057 CAS"),
                    datos.get("cargo_funcion", ""),
                    datos.get("dependencia_region", "EP MUJERES IQUITOS"),
                    datos.get("numero_celular", ""),
                    datos.get("fecha_ingreso_entidad"),
                    datos.get("ultimo_dia_laborado"),
                    datos.get("fecha_cese_laboral"),
                    datos.get("motivo_cese", ""),
                    datos.get("documento_sustento", ""),
                    datos.get("vacaciones_periodo_1_anio", "2024"),
                    datos.get("vacaciones_periodo_1_ini", "x"),
                    datos.get("vacaciones_periodo_1_fin", "x"),
                    float(datos.get("vacaciones_periodo_1_gozadas") or 0),
                    float(datos.get("vacaciones_periodo_1_pendientes") or 0),
                    datos.get("vacaciones_periodo_2_anio", "2025"),
                    datos.get("vacaciones_periodo_2_ini", ""),
                    datos.get("vacaciones_periodo_2_fin", ""),
                    float(datos.get("vacaciones_periodo_2_gozadas") or 0),
                    float(datos.get("vacaciones_periodo_2_pendientes") or 0),
                    int(datos.get("vacaciones_no_gozadas_truncas") or 0),
                    datos.get("asistencia_rango_periodo", ""),
                    datos.get("inasistencias_dias_minutos", "-"),
                    datos.get("inasistencias_fechas", ""),
                    datos.get("tardanzas_dias_minutos", "-"),
                    datos.get("tardanzas_fechas", ""),
                    datos.get("particulares_dias_minutos", "-"),
                    datos.get("particulares_fechas", ""),
                    datos.get("horas_compensar_total", "0"),
                    datos.get("horas_compensar_detalle", ""),
                    datos.get("observaciones", "NINGUNA"),
                    datos.get("responsable_rrhh", "Jefe de Recursos Humanos y/o Responsable de Control de Personal")
                ))
                id_rec = cur.lastrowid

            # Actualizar estado del empleado a CESADO
            cur.execute("""
                UPDATE empleados
                SET estado_laboral = 'CESADO',
                    observaciones = COALESCE(?, observaciones)
                WHERE id_empleado = ?
            """, (f"Cesado al {datos.get('fecha_cese_laboral', '')}. {datos.get('motivo_cese', '')}", id_empleado))

            conn.commit()
            return id_rec


