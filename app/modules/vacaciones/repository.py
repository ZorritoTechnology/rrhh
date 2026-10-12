from typing import List, Dict, Any, Optional
from app.core.database import get_connection, get_db_cursor

class VacacionesRepository:
    @staticmethod
    def get_consumo_consolidado() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT e.id_empleado, e.codigo_servidor, e.apellidos_nombres,
                       COALESCE(SUM(v.dias), 0) as dias_consumidos,
                       GROUP_CONCAT(v.periodo || ' (' || v.dias || 'd)', ', ') as desglose_periodos,
                       GROUP_CONCAT(v.observaciones, ' | ') as observaciones
                FROM empleados e
                LEFT JOIN reporte_vacaciones v ON e.id_empleado = v.id_empleado
                GROUP BY e.id_empleado
                ORDER BY dias_consumidos DESC, e.apellidos_nombres ASC
            """)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_solicitudes() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            # Asegurar tabla de solicitudes
            cur.execute("""
                CREATE TABLE IF NOT EXISTS solicitudes_vacaciones (
                    id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER NOT NULL,
                    periodo VARCHAR(50) NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_termino DATE NOT NULL,
                    dias_solicitados INTEGER NOT NULL,
                    estado VARCHAR(20) DEFAULT 'APROBADO',
                    tipo_uso VARCHAR(50) DEFAULT 'GOZADO',
                    observaciones TEXT,
                    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
                )
            """)
            cur.execute("""
                SELECT s.*, e.apellidos_nombres, e.codigo_servidor
                FROM solicitudes_vacaciones s
                JOIN empleados e ON s.id_empleado = e.id_empleado
                ORDER BY s.fecha_solicitud DESC
            """)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def obtener_saldo_personal_periodo(id_empleado: int, periodo: str) -> Dict[str, Any]:
        """Calcula los días gozados y el saldo restante (30 días por año) para un empleado y período."""
        with get_connection() as conn:
            cur = conn.cursor()
            # Fecha de ingreso más reciente en asistencia
            cur.execute("""
                SELECT fecha_ingreso_eepp FROM asistencia_mensual_personal
                WHERE id_empleado = ? AND fecha_ingreso_eepp IS NOT NULL AND fecha_ingreso_eepp != ''
                ORDER BY id_asistencia DESC LIMIT 1
            """, (id_empleado,))
            row_fecha = cur.fetchone()
            fecha_ingreso = row_fecha["fecha_ingreso_eepp"] if row_fecha else "No registrada"

            # Sumar días tomados en dicho período
            cur.execute("""
                SELECT COALESCE(SUM(dias), 0) as dias_gozados
                FROM reporte_vacaciones
                WHERE id_empleado = ? AND periodo = ?
            """, (id_empleado, str(periodo).strip()))
            dias_gozados = cur.fetchone()["dias_gozados"]
            dias_derecho = 30
            saldo_restante = max(0, dias_derecho - dias_gozados)

            return {
                "id_empleado": id_empleado,
                "periodo": periodo,
                "fecha_ingreso": fecha_ingreso,
                "dias_derecho": dias_derecho,
                "dias_gozados": dias_gozados,
                "saldo_restante": saldo_restante
            }

    @staticmethod
    def get_historial_completo_personal(id_empleado: Optional[int] = None) -> List[Dict[str, Any]]:

        """Obtiene el historial detallado de todas las salidas de vacaciones por servidor y período con fechas exactas."""
        with get_connection() as conn:
            cur = conn.cursor()
            query = """
                SELECT v.id_vacacion, v.id_empleado, e.codigo_servidor, e.dni, e.apellidos_nombres,
                       v.periodo, v.fecha_inicio, v.fecha_termino, v.dias, v.observaciones,
                       r.mes, r.anio
                FROM reporte_vacaciones v
                JOIN empleados e ON v.id_empleado = e.id_empleado
                JOIN reportes_cierre_mensual r ON v.id_reporte = r.id_reporte
            """
            params = []
            if id_empleado:
                query += " WHERE v.id_empleado = ?"
                params.append(id_empleado)
            query += " ORDER BY e.apellidos_nombres ASC, v.periodo DESC, v.fecha_inicio DESC"
            cur.execute(query, tuple(params))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_reporte_desplazados() -> List[Dict[str, Any]]:
        """Obtiene todos los servidores que han sido desplazados hacia otros penales/establecimientos."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT d.id_desplazamiento, d.id_empleado, e.codigo_servidor, e.dni, e.apellidos_nombres,
                       d.area, d.cargo_funcion, d.fecha_desplazamiento, d.observaciones,
                       r.mes, r.anio
                FROM reporte_desplazamientos d
                JOIN empleados e ON d.id_empleado = e.id_empleado
                JOIN reportes_cierre_mensual r ON d.id_reporte = r.id_reporte
                ORDER BY d.fecha_desplazamiento DESC, r.mes DESC
            """)
            return [dict(r) for r in cur.fetchall()]


