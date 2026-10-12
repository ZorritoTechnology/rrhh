from typing import List, Dict, Any, Optional
from app.core.database import get_connection

class CompensacionRepository:

    @staticmethod
    def get_matriz_mensualizada(anio: int = 2026) -> List[Dict[str, Any]]:
        """
        Genera la matriz del Anexo 03 (Reporte Mensualizado)
        con columnas para cada mes (1 a 12), total de días usados,
        saldo asignado por RD y saldo pendiente.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    e.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(sc.dias_asignados, 16) as dias_asignados,
                    COALESCE(sc.dias_utilizados, 0) as dias_utilizados,
                    COALESCE(sc.dias_disponibles, 16) as dias_disponibles,
                    sc.observaciones as obs_saldo,
                    r.nombre as regimen_nombre
                FROM saldos_compensacion sc
                JOIN empleados e ON sc.id_empleado = e.id_empleado
                LEFT JOIN asistencia_mensual_personal amp ON amp.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON amp.id_regimen = r.id_regimen
                WHERE sc.anio_goce = ?
                GROUP BY e.id_empleado
                ORDER BY e.apellidos_nombres ASC
            """, (anio,))
            empleados = [dict(r) for r in cur.fetchall()]

            cur.execute("""
                SELECT id_empleado, mes, SUM(dias_compensados) as total_mes
                FROM solicitudes_compensacion
                WHERE anio_goce = ? AND estado = 'APROBADO'
                GROUP BY id_empleado, mes
            """, (anio,))
            consumos_mes = cur.fetchall()

            mapa_meses = {}
            for r in consumos_mes:
                emp_id = r["id_empleado"]
                if emp_id not in mapa_meses:
                    mapa_meses[emp_id] = {}
                mapa_meses[emp_id][r["mes"]] = r["total_mes"]

            matriz = []
            for emp in empleados:
                emp_id = emp["id_empleado"]
                meses_data = mapa_meses.get(emp_id, {})
                total_anual = 0
                for m in range(1, 13):
                    val = meses_data.get(m, 0)
                    emp[f"m_{m}"] = val if val > 0 else "-"
                    total_anual += val
                emp["total_utilizado"] = total_anual
                emp["saldo_disponible"] = max(0, emp["dias_asignados"] - total_anual)
                matriz.append(emp)

            return matriz

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
                    s.dias_compensados,
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
    def get_saldo_empleado(id_empleado: int, anio: int = 2026) -> Dict[str, Any]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    sc.dias_asignados,
                    COALESCE(SUM(s.dias_compensados), 0) as dias_usados,
                    (sc.dias_asignados - COALESCE(SUM(s.dias_compensados), 0)) as saldo_disponible
                FROM saldos_compensacion sc
                LEFT JOIN solicitudes_compensacion s ON s.id_empleado = sc.id_empleado 
                     AND s.anio_goce = sc.anio_goce AND s.estado = 'APROBADO'
                WHERE sc.id_empleado = ? AND sc.anio_goce = ?
                GROUP BY sc.id_empleado
            """, (id_empleado, anio))
            row = cur.fetchone()
            if row:
                return dict(row)
            return {"dias_asignados": 16, "dias_usados": 0, "saldo_disponible": 16}

    @staticmethod
    def registrar_solicitud(
        id_empleado: int,
        anio_goce: int,
        mes: int,
        fecha_solicitud: str,
        fecha_compensacion: str,
        observaciones: str = "",
        jefe_inmediato: str = "PENDIENTE",
        especialista_personal: str = "PENDIENTE"
    ) -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO solicitudes_compensacion (
                    id_empleado, anio_goce, mes, fecha_solicitud, fecha_compensacion,
                    dias_compensados, jefe_inmediato, especialista_personal, estado, observaciones
                ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, 'APROBADO', ?)
            """, (
                id_empleado,
                anio_goce,
                mes,
                fecha_solicitud,
                fecha_compensacion,
                jefe_inmediato,
                especialista_personal,
                observaciones
            ))
            id_sol = cur.lastrowid
            cur.execute("""
                UPDATE saldos_compensacion
                SET dias_utilizados = dias_utilizados + 1,
                    dias_disponibles = dias_disponibles - 1
                WHERE id_empleado = ? AND anio_goce = ?
            """, (id_empleado, anio_goce))
            conn.commit()
            return id_sol

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