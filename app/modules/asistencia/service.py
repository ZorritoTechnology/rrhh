from typing import Dict, Any, List, Optional
from app.modules.asistencia.repository import AsistenciaRepository

class AsistenciaService:
    @staticmethod
    def asegurar_reporte_mes(anio: int, mes: int) -> int:
        return AsistenciaRepository.get_or_create_reporte_mensual(anio=anio, mes=mes)

    @staticmethod
    def obtener_libro_mes(anio: int, mes: int) -> Dict[str, Any]:
        rep_id = AsistenciaRepository.get_or_create_reporte_mensual(anio=anio, mes=mes)
        info = AsistenciaRepository.get_reporte_info(anio=anio, mes=mes)
        libro = AsistenciaRepository.get_libro_completo_mes(rep_id)
        catalogos = AsistenciaRepository.get_catalogos()

        # KPIs y contadores exactos para cada una de las hojas
        counts = {
            "personal": len(libro["personal"]),
            "funcionarios": len(libro["funcionarios"]),
            "sanciones": len(libro["sanciones"]),
            "renuncias": len(libro["renuncias"]),
            "reincorporaciones": len(libro["reincorporaciones"]),
            "desplazamientos": len(libro["desplazamientos"]),
            "licencias": len(libro["licencias"]),
            "vacaciones": len(libro["vacaciones"]),
            "tardanzas": len(libro["tardanzas"]),
            "permisos": len(libro["permisos"]),
            "inasistencias": len(libro["inasistencias"]),
            "no_registrados": len(libro["no_registrados"])
        }

        # Totales para resumen
        totales = {
            "total_trabajadores": counts["personal"],
            "dias_licencia": sum(l.get("dias", 0) for l in libro["licencias"]),
            "dias_vacaciones": sum(v.get("dias", 0) for v in libro["vacaciones"]),
            "dias_inasistencia": sum(i.get("dias", 0) for i in libro["inasistencias"]),
            "minutos_permisos": sum(p.get("minutos", 0) for p in libro["permisos"]),
            "minutos_tardanzas": sum(t.get("minutos", 0) for t in libro["tardanzas"])
        }

        kpis = {
            "total_novedades": sum(counts[k] for k in [
                "sanciones", "renuncias", "reincorporaciones", "desplazamientos",
                "licencias", "vacaciones", "tardanzas", "permisos", "inasistencias", "no_registrados"
            ]),
            "total_tardanzas_min": totales["minutos_tardanzas"],
            "total_dias_licencia": totales["dias_licencia"],
            "total_dias_vacaciones": totales["dias_vacaciones"],
            "total_inasistencias_dias": totales["dias_inasistencia"],
            "total_permisos_min": totales["minutos_permisos"],
        }

        return {
            "id_reporte": rep_id,
            "info": info,
            "libro": libro,
            "catalogos": catalogos,
            "counts": counts,
            "totales": totales,
            "kpis": kpis
        }

    @staticmethod
    def obtener_resumen_mes(anio: int, mes: int) -> Dict[str, Any]:
        """Compatibilidad con el dashboard."""
        return AsistenciaService.obtener_libro_mes(anio, mes)

    @staticmethod
    def obtener_historial_reportes() -> List[Dict[str, Any]]:
        return AsistenciaRepository.get_historial_reportes()

    @staticmethod
    def eliminar_registro(tabla: str, pk_col: str, id_valor: int) -> bool:
        return AsistenciaRepository.delete_registro(tabla=tabla, pk_col=pk_col, id_valor=id_valor)

    @staticmethod
    def cerrar_mes(anio: int, mes: int) -> bool:
        rep_id = AsistenciaRepository.get_or_create_reporte_mensual(anio=anio, mes=mes)
        return AsistenciaRepository.cambiar_estado_reporte(id_reporte=rep_id, nuevo_estado="CERRADO")

    @staticmethod
    def reabrir_mes(anio: int, mes: int) -> bool:
        rep_id = AsistenciaRepository.get_or_create_reporte_mensual(anio=anio, mes=mes)
        return AsistenciaRepository.cambiar_estado_reporte(id_reporte=rep_id, nuevo_estado="ABIERTO")

    @staticmethod
    def clonar_plantilla_mes_anterior(anio: int, mes: int) -> int:
        return AsistenciaRepository.traspasar_plantilla_mes_anterior(anio=anio, mes_destino=mes)

