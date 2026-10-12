from typing import List, Dict, Any, Optional
from datetime import date
from app.core.database import get_connection

class CompensacionRepository:

    @staticmethod
    def get_matriz_mensualizada(anio: int = 2026) -> List[Dict[str, Any]]:
        return CompensacionRepository.get_matriz_anexo3(anio)

    @staticmethod
    def get_matriz_anexo3(anio: int = 2026) -> List[Dict[str, Any]]:
        """
        Genera la matriz oficial del Anexo 03 (Reporte Mensualizado de Días Ganados)
        consolidando mes a mes (1 a 12) los días de trabajo en exceso generados
        por el personal de seguridad 24x48 conforme al Lineamiento LI-001-2023-INPE-OGA.
        Tope máximo computable: 16 días por año fiscal.
        """
        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT DISTINCT
                    e.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(r.nombre, 'LEY 29709') as regimen_nombre
                FROM empleados e
                JOIN asistencia_mensual_personal amp ON amp.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON amp.id_regimen = r.id_regimen
                WHERE amp.cargo_funcion = 'AGENTE DE SEGURIDAD'
                  AND amp.area_clasificacion = 'SEG'
                  AND (amp.horario_laboral LIKE '%24%' OR amp.horario_laboral LIKE '%25%')
                GROUP BY e.id_empleado
                ORDER BY e.apellidos_nombres ASC
            """)
            empleados = [dict(r) for r in cur.fetchall()]

            cur.execute("""
                SELECT id_empleado, mes, dias_exceso
                FROM compensacion_dias_ganados
                WHERE anio = ?
            """, (anio,))
            filas_ganadas = cur.fetchall()

            mapa_ganados = {}
            for r in filas_ganadas:
                emp_id = r["id_empleado"]
                if emp_id not in mapa_ganados:
                    mapa_ganados[emp_id] = {}
                mapa_ganados[emp_id][r["mes"]] = r["dias_exceso"]

            matriz = []
            for emp in empleados:
                emp_id = emp["id_empleado"]
                meses_data = mapa_ganados.get(emp_id, {})
                total_ganado_bruto = 0

                for m in range(1, 13):
                    val = meses_data.get(m, 0)
                    emp[f"m_{m}"] = val if val > 0 else "-"
                    total_ganado_bruto += val

                emp["total_ganado"] = min(16, total_ganado_bruto)
                emp["total_bruto"] = total_ganado_bruto
                matriz.append(emp)

            return matriz

    @staticmethod
    def get_grupos_guardia() -> List[Dict[str, Any]]:
        """
        Obtiene los 3 grupos de guardia con sus respectivos Alcaides.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    g.id_grupo,
                    g.nombre_grupo,
                    g.id_alcaide,
                    g.observaciones,
                    e.codigo_servidor as alcaide_cip,
                    e.dni as alcaide_dni,
                    e.apellidos_nombres as alcaide_nombre
                FROM grupos_guardia_seguridad g
                LEFT JOIN empleados e ON g.id_alcaide = e.id_empleado
                ORDER BY g.id_grupo ASC
            """)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def asignar_alcaide_grupo(id_grupo: int, id_alcaide: int) -> bool:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE grupos_guardia_seguridad
                SET id_alcaide = ?
                WHERE id_grupo = ?
            """, (id_alcaide, id_grupo))
            conn.commit()
            return True

    @staticmethod
    def registrar_rotacion_grupo(
        id_empleado: int,
        anio: int,
        mes: int,
        grupo_origen: str,
        grupo_destino: str,
        fecha_rotacion: str,
        numero_memorando: str,
        modalidad_dia_cambio: str = "24_HORAS",
        observaciones: str = ""
    ) -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO rotaciones_grupo_guardia (
                    id_empleado, anio, mes, grupo_origen, grupo_destino,
                    fecha_rotacion, numero_memorando, modalidad_dia_cambio, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_empleado, anio, mes, grupo_origen, grupo_destino,
                fecha_rotacion, numero_memorando, modalidad_dia_cambio, observaciones
            ))
            id_rot = cur.lastrowid

            # Actualizar grupo_guardia_default del empleado al nuevo grupo
            # Si el grupo destino es numérico (Grupo 1 -> 1, Grupo 2 -> 2, Grupo 3 -> 3)
            g_num = None
            if "1" in grupo_destino:
                g_num = 1
            elif "2" in grupo_destino:
                g_num = 2
            elif "3" in grupo_destino:
                g_num = 3

            if g_num:
                cur.execute("UPDATE empleados SET grupo_guardia_default = ? WHERE id_empleado = ?", (g_num, id_empleado))

            conn.commit()
            return id_rot

    @staticmethod
    def get_rotaciones_mes(anio: int, mes: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    r.*,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres
                FROM rotaciones_grupo_guardia r
                JOIN empleados e ON r.id_empleado = e.id_empleado
                WHERE r.anio = ? AND r.mes = ?
                ORDER BY r.fecha_rotacion DESC
            """, (anio, mes))
            return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def get_control_saldos(anio: int = 2026) -> List[Dict[str, Any]]:
        """
        Obtiene el control individual de saldos reconocidos, solicitudes tramitadas y saldo restante.
        """
        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute("""
                INSERT OR IGNORE INTO saldos_compensacion (id_empleado, anio_goce, dias_asignados, dias_utilizados, dias_disponibles)
                SELECT DISTINCT a.id_empleado, ?, 16, 0, 16
                FROM asistencia_mensual_personal a
                WHERE a.cargo_funcion = 'AGENTE DE SEGURIDAD'
                  AND a.area_clasificacion = 'SEG'
                  AND (a.horario_laboral LIKE '%24%' OR a.horario_laboral LIKE '%25%')
            """, (anio,))
            conn.commit()

            cur.execute("""
                SELECT 
                    e.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(e.grupo_guardia_default, 1) as grupo_guardia_default,
                    COALESCE(sc.dias_asignados, 16) as dias_asignados,
                    COALESCE(sc.dias_utilizados, 0) as dias_utilizados,
                    COALESCE(sc.dias_disponibles, 16) as dias_disponibles,
                    COALESCE(r.nombre, 'LEY 29709') as regimen_nombre
                FROM saldos_compensacion sc
                JOIN empleados e ON sc.id_empleado = e.id_empleado
                JOIN asistencia_mensual_personal amp ON amp.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON amp.id_regimen = r.id_regimen
                WHERE sc.anio_goce = ?
                  AND amp.cargo_funcion = 'AGENTE DE SEGURIDAD'
                  AND amp.area_clasificacion = 'SEG'
                GROUP BY e.id_empleado
                ORDER BY e.apellidos_nombres ASC
            """, (anio,))
            saldos = [dict(r) for r in cur.fetchall()]

            # Solicitudes tramitadas por cada servidor
            cur.execute("""
                SELECT 
                    id_solicitud, id_empleado, fecha_compensacion, 
                    COALESCE(dias_solicitados, dias_compensados, 1) as dias_solicitados,
                    fechas_compensacion_detalle, numero_solicitud, observaciones
                FROM solicitudes_compensacion
                WHERE anio_goce = ? AND estado = 'APROBADO'
                ORDER BY fecha_compensacion DESC
            """, (anio,))
            usos = cur.fetchall()

            mapa_solicitudes = {}
            for u in usos:
                emp_id = u["id_empleado"]
                if emp_id not in mapa_solicitudes:
                    mapa_solicitudes[emp_id] = []
                mapa_solicitudes[emp_id].append(dict(u))

            for s in saldos:
                s["solicitudes_detalle"] = mapa_solicitudes.get(s["id_empleado"], [])

            return saldos

    @staticmethod
    def get_reporte_mensual_gastos(anio: int = 2026, mes: int = 1) -> List[Dict[str, Any]]:
        """
        Genera el reporte oficial de consumo mensual para remitir a la Oficina Regional:
        Quién gastó días en el mes, total acumulado gastado y saldo restante que le va quedando.
        """
        with get_connection() as conn:
            cur = conn.cursor()

            # Obtener servidores de seguridad 24x48
            cur.execute("""
                SELECT 
                    e.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(r.nombre, 'LEY 29709') as regimen_nombre,
                    COALESCE(sc.dias_asignados, 16) as saldo_reconocido
                FROM saldos_compensacion sc
                JOIN empleados e ON sc.id_empleado = e.id_empleado
                JOIN asistencia_mensual_personal amp ON amp.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON amp.id_regimen = r.id_regimen
                WHERE sc.anio_goce = ?
                  AND amp.cargo_funcion = 'AGENTE DE SEGURIDAD'
                  AND amp.area_clasificacion = 'SEG'
                GROUP BY e.id_empleado
                ORDER BY e.apellidos_nombres ASC
            """, (anio,))
            personal = [dict(r) for r in cur.fetchall()]

            # Consumo en el mes específico
            cur.execute("""
                SELECT 
                    id_empleado, 
                    SUM(COALESCE(dias_solicitados, dias_compensados, 1)) as dias_mes,
                    GROUP_CONCAT(COALESCE(fechas_compensacion_detalle, fecha_compensacion), ' | ') as detalle_fechas
                FROM solicitudes_compensacion
                WHERE anio_goce = ? AND mes = ? AND estado = 'APROBADO'
                GROUP BY id_empleado
            """, (anio, mes))
            consumo_mes = {r["id_empleado"]: dict(r) for r in cur.fetchall()}

            # Consumo acumulado hasta el mes
            cur.execute("""
                SELECT 
                    id_empleado, 
                    SUM(COALESCE(dias_solicitados, dias_compensados, 1)) as dias_acum
                FROM solicitudes_compensacion
                WHERE anio_goce = ? AND mes <= ? AND estado = 'APROBADO'
                GROUP BY id_empleado
            """, (anio, mes))
            consumo_acum = {r["id_empleado"]: r["dias_acum"] for r in cur.fetchall()}

            reporte = []
            for emp in personal:
                emp_id = emp["id_empleado"]
                info_mes = consumo_mes.get(emp_id, {})
                dias_en_mes = info_mes.get("dias_mes", 0) or 0
                dias_acumulados = consumo_acum.get(emp_id, 0) or 0
                saldo_inicial = emp["saldo_reconocido"]
                saldo_restante = max(0, saldo_inicial - dias_acumulados)

                emp["dias_gastados_mes"] = dias_en_mes
                emp["fechas_detalle_mes"] = info_mes.get("detalle_fechas", "-")
                emp["dias_gastados_acumulado"] = dias_acumulados
                emp["saldo_restante"] = saldo_restante

                reporte.append(emp)

            return reporte

    @staticmethod
    def registrar_solicitud_compensacion(
        id_empleado: int,
        anio_goce: int,
        mes: int,
        fecha_solicitud: str,
        fecha_compensacion: str,
        dias_solicitados: int,
        fechas_compensacion_detalle: str,
        numero_solicitud: str = "",
        observaciones: str = ""
    ) -> Dict[str, Any]:
        with get_connection() as conn:
            cur = conn.cursor()

            # Consultar saldo actual
            cur.execute("""
                SELECT dias_asignados, dias_utilizados, dias_disponibles
                FROM saldos_compensacion
                WHERE id_empleado = ? AND anio_goce = ?
            """, (id_empleado, anio_goce))
            saldo_row = cur.fetchone()

            if not saldo_row:
                saldo_inicial = 16
                dias_usados = 0
                dias_disponibles = 16
                cur.execute("""
                    INSERT INTO saldos_compensacion (id_empleado, anio_goce, dias_asignados, dias_utilizados, dias_disponibles)
                    VALUES (?, ?, 16, 0, 16)
                """, (id_empleado, anio_goce))
            else:
                saldo_inicial = saldo_row["dias_asignados"]
                dias_usados = saldo_row["dias_utilizados"]
                dias_disponibles = saldo_row["dias_disponibles"]

            if dias_solicitados > dias_disponibles:
                return {
                    "success": False,
                    "message": f"Días solicitados ({dias_solicitados}) superan el saldo disponible ({dias_disponibles} días)."
                }

            saldo_restante = dias_disponibles - dias_solicitados

            cur.execute("""
                INSERT INTO solicitudes_compensacion (
                    id_empleado, anio_goce, mes, fecha_solicitud, fecha_compensacion,
                    dias_compensados, dias_solicitados, fechas_compensacion_detalle,
                    saldo_anterior, saldo_restante, numero_solicitud, jefe_inmediato,
                    especialista_personal, estado, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'AUTORIZADO', 'CONFORME', 'APROBADO', ?)
            """, (
                id_empleado, anio_goce, mes, fecha_solicitud, fecha_compensacion,
                dias_solicitados, dias_solicitados, fechas_compensacion_detalle,
                dias_disponibles, saldo_restante, numero_solicitud, observaciones
            ))
            id_sol = cur.lastrowid

            # Actualizar tabla de saldos
            cur.execute("""
                UPDATE saldos_compensacion
                SET dias_utilizados = dias_utilizados + ?,
                    dias_disponibles = dias_disponibles - ?
                WHERE id_empleado = ? AND anio_goce = ?
            """, (dias_solicitados, dias_solicitados, id_empleado, anio_goce))

            conn.commit()

            return {
                "success": True,
                "id_solicitud": id_sol,
                "saldo_anterior": dias_disponibles,
                "dias_solicitados": dias_solicitados,
                "saldo_restante": saldo_restante,
                "message": f"Solicitud registrada exitosamente por {dias_solicitados} día(s). Saldo restante: {saldo_restante} días."
            }

    @staticmethod
    def eliminar_solicitud_compensacion(id_solicitud: int) -> Dict[str, Any]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_empleado, anio_goce, COALESCE(dias_solicitados, dias_compensados, 1) as cant_dias
                FROM solicitudes_compensacion
                WHERE id_solicitud = ?
            """, (id_solicitud,))
            sol = cur.fetchone()
            if not sol:
                return {"success": False, "message": "Solicitud no encontrada."}

            emp_id = sol["id_empleado"]
            anio_goce = sol["anio_goce"]
            cant_dias = sol["cant_dias"]

            cur.execute("DELETE FROM solicitudes_compensacion WHERE id_solicitud = ?", (id_solicitud,))

            # Reintegrar días
            cur.execute("""
                UPDATE saldos_compensacion
                SET dias_utilizados = max(0, dias_utilizados - ?),
                    dias_disponibles = min(dias_asignados, dias_disponibles + ?)
                WHERE id_empleado = ? AND anio_goce = ?
            """, (cant_dias, cant_dias, emp_id, anio_goce))

            conn.commit()
            return {"success": True, "message": f"Solicitud eliminada. Se han reintegrado {cant_dias} día(s) al saldo del servidor."}

    @staticmethod
    def get_solicitudes(anio: int = 2026) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    s.id_solicitud,
                    s.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    s.anio_goce,
                    s.mes,
                    s.fecha_solicitud,
                    s.fecha_compensacion,
                    COALESCE(s.dias_solicitados, s.dias_compensados, 1) as dias_solicitados,
                    COALESCE(s.fechas_compensacion_detalle, s.fecha_compensacion) as fechas_detalle,
                    s.saldo_anterior,
                    s.saldo_restante,
                    s.numero_solicitud,
                    s.jefe_inmediato,
                    s.especialista_personal,
                    s.estado,
                    s.observaciones,
                    s.created_at
                FROM solicitudes_compensacion s
                JOIN empleados e ON s.id_empleado = e.id_empleado
                WHERE s.anio_goce = ?
                ORDER BY s.fecha_compensacion DESC, s.id_solicitud DESC
            """, (anio,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_solicitud_detalle(id_solicitud: int) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    s.*,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    amp.cargo_funcion,
                    amp.horario_laboral,
                    amp.direccion_oficina,
                    rc.numero_resolucion
                FROM solicitudes_compensacion s
                JOIN empleados e ON s.id_empleado = e.id_empleado
                LEFT JOIN asistencia_mensual_personal amp ON amp.id_empleado = e.id_empleado
                LEFT JOIN saldos_compensacion sc ON sc.id_empleado = e.id_empleado AND sc.anio_goce = s.anio_goce
                LEFT JOIN resoluciones_compensacion rc ON sc.id_resolucion = rc.id_resolucion
                WHERE s.id_solicitud = ?
                LIMIT 1
            """, (id_solicitud,))
            row = cur.fetchone()
            return dict(row) if row else None