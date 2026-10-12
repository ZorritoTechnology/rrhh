from datetime import datetime, date
from typing import Dict, Any, List
from app.core.database import get_connection
from app.modules.compensacion.repository import CompensacionRepository

class CompensacionService:

    @staticmethod
    def validar_y_registrar_solicitud(
        id_empleado: int,
        fecha_solicitud: str,
        fecha_compensacion: str,
        observaciones: str = "",
        es_regularizacion: bool = False,
        jefe_inmediato: str = "AUTORIZADO",
        especialista_personal: str = "CONFORME"
    ) -> Dict[str, Any]:
        """
        Valida las reglas estrictas del Lineamiento LI-001-2023-INPE-OGA:
        1. No fraccionable (1 jornada completa = 24 horas = 1 día).
        2. Saldo disponible máximo según RD (hasta 16 días al año 2026).
        3. Anticipación mínima de 5 días calendario (numeral 5.3).
        4. No cruce con otras solicitudes del mismo día.
        5. Coherencia cronológica (fecha_compensacion >= fecha_solicitud).
        """
        try:
            d_sol = datetime.strptime(fecha_solicitud, "%Y-%m-%d").date()
            d_comp = datetime.strptime(fecha_compensacion, "%Y-%m-%d").date()
        except ValueError:
            return {"success": False, "message": "Formato de fechas inválido (debe ser YYYY-MM-DD)"}

        anio_goce = d_comp.year
        mes = d_comp.month

        # Validación 0: Año fiscal 2026
        if anio_goce != 2026:
            return {
                "success": False,
                "message": f"La fecha de compensación debe corresponder al ejercicio fiscal 2026. Ha ingresado fecha del año {anio_goce}."
            }

        # Validación 1: Coherencia temporal (no compensar fechas anteriores a la solicitud)
        if d_comp < d_sol:
            return {
                "success": False,
                "message": f"Inconsistencia en fechas: La fecha a compensar ({fecha_compensacion}) no puede ser anterior a la fecha de solicitud ({fecha_solicitud})."
            }

        # Validación 2: Anticipación mínima de 5 días calendario (Directiva numeral 5.3)
        diff_dias = (d_comp - d_sol).days
        if diff_dias < 5:
            if not es_regularizacion and "regulariz" not in observaciones.lower() and "necesidad" not in observaciones.lower():
                return {
                    "success": False,
                    "message": f"Conforme al numeral 5.3 del Lineamiento LI-001-2023-INPE-OGA, la solicitud debe presentarse con mínimo 5 días de anticipación (diferencia actual: {diff_dias} días). Si es un caso excepcional autorizado, consigne el motivo de regularización."
                }
            observaciones += f" [Regularización autorizada: Solicitado con {diff_dias} días de antelación]"

        # Validación 3: Saldo disponible
        saldo = CompensacionRepository.get_saldo_empleado(id_empleado, anio_goce)
        if saldo["saldo_disponible"] <= 0:
            return {
                "success": False,
                "message": f"El servidor no cuenta con saldo disponible de compensación para el año {anio_goce}. Límite alcanzado: {saldo['dias_usados']}/{saldo['dias_asignados']} días."
            }

        # Validación 3: No duplicar el mismo día
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_solicitud FROM solicitudes_compensacion
                WHERE id_empleado = ? AND fecha_compensacion = ? AND estado != 'RECHAZADO'
            """, (id_empleado, fecha_compensacion))
            if cur.fetchone():
                return {
                    "success": False,
                    "message": f"Ya existe una compensación registrada para este servidor en la fecha {fecha_compensacion}."
                }

        # Registro exitoso
        id_sol = CompensacionRepository.registrar_solicitud(
            id_empleado=id_empleado,
            anio_goce=anio_goce,
            mes=mes,
            fecha_solicitud=fecha_solicitud,
            fecha_compensacion=fecha_compensacion,
            observaciones=observaciones,
            jefe_inmediato=jefe_inmediato,
            especialista_personal=especialista_personal
        )

        return {
            "success": True,
            "id_solicitud": id_sol,
            "message": "Solicitud de Compensación (Anexo 01) procesada y autorizada exitosamente conforme al Lineamiento LI-001-2023-INPE-OGA."
        }
