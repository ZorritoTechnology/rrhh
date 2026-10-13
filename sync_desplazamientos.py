import sqlite3
import re

def sync():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT rd.id_desplazamiento, rd.id_empleado, rd.fecha_desplazamiento, rd.documento_resolucion, rd.observaciones
        FROM reporte_desplazamientos rd
    """)
    filas = cur.fetchall()

    for f in filas:
        id_rd, id_emp, fecha_desp, doc, obs = f
        obs_str = str(obs or "")
        doc_str = doc or ""

        if not doc_str and "(" in obs_str:
            doc_str = obs_str.split("(")[0].strip()
        if not doc_str:
            doc_str = "RESOLUCION OFICIAL DE DESPLAZAMIENTO"

        # Determinar si es SALIDA (BAJA) o LLEGADA (ALTA)
        es_salida = False
        penal_ext = "OTRO PENAL"

        if "722 a " in obs_str or "EP. MUJERES IQUITOS a " in obs_str:
            es_salida = True
            # Extraer destino
            m = re.search(r"a\s+(\d+\s+)?(EP\.\s*[A-Z\s]+)", obs_str)
            if m:
                penal_ext = m.group(2).strip()
            elif "CHACHAPOYAS" in obs_str:
                penal_ext = "EP. CHACHAPOYAS"
            elif "VIRGEN DE FATIMA" in obs_str:
                penal_ext = "EP. VIRGEN DE FATIMA"
            elif "MOYOBAMBA" in obs_str:
                penal_ext = "EP. MOYOBAMBA"
            elif "721" in obs_str or "IQUITOS" in obs_str:
                penal_ext = "EP. IQUITOS (VARONES)"
        else:
            # Es ALTA_RECEPCION
            m = re.search(r"(\d+\s+)?(EP\.\s*[A-Z\s]+)\s+a\s+722", obs_str)
            if m:
                penal_ext = m.group(2).strip()
            elif "721" in obs_str:
                penal_ext = "EP. IQUITOS (VARONES)"
            elif "236" in obs_str:
                penal_ext = "EP. VIRGEN DE FATIMA"

        tipo = "BAJA_SALIDA" if es_salida else "ALTA_RECEPCION"

        # Verificar si ya existe en desplazamientos_personal
        cur.execute("""
            SELECT id_desplazamiento FROM desplazamientos_personal
            WHERE id_empleado = ? AND fecha_desplazamiento = ?
        """, (id_emp, fecha_desp))
        existe = cur.fetchone()

        if not existe:
            if es_salida:
                cur.execute("""
                    INSERT INTO desplazamientos_personal (
                        id_empleado, tipo_movimiento, id_establecimiento_origen, id_establecimiento_destino,
                        nombre_origen_ext, nombre_destino_ext, fecha_desplazamiento, fecha_presentacion_eepp,
                        documento_oficial, vacaciones_periodo, vacaciones_gozadas_origen, vacaciones_saldo_origen,
                        comp_anio_fiscal, comp_ganadas_origen, comp_gozadas_origen, comp_saldo_origen,
                        observaciones, estado
                    ) VALUES (
                        ?, 'BAJA_SALIDA', 722, NULL,
                        'EP. MUJERES IQUITOS (722)', ?, ?, ?,
                        ?, '2025-2026', 0, 30,
                        2026, 0, 0, 0,
                        ?, 'TRASLADADO'
                    )
                """, (id_emp, penal_ext, fecha_desp, fecha_desp, doc_str, obs_str))
            else:
                cur.execute("""
                    INSERT INTO desplazamientos_personal (
                        id_empleado, tipo_movimiento, id_establecimiento_origen, id_establecimiento_destino,
                        nombre_origen_ext, nombre_destino_ext, fecha_desplazamiento, fecha_presentacion_eepp,
                        documento_oficial, vacaciones_periodo, vacaciones_gozadas_origen, vacaciones_saldo_origen,
                        comp_anio_fiscal, comp_ganadas_origen, comp_gozadas_origen, comp_saldo_origen,
                        observaciones, estado
                    ) VALUES (
                        ?, 'ALTA_RECEPCION', NULL, 722,
                        ?, 'EP. MUJERES IQUITOS (722)', ?, ?,
                        ?, '2025-2026', 0, 30,
                        2026, 0, 0, 0,
                        ?, 'ACTIVO'
                    )
                """, (id_emp, penal_ext, fecha_desp, fecha_desp, doc_str, obs_str))
            print(f"Sincronizado desp emp {id_emp} ({tipo}) - {fecha_desp} - {penal_ext}")

    conn.commit()
    print("Sincronización de desplazamientos finalizada exitosamente.")

if __name__ == "__main__":
    sync()
