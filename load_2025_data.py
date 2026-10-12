import sqlite3

def load_2025_data(db_path="rrhh_control.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Asegurar regímenes
    regimenes = [
        ("LEY_29709", "Ley N° 29709"),
        ("DL_276", "D.L. N° 276"),
        ("DL_1057", "D.L. N° 1057 (CAS)")
    ]
    for cod, nom in regimenes:
        cur.execute("INSERT OR IGNORE INTO regimenes_laborales (codigo, nombre) VALUES (?, ?)", (cod, nom))
    conn.commit()

    # Mapeo de códigos de régimen
    cur.execute("SELECT codigo, id_regimen FROM regimenes_laborales")
    reg_map = dict(cur.fetchall())

    # Lista consolidada del personal del Establecimiento 722 (EP. Mujeres Iquitos)
    # codigo, dni, nombres
    empleados_list = [
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
        ("910465", "48009378", "MELENDEZ AMASIFUEN MAILITH"),
        ("914591", "44306146", "HIDALGO NASHNATE LEIDY VANESSA")
    ]

    for cod, dni, nom in empleados_list:
        cur.execute("""
            INSERT INTO empleados (codigo_servidor, dni, apellidos_nombres)
            VALUES (?, ?, ?)
            ON CONFLICT(codigo_servidor) DO UPDATE SET dni=excluded.dni, apellidos_nombres=excluded.apellidos_nombres
        """, (cod, dni, nom))
    conn.commit()

    # Mapeo de IDs de empleados
    cur.execute("SELECT codigo_servidor, id_empleado FROM empleados")
    emp_map = dict(cur.fetchall())
    id_directora = emp_map["099132"]

    # Meses a cerrar 2025: Septiembre (9), Octubre (10), Noviembre (11), Diciembre (12)
    cierres = [
        (2025, 9, 722, id_directora, 28, "Cierre mensual Setiembre 2025 cerrado conforme."),
        (2025, 10, 722, id_directora, 28, "Cierre mensual Octubre 2025 cerrado conforme."),
        (2025, 11, 722, id_directora, 29, "Cierre mensual Noviembre 2025 cerrado conforme. Se incorpora técnica Hidalgo Nashnate."),
        (2025, 12, 722, id_directora, 29, "Cierre mensual Diciembre 2025 y Cierre de Ejercicio Anual 2025.")
    ]

    for anio, mes, est, resp, total, obs in cierres:
        cur.execute("""
            INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, observaciones_generales)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(anio, mes, id_establecimiento) DO UPDATE SET
                total_trabajadores=excluded.total_trabajadores,
                observaciones_generales=excluded.observaciones_generales
        """, (anio, mes, est, resp, total, obs))
    conn.commit()

    # Mapear reportes
    cur.execute("SELECT mes, id_reporte FROM reportes_cierre_mensual WHERE anio=2025 AND id_establecimiento=722")
    rep_map = dict(cur.fetchall())

    # --- 1. SANCIONES (0 en todos los reportes analizados) ---

    # --- 2. RENUNCIAS (0 en todos los reportes analizados) ---

    # --- 3. REINCORPORACIONES (0 registradas formalmente en hoja de novedades) ---

    # --- 4. TARDANZAS 2025 ---
    # Setiembre: Bardales Lozano (10m), Bardales Lozano Ambar (17m)
    # Octubre: Bardales Lozano Carmen (15m)
    # Diciembre: Caceres Rios Jaxson (334m)
    tardanzas = [
        (rep_map[9], emp_map["102595"], 10, "SETIEMBRE"),
        (rep_map[9], emp_map["913371"], 17, "SETIEMBRE"),
        (rep_map[10], emp_map["102595"], 15, "OCTUBRE"),
        (rep_map[12], emp_map["103097"], 334, "DICIEMBRE")
    ]
    cur.executemany("""
        INSERT INTO reporte_tardanzas (id_reporte, id_empleado, minutos, observaciones)
        VALUES (?, ?, ?, ?)
    """, tardanzas)

    # --- 5. PERMISOS PARTICULARES 2025 ---
    permisos = [
        # Setiembre
        (rep_map[9], emp_map["102595"], 360, "SETIEMBRE"),
        (rep_map[9], emp_map["910945"], 344, "SETIEMBRE"),
        (rep_map[9], emp_map["910668"], 110, "SETIEMBRE"),
        (rep_map[9], emp_map["911382"], 40, "SETIEMBRE"),
        (rep_map[9], emp_map["910465"], 85, "SETIEMBRE"),
        (rep_map[9], emp_map["102747"], 110, "SETIEMBRE"),
        (rep_map[9], emp_map["103097"], 100, "SETIEMBRE"),
        # Octubre
        (rep_map[10], emp_map["102595"], 355, "OCTUBRE"),
        (rep_map[10], emp_map["913148"], 120, "OCTUBRE"),
        (rep_map[10], emp_map["912244"], 26, "OCTUBRE"),
        (rep_map[10], emp_map["910940"], 90, "OCTUBRE"),
        (rep_map[10], emp_map["910668"], 69, "OCTUBRE"),
        (rep_map[10], emp_map["913429"], 207, "OCTUBRE"),
        (rep_map[10], emp_map["102747"], 110, "OCTUBRE"),
        (rep_map[10], emp_map["910332"], 90, "OCTUBRE"),
        # Diciembre
        (rep_map[12], emp_map["103097"], 106, "DICIEMBRE"),
        (rep_map[12], emp_map["102595"], 420, "DICIEMBRE"),
        (rep_map[12], emp_map["913148"], 163, "DICIEMBRE"),
        (rep_map[12], emp_map["104449"], 120, "DICIEMBRE"),
        (rep_map[12], emp_map["912244"], 126, "DICIEMBRE")
    ]
    cur.executemany("""
        INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones)
        VALUES (?, ?, ?, ?)
    """, permisos)

    # --- 6. INASISTENCIAS INJUSTIFICADAS 2025 ---
    inasistencias = [
        (rep_map[9], emp_map["913429"], 3, "26, 27 y 28", "SETIEMBRE"),
        (rep_map[10], emp_map["102595"], 1, "10", "OCTUBRE"),
        (rep_map[12], emp_map["913429"], 5, "15, 28, 29, 30 y 31", "DICIEMBRE")
    ]
    cur.executemany("""
        INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones)
        VALUES (?, ?, ?, ?, ?)
    """, inasistencias)

    # --- 7. LICENCIAS 2025 ---
    licencias = [
        # Setiembre
        (rep_map[9], emp_map["102595"], "ENFERMEDAD", "PARTICULAR", "2025-09-09", "2025-09-10", 2, ""),
        (rep_map[9], emp_map["104449"], "ENFERMEDAD", "PARTICULAR", "2025-09-19", "2025-09-21", 3, ""),
        (rep_map[9], emp_map["910396"], "ENFERMEDAD", "PARTICULAR", "2025-08-31", "2025-09-02", 3, ""),
        (rep_map[9], emp_map["910465"], "ONOMASTICO", "INPE", "2025-09-16", "2025-09-18", 3, ""),
        (rep_map[9], emp_map["103097"], "ENFERMEDAD", "ESSALUD", "2025-09-29", "2025-09-30", 2, ""),
        (rep_map[9], emp_map["103097"], "ENFERMEDAD", "PARTICULAR", "2025-09-24", "2025-09-26", 3, ""),
        # Octubre
        (rep_map[10], emp_map["102595"], "ONOMASTICO", "INPE", "2025-10-03", "2025-10-03", 1, ""),
        (rep_map[10], emp_map["009881"], "ONOMASTICO", "INPE", "2025-10-04", "2025-10-06", 3, ""),
        (rep_map[10], emp_map["911662"], "ONOMASTICO", "INPE", "2025-10-16", "2025-10-18", 3, ""),
        (rep_map[10], emp_map["913371"], "ONOMASTICO", "INPE", "2025-10-27", "2025-10-29", 3, ""),
        (rep_map[10], emp_map["912503"], "ENFERMEDAD", "ESSALUD", "2025-10-06", "2025-10-20", 15, ""),
        (rep_map[10], emp_map["913429"], "ENFERMEDAD", "PARTICULAR", "2025-10-26", "2025-11-04", 10, ""),
        # Noviembre
        (rep_map[11], emp_map["912503"], "ONOMASTICO", "INPE", "2025-11-06", "2025-11-08", 3, ""),
        (rep_map[11], emp_map["910748"], "ONOMASTICO", "INPE", "2025-11-04", "2025-11-06", 3, ""),
        (rep_map[11], emp_map["103097"], "ONOMASTICO", "INPE", "2025-11-21", "2025-11-21", 1, ""),
        (rep_map[11], emp_map["910668"], "ONOMASTICO", "INPE", "2025-11-23", "2025-11-25", 3, ""),
        (rep_map[11], emp_map["910940"], "ONOMASTICO", "INPE", "2025-11-11", "2025-11-13", 3, ""),
        (rep_map[11], emp_map["912244"], "ENFERMEDAD", "PARTICULAR", "2025-11-02", "2025-11-04", 3, ""),
        (rep_map[11], emp_map["103097"], "ENFERMEDAD", "ESSALUD", "2025-11-04", "2025-11-05", 2, ""),
        (rep_map[11], emp_map["102595"], "ENFERMEDAD", "PARTICULAR", "2025-11-13", "2025-11-14", 2, ""),
        (rep_map[11], emp_map["910869"], "ENFERMEDAD", "ESSALUD", "2025-11-03", "2025-11-04", 2, ""),
        (rep_map[11], emp_map["104449"], "ENFERMEDAD", "PARTICULAR", "2025-11-15", "2025-11-17", 3, ""),
        (rep_map[11], emp_map["910332"], "ENFERMEDAD", "ESSALUD", "2025-11-16", "2025-11-18", 3, ""),
        (rep_map[11], emp_map["910465"], "ENFERMEDAD", "ESSALUD", "2025-11-24", "2025-11-25", 2, ""),
        (rep_map[11], emp_map["911664"], "ENFERMEDAD", "ESSALUD", "2025-11-05", "2025-11-11", 7, ""),
        # Diciembre
        (rep_map[12], emp_map["009881"], "ENFERMEDAD", "PARTICULAR", "2025-12-02", "2025-12-04", 3, ""),
        (rep_map[12], emp_map["910869"], "ENFERMEDAD", "ESSALUD", "2025-12-06", "2025-12-08", 3, ""),
        (rep_map[12], emp_map["911382"], "ENFERMEDAD", "ESSALUD", "2025-12-10", "2025-12-12", 3, ""),
        (rep_map[12], emp_map["913148"], "ONOMASTICO", "INPE", "2025-12-30", "2025-12-30", 1, ""),
        (rep_map[12], emp_map["104449"], "ENFERMEDAD", "PARTICULAR", "2025-12-01", "2025-12-02", 2, ""),
        (rep_map[12], emp_map["911387"], "ENFERMEDAD", "ESSALUD", "2025-12-16", "2025-12-18", 3, ""),
        (rep_map[12], emp_map["910945"], "ENFERMEDAD", "PARTICULAR", "2025-12-13", "2025-12-15", 3, ""),
        (rep_map[12], emp_map["913429"], "ENFERMEDAD", "ESSALUD", "2025-12-13", "2025-12-14", 2, ""),
        (rep_map[12], emp_map["913429"], "ENFERMEDAD", "PARTICULAR", "2025-12-19", "2025-12-27", 9, ""),
        (rep_map[12], emp_map["913371"], "ENFERMEDAD", "PARTICULAR", "2025-12-14", "2025-12-16", 3, ""),
        (rep_map[12], emp_map["910668"], "ENFERMEDAD", "PARTICULAR", "2025-12-05", "2025-12-07", 3, ""),
        (rep_map[12], emp_map["102595"], "ENFERMEDAD", "PARTICULAR", "2025-12-30", "2025-12-31", 2, ""),
        (rep_map[12], emp_map["908917"], "ENFERMEDAD", "ESSALUD", "2025-12-31", "2026-01-01", 2, "")
    ]
    cur.executemany("""
        INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, licencias)

    # --- 8. VACACIONES 2025 ---
    vacaciones = [
        # Setiembre
        (rep_map[9], emp_map["910945"], "2023-2024", "2025-09-26", "2025-10-04", 9, ""),
        (rep_map[9], emp_map["102595"], "2024-2025", "2025-09-16", "2025-09-16", 1, "ADELANTO DE VACACIONES, SOLO LE RESTA 29 DIAS"),
        (rep_map[9], emp_map["910396"], "2024-2025", "2025-09-28", "2025-09-30", 3, ""),
        (rep_map[9], emp_map["912244"], "2025-2025", "2025-09-06", "2025-10-05", 30, ""),
        (rep_map[9], emp_map["913429"], "2025-2025", "2025-09-02", "2025-09-16", 15, ""),
        # Octubre
        (rep_map[10], emp_map["102595"], "2025", "2025-10-24", "2025-10-26", 3, "adelanto vacaciones"),
        (rep_map[10], emp_map["104449"], "2024", "2025-10-16", "2025-10-27", 12, ""),
        (rep_map[10], emp_map["911664"], "2024", "2025-10-06", "2025-11-04", 30, ""),
        (rep_map[10], emp_map["009881"], "2024", "2025-10-09", "2025-11-07", 30, ""),
        # Diciembre
        (rep_map[12], emp_map["103097"], "2023-2024", "2025-12-22", "2026-01-02", 12, ""),
        (rep_map[12], emp_map["911382"], "2023-2024", "2025-12-13", "2025-12-27", 15, ""),
        (rep_map[12], emp_map["913148"], "2025", "2025-12-31", "2026-01-29", 30, ""),
        (rep_map[12], emp_map["102747"], "2023-2024", "2025-12-18", "2025-12-20", 3, "")
    ]
    cur.executemany("""
        INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, vacaciones)

    # --- 9. FUNCIONARIOS ---
    for mes_num in [9, 10, 11, 12]:
        cur.execute("""
            INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rep_map[mes_num], id_directora, "DIRECTORA", "S4", "2023-12-29", "RP N°325-2023-INPE/P"))

    # Crear tabla de Cierre Anual para consolidar el año 2025
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cierres_anuales (
            id_cierre SERIAL PRIMARY KEY,
            anio INTEGER UNIQUE NOT NULL,
            id_establecimiento INTEGER NOT NULL,
            estado VARCHAR(50) DEFAULT 'CERRADO',
            total_meses_reportados INTEGER DEFAULT 0,
            observaciones TEXT,
            fecha_cierre TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_establecimiento) REFERENCES establecimientos(id_establecimiento)
        )
    """.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT"))

    cur.execute("""
        INSERT INTO cierres_anuales (anio, id_establecimiento, estado, total_meses_reportados, observaciones)
        VALUES (2025, 722, 'CERRADO', 4, 'Cierre del Ejercicio 2025 completado con los meses disponibles (Setiembre, Octubre, Noviembre, Diciembre).')
        ON CONFLICT(anio) DO UPDATE SET estado='CERRADO', total_meses_reportados=4
    """)

    conn.commit()
    conn.close()
    print("Datos históricos y Cierre del año 2025 cargados con éxito.")

if __name__ == "__main__":
    load_2025_data()

