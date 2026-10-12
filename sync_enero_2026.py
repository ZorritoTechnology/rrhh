import sqlite3

def load_enero_2026_real():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    # 1. Asegurar reporte de Enero 2026
    cur.execute("""
        SELECT id_reporte FROM reportes_cierre_mensual 
        WHERE anio = 2026 AND mes = 1 AND id_establecimiento = 722
    """)
    row = cur.fetchone()
    if row:
        id_reporte = row[0]
    else:
        cur.execute("""
            INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, observaciones_generales)
            VALUES (2026, 1, 722, 1, 28, 'REPORTE OFICIAL ENERO 2026')
        """)
        id_reporte = cur.lastrowid

    # 2. Registrar/Actualizar Empleados del mes
    # (codigo, dni, nombres)
    personal = [
        ("099132", "07032370", "ZAPATA ROQUE SANTOS DELCIA"),
        ("103913", "43945591", "LOPEZ TAMANI BLANCA CARINA"),
        ("103097", "43574815", "CACERES RIOS JAXSON CHARLES"),
        ("102595", "42714779", "BARDALES LOZANO CARMEN ROSA"),
        ("913148", "42208613", "NOVOA MIÑOPE EMILIA KATHERINE"),
        ("913371", "70185836", "BARDALES LOZANO AMBAR GRECIA TAMARA"),
        ("911381", "74576560", "CARO SILVA FRANK REDI"),
        ("910668", "44687160", "CASTILLO SOLIS DALIA MILAGROS"),
        ("911664", "76210282", "CAVERO DIAZ ANGEL GABRIEL"),
        ("911382", "42036844", "CULQUI RENGIFO CLARA URSULA PATRICIA"),
        ("912244", "70929943", "CHUQUIVAL RODRIGUEZ EDINSON"),
        ("102747", "15864987", "CANALES PAREDES ADELA ISABEL"),
        ("910748", "46187186", "FLORES CARDENAS FRANCO CHRISTOPHER"),
        ("909967", "45519121", "MANIHUARI VASQUEZ ALEXANDER"),
        ("910332", "45857066", "NUÑEZ GONGORA RALF FRANCOIS"),
        ("910869", "43908245", "PANDURO PARANA LLOYSI LLERLITA"),
        ("908917", "46051088", "PARANO OROCHE BRIGITTE"),
        ("911387", "46188189", "PIÑA GONGORA CRISTIAN"),
        ("910945", "42341212", "SANDY DEL CASTILLO DELIA ANITA"),
        ("910940", "45481934", "SANCHEZ PIZANGO MAYRA SOVEYDA"),
        ("910396", "46783856", "SOLSOL FONSECA ADRIAN ALFREDO"),
        ("009881", "29557455", "TEJADA ZUÑIGA CELIA YENNI"),
        ("103793", "41616632", "VALLEJOS LEYVA ERIC JHON"),
        ("911662", "46924524", "VALLE SANCHEZ EYLIN"),
        ("913429", "72362380", "GUEVARA CASTILLO MICHAEL STEFANNY"),
        ("912503", "48566494", "LOMAS ROMERO MONICA ANGELICA"),
        ("104449", "40869121", "OLANO SALAZAR CARLOS ALBERTO"),
        ("910465", "48009378", "MELENDEZ AMASIFUEN MAILITH")
    ]
    emp_ids = {}
    for cod, dni, nom in personal:
        cur.execute("""
            INSERT INTO empleados (codigo_servidor, dni, apellidos_nombres)
            VALUES (?, ?, ?)
            ON CONFLICT(codigo_servidor) DO UPDATE SET dni=excluded.dni, apellidos_nombres=excluded.apellidos_nombres
        """, (cod, dni, nom))
        cur.execute("SELECT id_empleado FROM empleados WHERE codigo_servidor = ?", (cod,))
        emp_ids[cod] = cur.fetchone()[0]

    # Regímenes
    cur.execute("SELECT codigo, id_regimen FROM regimenes_laborales")
    regs = dict(cur.fetchall())

    # 3. Pestaña 1: Personal General de Enero 2026 (28 servidores activos/registrados)
    # Limpiar mes previo para cargar exacto
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte = ?", (id_reporte,))
    
    plantilla = [
        ("099132", regs.get("LEY_29709"), "T2", "AGENTE DE SEGURIDAD II", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2023-12-29", "RP N°325-2023-INPE/P", ""),
        ("103913", regs.get("DL_276"), "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE DIVISION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2020-12-30", "RD 260-2020-INPE/ORNOSM", ""),
        ("103097", regs.get("LEY_29709"), "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "2021-04-01", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", regs.get("LEY_29709"), "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "2024-12-05", "RD N°303-2024-INPE-P", ""),
        ("913148", regs.get("DL_1057"), "SNR", "OBSTETRA", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "2019-09-10", "CONTRATO", ""),
        ("913371", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911381", regs.get("DL_1057"), "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-07-06", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP. N°203-2024-INPE/P", ""),
        ("911664", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-15", "RP N°339-2023-INPE/P", ""),
        ("911382", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("912244", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-18", "RP N°339-2023-INPE/P", ""),
        ("102747", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-04-11", "RD N°057-2025-INPE/ORNOSM", ""),
        ("910748", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("909967", regs.get("DL_1057"), "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-01-06", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910332", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-06-20", "MEMORANDO N°125-2024-INPE/ORNOSM-ERRHH", ""),
        ("910869", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-07", "RP N°203-2024-INPE/P", ""),
        ("908917", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911387", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2018-04-15", "MEMO MULT. N°002-2018-INPE", ""),
        ("910396", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP N°203-2024-INPE/P", ""),
        ("009881", regs.get("LEY_29709"), "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2014-11-09", "RD N°251-2014-INPE/21", ""),
        ("103793", regs.get("DL_276"), "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2017-07-02", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-29", "RP N°339-2023-INPE/P", ""),
        ("913429", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-11-21", "RP N°203-2024-INPE/P", ""),
        ("912503", regs.get("LEY_29709"), "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-08", "RP N°203-2024-INPE/P", ""),
        ("104449", regs.get("DL_276"), "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-05", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", regs.get("LEY_29709"), "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-06", "RD N°607-2025-INPE/OGA-URH", "")
    ]

    for item in plantilla:
        cod = item[0]
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral, 
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion, 
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_reporte, emp_ids[cod], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12], item[13]))

    # 4. Pestaña 2: Funcionarios (1 registro: Zapata Roque Santos Delcia)
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte = ?", (id_reporte,))
    cur.execute("""
        INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones)
        VALUES (?, ?, 'DIRECTORA', 'S4', '2023-12-29', 'RP N°325-2023-INPE/P', '')
    """, (id_reporte, emp_ids["099132"]))

    # 5. Pestaña 7: Licencias (10 registros exactos)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte = ?", (id_reporte,))
    licencias_enero = [
        ("913429", "ENFERMEDAD", "PARTICULAR", "2026-01-05", "2026-01-10", 6, ""),
        ("910748", "ENFERMEDAD", "PARTICULAR", "2026-01-03", "2026-01-05", 3, ""),
        ("908917", "MATERNIDAD", "ESSALUD", "2026-01-02", "2026-04-09", 98, ""),
        ("910396", "ONOMÁSTICO", "INPE", "2026-01-20", "2026-01-22", 3, ""),
        ("910396", "ENFERMEDAD", "PARTICULAR", "2026-01-11", "2026-01-13", 3, ""),
        ("912244", "ENFERMEDAD", "PARTICULAR", "2026-01-25", "2026-01-27", 3, ""),
        ("103097", "ENFERMEDAD", "ESSALUD", "2026-01-16", "2026-01-16", 1, ""),
        ("911382", "ENFERMEDAD", "ESSALUD", "2026-01-08", "2026-01-30", 23, ""),
        ("910945", "ENFERMEDAD", "PARTICULAR", "2026-01-27", "2026-01-29", 3, ""),
        ("913429", "ENFERMEDAD", "PARTICULAR", "2026-01-27", "2026-02-04", 9, "")
    ]
    for cod, tipo, ent, fi, ft, dias, obs in licencias_enero:
        cur.execute("""
            INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_reporte, emp_ids[cod], tipo, ent, fi, ft, dias, obs))

    # 6. Pestaña 8: Vacaciones (5 registros exactos)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte = ?", (id_reporte,))
    vacaciones_enero = [
        ("910869", "2025", "2026-01-02", "2026-01-31", 30, ""),
        ("910332", "2025", "2026-01-03", "2026-02-01", 30, ""),
        ("102595", "2025", "2026-01-05", "2026-01-22", 18, ""),
        ("913429", "2025", "2026-01-11", "2026-01-15", 5, "ADELANTO VACACIONES Y TERMINO 2025"),
        ("911382", "2024", "2026-01-31", "2026-02-05", 6, "TERMINO")
    ]
    for cod, per, fi, ft, dias, obs in vacaciones_enero:
        cur.execute("""
            INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_reporte, emp_ids[cod], per, fi, ft, dias, obs))

    # 7. Pestaña 10: Permisos Particulares (2 registros)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte = ?", (id_reporte,))
    permisos_enero = [
        ("102595", 60, "SALDO DEL TOTAL MINUTOS"),
        ("910668", 178, "")
    ]
    for cod, min_val, obs in permisos_enero:
        cur.execute("""
            INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones)
            VALUES (?, ?, ?, ?)
        """, (id_reporte, emp_ids[cod], min_val, obs))

    # 8. Pestaña 11: Inasistencias Injustificadas (3 registros)
    cur.execute("DELETE FROM reporte_inasistencias WHERE id_reporte = ?", (id_reporte,))
    inasistencias_enero = [
        ("913429", 8, "2,3,4,16,17", "ENERO"),
        ("102595", 1, "", "POR ACUMULACIÓN MINUTOS P/P"),
        ("913148", 1, "30", "ENERO")
    ]
    for cod, dias, fechas, obs in inasistencias_enero:
        cur.execute("""
            INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (id_reporte, emp_ids[cod], dias, fechas, obs))

    # Limpiar tablas que para Enero 2026 tienen NRO. TRAB = 0 (Sanciones, Renuncias, Reincorporaciones, Desplazamientos, Tardanzas)
    cur.execute("DELETE FROM reporte_sanciones WHERE id_reporte = ?", (id_reporte,))
    cur.execute("DELETE FROM reporte_renuncias WHERE id_reporte = ?", (id_reporte,))
    cur.execute("DELETE FROM reporte_reincorporaciones WHERE id_reporte = ?", (id_reporte,))
    cur.execute("DELETE FROM reporte_desplazamientos WHERE id_reporte = ?", (id_reporte,))
    cur.execute("DELETE FROM reporte_tardanzas WHERE id_reporte = ?", (id_reporte,))

    conn.commit()
    conn.close()
    print("Datos oficiales de Enero 2026 sincronizados al 100%.")

if __name__ == "__main__":
    load_enero_2026_real()
