from typing import List, Dict, Any, Optional
from app.core.database import get_connection

class DesplazamientoRepository:

    @staticmethod
    def listar_establecimientos() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_establecimiento, id_or, nombre FROM establecimientos ORDER BY nombre ASC")
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def listar_desplazamientos(tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            query = """
                SELECT 
                    d.*,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(eo.nombre, d.nombre_origen_ext, 'No especificado') as establecimiento_origen,
                    COALESCE(ed.nombre, d.nombre_destino_ext, 'No especificado') as establecimiento_destino
                FROM desplazamientos_personal d
                JOIN empleados e ON d.id_empleado = e.id_empleado
                LEFT JOIN establecimientos eo ON d.id_establecimiento_origen = eo.id_establecimiento
                LEFT JOIN establecimientos ed ON d.id_establecimiento_destino = ed.id_establecimiento
            """
            params = []
            if tipo:
                query += " WHERE d.tipo_movimiento = ? "
                params.append(tipo)
            query += " ORDER BY d.fecha_desplazamiento DESC, d.id_desplazamiento DESC"
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def obtener_desplazamiento_detalle(id_desplazamiento: int) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    d.*,
                    e.codigo_servidor,
                    e.dni,
                    e.apellidos_nombres,
                    COALESCE(eo.nombre, d.nombre_origen_ext, 'No especificado') as establecimiento_origen,
                    COALESCE(ed.nombre, d.nombre_destino_ext, 'No especificado') as establecimiento_destino,
                    amp.cargo_funcion,
                    amp.horario_laboral,
                    amp.nivel
                FROM desplazamientos_personal d
                JOIN empleados e ON d.id_empleado = e.id_empleado
                LEFT JOIN establecimientos eo ON d.id_establecimiento_origen = eo.id_establecimiento
                LEFT JOIN establecimientos ed ON d.id_establecimiento_destino = ed.id_establecimiento
                LEFT JOIN asistencia_mensual_personal amp ON amp.id_empleado = e.id_empleado
                WHERE d.id_desplazamiento = ?
                LIMIT 1
            """, (id_desplazamiento,))
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def registrar_alta_desplazamiento(
        id_empleado: int,
        id_establecimiento_origen: Optional[int],
        nombre_origen_ext: str,
        fecha_desplazamiento: str,
        fecha_presentacion_eepp: str,
        documento_oficial: str,
        vacaciones_periodo: str = "2025-2026",
        vacaciones_gozadas_origen: int = 0,
        vacaciones_saldo_origen: int = 30,
        comp_anio_fiscal: int = 2026,
        comp_ganadas_origen: int = 0,
        comp_gozadas_origen: int = 0,
        comp_saldo_origen: int = 0,
        observaciones: str = ""
    ) -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO desplazamientos_personal (
                    id_empleado, tipo_movimiento, id_establecimiento_origen, id_establecimiento_destino,
                    nombre_origen_ext, nombre_destino_ext, fecha_desplazamiento, fecha_presentacion_eepp,
                    documento_oficial, vacaciones_periodo, vacaciones_gozadas_origen, vacaciones_saldo_origen,
                    comp_anio_fiscal, comp_ganadas_origen, comp_gozadas_origen, comp_saldo_origen,
                    observaciones, estado
                ) VALUES (
                    ?, 'ALTA_RECEPCION', ?, 722,
                    ?, 'EP. MUJERES IQUITOS (722)', ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, 'ACTIVO'
                )
            """, (
                id_empleado, id_establecimiento_origen, nombre_origen_ext,
                fecha_desplazamiento, fecha_presentacion_eepp, documento_oficial,
                vacaciones_periodo, vacaciones_gozadas_origen, vacaciones_saldo_origen,
                comp_anio_fiscal, comp_ganadas_origen, comp_gozadas_origen, comp_saldo_origen,
                observaciones
            ))
            id_desp = cur.lastrowid
            conn.commit()
            return id_desp

    @staticmethod
    def registrar_baja_desplazamiento(
        id_empleado: int,
        id_establecimiento_destino: Optional[int],
        nombre_destino_ext: str,
        fecha_desplazamiento: str,
        documento_oficial: str,
        vacaciones_periodo: str = "2025-2026",
        vacaciones_gozadas_iquitos: int = 0,
        vacaciones_saldo_iquitos: int = 30,
        comp_anio_fiscal: int = 2026,
        comp_ganadas_iquitos: int = 0,
        comp_gozadas_iquitos: int = 0,
        comp_saldo_iquitos: int = 0,
        observaciones: str = ""
    ) -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO desplazamientos_personal (
                    id_empleado, tipo_movimiento, id_establecimiento_origen, id_establecimiento_destino,
                    nombre_origen_ext, nombre_destino_ext, fecha_desplazamiento, fecha_presentacion_eepp,
                    documento_oficial, vacaciones_periodo, vacaciones_gozadas_origen, vacaciones_saldo_origen,
                    comp_anio_fiscal, comp_ganadas_origen, comp_gozadas_origen, comp_saldo_origen,
                    observaciones, estado
                ) VALUES (
                    ?, 'BAJA_SALIDA', 722, ?,
                    'EP. MUJERES IQUITOS (722)', ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, 'TRASLADADO'
                )
            """, (
                id_empleado, id_establecimiento_destino, nombre_destino_ext,
                fecha_desplazamiento, fecha_desplazamiento, documento_oficial,
                vacaciones_periodo, vacaciones_gozadas_iquitos, vacaciones_saldo_iquitos,
                comp_anio_fiscal, comp_ganadas_iquitos, comp_gozadas_iquitos, comp_saldo_iquitos,
                observaciones
            ))
            id_desp = cur.lastrowid
            conn.commit()
            return id_desp
