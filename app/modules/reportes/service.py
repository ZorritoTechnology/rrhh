from typing import List, Dict, Any
from app.core.database import get_connection

class ReportesService:
    @staticmethod
    def get_catalogo_anexos() -> List[Dict[str, Any]]:
        """Catálogo oficial de Anexos según Directiva 003-2023-INPE-OGA."""
        return [
            {"id": 1, "codigo": "ANEXO-01", "titulo": "Reporte Mensual de Asistencia del Personal", "descripcion": "Consolidado maestro de asistencia, modalidades y regímenes laborales del mes."},
            {"id": 2, "codigo": "ANEXO-02", "titulo": "Reporte de Funcionarios y Directivos", "descripcion": "Altas y asignación de cargos directivos y de confianza (F-1 a F-6, S3 a S5)."},
            {"id": 3, "codigo": "ANEXO-03", "titulo": "Reporte de Sanciones Disciplinarias", "descripcion": "Medidas disciplinarias, suspensiones, amonestaciones y ceses temporales."},
            {"id": 4, "codigo": "ANEXO-04", "titulo": "Reporte de Renuncias", "descripcion": "Ceses voluntarios, recepción de cartas y último día laborado."},
            {"id": 5, "codigo": "ANEXO-05", "titulo": "Reporte de Reincorporaciones", "descripcion": "Retornos por mandato judicial, fin de licencias o ceses temporales."},
            {"id": 6, "codigo": "ANEXO-06", "titulo": "Reporte de Desplazamientos y Rotaciones", "descripcion": "Traslados entre establecimientos penitenciarios o áreas internas."},
            {"id": 7, "codigo": "ANEXO-07", "titulo": "Reporte de Licencias con y sin Goce de Haber", "descripcion": "Licencias médicas (ESSALUD/MINSA/PARTICULAR), onomásticos, maternidad, etc."},
            {"id": 8, "codigo": "ANEXO-08", "titulo": "Reporte de Vacaciones Gozadas y Fraccionamientos", "descripcion": "Registro detallado de períodos vacacionales gozados en el mes."},
            {"id": 9, "codigo": "ANEXO-09", "titulo": "Reporte de Tardanzas y Permisos Particulares", "descripcion": "Cómputo en minutos para deducciones de planillas."},
            {"id": 10, "codigo": "ANEXO-10", "titulo": "Reporte de Inasistencias Injustificadas", "descripcion": "Días no laborados sin justificación y detalle de fechas exactas."}
        ]

    @staticmethod
    def obtener_datos_anexo(id_anexo: int, anio: int = 2026, mes: int = 1) -> Dict[str, Any]:
        with get_connection() as conn:
            cur = conn.cursor()
            
            # Buscar reporte mensual
            cur.execute("SELECT id_reporte FROM reportes_cierre_mensual WHERE anio = ? AND mes = ?", (anio, mes))
            rep = cur.fetchone()
            rep_id = rep["id_reporte"] if rep else None

            datos = []
            if rep_id:
                if id_anexo == 1: # Personal General del Mes
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, a.cargo_funcion as tipo, 
                               a.area_clasificacion as computo, a.resolucion_documento as observaciones,
                               a.nivel, a.horario_laboral
                        FROM asistencia_mensual_personal a
                        JOIN empleados e ON a.id_empleado = e.id_empleado
                        WHERE a.id_reporte = ?
                        ORDER BY a.id_asistencia ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 2: # Funcionarios
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, f.cargo_funcion as tipo, 
                               f.nivel as computo, f.resolucion_documento as observaciones, f.fecha_inicio_funciones
                        FROM reporte_funcionarios f
                        JOIN empleados e ON f.id_empleado = e.id_empleado
                        WHERE f.id_reporte = ?
                        ORDER BY f.id_funcionario ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 3: # Sanciones
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, s.tipo_sancion as tipo,
                               s.dias as dias, s.resolucion_documento as observaciones, s.tiempo_que_resuelve
                        FROM reporte_sanciones s
                        JOIN empleados e ON s.id_empleado = e.id_empleado
                        WHERE s.id_reporte = ?
                        ORDER BY s.id_sancion ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 4: # Renuncias
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, ren.motivos as tipo,
                               ren.ultimo_dia_laborado as computo, ren.observaciones
                        FROM reporte_renuncias ren
                        JOIN empleados e ON ren.id_empleado = e.id_empleado
                        WHERE ren.id_reporte = ?
                        ORDER BY ren.id_renuncia ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 5: # Reincorporaciones
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, reinc.motivo_reincorporacion as tipo,
                               reinc.fecha_reincorporacion as computo, reinc.observaciones
                        FROM reporte_reincorporaciones reinc
                        JOIN empleados e ON reinc.id_empleado = e.id_empleado
                        WHERE reinc.id_reporte = ?
                        ORDER BY reinc.id_reincorporacion ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 6: # Desplazamientos
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, d.area as tipo,
                               d.cargo_funcion as computo, d.fecha_desplazamiento, d.observaciones
                        FROM reporte_desplazamientos d
                        JOIN empleados e ON d.id_empleado = e.id_empleado
                        WHERE d.id_reporte = ?
                        ORDER BY d.id_desplazamiento ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 7: # Licencias
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, l.tipo, l.entidad,
                               l.fecha_inicio, l.fecha_termino, l.dias, l.observaciones
                        FROM reporte_licencias l
                        JOIN empleados e ON l.id_empleado = e.id_empleado
                        WHERE l.id_reporte = ?
                        ORDER BY l.id_licencia ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 8: # Vacaciones
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, v.periodo,
                               v.fecha_inicio, v.fecha_termino, v.dias, v.observaciones
                        FROM reporte_vacaciones v
                        JOIN empleados e ON v.id_empleado = e.id_empleado
                        WHERE v.id_reporte = ?
                        ORDER BY v.id_vacacion ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 9: # Tardanzas y permisos
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres,
                               COALESCE(t.minutos, 0) as tardanzas_min,
                               COALESCE(p.minutos, 0) as permisos_min,
                               COALESCE(t.observaciones, p.observaciones) as observaciones
                        FROM empleados e
                        LEFT JOIN reporte_tardanzas t ON e.id_empleado = t.id_empleado AND t.id_reporte = ?
                        LEFT JOIN reporte_permisos p ON e.id_empleado = p.id_empleado AND p.id_reporte = ?
                        WHERE t.id_tardanza IS NOT NULL OR p.id_permiso IS NOT NULL
                    """, (rep_id, rep_id))
                    datos = [dict(r) for r in cur.fetchall()]

                elif id_anexo == 10: # Inasistencias
                    cur.execute("""
                        SELECT e.codigo_servidor, e.dni, e.apellidos_nombres, i.dias,
                               i.fechas_detalle, i.observaciones
                        FROM reporte_inasistencias i
                        JOIN empleados e ON i.id_empleado = e.id_empleado
                        WHERE i.id_reporte = ?
                        ORDER BY i.id_inasistencia ASC
                    """, (rep_id,))
                    datos = [dict(r) for r in cur.fetchall()]

            return {
                "id_anexo": id_anexo,
                "anio": anio,
                "mes": mes,
                "datos": datos,
                "total_registros": len(datos)
            }
