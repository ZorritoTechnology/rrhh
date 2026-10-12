import sqlite3

def load_todos_los_meses_hasta_setiembre():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    # 1. Registrar todos los empleados nuevos detectados en los meses de Mayo a Setiembre
    nuevos_empleados = [
        ("009889", "09756696", "TORRES OBREGON EDITH MODESTA"),
        ("103095", "42916467", "VELA VILLENA JHULY ANGELA"),
        ("909794", "45568033", "AYASTA AGAPITO SEGUNDO CRISTIAN"),
        ("911117", "45765846", "CUEVA RODRIGUEZ JUAN CARLOS"),
        ("103986", "45810415", "DAVALOS LAZARO ELIZABETH ISABEL"),
        ("910717", "43818009", "DAVILA FLORES MARISSA ISABEL"),
        ("910490", "61101713", "CAHUAZA CHOTA ROY JUNIOR"),
        ("910854", "46370605", "MOZOMBITE AHUANARI DAVID ALBERTO"),
        ("910524", "72556894", "RIOS ANGELES JULIO CESAR"),
        ("911755", "45675819", "SALDAÑA TUANAMA JARRIN TUNNER"),
        ("910721", "71851435", "DE LOAYZA TORRES AMBAR CRISTINA")
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

    resp_torres = emp_map["009889"]

    def upsert_reporte(mes, total_trab, estado, obs):
        cur.execute("SELECT id_reporte FROM reportes_cierre_mensual WHERE anio=2026 AND mes=? AND id_establecimiento=722", (mes,))
        row = cur.fetchone()
        if row:
            rep_id = row[0]
            cur.execute("UPDATE reportes_cierre_mensual SET id_responsable=?, total_trabajadores=?, estado=?, observaciones_generales=? WHERE id_reporte=?",
                        (resp_torres, total_trab, estado, obs, rep_id))
            return rep_id
        else:
            cur.execute("""
                INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, estado, observaciones_generales)
                VALUES (2026, ?, 722, ?, ?, ?, ?)
            """, (mes, resp_torres, total_trab, estado, obs))
            return cur.lastrowid

    # =========================================================================
    # MAYO 2026 (26 TRABAJADORES, CERRADO)
    # =========================================================================
    id_may = upsert_reporte(5, 26, "CERRADO", "REPORTE OFICIAL MAYO 2026")
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte=?", (id_may,))
    plantilla_mayo = [
        ("009889", reg_29709, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2026-02-18", "RP N° 089-2026-INPE/P", ""),
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
        ("908917", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911387", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-01-01", "RP N° 534-2025-INPE/P", ""),
        ("910396", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP N°203-2024-INPE/P", ""),
        ("009881", reg_29709, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2014-11-09", "RD N°251-2014-INPE/21", ""),
        ("103793", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2017-07-02", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-29", "RP N°339-2023-INPE/P", ""),
        ("912503", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-08", "RP N°203-2024-INPE/P", ""),
        ("104449", reg_276, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-05", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-06", "RD N°607-2025-INPE/OGA-URH", "")
    ]
    for row in plantilla_mayo:
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_may, emp_map[row[0]], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

    # Funcionarios Mayo
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte=?", (id_may,))
    for cod, car, niv, fi, res, obs in [
        ("009889", "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", "")
    ]:
        cur.execute("INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_may, emp_map[cod], car, niv, fi, res, obs))

    # Licencias Mayo (8)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte=?", (id_may,))
    lic_may = [
        ("911662", "ENFERMEDAD", "ESSALUD", "2026-05-04", "2026-05-04", 1, "CITT N° A-439-00010679-26"),
        ("911662", "ENFERMEDAD", "ESSALUD", "2026-05-06", "2026-05-06", 1, "CITT N° A-439-00010692-26"),
        ("910332", "ENFERMEDAD", "ESSALUD", "2026-05-01", "2026-05-03", 3, "CITT N° A-062-00013477-26"),
        ("910869", "ENFERMEDAD", "ESSALUD", "2026-05-09", "2026-05-10", 2, "CITT N° A-062-00013694-26"),
        ("910332", "ENFERMEDAD", "PARTICULAR", "2026-05-10", "2026-05-12", 3, "Cert. Med. N° 0090963"),
        ("913371", "ENFERMEDAD", "PARTICULAR", "2026-05-26", "2026-05-30", 5, "Cert. Med. N° 0092175"),
        ("910396", "ENFERMEDAD", "PARTICULAR", "2026-05-30", "2026-06-01", 3, "Cert. Med. N° 0092506"),
        ("910869", "ENFERMEDAD", "PARTICULAR", "2026-05-30", "2026-06-01", 3, "Cert. Med. N° 0092385")
    ]
    for cod, tip, ent, fi, ft, dia, obs in lic_may:
        cur.execute("INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (id_may, emp_map[cod], tip, ent, fi, ft, dia, obs))

    # Vacaciones Mayo (1)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte=?", (id_may,))
    cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, '2025', '2026-05-29', '2026-05-31', 3, '')",
                (id_may, emp_map["910668"]))

    # Permisos Particulares Mayo (4)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte=?", (id_may,))
    for cod, min_v in [("102747", 60), ("912244", 240), ("913148", 85), ("102595", 180)]:
        cur.execute("INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, ?, 'MAYO')", (id_may, emp_map[cod], min_v))

    # Inasistencias Mayo (2)
    cur.execute("DELETE FROM reporte_inasistencias WHERE id_reporte=?", (id_may,))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 1, '11/05/2026', 'MAYO')", (id_may, emp_map["910869"]))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 1, '29/05/2026', 'MAYO')", (id_may, emp_map["102595"]))

    # =========================================================================
    # JUNIO 2026 (30 TRABAJADORES, CERRADO)
    # =========================================================================
    id_jun = upsert_reporte(6, 30, "CERRADO", "REPORTE OFICIAL JUNIO 2026")
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte=?", (id_jun,))
    # Plantilla de Junio con desplazados internos/externos y nuevos ingresantes
    plantilla_junio = [
        ("009889", reg_29709, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2026-02-18", "RP N° 089-2026-INPE/P", ""),
        ("103097", reg_29709, "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "2021-04-01", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", reg_29709, "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "2024-12-05", "RD N°303-2024-INPE-P", ""),
        ("913148", reg_1057, "SNR", "OBSTETRA", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "2019-09-10", "CONTRATO", ""),
        ("913371", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911381", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-07-06", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP. N°203-2024-INPE/P", ""),
        ("911382", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("912244", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-18", "RP N°339-2023-INPE/P", ""),
        ("102747", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "DESPLAZADO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-04-11", "RD N°057-2025-INPE/ORNOSM", "DESPLAZADO EP. IQUITOS"),
        ("910748", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("909967", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-01-06", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910332", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "DESPLAZADO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-06-20", "MEMORANDO N°125-2024-INPE/ORNOSM-ERRHH", "DESPLAZADO EP. IQUITOS"),
        ("910869", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-07", "RP N°203-2024-INPE/P", ""),
        ("908917", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911387", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-01-01", "RP N° 534-2025-INPE/P", ""),
        ("910396", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP N°203-2024-INPE/P", ""),
        ("009881", reg_29709, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2014-11-09", "RD N°251-2014-INPE/21", ""),
        ("103793", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2017-07-02", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-29", "RP N°339-2023-INPE/P", ""),
        ("912503", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "DESPLAZADO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-08", "RP N°203-2024-INPE/P", "DESPLAZADO EP. IQUITOS"),
        ("104449", reg_276, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-05", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-06", "RD N°607-2025-INPE/OGA-URH", ""),
        ("909794", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "25 x 48", "2026-06-12", "RD N°189-2026-INPE/ORNOSM", ""),
        ("911117", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "25 x 48", "2026-06-14", "RD N°189-2026-INPE/ORNOSM", ""),
        ("103986", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "25 x 48", "2026-06-15", "RD N°189-2026-INPE/ORNOSM", ""),
        ("910717", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "25 x 48", "2026-06-15", "RD N°189-2026-INPE/ORNOSM", "")
    ]
    for row in plantilla_junio:
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_jun, emp_map[row[0]], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

    # Funcionarios Junio (2)
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte=?", (id_jun,))
    for cod, car, niv, fi, res, obs in [
        ("009889", "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", "")
    ]:
        cur.execute("INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_jun, emp_map[cod], car, niv, fi, res, obs))

    # Desplazamientos Junio (7)
    cur.execute("DELETE FROM reporte_desplazamientos WHERE id_reporte=?", (id_jun,))
    desp_jun = [
        ("102747", "SEG", "TECNICO DE SEGURIDAD", "2026-06-12", "RD N°189-2026-INPE/ORNOSM (722 a 721 EP. IQUITOS)"),
        ("910332", "SEG", "TECNICO DE SEGURIDAD", "2026-06-12", "RD N°189-2026-INPE/ORNOSM (722 a 721 EP. IQUITOS)"),
        ("912503", "SEG", "TECNICO DE SEGURIDAD", "2026-06-12", "RD N°189-2026-INPE/ORNOSM (722 a 721 EP. IQUITOS)"),
        ("909794", "SEG", "TECNICO DE SEGURIDAD", "2026-06-12", "RD N°189-2026-INPE/ORNOSM (721 a 722 EP. MUJERES IQUITOS)"),
        ("911117", "SEG", "TECNICO DE SEGURIDAD", "2026-06-14", "RD N°189-2026-INPE/ORNOSM (721 a 722 EP. MUJERES IQUITOS)"),
        ("103986", "SEG", "TECNICO DE SEGURIDAD", "2026-06-15", "RD N°189-2026-INPE/ORNOSM (721 a 722 EP. MUJERES IQUITOS)"),
        ("910717", "SEG", "TECNICO DE SEGURIDAD", "2026-06-15", "RD N°189-2026-INPE/ORNOSM (721 a 722 EP. MUJERES IQUITOS)")
    ]
    for cod, ar, car, fe, obs in desp_jun:
        cur.execute("INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, area, cargo_funcion, fecha_desplazamiento, observaciones) VALUES (?, ?, ?, ?, ?, ?)",
                    (id_jun, emp_map[cod], ar, car, fe, obs))

    # Licencias Junio (10)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte=?", (id_jun,))
    lic_jun = [
        ("910869", "ENFERMEDAD", "PARTICULAR", "2026-06-05", "2026-06-07", 3, "CM. 0092870"),
        ("910332", "ENFERMEDAD", "PARTICULAR", "2026-06-06", "2026-06-08", 3, "CM. 0092847"),
        ("102595", "ENFERMEDAD", "PARTICULAR", "2026-06-01", "2026-06-02", 2, "CM. 0091900"),
        ("103097", "ENFERMEDAD", "PARTICULAR", "2026-06-12", "2026-06-12", 1, "CM. 0091384"),
        ("910869", "ENFERMEDAD", "PARTICULAR", "2026-06-20", "2026-06-25", 6, "CM. 0093919"),
        ("102595", "ENFERMEDAD", "PARTICULAR", "2026-06-16", "2026-06-18", 3, "CM. 0092757"),
        ("913371", "ENFERMEDAD", "PARTICULAR", "2026-06-18", "2026-06-20", 3, "CM. 0093467"),
        ("912244", "ONOMASTICO", "INPE", "2026-06-04", "2026-06-06", 3, ""),
        ("911387", "ONOMASTICO", "INPE", "2026-06-24", "2026-06-26", 3, ""),
        ("103986", "ENFERMEDAD", "PARTICULAR", "2026-06-29", "2026-07-01", 3, "CM. 0094208")
    ]
    for cod, tip, ent, fi, ft, dia, obs in lic_jun:
        cur.execute("INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (id_jun, emp_map[cod], tip, ent, fi, ft, dia, obs))

    # Vacaciones Junio (2)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte=?", (id_jun,))
    cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, '2025', '2026-06-14', '2026-06-16', 3, '')",
                (id_jun, emp_map["104449"]))
    cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, '2025', '2026-06-20', '2026-07-04', 15, '')",
                (id_jun, emp_map["910748"]))

    # Permisos Junio (5)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte=?", (id_jun,))
    for cod, min_v in [("102595", 180), ("910332", 120), ("104449", 20), ("913148", 83), ("103097", 410)]:
        cur.execute("INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, ?, 'JUNIO')", (id_jun, emp_map[cod], min_v))

    # Inasistencias Junio (1)
    cur.execute("DELETE FROM reporte_inasistencias WHERE id_reporte=?", (id_jun,))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 1, '19', 'JUNIO')", (id_jun, emp_map["102595"]))

    # =========================================================================
    # JULIO 2026 (31 TRABAJADORES, CERRADO)
    # =========================================================================
    id_jul = upsert_reporte(7, 31, "CERRADO", "REPORTE OFICIAL JULIO 2026")
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte=?", (id_jul,))
    # Plantilla Julio (31)
    plantilla_julio = [
        ("009889", reg_29709, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2026-02-18", "RP N° 089-2026-INPE/P", ""),
        ("103097", reg_29709, "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "2021-04-01", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", reg_29709, "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "2024-12-05", "RD N°303-2024-INPE-P", ""),
        ("913148", reg_1057, "SNR", "OBSTETRA", "LICENCIA SIN GOCE", "NO APLICA", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "2019-09-10", "CONTRATO", "RD N° 1100-2026-INPE/OGA-URH"),
        ("913371", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911381", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-07-06", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP. N°203-2024-INPE/P", ""),
        ("911382", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("912244", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-18", "RP N°339-2023-INPE/P", ""),
        ("910748", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("909967", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-01-06", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910869", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "LICENCIA MATERNIDAD", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-07", "RP N°203-2024-INPE/P", "03/07/2026 al 08/10/2026 CITT N° A-062-00015323-26"),
        ("908917", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911387", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-01-01", "RP N° 534-2025-INPE/P", ""),
        ("910396", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP N°203-2024-INPE/P", ""),
        ("009881", reg_29709, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2014-11-09", "RD N°251-2014-INPE/21", ""),
        ("103793", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2017-07-02", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-29", "RP N°339-2023-INPE/P", ""),
        ("104449", reg_276, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-05", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-08-06", "RD N°607-2025-INPE/OGA-URH", ""),
        ("909794", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-06-12", "RD N°189-2026-INPE/ORNOSM", ""),
        ("911117", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-06-14", "RD N°189-2026-INPE/ORNOSM", ""),
        ("103986", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-06-15", "RD N°189-2026-INPE/ORNOSM", ""),
        ("910717", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-06-15", "RD N°189-2026-INPE/ORNOSM", ""),
        ("910490", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-07-09", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("910854", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-07-09", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("910524", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-07-09", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("911755", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2026-07-09", "RD N° D000131-2026-INPE-STLCEPP", "")
    ]
    for row in plantilla_julio:
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_jul, emp_map[row[0]], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

    # Funcionarios Julio (2)
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte=?", (id_jul,))
    for cod, car, niv, fi, res, obs in [
        ("009889", "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", "")
    ]:
        cur.execute("INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_jul, emp_map[cod], car, niv, fi, res, obs))

    # Sanciones Julio (1)
    cur.execute("DELETE FROM reporte_sanciones WHERE id_reporte=?", (id_jul,))
    cur.execute("""
        INSERT INTO reporte_sanciones (id_reporte, id_empleado, tipo_sancion, fecha_inicio, fecha_termino, dias, tiempo_que_resuelve, resolucion_documento, observaciones)
        VALUES (?, ?, 'SUSPENSION', '2026-07-15', '2026-07-29', 15, 'EN DIAS', 'RTDL N° 231-2026-INPE/TD', 'Resolución de Tribunal disciplinario Ley N° 29709')
    """, (id_jul, emp_map["909794"]))

    # Desplazamientos Julio (4)
    cur.execute("DELETE FROM reporte_desplazamientos WHERE id_reporte=?", (id_jul,))
    for cod in ["910490", "910854", "910524", "911755"]:
        cur.execute("""
            INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, area, cargo_funcion, fecha_desplazamiento, observaciones)
            VALUES (?, ?, 'SEG', 'TECNICO DE SEGURIDAD', '2026-07-09', 'RD N° D000131-2026-INPE-STLCEPP (721 EP. IQUITOS a 722 EP. MUJERES IQUITOS - DESPLAZADO POR INICIO DE PADI)')
        """, (id_jul, emp_map[cod]))

    # Licencias Julio (9)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte=?", (id_jul,))
    lic_jul = [
        ("910869", "ENFERMEDAD", "ESSALUD", "2026-07-02", "2026-07-02", 1, "CITT N° A-062-00015431-26"),
        ("910869", "MATERNIDAD", "ESSALUD", "2026-07-03", "2026-10-08", 98, "CITT N° A-062-00015323-26"),
        ("009881", "ENFERMEDAD", "PARTICULAR", "2026-07-07", "2026-07-11", 5, "CM N° 0094828"),
        ("009881", "ENFERMEDAD", "ESSALUD", "2026-07-30", "2026-07-31", 2, "CITT N° A-439-00011284-26"),
        ("911387", "ENFERMEDAD", "ESSALUD", "2026-07-18", "2026-07-20", 3, "CITT N° A-441-00011709-26"),
        ("912244", "ENFERMEDAD", "PARTICULAR", "2026-07-31", "2026-08-02", 3, "CM N° 0095890"),
        ("103986", "ONOMASTICO", "INPE", "2026-07-11", "2026-07-13", 3, ""),
        ("911381", "ONOMASTICO", "INPE", "2026-07-18", "2026-07-20", 3, ""),
        ("913148", "PARTICULAR", "INPE", "2026-07-16", "2026-11-16", 124, "Licencia sin Goce : RD N° 1100-2026-INPE/OGA-URH")
    ]
    for cod, tip, ent, fi, ft, dia, obs in lic_jul:
        cur.execute("INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (id_jul, emp_map[cod], tip, ent, fi, ft, dia, obs))

    # Vacaciones Julio (3)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte=?", (id_jul,))
    cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, '2026', '2026-07-30', '2026-08-05', 7, '')", (id_jul, emp_map["102595"]))
    cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, '2025', '2026-07-19', '2026-07-21', 3, '')", (id_jul, emp_map["910465"]))
    cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, '2025', '2026-07-05', '2026-07-16', 12, '')", (id_jul, emp_map["911117"]))

    # Permisos Julio (6)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte=?", (id_jul,))
    for cod, min_v in [("102595", 360), ("912244", 240), ("910668", 188), ("103986", 161), ("103097", 150), ("911117", 100)]:
        cur.execute("INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, ?, 'JULIO')", (id_jul, emp_map[cod], min_v))

    # Inasistencias Julio (3)
    cur.execute("DELETE FROM reporte_inasistencias WHERE id_reporte=?", (id_jul,))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 3, '13,14,15', 'JULIO')", (id_jul, emp_map["912244"]))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 1, '24', 'JULIO')", (id_jul, emp_map["102595"]))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 3, '29,30,31', 'JULIO')", (id_jul, emp_map["911381"]))

    # =========================================================================
    # AGOSTO 2026 (31 TRABAJADORES, CERRADO)
    # =========================================================================
    id_ago = upsert_reporte(8, 31, "CERRADO", "REPORTE OFICIAL AGOSTO 2026")
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte=?", (id_ago,))
    # Plantilla Agosto: 31 trabajadores (incluye los 4 sancionados Cahauza, Mozombite, Rios, Saldaña)
    plantilla_agosto = [
        ("009889", reg_29709, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2026-02-18", "RP N° 089-2026-INPE/P", ""),
        ("103097", reg_29709, "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "2021-04-01", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", reg_29709, "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "2024-12-05", "RD N°303-2024-INPE-P", ""),
        ("913148", reg_1057, "SNR", "OBSTETRA", "LICENCIA SIN GOCE", "NO APLICA", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "2019-09-10", "CONTRATO", "RD N° 1100-2026-INPE/OGA-URH"),
        ("913371", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911381", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-07-06", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP. N°203-2024-INPE/P", ""),
        ("911382", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("912244", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-18", "RP N°339-2023-INPE/P", ""),
        ("910748", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("909967", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-01-06", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910869", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "LICENCIA MATERNIDAD", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-07", "RP N°203-2024-INPE/P", "03/072026 al 08/10/2026 CITT N° A-062-00015323-26"),
        ("908917", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911387", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "1/01/2026", "RP N° 534-2025-INPE/P", ""),
        ("910396", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/09/2024", "RP N°203-2024-INPE/P", ""),
        ("009881", reg_29709, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/11/2014", "RD N°251-2014-INPE/21", ""),
        ("103793", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2/07/2017", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/01/2024", "RP N°339-2023-INPE/P", ""),
        ("104449", reg_276, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "5/08/2025", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/08/2025", "RD N°607-2025-INPE/OGA-URH", ""),
        ("909794", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "12/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("911117", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "14/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("103986", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "15/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("910717", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "15/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("910490", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("910854", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("910524", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("911755", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", "")
    ]
    for row in plantilla_agosto:
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_ago, emp_map[row[0]], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

    # Funcionarios Agosto (2)
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte=?", (id_ago,))
    for cod, car, niv, fi, res, obs in [
        ("009889", "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", "")
    ]:
        cur.execute("INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_ago, emp_map[cod], car, niv, fi, res, obs))

    # Sanciones Agosto (4)
    cur.execute("DELETE FROM reporte_sanciones WHERE id_reporte=?", (id_ago,))
    sanc_ago = [
        ("910490", "SUSPENSION", "2026-08-29", "2027-02-28", 184, "EN MESES", "R. N° 275-2026-INPE/TD", "SUSPENSION 6 MESES"),
        ("910854", "SUSPENSION", "2026-08-29", "2026-12-29", 123, "EN MESES", "R. N° 275-2026-INPE/TD", "SUSPENSION 4 MESES"),
        ("910524", "SUSPENSION", "2026-08-29", "2027-02-28", 184, "EN MESES", "R. N° 275-2026-INPE/TD", "SUSPENSION 6 MESES"),
        ("911755", "SUSPENSION", "2026-08-29", "2027-02-28", 184, "EN MESES", "R. N° 275-2026-INPE/TD", "SUSPENSION 6 MESES")
    ]
    for cod, tip, fi, ft, dia, tr, res, obs in sanc_ago:
        cur.execute("""
            INSERT INTO reporte_sanciones (id_reporte, id_empleado, tipo_sancion, fecha_inicio, fecha_termino, dias, tiempo_que_resuelve, resolucion_documento, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_ago, emp_map[cod], tip, fi, ft, dia, tr, res, obs))

    # Licencias Agosto (13)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte=?", (id_ago,))
    lic_ago = [
        ("910748", "ENFERMEDAD", "PARTICULAR", "2026-08-01", "2026-08-03", 3, "CM N° 0095894"),
        ("910465", "ENFERMEDAD", "PARTICULAR", "2026-08-02", "2026-08-04", 3, "CM N° 0095902"),
        ("910396", "ENFERMEDAD", "PARTICULAR", "2026-08-04", "2026-08-06", 3, "CM N° 0096062"),
        ("103986", "ENFERMEDAD", "PARTICULAR", "2026-08-04", "2026-08-06", 3, "CM N° 0095920"),
        ("909794", "ENFERMEDAD", "ESSALUD", "2026-08-03", "2026-08-07", 5, "CITT N° A-496-00018808-26"),
        ("909794", "FALLECIMIENTO", "RENIEC", "2026-08-08", "2026-08-19", 12, "CERTIFICADO DEFUNCION N° 2001314668"),
        ("910668", "ENFERMEDAD", "ESSALUD", "2026-08-12", "2026-08-25", 14, "CITT N° A-062-00016768-26"),
        ("103097", "ENFERMEDAD", "PARTICULAR", "2026-08-20", "2026-08-21", 2, "CM N° 0097020"),
        ("911382", "ENFERMEDAD", "ESSALUD", "2026-08-22", "2026-08-27", 6, "CITA MEDICA HOSP. REBAGLIATI - LIMA"),
        ("910668", "ENFERMEDAD", "ESSALUD", "2026-08-26", "2026-08-26", 1, "CITT N° A-062-00017184-26"),
        ("910396", "ENFERMEDAD", "PARTICULAR", "2026-08-28", "2026-08-30", 3, "DM N° 0096118"),
        ("910869", "MATERNIDAD", "ESSALUD", "2026-07-03", "2026-10-08", 98, "CITT N° A-062-00015323-26"),
        ("913148", "PARTICULAR", "INPE", "2026-07-16", "2026-11-16", 124, "Licencia sin Goce : RD N° 1100-2026-INPE/OGA")
    ]
    for cod, tip, ent, fi, ft, dia, obs in lic_ago:
        cur.execute("INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (id_ago, emp_map[cod], tip, ent, fi, ft, dia, obs))

    # Vacaciones Agosto (7)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte=?", (id_ago,))
    vac_ago = [
        ("909794", "2026", "2026-08-20", "2026-08-29", 10, "ADELANTO VACACIONES"),
        ("910490", "2025", "2026-08-02", "2026-08-10", 9, ""),
        ("910748", "2025", "2026-08-22", "2026-09-05", 15, ""),
        ("909967", "2024", "2026-08-24", "2026-09-22", 30, ""),
        ("104449", "2025", "2026-08-23", "2026-09-03", 12, ""),
        ("910524", "2025", "2026-08-15", "2026-08-17", 3, ""),
        ("102595", "2026", "2026-08-25", "2026-08-25", 1, "ADELANTO")
    ]
    for cod, per, fi, ft, dia, obs in vac_ago:
        cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_ago, emp_map[cod], per, fi, ft, dia, obs))

    # Permisos Particulares Agosto (2)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte=?", (id_ago,))
    cur.execute("INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, 180, 'AGOSTO')", (id_ago, emp_map["102595"]))
    cur.execute("INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, 120, 'AGOSTO')", (id_ago, emp_map["912244"]))

    # =========================================================================
    # SETIEMBRE 2026 (32 TRABAJADORES, CERRADO)
    # =========================================================================
    id_set = upsert_reporte(9, 32, "CERRADO", "REPORTE OFICIAL SETIEMBRE 2026")
    cur.execute("DELETE FROM asistencia_mensual_personal WHERE id_reporte=?", (id_set,))
    # Plantilla Setiembre (32 trabajadores: incluye De Loayza Torres Ambar Cristina)
    plantilla_setiembre = [
        ("009889", reg_29709, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "2026-02-18", "RP N° 089-2026-INPE/P", ""),
        ("103097", reg_29709, "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "2021-04-01", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", reg_29709, "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "2024-12-05", "RD N°303-2024-INPE-P", ""),
        ("913148", reg_1057, "SNR", "OBSTETRA", "LICENCIA SIN GOCE", "NO APLICA", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "2019-09-10", "CONTRATO", "RD N° 1100-2026-INPE/OGA-URH"),
        ("913371", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911381", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-07-06", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-06", "RP. N°203-2024-INPE/P", ""),
        ("911382", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("912244", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-01-18", "RP N°339-2023-INPE/P", ""),
        ("910748", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("909967", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2025-01-06", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910869", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "LICENCIA MATERNIDAD", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-07", "RP N°203-2024-INPE/P", "03/07/2026 al 08/10/2026 CITT N° A-062-00015323-26"),
        ("908917", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("911387", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2024-09-13", "RP N°203-2024-INPE/P", ""),
        ("910945", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2023-12-29", "RP N°339-2023-INPE/P", ""),
        ("910940", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "1/01/2026", "RP N° 534-2025-INPE/P", ""),
        ("910396", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/09/2024", "RP N°203-2024-INPE/P", ""),
        ("009881", reg_29709, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/11/2014", "RD N°251-2014-INPE/21", ""),
        ("103793", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2/07/2017", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/01/2024", "RP N°339-2023-INPE/P", ""),
        ("104449", reg_276, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "5/08/2025", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/08/2025", "RD N°607-2025-INPE/OGA-URH", ""),
        ("909794", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "12/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("911117", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "14/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("103986", reg_276, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "15/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("910717", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "15/06/2026", "RD N°189-2026-INPE/ORNOSM", ""),
        ("910490", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("910854", reg_29709, "T1", "TÉCNICO EN SEGURIDAD", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("910524", reg_29709, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("911755", reg_29709, "T1", "AGENTE DE SEGURIDAD I", "SANCIONADO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/07/2026", "RD N° D000131-2026-INPE-STLCEPP", ""),
        ("910721", reg_1057, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "DIRECCION", "AUXILIAR ADMINISTRATIVO", "ADM", "08:00 - 17:00", "3/09/2026", "Memorando No. D000237-2026-INPE/ORNOSM", "")
    ]
    for row in plantilla_setiembre:
        cur.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural, estado_laboral,
                modalidad_laboral, direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                horario_laboral, fecha_ingreso_eepp, resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_set, emp_map[row[0]], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

    # Funcionarios Setiembre (2)
    cur.execute("DELETE FROM reporte_funcionarios WHERE id_reporte=?", (id_set,))
    for cod, car, niv, fi, res, obs in [
        ("009889", "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", ""),
        ("103095", "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", "")
    ]:
        cur.execute("INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_set, emp_map[cod], car, niv, fi, res, obs))

    # Sanciones Setiembre (4)
    cur.execute("DELETE FROM reporte_sanciones WHERE id_reporte=?", (id_set,))
    for cod, tip, fi, ft, dia, tr, res, obs in sanc_ago:
        cur.execute("""
            INSERT INTO reporte_sanciones (id_reporte, id_empleado, tipo_sancion, fecha_inicio, fecha_termino, dias, tiempo_que_resuelve, resolucion_documento, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_set, emp_map[cod], tip, fi, ft, dia, tr, res, obs))

    # Desplazamientos Setiembre (1)
    cur.execute("DELETE FROM reporte_desplazamientos WHERE id_reporte=?", (id_set,))
    cur.execute("""
        INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, area, cargo_funcion, fecha_desplazamiento, observaciones)
        VALUES (?, ?, 'DIRECCION', 'AUXILIAR ADMINISTRATIVO', '2026-09-03', 'MEMORANDO N°D000237-2026-INPE-ORNOSM (7220 EAPP Y EPLD ANEXO IQUITOS a 722 EP. MUJERES IQUITOS)')
    """, (id_set, emp_map["910721"]))

    # Licencias Setiembre (8)
    cur.execute("DELETE FROM reporte_licencias WHERE id_reporte=?", (id_set,))
    lic_set = [
        ("910869", "MATERNIDAD", "ESSALUD", "2026-07-03", "2026-10-08", 98, "CITT N° A-062-00015323-26"),
        ("913148", "PARTICULAR", "INPE", "2026-07-16", "2026-11-16", 124, "Licencia sin Goce : RD N° 1100-2026-INPE/OGA-URH"),
        ("103097", "ENFERMEDAD", "ESSALUD", "2026-09-03", "2026-09-04", 2, "A-062-00017493-26"),
        ("910940", "ENFERMEDAD", "ESSALUD", "2026-09-07", "2026-09-14", 8, "A-062-00017808-26"),
        ("103095", "ENFERMEDAD", "ESSALUD", "2026-09-10", "2026-09-10", 1, "A-062-00017779-26"),
        ("913371", "ENFERMEDAD", "ESSALUD", "2026-09-15", "2026-09-17", 3, "CM N 0097979"),
        ("910465", "ONOMASTICO", "INPE", "2026-09-28", "2026-09-30", 3, ""),
        ("910940", "ENFERMEDAD", "ESSALUD", "2026-09-21", "2026-10-02", 12, "A-062-00018352-26")
    ]
    for cod, tip, ent, fi, ft, dia, obs in lic_set:
        cur.execute("INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (id_set, emp_map[cod], tip, ent, fi, ft, dia, obs))

    # Vacaciones Setiembre (8)
    cur.execute("DELETE FROM reporte_vacaciones WHERE id_reporte=?", (id_set,))
    vac_set = [
        ("104449", "2025", "2026-09-04", "2026-09-18", 15, ""),
        ("910465", "2025", "2026-09-01", "2026-09-27", 27, ""),
        ("103986", "2026", "2026-09-12", "2026-09-20", 9, ""),
        ("909967", "2024", "2026-08-24", "2026-09-22", 30, ""),
        ("910668", "2026", "2026-09-02", "2026-09-16", 15, ""),
        ("103097", "2024", "2026-09-07", "2026-09-13", 7, ""),
        ("910396", "2025", "2026-09-21", "2026-09-29", 9, ""),
        ("102595", "2026", "2026-09-16", "2026-09-16", 1, "")
    ]
    for cod, per, fi, ft, dia, obs in vac_set:
        cur.execute("INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_set, emp_map[cod], per, fi, ft, dia, obs))

    # Tardanzas Setiembre (1: Bardales Lozano Carmen Rosa 11 min)
    cur.execute("DELETE FROM reporte_tardanzas WHERE id_reporte=?", (id_set,))
    cur.execute("INSERT INTO reporte_tardanzas (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, 11, 'SETIEMBRE')", (id_set, emp_map["102595"]))

    # Permisos Particulares Setiembre (5)
    cur.execute("DELETE FROM reporte_permisos WHERE id_reporte=?", (id_set,))
    for cod, min_v in [("103097", 110), ("103986", 140), ("911382", 50), ("912244", 235), ("102595", 295)]:
        cur.execute("INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones) VALUES (?, ?, ?, 'SETIEMBRE')", (id_set, emp_map[cod], min_v))

    # Inasistencias Setiembre (2)
    cur.execute("DELETE FROM reporte_inasistencias WHERE id_reporte=?", (id_set,))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 3, '27,28,29', 'SETIEMBRE')", (id_set, emp_map["103986"]))
    cur.execute("INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones) VALUES (?, ?, 3, '28,29,30', 'SETIEMBRE')", (id_set, emp_map["911381"]))

    conn.commit()
    conn.close()
    print("Meses de Mayo, Junio, Julio, Agosto y Setiembre 2026 cargados y sincronizados al 100%.")

if __name__ == "__main__":
    load_todos_los_meses_hasta_setiembre()
