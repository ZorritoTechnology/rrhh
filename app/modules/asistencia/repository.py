from typing import List, Dict, Any, Optional
from app.core.database import get_connection, get_db_cursor

class AsistenciaRepository:
    @staticmethod
    def get_or_create_reporte_mensual(anio: int, mes: int, id_establecimiento: int = 722, id_responsable: int = 1, obs: str = "") -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_reporte FROM reportes_cierre_mensual 
                WHERE anio = ? AND mes = ? AND id_establecimiento = ?
            """, (anio, mes, id_establecimiento))
            row = cur.fetchone()
            if row:
                return row["id_reporte"]

        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM empleados")
            total = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, observaciones_generales)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (anio, mes, id_establecimiento, id_responsable, total, obs or f"Reporte de Asistencia {mes:02d}/{anio}"))
            return cur.lastrowid

    @staticmethod
    def get_reporte_info(anio: int, mes: int, id_establecimiento: int = 722) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.*, e.nombre as nombre_establecimiento, resp.apellidos_nombres as responsable_nombre
                FROM reportes_cierre_mensual r
                LEFT JOIN establecimientos e ON r.id_establecimiento = e.id_establecimiento
                LEFT JOIN empleados resp ON r.id_responsable = resp.id_empleado
                WHERE r.anio = ? AND r.mes = ? AND r.id_establecimiento = ?
            """, (anio, mes, id_establecimiento))
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_historial_reportes() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.*, e.nombre as nombre_establecimiento, resp.apellidos_nombres as responsable_nombre
                FROM reportes_cierre_mensual r
                LEFT JOIN establecimientos e ON r.id_establecimiento = e.id_establecimiento
                LEFT JOIN empleados resp ON r.id_responsable = resp.id_empleado
                ORDER BY r.anio DESC, r.mes DESC
            """)
            return [dict(row) for row in cur.fetchall()]


    @staticmethod
    def get_catalogos() -> Dict[str, List[Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT nombre, descripcion FROM catalogo_tipos_sancion ORDER BY nombre")
            sanciones = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT nombre, descripcion FROM catalogo_tipos_licencia ORDER BY nombre")
            licencias = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT nombre FROM catalogo_entidades_licencia ORDER BY nombre")
            entidades = [r["nombre"] for r in cur.fetchall()]

            cur.execute("SELECT codigo, regimen FROM catalogo_niveles_directivos ORDER BY codigo")
            niveles_dir = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT id_regimen, codigo, nombre FROM regimenes_laborales ORDER BY id_regimen")
            regimenes = [dict(r) for r in cur.fetchall()]

            return {
                "sanciones": sanciones,
                "licencias": licencias,
                "entidades": entidades,
                "niveles_directivos": niveles_dir,
                "regimenes": regimenes
            }

    @staticmethod
    def get_personal_del_mes(id_reporte: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT a.*, e.codigo_servidor, e.dni, e.apellidos_nombres, r.nombre as nombre_regimen
                FROM asistencia_mensual_personal a
                JOIN empleados e ON a.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON a.id_regimen = r.id_regimen
                WHERE a.id_reporte = ?
                ORDER BY a.id_asistencia ASC
            """, (id_reporte,))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_libro_completo_mes(id_reporte: int) -> Dict[str, Any]:
        """Obtiene todas las pestañas de datos del mes específico."""
        with get_connection() as conn:
            cur = conn.cursor()

            # 1. Personal General
            cur.execute("""
                SELECT a.*, e.codigo_servidor, e.dni, e.apellidos_nombres, r.nombre as nombre_regimen
                FROM asistencia_mensual_personal a
                JOIN empleados e ON a.id_empleado = e.id_empleado
                LEFT JOIN regimenes_laborales r ON a.id_regimen = r.id_regimen
                WHERE a.id_reporte = ?
                ORDER BY a.id_asistencia ASC
            """, (id_reporte,))
            personal = [dict(r) for r in cur.fetchall()]

            # 2. Funcionarios
            cur.execute("""
                SELECT f.*, e.codigo_servidor, e.dni, e.apellidos_nombres, 'Ley N° 29709' as regimen
                FROM reporte_funcionarios f
                JOIN empleados e ON f.id_empleado = e.id_empleado
                WHERE f.id_reporte = ?
                ORDER BY f.id_funcionario ASC
            """, (id_reporte,))
            funcionarios = [dict(r) for r in cur.fetchall()]

            # 3. Sanciones
            cur.execute("""
                SELECT s.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_sanciones s
                JOIN empleados e ON s.id_empleado = e.id_empleado
                WHERE s.id_reporte = ?
                ORDER BY s.id_sancion ASC
            """, (id_reporte,))
            sanciones = [dict(r) for r in cur.fetchall()]

            # 4. Renuncias
            cur.execute("""
                SELECT ren.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_renuncias ren
                JOIN empleados e ON ren.id_empleado = e.id_empleado
                WHERE ren.id_reporte = ?
                ORDER BY ren.id_renuncia ASC
            """, (id_reporte,))
            renuncias = [dict(r) for r in cur.fetchall()]

            # 5. Reincorporaciones
            cur.execute("""
                SELECT reinc.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_reincorporaciones reinc
                JOIN empleados e ON reinc.id_empleado = e.id_empleado
                WHERE reinc.id_reporte = ?
                ORDER BY reinc.id_reincorporacion ASC
            """, (id_reporte,))
            reincorporaciones = [dict(r) for r in cur.fetchall()]

            # 6. Desplazamientos
            cur.execute("""
                SELECT d.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_desplazamientos d
                JOIN empleados e ON d.id_empleado = e.id_empleado
                WHERE d.id_reporte = ?
                ORDER BY d.id_desplazamiento ASC
            """, (id_reporte,))
            desplazamientos = [dict(r) for r in cur.fetchall()]

            # 7. Licencias
            cur.execute("""
                SELECT l.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_licencias l
                JOIN empleados e ON l.id_empleado = e.id_empleado
                WHERE l.id_reporte = ?
                ORDER BY l.id_licencia ASC
            """, (id_reporte,))
            licencias = [dict(r) for r in cur.fetchall()]

            # 8. Vacaciones
            cur.execute("""
                SELECT v.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_vacaciones v
                JOIN empleados e ON v.id_empleado = e.id_empleado
                WHERE v.id_reporte = ?
                ORDER BY v.id_vacacion ASC
            """, (id_reporte,))
            vacaciones = [dict(r) for r in cur.fetchall()]

            # 9. Tardanzas
            cur.execute("""
                SELECT t.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_tardanzas t
                JOIN empleados e ON t.id_empleado = e.id_empleado
                WHERE t.id_reporte = ?
                ORDER BY t.id_tardanza ASC
            """, (id_reporte,))
            tardanzas = [dict(r) for r in cur.fetchall()]

            # 10. Permisos Particulares
            cur.execute("""
                SELECT p.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_permisos p
                JOIN empleados e ON p.id_empleado = e.id_empleado
                WHERE p.id_reporte = ?
                ORDER BY p.id_permiso ASC
            """, (id_reporte,))
            permisos = [dict(r) for r in cur.fetchall()]

            # 11. Inasistencias Injustificadas
            cur.execute("""
                SELECT i.*, e.codigo_servidor, e.dni, e.apellidos_nombres
                FROM reporte_inasistencias i
                JOIN empleados e ON i.id_empleado = e.id_empleado
                WHERE i.id_reporte = ?
                ORDER BY i.id_inasistencia ASC
            """, (id_reporte,))
            inasistencias = [dict(r) for r in cur.fetchall()]

            # 12. No Registrados
            cur.execute("""
                SELECT * FROM reporte_no_registrados WHERE id_reporte = ?
            """, (id_reporte,))
            no_registrados = [dict(r) for r in cur.fetchall()]

            return {
                "personal": personal,
                "funcionarios": funcionarios,
                "sanciones": sanciones,
                "renuncias": renuncias,
                "reincorporaciones": reincorporaciones,
                "desplazamientos": desplazamientos,
                "licencias": licencias,
                "vacaciones": vacaciones,
                "tardanzas": tardanzas,
                "permisos": permisos,
                "inasistencias": inasistencias,
                "no_registrados": no_registrados
            }

    @staticmethod
    def insert_personal_mes(id_reporte: int, id_empleado: int, id_regimen: int, nivel: str, cargo_estructural: str,
                            estado_laboral: str, modalidad_laboral: str, direccion_oficina: str, jefatura_area: str,
                            cargo_funcion: str, area_clasificacion: str, horario_laboral: str, fecha_ingreso_eepp: str,
                            resolucion_documento: str, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO asistencia_mensual_personal (
                    id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                    modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                    horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                  modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                  horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_funcionario(id_reporte: int, id_empleado: int, cargo_funcion: str, nivel: str,
                           fecha_inicio_funciones: str, resolucion_documento: str, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_sancion(id_reporte: int, id_empleado: int, tipo_sancion: str, fecha_inicio: str,
                       fecha_termino: str, dias: int, tiempo_que_resuelve: str, resolucion_documento: str, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_sanciones (id_reporte, id_empleado, tipo_sancion, fecha_inicio, fecha_termino, dias, tiempo_que_resuelve, resolucion_documento, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, tipo_sancion, fecha_inicio, fecha_termino, dias, tiempo_que_resuelve, resolucion_documento, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_renuncia(id_reporte: int, id_empleado: int, a_partir_del: str, carta_fecha: str,
                        fecha_recepcion: str, motivos: str, ultimo_dia_laborado: str, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_renuncias (id_reporte, id_empleado, a_partir_del, carta_fecha, fecha_recepcion, motivos, ultimo_dia_laborado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, a_partir_del, carta_fecha, fecha_recepcion, motivos, ultimo_dia_laborado, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_reincorporacion(id_reporte: int, id_empleado: int, fecha_inicio_inactividad: str,
                               motivo_inactividad: str, fecha_reincorporacion: str, motivo_reincorporacion: str, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_reincorporaciones (id_reporte, id_empleado, fecha_inicio_inactividad, motivo_inactividad, fecha_reincorporacion, motivo_reincorporacion, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, fecha_inicio_inactividad, motivo_inactividad, fecha_reincorporacion, motivo_reincorporacion, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_desplazamiento(id_reporte: int, id_empleado: int, area: str, cargo_funcion: str, fecha: str, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, area, cargo_funcion, fecha_desplazamiento, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, area, cargo_funcion, fecha, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_licencia(id_reporte: int, id_empleado: int, tipo: str, entidad: str, fecha_inicio: str, fecha_termino: str, dias: int, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_vacacion(id_reporte: int, id_empleado: int, periodo: str, fecha_inicio: str, fecha_termino: str, dias: int, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_tardanza(id_reporte: int, id_empleado: int, minutos: int, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_tardanzas (id_reporte, id_empleado, minutos, observaciones)
                VALUES (?, ?, ?, ?)
            """, (id_reporte, id_empleado, minutos, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_permiso(id_reporte: int, id_empleado: int, minutos: int, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones)
                VALUES (?, ?, ?, ?)
            """, (id_reporte, id_empleado, minutos, observaciones))
            return cur.lastrowid

    @staticmethod
    def insert_inasistencia(id_reporte: int, id_empleado: int, dias: int, fechas_detalle: str, observaciones: str) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (id_reporte, id_empleado, dias, fechas_detalle, observaciones))
            return cur.lastrowid

    @staticmethod
    def cambiar_estado_reporte(id_reporte: int, nuevo_estado: str) -> bool:
        """Cambia el estado del reporte entre ABIERTO y CERRADO."""
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE reportes_cierre_mensual 
                SET estado = ?, fecha_cierre = CASE WHEN ? = 'CERRADO' THEN DATE('now') ELSE NULL END
                WHERE id_reporte = ?
            """, (nuevo_estado, nuevo_estado, id_reporte))
            return cur.rowcount > 0

    @staticmethod
    def traspasar_plantilla_mes_anterior(anio: int, mes_destino: int, id_establecimiento: int = 722) -> int:
        """Copia automáticamente la plantilla de personal del mes anterior al mes actual para dar continuidad operativa."""
        if mes_destino == 1:
            mes_origen = 12
            anio_origen = anio - 1
        else:
            mes_origen = mes_destino - 1
            anio_origen = anio

        with get_connection() as conn:
            cur = conn.cursor()
            # Buscar reporte origen
            cur.execute("""
                SELECT id_reporte, id_responsable FROM reportes_cierre_mensual
                WHERE anio = ? AND mes = ? AND id_establecimiento = ?
            """, (anio_origen, mes_origen, id_establecimiento))
            rep_origen = cur.fetchone()
            if not rep_origen:
                return 0
            
            id_rep_origen = rep_origen["id_reporte"]
            resp_id = rep_origen["id_responsable"]

            # Obtener personal de origen
            cur.execute("""
                SELECT id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                       modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                       horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
                FROM asistencia_mensual_personal
                WHERE id_reporte = ?
            """, (id_rep_origen,))
            filas = [dict(r) for r in cur.fetchall()]

        if not filas:
            return 0

        # Crear o buscar reporte destino
        id_rep_dest = AsistenciaRepository.get_or_create_reporte_mensual(
            anio=anio, mes=mes_destino, id_establecimiento=id_establecimiento, id_responsable=resp_id
        )

        with get_db_cursor() as cur:
            # Eliminar existentes para evitar duplicación
            cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte = ?", (id_rep_dest,))
            for f in filas:
                cur.execute("""
                    INSERT INTO asistencia_mensual_personal (
                        id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                        modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                        horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_rep_dest, f["id_empleado"], f["id_regimen"], f["nivel"], f["cargo_estructural"],
                    f["estado_laboral"], f["modalidad_laboral"], f["direccion_oficina"], f["jefatura_area"],
                    f["cargo_funcion"], f["area_clasificacion"], f["horario_laboral"], f["fecha_ingreso_eepp"],
                    f["resolucion_documento"], f["observaciones"]
                ))
            # Actualizar total trabajadores
            cur.execute("UPDATE reportes_cierre_mensual SET total_trabajadores = ? WHERE id_reporte = ?", (len(filas), id_rep_dest))
            return len(filas)

    @staticmethod
    def delete_registro(tabla: str, pk_col: str, id_valor: int) -> bool:
        tablas_permitidas = [
            "asistencia_mensual_personal", "reporte_funcionarios", "reporte_sanciones",
            "reporte_renuncias", "reporte_reincorporaciones", "reporte_desplazamientos",
            "reporte_licencias", "reporte_vacaciones", "reporte_tardanzas",
            "reporte_permisos", "reporte_inasistencias", "reporte_no_registrados"
        ]
        if tabla not in tablas_permitidas:
            raise ValueError(f"Tabla no autorizada: {tabla}")
        
        with get_db_cursor() as cur:
            cur.execute(f"DELETE FROM {tabla} WHERE {pk_col} = ?", (id_valor,))
            return cur.rowcount > 0


