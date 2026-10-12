import sqlite3

def load_febrero_marzo_data():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    # 1. Registrar a Edith Modesta Torres Obregón (009889) y Jhuly Angela Vela Villena (103095) en empleados si no existen
    nuevos_empleados = [
        ("009889", "09756696", "TORRES OBREGON EDITH MODESTA"),
        ("103095", "42916467", "VELA VILLENA JHULY ANGELA")
    ]
    for cod, dni, nom in nuevos_empleados:
        cur.execute("""
            INSERT INTO empleados (codigo_servidor, dni, apellidos_nombres)
            VALUES (?, ?, ?)
            ON CONFLICT(codigo_servidor) DO UPDATE SET dni=excluded.dni, apellidos_nombres=excluded.apellidos_nombres
        """, (cod, dni, nom))
    conn.commit()

    cur.execute("SELECT codigo_servidor, id_empleado FROM empleados")
    emp_map = dict(cur.fetchall())

    cur.execute("SELECT codigo, id_regimen FROM regimenes_laborales")
    reg_map = dict(cur.fetchall())
    reg_29709 = reg_map.get("LEY_29709")
    reg_276 = reg_map.get("DL_276")
    reg_1057 = reg_map.get("DL_1057")

    # =========================================================================
    # FEBRERO 2026 (30 TRABAJADORES, RESPONSABLE: 009889 TORRES OBREGON EDITH MODESTA)
    # =========================================================================
    cur.execute("""
        SELECT id_reporte FROM reportes_cierre_mensual 
        WHERE anio = 2026 AND mes = 2 AND id_establecimiento = 722
    """)
    row_feb = cur.fetchone()
    if row_feb:
        id_feb = row_feb[0]
        cur.execute("UPDATE reportes_cierre_mensual SET id_responsable = ?, total_trabajadores = 30, estado = 'CERRADO' WHERE id_reporte = ?", (emp_map["009889"], id_feb))
    else:
        cur.execute("""
            INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, estado, observaciones_generales)
            VALUES (2026, 2, 722, ?, 30, 'CERRADO', 'REPORTE OFICIAL FEBRERO 2026')
        """, (emp_map["009889"],))
        id_feb = cur.lastrowid

    # Plantilla Febrero 2026 (30 trabajadores)
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte = ?", (id_feb,))
    plantilla_feb = [
        ("009889", reg_29709, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2026-02-18", "RP N° 089-2026-INPE/P", ""),
        ("099132", reg_29709, "T2", "AGENTE DE SEGURIDAD II", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2023-12-29", "RP N°325-2023-INPE/P", "Término de Función"),
        ("103913", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE DIVISION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2020-12-30", "RD 260-2020-INPE/ORNOSM", "Ha relevado Jefatura Seguridad, 18-02-2026, Dirección, RR.HH., Administración el 20,23,24,25 de febrero 2026."),
        ("103097", reg_29709, "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "2021-04-01", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", reg_29709, "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "2024-12-05", "RD N°303-2024-INPE-P", ""),
        ("913148", reg_1057, "SNR", "OBSTETRA", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "2019-09-10", "CONTRATO", ""),
        ("913371", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911381", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-07-06", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP. N°203-2024-INPE/P", ""),
        ("911664", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "DESPLAZADO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-15", "RP N°339-2023-INPE/P", "Desplazado EP Chachapoyas"),
        ("911382", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("912244", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-18", "RP N°339-2023-INPE/P", ""),
        ("102747", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-04-11", "RD N°057-2025-INPE/ORNOSM", ""),
        ("910748", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("909967", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-01-06", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910332", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-06-20", "MEMORANDO N°125-2024-INPE/ORNOSM-ERRHH", ""),
        ("910869", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-07", "RP N°203-2024-INPE/P", ""),
        ("908917", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "LICENCIA MATERNIDAD", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", "Licencia por maternidad 02/01/2026 al 09/04/2026"),
        ("911387", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-01-01", "RP N° 534-2025-INPE/P", "INCORPORACIÓN A LEY 29709"),
        ("910396", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP N°203-2024-INPE/P", ""),
        ("009881", reg_29709, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2014-11-09", "RD N°251-2014-INPE/21", ""),
        ("103793", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2017-07-02", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-29", "RP N°339-2023-INPE/P", ""),
        ("913429", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "DESPLAZADO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-11-21", "RP N°203-2024-INPE/P", "Desplazado EP Virgen de Fátima"),
        ("912503", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-08", "RP N°203-2024-INPE/P", ""),
        ("104449", reg_276, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-05", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-06", "RD N°607-2025-INPE/OGA-URH", "")
    ]
    for row in plantilla_feb:
        cod = row[0]
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_feb, emp_map[cod], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

    # Funcionarios Febrero (3: Zapata Roque, Torres Obregón, Vela Villena)
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte = ?", (id_feb,))
    func_feb = [
        ("099132", "DIRECTORA", "S4", "2023-12-29", "RP N°325-2023-INPE/P", "DAR POR CONCLUIDA SUS FUNCIONES, RP N° 089-2026-INPE/P"),
        ("009889", "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", "ASUME CARGO DE DIRECTORA, RP N° 089-2026-INPE/P"),
        ("103095", "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", "ASUME CARGO, RP N° 089-2026-INPE/P")
    ]
    for cod, car, niv, fi, res, obs in func_feb:
        cur.execute("""
            INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_feb, emp_map[cod], car, niv, fi, res, obs))

    # Desplazamientos Febrero (4 registros)
    cur.execute("DELETE FROM reporte_desplazamientos WHERE id_reporte = ?", (id_feb,))
    desp_feb = [
        ("911664", "SEG", "TECNICO DE SEGURIDAD", "2026-02-13", "RD. N° 036-2026-INPE/ORNOSM (722 a 733 EP. CHACHAPOYAS)"),
        ("913429", "SEG", "TECNICO DE SEGURIDAD", "2026-02-17", "RD N° 144-2026-INPE/OGA-URH (722 a 236 EP. VIRGEN DE FATIMA)"),
        ("009889", "ADM", "DIRECTORA", "2026-02-20", "RP N° 089-2026-INPE/P (236 a 722 EP. MUJERES IQUITOS)"),
        ("103095", "ADM", "JEFE DE SECCION DE SEGURIDAD", "2026-02-18", "RP N° 089-2026-INPE/P (721 a 722 EP. MUJERES IQUITOS)")
    ]
    for cod, ar, car, fe, obs in desp_feb:
        cur.execute("""
            INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, area, cargo_funcion, fecha_desplazamiento, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_feb, emp_map[cod], ar, car, fe, obs))

    # Licencias Febrero (11 registros)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte = ?", (id_feb,))
    lic_feb = [
        ("913429", "ENFERMEDAD", "PARTICULAR", "2026-02-11", "2026-02-16", 6, "Certificado Médico N° 39378"),
        ("102595", "ENFERMEDAD", "PARTICULAR", "2026-02-04", "2026-02-05", 2, "Certificado Médico N° 49731"),
        ("910668", "ENFERMEDAD", "PARTICULAR", "2026-02-02", "2026-02-04", 3, "Certificado Médico N° 3937"),
        ("910332", "ENFERMEDAD", "PARTICULAR", "2026-02-14", "2026-02-16", 3, "Certificado Médico N° 34378"),
        ("912244", "ENFERMEDAD", "PARTICULAR", "2026-02-15", "2026-02-17", 3, "Certificado Médico N° 100254"),
        ("102595", "ENFERMEDAD", "PARTICULAR", "2026-02-20", "2026-02-20", 1, "Certificado Médico N° 42988"),
        ("910332", "ENFERMEDAD", "ESSALUD", "2026-02-20", "2026-02-22", 3, "CITT N°A-062-00011212-26"),
        ("104449", "ONOMÁSTICO", "INPE", "2026-02-04", "2026-02-04", 1, "DNI N° 40869121"),
        ("913429", "ONOMÁSTICO", "INPE", "2026-02-05", "2026-02-05", 1, "DNI N° 72362380"),
        ("910869", "ONOMÁSTICO", "INPE", "2026-02-19", "2026-02-19", 1, "DNI N° 43908245"),
        ("908917", "MATERNIDAD", "ESSALUD", "2026-01-02", "2026-04-09", 98, "CITT N° A-062-00021208-25")
    ]
    for cod, tip, ent, fi, ft, dia, obs in lic_feb:
        cur.execute("""
            INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_feb, emp_map[cod], tip, ent, fi, ft, dia, obs))

    # Vacaciones Febrero (11 registros)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte = ?", (id_feb,))
    vac_feb = [
        ("912244", "2025", "2026-01-31", "2026-02-14", 15, ""),
        ("911381", "2025", "2026-02-01", "2026-02-15", 15, ""),
        ("910396", "2025", "2026-02-16", "2026-03-02", 15, ""),
        ("913148", "2026", "2026-01-30", "2026-02-18", 20, ""),
        ("910945", "2025", "2026-02-17", "2026-03-03", 15, ""),
        ("103097", "2025", "2026-02-04", "2026-02-10", 7, ""),
        ("911382", "2025", "2026-02-06", "2026-02-25", 20, ""),
        ("911382", "2025", "2026-02-26", "2026-03-07", 10, ""),
        ("913371", "2025", "2026-02-15", "2026-03-01", 15, ""),
        ("099132", "2025", "2026-02-02", "2026-03-03", 30, ""),
        ("103913", "2024", "2026-02-26", "2026-03-20", 23, "")
    ]
    for cod, per, fi, ft, dia, obs in vac_feb:
        cur.execute("""
            INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_feb, emp_map[cod], per, fi, ft, dia, obs))

    # Permisos Particulares Febrero (1 registro: Bardales Lozano Carmen Rosa 180 min)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte = ?", (id_feb,))
    cur.execute("INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, 180, 'FEBRERO')",
                (id_feb, emp_map["102595"]))

    # Limpiar tablas en cero para Febrero
    cur.execute("DELETE FROM reporte_sanciones WHERE id_reporte = ?", (id_feb,))
    cur.execute("DELETE FROM reporte_renuncias WHERE id_reporte = ?", (id_feb,))
    cur.execute("DELETE FROM reporte_reincorporaciones WHERE id_reporte = ?", (id_feb,))
    cur.execute("DELETE FROM reporte_tardanzas WHERE id_reporte = ?", (id_feb,))
    cur.execute("DELETE FROM reporte_inasistencias WHERE id_reporte = ?", (id_feb,))

    # =========================================================================
    # MARZO 2026 (28 TRABAJADORES, RESPONSABLE: 009889 TORRES OBREGON EDITH MODESTA)
    # =========================================================================
    cur.execute("""
        SELECT id_reporte FROM reportes_cierre_mensual 
        WHERE anio = 2026 AND mes = 3 AND id_establecimiento = 722
    """)
    row_mar = cur.fetchone()
    if row_mar:
        id_mar = row_mar[0]
        cur.execute("UPDATE reportes_cierre_mensual SET id_responsable = ?, total_trabajadores = 28, estado = 'ABIERTO' WHERE id_reporte = ?", (emp_map["009889"], id_mar))
    else:
        cur.execute("""
            INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, estado, observaciones_generales)
            VALUES (2026, 3, 722, ?, 28, 'ABIERTO', 'REPORTE OFICIAL MARZO 2026')
        """, (emp_map["009889"],))
        id_mar = cur.lastrowid

    # Plantilla Marzo 2026 (28 trabajadores: salieron Cavero Diaz y Guevara Castillo; Zapata Roque figura como DESPLAZADO a EP Moyobamba)
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte = ?", (id_mar,))
    plantilla_mar = [
        ("009889", reg_29709, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2026-02-18", "RP N° 089-2026-INPE/P", ""),
        ("099132", reg_29709, "T2", "AGENTE DE SEGURIDAD II", "DESPLAZADO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2023-12-29", "RP N°325-2023-INPE/P", "Desplazado EP. Moyobamba"),
        ("103913", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE DIVISION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2020-12-30", "RD 260-2020-INPE/ORNOSM", ""),
        ("103097", reg_29709, "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "2021-04-01", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", reg_29709, "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "2024-12-05", "RD N°303-2024-INPE-P", ""),
        ("913148", reg_1057, "SNR", "OBSTETRA", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "2019-09-10", "CONTRATO", ""),
        ("913371", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911381", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-07-06", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP. N°203-2024-INPE/P", ""),
        ("911382", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("912244", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-18", "RP N°339-2023-INPE/P", ""),
        ("102747", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-04-11", "RD N°057-2025-INPE/ORNOSM", ""),
        ("910748", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("909967", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-01-06", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910332", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-06-20", "MEMORANDO N°125-2024-INPE/ORNOSM-ERRHH", ""),
        ("910869", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-07", "RP N°203-2024-INPE/P", ""),
        ("908917", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "LICENCIA MATERNIDAD", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", "Licencia por maternidad 02/01/2026 al 09/04/2026"),
        ("911387", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-01-01", "RP N° 534-2025-INPE/P", "INCORPORACIÓN A LEY 29709"),
        ("910396", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP N°203-2024-INPE/P", ""),
        ("009881", reg_29709, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2014-11-09", "RD N°251-2014-INPE/21", ""),
        ("103793", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2017-07-02", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-29", "RP N°339-2023-INPE/P", ""),
        ("912503", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-08", "RP N°203-2024-INPE/P", ""),
        ("104449", reg_276, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-05", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-06", "RD N°607-2025-INPE/OGA-URH", "")
    ]
    for row in plantilla_mar:
        cod = row[0]
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_mar, emp_map[cod], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

    # Funcionarios Marzo (2: Torres Obregón Edith Modesta, Vela Villena Jhuly Angela)
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte = ?", (id_mar,))
    func_mar = [
        ("009889", "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", "")
    ]
    for cod, car, niv, fi, res, obs in func_mar:
        cur.execute("""
            INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_mar, emp_map[cod], car, niv, fi, res, obs))

    # Desplazamientos Marzo (1: Zapata Roque Santos Delcia a EP. Moyobamba)
    cur.execute("DELETE FROM reporte_desplazamientos WHERE id_reporte = ?", (id_mar,))
    cur.execute("""
        INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, area, cargo_funcion, fecha_desplazamiento, observaciones)
        VALUES (?, ?, 'ADM', 'DIRECTORA', '2026-03-06', 'RP. N°089-2026-INPE/P (722 EP. MUJERES IQUITOS a 701 EP. MOYOBAMBA)')
    """, (id_mar, emp_map["099132"]))

    # Licencias Marzo (7 registros)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte = ?", (id_mar,))
    lic_mar = [
        ("908917", "MATERNIDAD", "ESSALUD", "2026-01-02", "2026-04-09", 98, "CITT N° A-062-00021208-25"),
        ("910869", "ENFERMEDAD", "ESSALUD", "2026-03-06", "2026-03-07", 2, "CITT N° A-440-00010271-26"),
        ("103097", "ENFERMEDAD", "ESSALUD", "2026-03-09", "2026-03-10", 2, "CITT N° A-062-00011671-26"),
        ("103097", "ENFERMEDAD", "ESSALUD", "2026-03-11", "2026-03-11", 1, "CITT N° A-062-00011794-26"),
        ("910945", "ONOMÁSTICO", "INPE", "2026-03-30", "2026-04-01", 3, ""),
        ("103095", "ONOMÁSTICO", "INPE", "2026-03-27", "2026-03-27", 1, ""),
        ("911382", "ONOMÁSTICO", "INPE", "2026-03-10", "2026-03-12", 3, "")
    ]
    for cod, tip, ent, fi, ft, dia, obs in lic_mar:
        cur.execute("""
            INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_mar, emp_map[cod], tip, ent, fi, ft, dia, obs))

    # Vacaciones Marzo (4 registros)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte = ?", (id_mar,))
    vac_mar = [
        ("911382", "2026", "2026-03-24", "2026-04-02", 10, ""),
        ("103913", "2025", "2026-03-25", "2026-03-31", 7, ""),
        ("103097", "2025", "2026-03-02", "2026-03-08", 7, ""),
        ("912244", "2025", "2026-03-05", "2026-03-10", 6, "")
    ]
    for cod, per, fi, ft, dia, obs in vac_mar:
        cur.execute("""
            INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_mar, emp_map[cod], per, fi, ft, dia, obs))

    # Permisos Particulares Marzo (5 registros)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte = ?", (id_mar,))
    perm_mar = [
        ("103097", 180, "MARZO"),
        ("102595", 360, "MARZO"),
        ("910668", 44, "MARZO"),
        ("913148", 81, "MARZO"),
        ("102747", 119, "MARZO")
    ]
    for cod, minu, obs in perm_mar:
        cur.execute("""
            INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones)
            VALUES (?, ?, ?, ?)
        """, (id_mar, emp_map[cod], minu, obs))

    # Inasistencias Injustificadas Marzo (1 registro: Caro Silva Frank Redi, 3 días: 15,16,17)
    cur.execute("DELETE FROM reporte_inasistencias WHERE id_reporte = ?", (id_mar,))
    cur.execute("""
        INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones)
        VALUES (?, ?, 3, '15,16,17', 'MARZO')
    """, (id_mar, emp_map["911381"]))

    # Limpiar tablas en cero para Marzo
    cur.execute("DELETE FROM reporte_sanciones WHERE id_reporte = ?", (id_mar,))
    cur.execute("DELETE FROM reporte_renuncias WHERE id_reporte = ?", (id_mar,))
    cur.execute("DELETE FROM reporte_reincorporaciones WHERE id_reporte = ?", (id_mar,))
    cur.execute("DELETE FROM reporte_tardanzas WHERE id_reporte = ?", (id_mar,))

    conn.commit()
    conn.close()
    print("Febrero 2026 y Marzo 2026 sincronizados e insertados al 100%.")

if __name__ == "__main__":
    load_febrero_marzo_data()
