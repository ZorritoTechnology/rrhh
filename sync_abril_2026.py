import sqlite3

def sync_abril_2026():
    conn = sqlite3.connect('rrhh_control.db')
    c = conn.cursor()

    # 1. Obtener id_reporte para anio=2026, mes=4
    c.execute("SELECT id_reporte FROM reportes_cierre_mensual WHERE anio=2026 AND mes=4")
    row = c.fetchone()
    if row:
        id_reporte = row[0]
    else:
        c.execute("""
            INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, fecha_cierre, observaciones_generales, created_at, estado)
            VALUES (2026, 4, 722, 89, 27, '2026-10-11', 'Reporte de Asistencia 04/2026', datetime('now'), 'CERRADO')
        """)
        id_reporte = c.lastrowid

    print(f"Sincronizando Abril 2026 con id_reporte = {id_reporte}")

    # Limpiar tablas hijas asociadas a id_reporte
    subtablas = [
        'asistencia_mensual_personal',
        'reporte_funcionarios',
        'reporte_sanciones',
        'reporte_renuncias',
        'reporte_reincorporaciones',
        'reporte_desplazamientos',
        'reporte_licencias',
        'reporte_vacaciones',
        'reporte_tardanzas',
        'reporte_permisos',
        'reporte_inasistencias',
        'reporte_no_registrados'
    ]
    for st in subtablas:
        c.execute(f"DELETE FROM {st} WHERE id_reporte = ?", (id_reporte,))

    # Actualizar cabecera del reporte
    c.execute("""
        UPDATE reportes_cierre_mensual 
        SET total_trabajadores = 27, id_responsable = 89, estado = 'CERRADO'
        WHERE id_reporte = ?
    """, (id_reporte,))

    # Diccionario de empleados para mapeo
    c.execute("SELECT codigo_servidor, id_empleado FROM empleados")
    emp_map = {r[0]: r[1] for r in c.fetchall()}

    # Lista oficial de los 27 servidores según PDF Hoja 1
    # Columnas:
    # (codigo, regimen_str, nivel, cargo_est, estado, mod, dir_of, jef_area, cargo_func, area, horario, fecha_ing, resolucion, obs)
    personal_data = [
        ("009889", 1, "T3", "ALCAIDE DE GRUPO", "ACTIVO", "PRESENCIAL", "DIRECCION", "DIRECCION", "DIRECTORA", "ADM", "08:00 - 17:00", "20/02/2026", "RP N° 089-2026-INPE/P", ""),
        ("103095", 1, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE SECCION DE SEGURIDAD", "ADM", "08:00 - 17:00", "18/02/2026", "RP N° 089-2026-INPE/P", ""),
        ("103913", 2, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "ADMINISTRATIVO", "SEGURIDAD", "JEFE DE DIVISION DE SEGURIDAD", "ADM", "08:00 - 17:00", "30/12/2020", "RD 260-2020-INPE/ORNOSM", ""),
        ("103097", 1, "T1", "GESTOR DE BASE DE DATOS", "ACTIVO", "PRESENCIAL", "REGISTRO", "REGISTRO PENITENCIARIO", "JEFE DE REGISTRO PENITENCIARIO", "ADM", "08:00 - 17:00", "1/04/2021", "RD 42-2021-INPE/ORNOSM", ""),
        ("102595", 1, "S1", "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "EDUCACION", "COORDINADORA DE EDUCACION", "TRA", "08:00 - 17:00", "5/12/2024", "RD N°303-2024-INPE-P", ""),
        ("913148", 3, "SNR", "OBSTETRA", "ACTIVO", "PRESENCIAL", "TRATAMIENTO", "SALUD PENITENCIARIA", "OBSTETRIZ", "TRA", "08:00 - 17:00", "10/09/2019", "CONTRATO", ""),
        ("913371", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/12/2023", "RP N°339-2023-INPE/P", ""),
        ("911381", 3, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/07/2023", "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", ""),
        ("910668", 1, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/09/2024", "RP. N°203-2024-INPE/P", ""),
        ("911382", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/12/2023", "RP N°339-2023-INPE/P", ""),
        ("912244", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "18/01/2024", "RP N°339-2023-INPE/P", ""),
        ("102747", 1, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "11/04/2025", "RD N°057-2025-INPE/ORNOSM", ""),
        ("910748", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/12/2023", "RP N°339-2023-INPE/P", ""),
        ("909967", 3, "SNR", "AGENTE DE SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/01/2025", "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", ""),
        ("910332", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "20/06/2024", "MEMORANDO N°125-2024-INPE/ORNOSM-ERRHH", ""),
        ("910869", 1, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "7/09/2024", "RP N°203-2024-INPE/P", ""),
        ("908917", 1, "T1", "TÉCNICO EN SEGURIDAD", "LICENCIA MATERNIDAD", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/12/2023", "RP N°339-2023-INPE/P", "Licencia por maternidad 02/01/2026 al 09/04/2026"),
        ("911387", 1, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "13/09/2024", "RP N°203-2024-INPE/P", ""),
        ("910945", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/12/2023", "RP N°339-2023-INPE/P", ""),
        ("910940", 1, "T1", "AGENTE DE SEGURIDAD I", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "1/01/2026", "RP N° 534-2025-INPE/P", ""),
        ("910396", 1, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/09/2024", "RP N°203-2024-INPE/P", ""),
        ("009881", 1, "T3", "SUPERVISOR DE GRUPO", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "9/11/2014", "RD N°251-2014-INPE/21", ""),
        ("103793", 2, "STF", "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "ABANDONO", "NO APLICA", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "2/07/2017", "RD N°461-2016-INPE/P", "abandono laboral desde el 10/05/2021"),
        ("911662", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "29/01/2024", "RP N°339-2023-INPE/P", ""),
        ("912503", 1, "T1", "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "8/09/2024", "RP N°203-2024-INPE/P", ""),
        ("104449", 2, "STF", "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "5/08/2025", "RD N°607-2025-INPE/OGA-URH", ""),
        ("910465", 1, "T1", "TÉCNICO EN SEGURIDAD", "ACTIVO", "PRESENCIAL", "SEGURIDAD PENITENCIARIA", "SEGURIDAD PENITENCIARIA", "AGENTE DE SEGURIDAD", "SEG", "24 x 48", "6/08/2025", "RD N°607-2025-INPE/OGA-URH", "")
    ]

    for item in personal_data:
        cod = item[0]
        emp_id = emp_map[cod]
        c.execute("""
            INSERT INTO asistencia_mensual_personal (
                id_reporte, id_empleado, id_regimen, nivel, cargo_estructural,
                estado_laboral, modalidad_laboral, direccion_oficina, jefatura_area,
                cargo_funcion, area_clasificacion, horario_laboral, fecha_ingreso_eepp,
                resolucion_documento, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_reporte, emp_id, item[1], item[2], item[3],
            item[4], item[5], item[6], item[7],
            item[8], item[9], item[10], item[11],
            item[12], item[13]
        ))
    print(f"Insertados {len(personal_data)} servidores en asistencia_mensual_personal.")

    # Hoja 2: Funcionarios (2)
    # 009889 DIRECTORA S4 20/02/2026 RP N° 089-2026-INPE/P
    # 103095 JEFE DE SECCION DE SEGURIDAD S3 18/02/2026 RP N° 089-2026-INPE/P
    c.execute("""
        INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (id_reporte, emp_map["009889"], "DIRECTORA", "S4", "2026-02-20", "RP N° 089-2026-INPE/P", ""))
    c.execute("""
        INSERT INTO reporte_funcionarios (id_reporte, id_empleado, cargo_funcion, nivel, fecha_inicio_funciones, resolucion_documento, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (id_reporte, emp_map["103095"], "JEFE DE SECCION DE SEGURIDAD", "S3", "2026-02-18", "RP N° 089-2026-INPE/P", ""))
    print("Insertados 2 Funcionarios.")

    # Hoja 6: Desplazamientos (1)
    # 103913 LOPEZ TAMANI BLANCA CARINA DL N° 276 722 EP. MUJERES IQUITOS -> 721 EP. IQUITOS, SEG, AGENTE DE SEGURIDAD, 10/04/2026, RD. N° 122-2026-INPE/ORNOSM
    c.execute("""
        INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, id_establecimiento_origen, id_establecimiento_destino, area, cargo_funcion, fecha_desplazamiento, documento_resolucion, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_reporte, emp_map["103913"], None, None, "SEG", "AGENTE DE SEGURIDAD", "2026-04-10", "RD. N° 122-2026-INPE/ORNOSM", "RD. N° 122-2026-INPE/ORNOSM (722 EP. MUJERES IQUITOS a 721 EP. IQUITOS)"))
    print("Insertado 1 Desplazamiento.")

    # Hoja 7: Licencias (5)
    # 1 103097 CACERES RIOS JAXSON CHARLES ENFERMEDAD PARTICULAR 09/04/2026 09/04/2026 1 CMP N° 39566
    # 2 103097 CACERES RIOS JAXSON CHARLES ENFERMEDAD ESSALUD 23/04/2026 23/04/2026 1 CITT N° A-062-00013166-26
    # 3 102747 CANALES PAREDES ADELA ISABEL ENFERMEDAD ESSALUD 10/04/2026 12/04/2026 3 CITA MEDICA HOSP. REBAGLIATI - LIMA
    # 4 910332 NUÑEZ GONGORA RALF FRANCOIS ENFERMEDAD ESSALUD 04/04/2026 06/04/2026 3 CITT N° A-062-00012523-26
    # 5 908917 PARANO OROCHE BRIGITTE ONOMASTICO INPE 10/04/2026 12/04/2026 3 SOLICITUD
    licencias_data = [
        ("103097", "ENFERMEDAD", "PARTICULAR", "2026-04-09", "2026-04-09", 1, "CMP N° 39566"),
        ("103097", "ENFERMEDAD", "ESSALUD", "2026-04-23", "2026-04-23", 1, "CITT N° A-062-00013166-26"),
        ("102747", "ENFERMEDAD", "ESSALUD", "2026-04-10", "2026-04-12", 3, "CITA MEDICA HOSP. REBAGLIATI - LIMA"),
        ("910332", "ENFERMEDAD", "ESSALUD", "2026-04-04", "2026-04-06", 3, "CITT N° A-062-00012523-26"),
        ("908917", "ONOMASTICO", "INPE", "2026-04-10", "2026-04-12", 3, "SOLICITUD")
    ]
    for lic in licencias_data:
        c.execute("""
            INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_reporte, emp_map[lic[0]], lic[1], lic[2], lic[3], lic[4], lic[5], lic[6]))
    print(f"Insertadas {len(licencias_data)} Licencias.")

    # Hoja 8: Vacaciones (2)
    # 1 912244 CHUQUIVAL RODRIGUEZ EDINSON 2025 5/04/2026 10/04/2026 6
    # 2 908917 PARANO OROCHE BRIGITTE 2025 13/04/2026 12/05/2026 30
    vac_data = [
        ("912244", 2025, "2026-04-05", "2026-04-10", 6, ""),
        ("908917", 2025, "2026-04-13", "2026-05-12", 30, "")
    ]
    for v in vac_data:
        c.execute("""
            INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_reporte, emp_map[v[0]], v[1], v[2], v[3], v[4], v[5]))
    print(f"Insertadas {len(vac_data)} Vacaciones.")

    # Hoja 9: Tardanzas (2)
    # 1 103097 CACERES RIOS JAXSON CHARLES 42 min
    # 2 911382 CULQUI RENGIFO CLARA URSULA PATRICIA 13 min
    tard_data = [
        ("103097", 42, ""),
        ("911382", 13, "")
    ]
    for t in tard_data:
        c.execute("""
            INSERT INTO reporte_tardanzas (id_reporte, id_empleado, minutos, observaciones)
            VALUES (?, ?, ?, ?)
        """, (id_reporte, emp_map[t[0]], t[1], t[2]))
    print(f"Insertadas {len(tard_data)} Tardanzas.")

    # Hoja 10: Permisos Particulares (4)
    # 1 103097 CACERES RIOS JAXSON CHARLES 345 ABRIL
    # 2 102595 BARDALES LOZANO CARMEN ROSA 360 ABRIL
    # 3 910332 NUÑEZ GONGORA RALF FRANCOIS 176 ABRIL
    # 4 913371 BARDALES LOZANO AMBAR GRECIA TAMARA 82 ABRIL
    perm_data = [
        ("103097", 345, "ABRIL"),
        ("102595", 360, "ABRIL"),
        ("910332", 176, "ABRIL"),
        ("913371", 82, "ABRIL")
    ]
    for p in perm_data:
        c.execute("""
            INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones)
            VALUES (?, ?, ?, ?)
        """, (id_reporte, emp_map[p[0]], p[1], p[2]))
    print(f"Insertados {len(perm_data)} Permisos.")

    # Hoja 11: Inasistencias Injustificadas (1)
    # 1 911381 CARO SILVA FRANK REDI DL N° 1057 3 dias, fechas: 26,27,28, obs: ABRIL 24x48
    c.execute("""
        INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones)
        VALUES (?, ?, ?, ?, ?)
    """, (id_reporte, emp_map["911381"], 3, "26, 27, 28", "ABRIL 24x48"))
    print("Insertada 1 Inasistencia.")

    conn.commit()
    conn.close()
    print("¡Sincronización de Abril 2026 completada con éxito!")

if __name__ == "__main__":
    sync_abril_2026()
