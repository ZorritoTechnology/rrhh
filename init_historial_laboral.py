import sqlite3

def init_historial():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS empleados_historial_laboral (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empleado INTEGER NOT NULL,
            tipo_evento TEXT NOT NULL,       -- INGRESO_INPE, CAMBIO_REGIMEN, CONCURSO_MERITOS, ASCENSO, NOMBRAMIENTO, CONTRATO, ASIGNACION_CARGO, INCORPORACION_LEY_29709
            fecha_evento DATE NOT NULL,
            regimen_laboral TEXT,            -- D.L. 1057 (CAS), D.L. 276, Ley N° 29709
            nivel_cargo TEXT,                -- T1, T2, T3, S1, STF, SNR
            cargo_funcion TEXT,              -- Agente de Seguridad, Jefe de Sección, etc.
            resolucion_documento TEXT,       -- RP N°..., RD N°..., Contrato CAS N°...
            detalles TEXT,                   -- Descripción / motivo del cambio
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
        )
    """)
    conn.commit()

    # Pre-poblar hitos para los 40 empleados
    cur.execute("""
        SELECT id_empleado, codigo_servidor, dni, apellidos_nombres, regimen_nombre, nivel,
               cargo_estructural, cargo_funcion, fecha_ingreso_inpe, fecha_ingreso_eepp,
               resolucion_documento, observaciones
        FROM empleados
    """)
    empleados = cur.fetchall()

    for emp in empleados:
        emp_id, cip, dni, nom, reg, niv, cargo_est, cargo_func, f_inpe, f_eepp, res_doc, obs = emp

        # 1. Hito de Ingreso al INPE
        if f_inpe:
            cur.execute("""
                SELECT id_historial FROM empleados_historial_laboral
                WHERE id_empleado = ? AND tipo_evento = 'INGRESO_INPE'
            """, (emp_id,))
            if not cur.fetchone():
                det = f"Ingreso oficial al Instituto Nacional Penitenciario (INPE)"
                if "1057" in str(reg) or "CAS" in str(reg).upper():
                    det += " bajo Régimen Especial de Contratación Administrativa de Servicios (D.L. 1057)."
                elif "276" in str(reg):
                    det += " bajo Régimen del Decreto Legislativo N° 276 (Carrera Administrativa)."
                else:
                    det += " en la Carrera Especial Pública Penitenciaria."

                cur.execute("""
                    INSERT INTO empleados_historial_laboral (
                        id_empleado, tipo_evento, fecha_evento, regimen_laboral, nivel_cargo,
                        cargo_funcion, resolucion_documento, detalles
                    ) VALUES (?, 'INGRESO_INPE', ?, ?, ?, ?, ?, ?)
                """, (emp_id, f_inpe, reg or 'Ley N° 29709', niv or 'T1', cargo_func or cargo_est or 'Servidor Penitenciario', res_doc or 'RESOLUCIÓN INPE', det))

        # 2. Hito de Incorporación a Ley 29709 o Concurso de Méritos si aplica
        if "INCORPORACIÓN" in str(obs).upper() or "INCORPORACION" in str(obs).upper() or "LEY 29709" in str(obs).upper():
            cur.execute("""
                SELECT id_historial FROM empleados_historial_laboral
                WHERE id_empleado = ? AND tipo_evento = 'INCORPORACION_LEY_29709'
            """, (emp_id,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO empleados_historial_laboral (
                        id_empleado, tipo_evento, fecha_evento, regimen_laboral, nivel_cargo,
                        cargo_funcion, resolucion_documento, detalles
                    ) VALUES (?, 'INCORPORACION_LEY_29709', ?, 'Ley N° 29709', ?, ?, ?, ?)
                """, (emp_id, f_eepp or f_inpe, niv or 'T1', cargo_func or 'Agente de Seguridad I', res_doc or 'RP N° 534-2025-INPE/P', 'Incorporación a la Carrera Especial Pública Penitenciaria (Ley N° 29709) mediante Concurso Público de Méritos.'))

        # 3. Hito de Asignación / Cargo de Jefatura o Nombramiento específico si fecha_ingreso_eepp es posterior
        if f_eepp and f_inpe and f_eepp != f_inpe and "INCORPORACIÓN" not in str(obs).upper():
            cur.execute("""
                SELECT id_historial FROM empleados_historial_laboral
                WHERE id_empleado = ? AND fecha_evento = ?
            """, (emp_id, f_eepp))
            if not cur.fetchone():
                tipo = 'ASIGNACION_CARGO' if ('JEFE' in str(cargo_func).upper() or 'DIRECTOR' in str(cargo_func).upper()) else 'ASIGNACION_EEPP'
                det = f"Asignación de funciones en EP Mujeres Iquitos como {cargo_func or cargo_est} ({reg})."
                cur.execute("""
                    INSERT INTO empleados_historial_laboral (
                        id_empleado, tipo_evento, fecha_evento, regimen_laboral, nivel_cargo,
                        cargo_funcion, resolucion_documento, detalles
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (emp_id, tipo, f_eepp, reg or 'Ley N° 29709', niv or 'T1', cargo_func or cargo_est or 'Servidor', res_doc or 'RESOLUCIÓN INSTITUCIONAL', det))

    conn.commit()
    cur.execute("SELECT count(*) FROM empleados_historial_laboral")
    print(f"Historial laboral inicial creado con {cur.fetchone()[0]} eventos registrados.")
    conn.close()

if __name__ == "__main__":
    init_historial()
