import calendar
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import json

from app.core.database import get_connection
from app.modules.compensacion.calendar_utils import generar_calendario_mes
from app.modules.compensacion.repository import CompensacionRepository

class CompensacionService:

    @staticmethod
    def calcular_anexo2_mes(anio: int, mes: int) -> Dict[str, Any]:
        """
        Calcula la matriz oficial del Anexo 02 (Control Mensual de Días por Compensar)
        organizado por Grupo 1, Grupo 2 y Grupo 3 con sus respectivos Alcaides de Grupo.
        Aplica las reglas normativas:
        1. Ciclo rotativo 24x48 por grupo (Grupo 1: día 1, 4...; Grupo 2: día 2, 5...; Grupo 3: día 3, 6...).
        2. Alcaide / Responsable de cada grupo identificado.
        3. Rotaciones por Memorando: si rota a las 5pm se marca '5P' (no cuenta como 24h);
           si rota haciendo guardia completa se marca '24'. Tras la rotación adopta su nuevo grupo.
        4. Semanas de Lunes a Domingo: el 3er turno de 24h efectivas genera 1 día de exceso.
        5. Exclusión de licencias (L), vacaciones (V), inasistencias (I) y sanciones (S).
        """
        calendario = generar_calendario_mes(anio, mes)
        num_dias = calendario["num_dias"]

        with get_connection() as conn:
            cur = conn.cursor()

            # 1. Reporte mensual de asistencia
            cur.execute("""
                SELECT id_reporte, estado FROM reportes_cierre_mensual 
                WHERE anio = ? AND mes = ? AND id_establecimiento = 722
            """, (anio, mes))
            rep_row = cur.fetchone()
            if not rep_row:
                return {
                    "calendario": calendario,
                    "grupos": [],
                    "total_exceso_mes": 0,
                    "mensaje": f"No se encontró reporte de asistencia cerrado para {mes:02d}/{anio}."
                }
            
            id_reporte = rep_row["id_reporte"]

            # 2. Información de los 3 grupos y sus alcaides
            grupos_info = CompensacionRepository.get_grupos_guardia()
            alcaides_map = {g["id_grupo"]: g for g in grupos_info}

            # 3. Personal de seguridad 24x48 del mes
            cur.execute("""
                SELECT 
                    a.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(e.grupo_guardia_default, 1) as grupo_guardia_default,
                    COALESCE(r.nombre, 'LEY 29709') as regimen_nombre,
                    a.cargo_funcion,
                    a.estado_laboral,
                    a.observaciones as asistencia_observaciones
                FROM asistencia_mensual_personal a
                JOIN empleados e ON a.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON a.id_regimen = r.id_regimen
                WHERE a.id_reporte = ? 
                  AND a.cargo_funcion = 'AGENTE DE SEGURIDAD' 
                  AND a.area_clasificacion = 'SEG'
                  AND (a.horario_laboral LIKE '%24%' OR a.horario_laboral LIKE '%25%')
                ORDER BY e.apellidos_nombres ASC
            """, (id_reporte,))
            personal = [dict(r) for r in cur.fetchall()]

            if not personal:
                return {
                    "calendario": calendario,
                    "grupos": [],
                    "total_exceso_mes": 0,
                    "mensaje": "No hay personal con jornada 24x48 registrado en este mes."
                }

            # 4. Novedades del mes (Licencias, Vacaciones, Sanciones, Inasistencias)
            cur.execute("SELECT id_empleado, fecha_inicio, fecha_termino FROM reporte_licencias WHERE id_reporte = ?", (id_reporte,))
            licencias = cur.fetchall()

            cur.execute("SELECT id_empleado, fecha_inicio, fecha_termino FROM reporte_vacaciones WHERE id_reporte = ?", (id_reporte,))
            vacaciones = cur.fetchall()

            cur.execute("SELECT id_empleado, fecha_inicio, fecha_termino FROM reporte_sanciones WHERE id_reporte = ?", (id_reporte,))
            sanciones = cur.fetchall()

            cur.execute("SELECT id_empleado, fechas_detalle FROM reporte_inasistencias WHERE id_reporte = ?", (id_reporte,))
            inasistencias = cur.fetchall()

            # Compensaciones gozadas
            cur.execute("""
                SELECT id_empleado, fecha_compensacion, fechas_compensacion_detalle 
                FROM solicitudes_compensacion 
                WHERE anio_goce = ? AND mes = ? AND estado = 'APROBADO'
            """, (anio, mes))
            compensaciones_gozadas = cur.fetchall()

            # Rotaciones registradas en este mes o previas
            cur.execute("""
                SELECT id_empleado, grupo_origen, grupo_destino, fecha_rotacion, modalidad_dia_cambio, numero_memorando
                FROM rotaciones_grupo_guardia
                WHERE anio = ? AND mes <= ?
                ORDER BY fecha_rotacion ASC
            """, (anio, mes))
            rotaciones_todas = cur.fetchall()
            rotaciones_por_emp = {}
            for rot in rotaciones_todas:
                emp_id = rot["id_empleado"]
                if emp_id not in rotaciones_por_emp:
                    rotaciones_por_emp[emp_id] = []
                rotaciones_por_emp[emp_id].append(dict(rot))

            # Mapear novedades por empleado y día
            novedades_map = {p["id_empleado"]: {} for p in personal}

            for lic in licencias:
                emp_id = lic["id_empleado"]
                if emp_id in novedades_map and lic["fecha_inicio"] and lic["fecha_termino"]:
                    try:
                        f_ini = max(date(anio, mes, 1), datetime.strptime(lic["fecha_inicio"], "%Y-%m-%d").date())
                        f_fin = min(date(anio, mes, num_dias), datetime.strptime(lic["fecha_termino"], "%Y-%m-%d").date())
                        curr = f_ini
                        while curr <= f_fin:
                            if curr.month == mes and curr.year == anio:
                                novedades_map[emp_id][curr.day] = "L"
                            curr += timedelta(days=1)
                    except Exception:
                        pass

            for vac in vacaciones:
                emp_id = vac["id_empleado"]
                if emp_id in novedades_map and vac["fecha_inicio"] and vac["fecha_termino"]:
                    try:
                        f_ini = max(date(anio, mes, 1), datetime.strptime(vac["fecha_inicio"], "%Y-%m-%d").date())
                        f_fin = min(date(anio, mes, num_dias), datetime.strptime(vac["fecha_termino"], "%Y-%m-%d").date())
                        curr = f_ini
                        while curr <= f_fin:
                            if curr.month == mes and curr.year == anio:
                                novedades_map[emp_id][curr.day] = "V"
                            curr += timedelta(days=1)
                    except Exception:
                        pass

            for sanc in sanciones:
                emp_id = sanc["id_empleado"]
                if emp_id in novedades_map and sanc["fecha_inicio"] and sanc["fecha_termino"]:
                    try:
                        f_ini = max(date(anio, mes, 1), datetime.strptime(sanc["fecha_inicio"], "%Y-%m-%d").date())
                        f_fin = min(date(anio, mes, num_dias), datetime.strptime(sanc["fecha_termino"], "%Y-%m-%d").date())
                        curr = f_ini
                        while curr <= f_fin:
                            if curr.month == mes and curr.year == anio:
                                novedades_map[emp_id][curr.day] = "S"
                            curr += timedelta(days=1)
                    except Exception:
                        pass

            for inas in inasistencias:
                emp_id = inas["id_empleado"]
                if emp_id in novedades_map and inas["fechas_detalle"]:
                    partes = str(inas["fechas_detalle"]).replace(" y ", ",").split(",")
                    for pt in partes:
                        pt = pt.strip()
                        if pt.isdigit():
                            d_num = int(pt)
                            if 1 <= d_num <= num_dias:
                                novedades_map[emp_id][d_num] = "I"

            for comp in compensaciones_gozadas:
                emp_id = comp["id_empleado"]
                if emp_id in novedades_map:
                    # fecha individual
                    if comp["fecha_compensacion"]:
                        try:
                            d_obj = datetime.strptime(comp["fecha_compensacion"], "%Y-%m-%d").date()
                            if d_obj.year == anio and d_obj.month == mes:
                                novedades_map[emp_id][d_obj.day] = "C"
                        except Exception:
                            pass
                    # fechas detalle si eran múltiples
                    if comp.get("fechas_compensacion_detalle"):
                        for f_str in comp["fechas_compensacion_detalle"].split(","):
                            try:
                                d_obj = datetime.strptime(f_str.strip(), "%Y-%m-%d").date()
                                if d_obj.year == anio and d_obj.month == mes:
                                    novedades_map[emp_id][d_obj.day] = "C"
                            except Exception:
                                pass

            # 5. Obtener días ya guardados en la BD
            cur.execute("""
                SELECT id_empleado, grupo_guardia, dias_exceso, detalle_dias, observaciones
                FROM compensacion_dias_ganados
                WHERE anio = ? AND mes = ?
            """, (anio, mes))
            guardados_map = {r["id_empleado"]: dict(r) for r in cur.fetchall()}

            # 6. Agrupación y cálculo
            grupos_dict = {
                1: {"id_grupo": 1, "nombre": "Grupo 1", "alcaide": alcaides_map.get(1, {}), "empleados": []},
                2: {"id_grupo": 2, "nombre": "Grupo 2", "alcaide": alcaides_map.get(2, {}), "empleados": []},
                3: {"id_grupo": 3, "nombre": "Grupo 3", "alcaide": alcaides_map.get(3, {}), "empleados": []}
            }

            total_exceso_mes = 0

            for emp in personal:
                emp_id = emp["id_empleado"]
                rec_guardado = guardados_map.get(emp_id)

                # Determinar grupo base del servidor (directamente desde su asignación oficial)
                g_base_id = emp.get("grupo_guardia_default", 1) or 1

                # Detectar condición de Abandono de Servicio
                estado_lab = str(emp.get("estado_laboral", "")).upper()
                obs_asist = str(emp.get("asistencia_observaciones", "")).lower()
                obs_prev = str(rec_guardado.get("observaciones", "") if rec_guardado else "").lower()
                es_abandono = (
                    "ABANDONO" in estado_lab or 
                    "abandono" in obs_asist or 
                    "abandono" in obs_prev
                )

                # Mapear rotaciones registradas del empleado ordenadas cronológicamente
                rotaciones_emp = rotaciones_por_emp.get(emp_id, [])
                rotaciones_emp.sort(key=lambda r: datetime.strptime(r["fecha_rotacion"], "%Y-%m-%d").date())

                rot_mes = None
                for r in rotaciones_emp:
                    r_fecha = datetime.strptime(r["fecha_rotacion"], "%Y-%m-%d").date()
                    if r_fecha.year == anio and r_fecha.month == mes:
                        rot_mes = r
                        break

                # Determinar grupo activo del empleado al cierre de este mes
                fecha_fin_mes = date(anio, mes, num_dias)
                g_mes_id = g_base_id
                if rotaciones_emp:
                    ult_rot_aplicable = None
                    for r in rotaciones_emp:
                        r_f = datetime.strptime(r["fecha_rotacion"], "%Y-%m-%d").date()
                        if r_f <= fecha_fin_mes:
                            ult_rot_aplicable = r
                    if ult_rot_aplicable:
                        g_mes_id = 1 if "1" in ult_rot_aplicable["grupo_destino"] else (2 if "2" in ult_rot_aplicable["grupo_destino"] else 3)
                    else:
                        g_mes_id = 1 if "1" in rotaciones_emp[0]["grupo_origen"] else (2 if "2" in rotaciones_emp[0]["grupo_origen"] else 3)

                fecha_base_anual = date(anio, 1, 1)

                def parse_g_num(val) -> int:
                    s = str(val)
                    if "1" in s: return 1
                    if "2" in s: return 2
                    if "3" in s: return 3
                    return 1

                def obtener_marca_dia_especifico(f_obj: date) -> str:
                    # Si es personal en abandono, no labora turnos y no genera compensación
                    if es_abandono:
                        return "AB"

                    # 1. Novedades registradas si es del mes actual (licencia, vacaciones, etc.)
                    if f_obj.year == anio and f_obj.month == mes and f_obj.day in novedades_map.get(emp_id, {}):
                        return novedades_map[emp_id][f_obj.day]

                    # 2. Rotaciones aplicables a esta fecha respetando estrictamente la historia previa
                    g_activo = g_base_id
                    if rotaciones_emp:
                        f_primera = datetime.strptime(rotaciones_emp[0]["fecha_rotacion"], "%Y-%m-%d").date()
                        # A partir del primer cambio NO se modifican los días anteriores:
                        # Si la fecha es anterior a la primera rotación, mantiene estrictamente su grupo de origen
                        if f_obj < f_primera:
                            g_activo = parse_g_num(rotaciones_emp[0]["grupo_origen"])
                        else:
                            # Evaluar en qué intervalo de rotaciones cae f_obj
                            rot_aplicable = None
                            for r in rotaciones_emp:
                                r_f = datetime.strptime(r["fecha_rotacion"], "%Y-%m-%d").date()
                                if f_obj == r_f:
                                    # El día exacto de la rotación con memorando aplica la modalidad específica
                                    if r["modalidad_dia_cambio"] == "ADMINISTRATIVO_5PM":
                                        return "5P"
                                    else:
                                        return "24"
                                elif r_f < f_obj:
                                    rot_aplicable = r

                            if rot_aplicable:
                                # A partir de la fecha de rotación y antes del siguiente cambio, trabaja en el grupo destino
                                g_activo = parse_g_num(rot_aplicable["grupo_destino"])

                    # 3. Ciclo 24x48 continuo en el año fiscal para el grupo activo en dicha fecha
                    delta = (f_obj - fecha_base_anual).days
                    offset = g_activo - 1
                    if ((delta - offset) % 3) == 0:
                        return "24"
                    return "D"

                dias_calculados = {}
                memo_rotacion_texto = ""

                # Generar marcas de todos los días del mes actual
                for d in range(1, num_dias + 1):
                    fecha_dia = date(anio, mes, d)
                    dias_calculados[d] = obtener_marca_dia_especifico(fecha_dia)

                if rot_mes:
                    mod_txt = "5P (Adm. hasta 5pm)" if rot_mes["modalidad_dia_cambio"] == "ADMINISTRATIVO_5PM" else "24h (Guardia)"
                    memo_rotacion_texto = f"Rotación ({rot_mes['fecha_rotacion']}): {rot_mes['numero_memorando']} [{rot_mes['grupo_origen']} → {rot_mes['grupo_destino']}, {mod_txt}]"

                # 7. Evaluar semanas (Lunes a Domingo) para exceso conforme a Directiva DI-003-2023
                dias_exceso_trabajador = 0
                semanas_detalle = []

                for sem in calendario["semanas"]:
                    dias_sem = sem["dias"]
                    dias_sem_info = []

                    # Verificar si la semana termina en Domingo dentro del mes
                    termina_en_domingo = (dias_sem[-1]["weekday"] == 6)

                    # Si termina en domingo y NO es abandono, evaluamos los 7 días naturales (Lunes a Domingo)
                    turnos_24_sem = 0
                    if termina_en_domingo and not es_abandono:
                        domingo_dia = dias_sem[-1]["dia"]
                        fecha_dom = date(anio, mes, domingo_dia)
                        # La evaluación de exceso no retrocede antes del 1 de enero del año fiscal
                        fecha_lun = max(date(anio, 1, 1), fecha_dom - timedelta(days=6))

                        # Contar turnos 24 en los 7 días naturales
                        curr_f = fecha_lun
                        while curr_f <= fecha_dom:
                            m_dia = obtener_marca_dia_especifico(curr_f)
                            if m_dia == "24":
                                turnos_24_sem += 1
                            curr_f += timedelta(days=1)

                    # Mapear celdas de la semana para la vista Anexo 02
                    for d_info in dias_sem:
                        dia_num = d_info["dia"]
                        marca = dias_calculados.get(dia_num, "D" if not es_abandono else "AB")
                        es_turno_exceso = False

                        # El Domingo que completa los 3 turnos se resalta como turno en exceso
                        if not es_abandono and d_info["weekday"] == 6 and marca == "24" and turnos_24_sem >= 3:
                            es_turno_exceso = True
                            dias_exceso_trabajador += 1

                        dias_sem_info.append({
                            "dia": dia_num,
                            "dia_letra": d_info["dia_letra"],
                            "marca": marca,
                            "es_exceso": es_turno_exceso
                        })

                    semanas_detalle.append({
                        "numero": sem["numero"],
                        "turnos_24": turnos_24_sem if not es_abandono else 0,
                        "dias": dias_sem_info
                    })

                if not es_abandono:
                    total_exceso_mes += dias_exceso_trabajador
                else:
                    dias_exceso_trabajador = 0

                obs_empleado = ""
                if es_abandono:
                    obs_empleado = emp.get("asistencia_observaciones") or "Abandono laboral desde el 10/05/2021"
                elif rec_guardado:
                    obs_empleado = rec_guardado.get("observaciones", "")

                grupo_destino_vista = g_mes_id if not es_abandono else g_base_id

                emp_data = {
                    "id_empleado": emp_id,
                    "codigo_servidor": emp["codigo_servidor"],
                    "dni": emp["dni"],
                    "apellidos_nombres": emp["apellidos_nombres"],
                    "regimen_nombre": emp["regimen_nombre"],
                    "cargo_funcion": emp["cargo_funcion"],
                    "grupo_id": grupo_destino_vista,
                    "grupo_nombre": f"Grupo {grupo_destino_vista}",
                    "dias_calculados": dias_calculados,
                    "semanas_detalle": semanas_detalle,
                    "dias_exceso": dias_exceso_trabajador,
                    "es_abandono": es_abandono,
                    "rotacion_memo": memo_rotacion_texto,
                    "observaciones": obs_empleado
                }

                if grupo_destino_vista in grupos_dict:
                    grupos_dict[grupo_destino_vista]["empleados"].append(emp_data)
                else:
                    grupos_dict[1]["empleados"].append(emp_data)

            lista_grupos = [grupos_dict[1], grupos_dict[2], grupos_dict[3]]

            return {
                "anio": anio,
                "mes": mes,
                "calendario": calendario,
                "grupos": lista_grupos,
                "total_exceso_mes": total_exceso_mes,
                "total_empleados": len(personal)
            }

    @staticmethod
    def guardar_anexo2_en_db(anio: int, mes: int, lista_grupos: List[Dict[str, Any]]) -> bool:
        with get_connection() as conn:
            cur = conn.cursor()
            for g in lista_grupos:
                g_nombre = g["nombre"]
                for emp in g["empleados"]:
                    emp_id = emp["id_empleado"]
                    dias_exceso = emp.get("dias_exceso", 0)
                    if emp.get("es_abandono"):
                        dias_exceso = 0
                    detalle_dias = json.dumps(emp.get("dias_calculados", {}))
                    obs = emp.get("rotacion_memo", "") or emp.get("observaciones", "")
                    if emp.get("es_abandono"):
                        obs = "ABANDONO LABORAL (Sin goce ni exceso)"

                    cur.execute("""
                        INSERT INTO compensacion_dias_ganados (
                            anio, mes, id_empleado, dias_exceso, grupo_guardia, detalle_dias, observaciones
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(anio, mes, id_empleado) DO UPDATE SET
                            dias_exceso = excluded.dias_exceso,
                            grupo_guardia = excluded.grupo_guardia,
                            detalle_dias = excluded.detalle_dias,
                            observaciones = excluded.observaciones
                    """, (anio, mes, emp_id, dias_exceso, g_nombre, detalle_dias, obs))

            conn.commit()
            return True

    @staticmethod
    def registrar_solicitud_compensacion(
        id_empleado: int,
        anio_goce: int,
        mes: int,
        fecha_solicitud: str,
        fecha_compensacion: str,
        dias_solicitados: int,
        fechas_compensacion_detalle: str = "",
        numero_solicitud: str = "",
        observaciones: str = ""
    ) -> Dict[str, Any]:
        """
        Registra la solicitud formal de compensación (1 o varios días/turnos)
        y descuenta del saldo reconocido del servidor.
        """
        try:
            d_comp = datetime.strptime(fecha_compensacion, "%Y-%m-%d").date()
            if not fecha_solicitud:
                fecha_solicitud = date.today().isoformat()
        except ValueError:
            return {"success": False, "message": "Formato de fecha inválido (debe ser YYYY-MM-DD)."}

        if not fechas_compensacion_detalle:
            fechas_compensacion_detalle = fecha_compensacion

        return CompensacionRepository.registrar_solicitud_compensacion(
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
