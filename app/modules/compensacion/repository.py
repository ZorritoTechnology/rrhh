from typing import List, Dict, Any, Optional
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

            # Obtener servidores de seguridad que laboran en régimen 24x48
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
                WHERE amp.horario_laboral LIKE '%24%' OR amp.area_clasificacion = 'SEG'
                GROUP BY e.id_empleado
                ORDER BY e.apellidos_nombres ASC
            """)
            empleados = [dict(r) for r in cur.fetchall()]

            # Obtener días de exceso ganados por mes desde compensacion_dias_ganados
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

                # Tope normativo de 16 días anuales (numeral 4.2 y 4.4)
                emp["total_ganado"] = min(16, total_ganado_bruto)
                emp["total_bruto"] = total_ganado_bruto
                matriz.append(emp)

            return matriz

    @staticmethod
    def get_control_saldos(anio: int = 2026) -> List[Dict[str, Any]]:
        """
        Obtiene el control de DÍAS USADOS y DÍAS RESTANTES (Goce de Compensación)
        para cada servidor de seguridad 24x48.
        """
        with get_connection() as conn:
            cur = conn.cursor()

            # Asegurar saldos para todos los empleados de seguridad
            cur.execute("""
                INSERT OR IGNORE INTO saldos_compensacion (id_empleado, anio_goce, dias_asignados, dias_utilizados, dias_disponibles)
                SELECT DISTINCT a.id_empleado, ?, 16, 0, 16
                FROM asistencia_mensual_personal a
                WHERE a.horario_laboral LIKE '%24%' OR a.area_clasificacion = 'SEG'
            """, (anio,))
            conn.commit()

            cur.execute("""
                SELECT 
                    e.id_empleado,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(sc.dias_asignados, 16) as dias_asignados,
                    COALESCE(sc.dias_utilizados, 0) as dias_utilizados,
                    COALESCE(sc.dias_disponibles, 16) as dias_disponibles,
                    COALESCE(r.nombre, 'LEY 29709') as regimen_nombre
                FROM saldos_compensacion sc
                JOIN empleados e ON sc.id_empleado = e.id_empleado
                LEFT JOIN asistencia_mensual_personal amp ON amp.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON amp.id_regimen = r.id_regimen
                WHERE sc.anio_goce = ?
                GROUP BY e.id_empleado
                ORDER BY e.apellidos_nombres ASC
            """, (anio,))
            saldos = [dict(r) for r in cur.fetchall()]

            # Fechas consumidas por cada servidor
            cur.execute("""
                SELECT id_empleado, fecha_compensacion, numero_solicitud, observaciones
                FROM solicitudes_compensacion
                WHERE anio_goce = ? AND estado = 'APROBADO'
                ORDER BY fecha_compensacion DESC
            """, (anio,))
            usos = cur.fetchall()

            mapa_fechas = {}
            for u in usos:
                emp_id = u["id_empleado"]
                if emp_id not in mapa_fechas:
                    mapa_fechas[emp_id] = []
                mapa_fechas[emp_id].append(dict(u))

            for s in saldos:
                s["historial_fechas"] = mapa_fechas.get(s["id_empleado"], [])

            return saldos

    @staticmethod
    def get_solicitudes(anio: int = 2026) -> List[Dict[str, Any]]:
        """
        Historial de papeletas manuales registradas en el año.
        """
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
                    s.numero_solicitud,
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