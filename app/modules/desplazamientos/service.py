from typing import Dict, Any, List, Optional
from app.core.database import get_connection
from app.modules.desplazamientos.repository import DesplazamientoRepository
from app.modules.compensacion.repository import CompensacionRepository

class DesplazamientoService:

    @staticmethod
    def procesar_alta_desplazamiento(
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
    ) -> Dict[str, Any]:
        """
        Procesa el alta de un servidor penitenciario recibido desde otro penal
        conforme al Anexo 06 (REG-006-URH) de la Directiva DI-003-2023-INPE-OGA.
        """
        if not id_empleado or not documento_oficial:
            return {"success": False, "message": "Debe seleccionar un servidor y consignar el documento oficial de desplazamiento."}

        # 1. Registrar desplazamiento en tabla histórica
        id_desp = DesplazamientoRepository.registrar_alta_desplazamiento(
            id_empleado=id_empleado,
            id_establecimiento_origen=id_establecimiento_origen,
            nombre_origen_ext=nombre_origen_ext,
            fecha_desplazamiento=fecha_desplazamiento,
            fecha_presentacion_eepp=fecha_presentacion_eepp,
            documento_oficial=documento_oficial,
            vacaciones_periodo=vacaciones_periodo,
            vacaciones_gozadas_origen=vacaciones_gozadas_origen,
            vacaciones_saldo_origen=vacaciones_saldo_origen,
            comp_anio_fiscal=comp_anio_fiscal,
            comp_ganadas_origen=comp_ganadas_origen,
            comp_gozadas_origen=comp_gozadas_origen,
            comp_saldo_origen=comp_saldo_origen,
            observaciones=observaciones
        )

        # 2. Sincronizar saldos de compensación 24x48
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_saldo, dias_asignados, dias_utilizados FROM saldos_compensacion
                WHERE id_empleado = ? AND anio_goce = ?
            """, (id_empleado, comp_anio_fiscal))
            row = cur.fetchone()

            obs_saldo = f"ALTA POR DESPLAZAMIENTO: Procedente de {nombre_origen_ext or 'otro penal'}. Trae {comp_gozadas_origen} días 24x48 gozados en origen. Doc: {documento_oficial}"

            if row:
                # Actualizar saldo existente
                dias_asig = row["dias_asignados"]
                dias_usados_totales = row["dias_utilizados"] + comp_gozadas_origen
                dias_disp = max(0, dias_asig - dias_usados_totales)
                cur.execute("""
                    UPDATE saldos_compensacion
                    SET dias_utilizados = ?,
                        dias_disponibles = ?,
                        observaciones = ?
                    WHERE id_saldo = ?
                """, (dias_usados_totales, dias_disp, obs_saldo, row["id_saldo"]))
            else:
                # Crear nuevo saldo para el año
                dias_disp = max(0, 16 - comp_gozadas_origen)
                cur.execute("""
                    INSERT INTO saldos_compensacion (
                        id_empleado, anio_goce, dias_asignados, dias_utilizados, dias_disponibles, observaciones
                    ) VALUES (?, ?, 16, ?, ?, ?)
                """, (id_empleado, comp_anio_fiscal, comp_gozadas_origen, dias_disp, obs_saldo))

            # Sincronizar estado laboral a ACTIVO en padrón de empleados
            cur.execute("""
                UPDATE empleados 
                SET estado_laboral = 'ACTIVO'
                WHERE id_empleado = ?
            """, (id_empleado,))

            conn.commit()

        return {
            "success": True,
            "id_desplazamiento": id_desp,
            "message": f"Servidor penitenciario incorporado exitosamente con récord de origen ({vacaciones_gozadas_origen} días vac. y {comp_gozadas_origen} días 24x48 gozados)."
        }

    @staticmethod
    def procesar_baja_desplazamiento(
        id_empleado: int,
        id_establecimiento_destino: Optional[int],
        nombre_destino_ext: str,
        fecha_desplazamiento: str,
        documento_oficial: str,
        observaciones: str = ""
    ) -> Dict[str, Any]:
        """
        Procesa el traslado / rotación de un servidor hacia otro establecimiento penitenciario.
        Calcula el récord acumulado en Iquitos para emitir el Anexo 06 (REG-006-URH).
        """
        if not id_empleado or not documento_oficial:
            return {"success": False, "message": "Debe seleccionar un servidor y consignar el documento oficial de desplazamiento."}

        # Obtener récord acumulado en Iquitos
        saldo_comp = CompensacionRepository.get_saldo_empleado(id_empleado, 2026)
        comp_gozadas = saldo_comp["dias_usados"]
        comp_saldo = saldo_comp["saldo_disponible"]

        # Registrar baja
        id_desp = DesplazamientoRepository.registrar_baja_desplazamiento(
            id_empleado=id_empleado,
            id_establecimiento_destino=id_establecimiento_destino,
            nombre_destino_ext=nombre_destino_ext,
            fecha_desplazamiento=fecha_desplazamiento,
            documento_oficial=documento_oficial,
            vacaciones_periodo="2025-2026",
            vacaciones_gozadas_iquitos=0, # Dinámico
            vacaciones_saldo_iquitos=30,
            comp_anio_fiscal=2026,
            comp_ganadas_iquitos=saldo_comp["dias_asignados"],
            comp_gozadas_iquitos=comp_gozadas,
            comp_saldo_iquitos=comp_saldo,
            observaciones=observaciones
        )

        # Actualizar estado en saldos_compensacion y estado_laboral en empleados
        with get_connection() as conn:
            cur = conn.cursor()
            obs_baja = f"DESPLAZADO A {nombre_destino_ext} EL {fecha_desplazamiento}. Doc: {documento_oficial}. Saldo remitido: {comp_saldo} días."
            cur.execute("""
                UPDATE saldos_compensacion
                SET observaciones = ?
                WHERE id_empleado = ? AND anio_goce = 2026
            """, (obs_baja, id_empleado))

            cur.execute("""
                UPDATE empleados
                SET estado_laboral = 'DESPLAZADO'
                WHERE id_empleado = ?
            """, (id_empleado,))

            conn.commit()

        return {
            "success": True,
            "id_desplazamiento": id_desp,
            "message": f"Baja por desplazamiento registrada exitosamente hacia {nombre_destino_ext}. Puede imprimir la Constancia Anexo 06."
        }

    @staticmethod
    def procesar_modificacion_desplazamiento(
        id_desplazamiento: int,
        tipo_movimiento: str,
        nombre_origen_ext: str,
        nombre_destino_ext: str,
        fecha_desplazamiento: str,
        fecha_presentacion_eepp: str,
        documento_oficial: str,
        vacaciones_periodo: str = "2025-2026",
        vacaciones_gozadas_origen: int = 0,
        vacaciones_saldo_origen: int = 30,
        comp_ganadas_origen: int = 0,
        comp_gozadas_origen: int = 0,
        comp_saldo_origen: int = 0,
        observaciones: str = ""
    ) -> Dict[str, Any]:
        """
        Modifica un registro de desplazamiento existente (Hoja de Traslado / Anexo 06)
        y sincroniza los saldos de compensación 24x48 y récord correspondiente.
        """
        desp = DesplazamientoRepository.obtener_desplazamiento_detalle(id_desplazamiento)
        if not desp:
            return {"success": False, "message": "Desplazamiento no encontrado."}

        id_empleado = desp["id_empleado"]

        datos = {
            "tipo_movimiento": tipo_movimiento,
            "nombre_origen_ext": nombre_origen_ext,
            "nombre_destino_ext": nombre_destino_ext,
            "fecha_desplazamiento": fecha_desplazamiento,
            "fecha_presentacion_eepp": fecha_presentacion_eepp,
            "documento_oficial": documento_oficial,
            "vacaciones_periodo": vacaciones_periodo,
            "vacaciones_gozadas_origen": vacaciones_gozadas_origen,
            "vacaciones_saldo_origen": vacaciones_saldo_origen,
            "comp_ganadas_origen": comp_ganadas_origen,
            "comp_gozadas_origen": comp_gozadas_origen,
            "comp_saldo_origen": comp_saldo_origen,
            "observaciones": observaciones
        }

        DesplazamientoRepository.actualizar_desplazamiento(id_desplazamiento, datos)

        # Sincronizar saldos de compensación
        with get_connection() as conn:
            cur = conn.cursor()
            if tipo_movimiento == "ALTA_RECEPCION":
                obs_saldo = f"ALTA POR DESPLAZAMIENTO: Procedente de {nombre_origen_ext or 'otro penal'}. Trae {comp_ganadas_origen} días ganados, {comp_gozadas_origen} gozados en origen. Doc: {documento_oficial}"
                cur.execute("""
                    SELECT id_saldo, dias_asignados, dias_utilizados FROM saldos_compensacion
                    WHERE id_empleado = ? AND anio_goce = 2026
                """, (id_empleado,))
                row = cur.fetchone()
                dias_disp = max(0, 16 - comp_gozadas_origen) if comp_saldo_origen == 0 else comp_saldo_origen
                if row:
                    cur.execute("""
                        UPDATE saldos_compensacion
                        SET dias_utilizados = ?,
                            dias_disponibles = ?,
                            observaciones = ?
                        WHERE id_saldo = ?
                    """, (comp_gozadas_origen, dias_disp, obs_saldo, row["id_saldo"]))
                else:
                    cur.execute("""
                        INSERT INTO saldos_compensacion (
                            id_empleado, anio_goce, dias_asignados, dias_utilizados, dias_disponibles, observaciones
                        ) VALUES (?, 2026, 16, ?, ?, ?)
                    """, (id_empleado, comp_gozadas_origen, dias_disp, obs_saldo))

                # Actualizar también fecha_ingreso_eepp y estado_laboral en empleados si aplica
                cur.execute("""
                    UPDATE empleados 
                    SET estado_laboral = 'ACTIVO',
                        fecha_ingreso_eepp = COALESCE(?, fecha_ingreso_eepp)
                    WHERE id_empleado = ?
                """, (fecha_presentacion_eepp if fecha_presentacion_eepp else None, id_empleado))
            else:
                obs_baja = f"DESPLAZADO A {nombre_destino_ext} EL {fecha_desplazamiento}. Doc: {documento_oficial}"
                cur.execute("""
                    UPDATE saldos_compensacion
                    SET observaciones = ?
                    WHERE id_empleado = ? AND anio_goce = 2026
                """, (obs_baja, id_empleado))
                cur.execute("""
                    UPDATE empleados 
                    SET estado_laboral = 'DESPLAZADO'
                    WHERE id_empleado = ?
                """, (id_empleado,))

            conn.commit()

        return {
            "success": True,
            "message": "Registro de desplazamiento y saldos sincronizados exitosamente."
        }
