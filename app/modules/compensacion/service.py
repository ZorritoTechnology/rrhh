import calendar
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import json

from app.core.database import get_connection
from app.modules.compensacion.calendar_utils import generar_calendario_mes

class CompensacionService:

    @staticmethod
    def calcular_anexo2_mes(anio: int, mes: int) -> Dict[str, Any]:
        """
        Calcula la matriz Anexo 02 (Control Mensual de Días por Compensar)
        para el personal de seguridad 24x48 activo en el mes cerrado.
        Aplica las reglas del Lineamiento LI-001-2023-INPE-OGA:
        1. Semanas completas de Lunes a Domingo.
        2. Días de 24 horas completas de trabajo efectivo.
        3. A partir del 3er turno de 24h en una semana (L-D) supera las 48h y genera 1 día de exceso.
        4. Excluye días con Licencias (L), Vacaciones (V), Inasistencias (I) o Sanciones (S).
        5. Corte semanal: Si la semana continúa al siguiente mes, el exceso se computa
           en el mes donde se ejecuta dicho turno de 24 horas.
        """
        calendario = generar_calendario_mes(anio, mes)
        num_dias = calendario["num_dias"]

        with get_connection() as conn:
            cur = conn.cursor()

            # 1. Obtener reporte del mes
            cur.execute("""
                SELECT id_reporte, estado FROM reportes_cierre_mensual 
                WHERE anio = ? AND mes = ? AND id_establecimiento = 722
            """, (anio, mes))
            rep_row = cur.fetchone()
            if not rep_row:
                return {
                    "calendario": calendario,
                    "empleados": [],
                    "total_exceso_mes": 0,
                    "mensaje": f"No se encontró reporte de asistencia para {mes:02d}/{anio}."
                }
            
            id_reporte = rep_row["id_reporte"]

            # 2. Obtener personal de seguridad 24x48 del mes
            cur.execute("""
                SELECT 
                    a.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(r.nombre, 'LEY 29709') as regimen_nombre,
                    a.cargo_funcion,
                    a.estado_laboral
                FROM asistencia_mensual_personal a
                JOIN empleados e ON a.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON a.id_regimen = r.id_regimen
                WHERE a.id_reporte = ? AND (a.horario_laboral LIKE '%24%' OR a.area_clasificacion = 'SEG')
                ORDER BY e.apellidos_nombres ASC
            """, (id_reporte,))
            personal = [dict(r) for r in cur.fetchall()]

            if not personal:
                return {
                    "calendario": calendario,
                    "empleados": [],
                    "total_exceso_mes": 0,
                    "mensaje": "No hay personal con jornada 24x48 en la plantilla de este mes."
                }

            # 3. Novedades del mes (Licencias, Vacaciones, Sanciones, Inasistencias)
            cur.execute("SELECT id_empleado, fecha_inicio, fecha_termino FROM reporte_licencias WHERE id_reporte = ?", (id_reporte,))
            licencias = cur.fetchall()

            cur.execute("SELECT id_empleado, fecha_inicio, fecha_termino FROM reporte_vacaciones WHERE id_reporte = ?", (id_reporte,))
            vacaciones = cur.fetchall()

            cur.execute("SELECT id_empleado, fecha_inicio, fecha_termino FROM reporte_sanciones WHERE id_reporte = ?", (id_reporte,))
            sanciones = cur.fetchall()

            cur.execute("SELECT id_empleado, fechas_detalle FROM reporte_inasistencias WHERE id_reporte = ?", (id_reporte,))
            inasistencias = cur.fetchall()

            # Compensaciones ya gozadas en este mes
            cur.execute("SELECT id_empleado, fecha_compensacion FROM solicitudes_compensacion WHERE strftime('%Y-%m', fecha_compensacion) = ?", (f"{anio}-{mes:02d}",))
            compensaciones_gozadas = cur.fetchall()

            # Mapear novedades por empleado y día
            novedades_map = {}
            for p in personal:
                novedades_map[p["id_empleado"]] = {}

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
                    # fechas_detalle puede ser '2,3,4,16,17'
                    partes = str(inas["fechas_detalle"]).replace(" y ", ",").split(",")
                    for pt in partes:
                        pt = pt.strip()
                        if pt.isdigit():
                            d_num = int(pt)
                            if 1 <= d_num <= num_dias:
                                novedades_map[emp_id][d_num] = "I"

            for comp in compensaciones_gozadas:
                emp_id = comp["id_empleado"]
                if emp_id in novedades_map and comp["fecha_compensacion"]:
                    try:
                        d_obj = datetime.strptime(comp["fecha_compensacion"], "%Y-%m-%d").date()
                        if d_obj.year == anio and d_obj.month == mes:
                            novedades_map[emp_id][d_obj.day] = "C"
                    except Exception:
                        pass

            # 4. Obtener si ya había datos guardados en compensacion_dias_ganados
            cur.execute("""
                SELECT id_empleado, grupo_guardia, dias_exceso, detalle_dias, observaciones
                FROM compensacion_dias_ganados
                WHERE anio = ? AND mes = ?
            """, (anio, mes))
            guardados_map = {r["id_empleado"]: dict(r) for r in cur.fetchall()}

            # 5. Calcular para cada servidor
            resultado_empleados = []
            total_exceso_mes = 0

            for idx, emp in enumerate(personal):
                emp_id = emp["id_empleado"]
                rec_guardado = guardados_map.get(emp_id)

                # Grupo de guardia: G1, G2, o G3 (rotativo por defecto si no está definido)
                if rec_guardado and rec_guardado.get("grupo_guardia"):
                    grupo = rec_guardado["grupo_guardia"]
                else:
                    grupo_idx = (idx % 3) + 1
                    grupo = f"G{grupo_idx}"

                offset_grupo = {"G1": 0, "G2": 1, "G3": 2}.get(grupo, 0)

                # Si ya tenía detalle_dias en base de datos, lo cargamos
                detalle_existente = {}
                if rec_guardado and rec_guardado.get("detalle_dias"):
                    try:
                        detalle_existente = json.loads(rec_guardado["detalle_dias"])
                    except Exception:
                        pass

                # Malla de días 1..num_dias
                dias_calculados = {}
                for d in range(1, num_dias + 1):
                    # Si ya tenía valor manual asignado en la BD
                    if str(d) in detalle_existente:
                        dias_calculados[d] = detalle_existente[str(d)]
                    # Si tiene novedad en asistencia
                    elif d in novedades_map[emp_id]:
                        dias_calculados[d] = novedades_map[emp_id][d]
                    # Rol ordinario 24x48: trabaja si (d - 1 - offset) % 3 == 0
                    elif ((d - 1 - offset_grupo) % 3) == 0:
                        dias_calculados[d] = "24"
                    else:
                        dias_calculados[d] = "D"

                # 6. Cálculo de exceso por SEMANAS (Lunes a Domingo)
                # Evaluamos semana a semana conforme al numeral 4.10
                dias_exceso_trabajador = 0
                semanas_detalle = []

                for sem in calendario["semanas"]:
                    dias_sem = sem["dias"]
                    turnos_24_sem = 0
                    dias_sem_info = []

                    for d_info in dias_sem:
                        dia_num = d_info["dia"]
                        marca = dias_calculados.get(dia_num, "D")
                        es_turno_exceso = False

                        if marca == "24":
                            turnos_24_sem += 1
                            # Si es el 3er turno de 24h dentro de la misma semana de Lunes a Domingo
                            if turnos_24_sem >= 3:
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
                        "turnos_24": turnos_24_sem,
                        "dias": dias_sem_info
                    })

                total_exceso_mes += dias_exceso_trabajador

                resultado_empleados.append({
                    "id_empleado": emp_id,
                    "codigo_servidor": emp["codigo_servidor"],
                    "dni": emp["dni"],
                    "apellidos_nombres": emp["apellidos_nombres"],
                    "regimen_nombre": emp["regimen_nombre"],
                    "cargo_funcion": emp["cargo_funcion"],
                    "grupo_guardia": grupo,
                    "dias_calculados": dias_calculados,
                    "semanas_detalle": semanas_detalle,
                    "dias_exceso": dias_exceso_trabajador,
                    "observaciones": rec_guardado.get("observaciones", "") if rec_guardado else ""
                })

            return {
                "anio": anio,
                "mes": mes,
                "calendario": calendario,
                "empleados": resultado_empleados,
                "total_exceso_mes": total_exceso_mes,
                "total_empleados": len(resultado_empleados)
            }

    @staticmethod
    def guardar_anexo2_en_db(anio: int, mes: int, lista_empleados: List[Dict[str, Any]]) -> bool:
        """
        Persiste el Anexo 02 en la base de datos y actualiza los días de exceso
        para que se reflejen en la columna correspondiente del Anexo 03.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            for item in lista_empleados:
                emp_id = item["id_empleado"]
                dias_exceso = item.get("dias_exceso", 0)
                grupo = item.get("grupo_guardia", "G1")
                detalle_dias = json.dumps(item.get("dias_calculados", {}))
                obs = item.get("observaciones", "")

                cur.execute("""
                    INSERT INTO compensacion_dias_ganados (
                        anio, mes, id_empleado, dias_exceso, grupo_guardia, detalle_dias, observaciones
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(anio, mes, id_empleado) DO UPDATE SET
                        dias_exceso = excluded.dias_exceso,
                        grupo_guardia = excluded.grupo_guardia,
                        detalle_dias = excluded.detalle_dias,
                        observaciones = excluded.observaciones
                """, (anio, mes, emp_id, dias_exceso, grupo, detalle_dias, obs))

            conn.commit()
            return True

    @staticmethod
    def registrar_goce_manual(
        id_empleado: int,
        fecha_compensacion: str,
        fecha_solicitud: str = None,
        numero_solicitud: str = "",
        observaciones: str = ""
    ) -> Dict[str, Any]:
        """
        Registra la compensación de 24 horas solicitada en físico/manual
        (Anexo 01) y descuenta 1 día del saldo disponible del servidor.
        """
        try:
            d_comp = datetime.strptime(fecha_compensacion, "%Y-%m-%d").date()
            if fecha_solicitud:
                d_sol = datetime.strptime(fecha_solicitud, "%Y-%m-%d").date()
            else:
                d_sol = date.today()
                fecha_solicitud = d_sol.isoformat()
        except ValueError:
            return {"success": False, "message": "Formato de fechas incorrecto (debe ser YYYY-MM-DD)."}

        anio_goce = d_comp.year
        mes = d_comp.month

        with get_connection() as conn:
            cur = conn.cursor()

            # Verificar saldo
            cur.execute("""
                SELECT dias_asignados, dias_utilizados, dias_disponibles
                FROM saldos_compensacion
                WHERE id_empleado = ? AND anio_goce = ?
            """, (id_empleado, anio_goce))
            saldo = cur.fetchone()

            if not saldo:
                # Inicializar con 16 días por defecto según lineamiento
                cur.execute("""
                    INSERT INTO saldos_compensacion (id_empleado, anio_goce, dias_asignados, dias_utilizados, dias_disponibles)
                    VALUES (?, ?, 16, 0, 16)
                """, (id_empleado, anio_goce))
                dias_disponibles = 16
            else:
                dias_disponibles = saldo["dias_disponibles"]

            if dias_disponibles <= 0:
                return {
                    "success": False,
                    "message": f"El servidor no cuenta con días disponibles de compensación para el año {anio_goce} (Saldo agotado: 0 días)."
                }

            # Verificar que no exista ya registro en la misma fecha
            cur.execute("""
                SELECT id_solicitud FROM solicitudes_compensacion
                WHERE id_empleado = ? AND fecha_compensacion = ? AND estado != 'RECHAZADO'
            """, (id_empleado, fecha_compensacion))
            if cur.fetchone():
                return {
                    "success": False,
                    "message": f"El servidor ya tiene una compensación registrada en la fecha {fecha_compensacion}."
                }

            # Insertar solicitud
            cur.execute("""
                INSERT INTO solicitudes_compensacion (
                    id_empleado, anio_goce, mes, fecha_solicitud, fecha_compensacion,
                    dias_compensados, numero_solicitud, jefe_inmediato, especialista_personal,
                    estado, observaciones
                ) VALUES (?, ?, ?, ?, ?, 1, ?, 'AUTORIZADO', 'CONFORME', 'APROBADO', ?)
            """, (
                id_empleado, anio_goce, mes, fecha_solicitud, fecha_compensacion,
                numero_solicitud or f"Solicitud Anexo 01 - {fecha_compensacion}",
                observaciones
            ))
            id_sol = cur.lastrowid

            # Actualizar saldos
            cur.execute("""
                UPDATE saldos_compensacion
                SET dias_utilizados = dias_utilizados + 1,
                    dias_disponibles = dias_disponibles - 1
                WHERE id_empleado = ? AND anio_goce = ?
            """, (id_empleado, anio_goce))

            conn.commit()

            # Obtener saldo actualizado
            cur.execute("SELECT dias_asignados, dias_utilizados, dias_disponibles FROM saldos_compensacion WHERE id_empleado = ? AND anio_goce = ?", (id_empleado, anio_goce))
            s_up = cur.fetchone()

            return {
                "success": True,
                "id_solicitud": id_sol,
                "dias_usados": s_up["dias_utilizados"],
                "dias_restantes": s_up["dias_disponibles"],
                "message": f"Compensación del día {fecha_compensacion} registrada exitosamente. Días usados: {s_up['dias_utilizados']}, Le quedan: {s_up['dias_disponibles']} días."
            }

    @staticmethod
    def eliminar_goce_manual(id_solicitud: int) -> Dict[str, Any]:
        """
        Elimina un registro de compensación manual y reintegra el día al saldo del servidor.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_empleado, anio_goce, fecha_compensacion 
                FROM solicitudes_compensacion WHERE id_solicitud = ?
            """, (id_solicitud,))
            sol = cur.fetchone()
            if not sol:
                return {"success": False, "message": "Registro no encontrado."}

            emp_id = sol["id_empleado"]
            anio_goce = sol["anio_goce"]

            cur.execute("DELETE FROM solicitudes_compensacion WHERE id_solicitud = ?", (id_solicitud,))

            # Reintegrar día
            cur.execute("""
                UPDATE saldos_compensacion
                SET dias_utilizados = max(0, dias_utilizados - 1),
                    dias_disponibles = min(dias_asignados, dias_disponibles + 1)
                WHERE id_empleado = ? AND anio_goce = ?
            """, (emp_id, anio_goce))

            conn.commit()
            return {"success": True, "message": f"Registro eliminado. El día ha sido reintegrado al saldo disponible del servidor."}
