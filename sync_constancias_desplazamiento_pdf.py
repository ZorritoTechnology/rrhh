import sqlite3

def sincronizar_constancias_pdf():
    conn = sqlite3.connect('rrhh_control.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Asegurar columna numero_constancia_oficial en desplazamientos_personal
    cur.execute("PRAGMA table_info(desplazamientos_personal)")
    cols = [c[1] for c in cur.fetchall()]
    if 'numero_constancia_oficial' not in cols:
        cur.execute("ALTER TABLE desplazamientos_personal ADD COLUMN numero_constancia_oficial VARCHAR(100)")
        print("Añadida columna numero_constancia_oficial")

    # Mapeo exacto de las 8 constancias del PDF:
    # Pag 8: REG. N° 001-2026: Cavero Díaz Angel Gabriel (id 10)
    cur.execute("""
        UPDATE desplazamientos_personal
        SET numero_constancia_oficial = 'REG. N° 001-2026-INPE/ORNOSM-EPA-IQT-RRHH',
            documento_oficial = 'RD N° 036-2026-INPE/ORNOSM',
            nombre_destino_ext = 'EP. CHACHAPOYAS',
            fecha_desplazamiento = '2026-02-13',
            vacaciones_periodo = '2024-2025',
            vacaciones_saldo_origen = 0,
            comp_gozadas_origen = 0,
            observaciones = 'Constancia REG. N° 001-2026. Franco 14-15 feb. Desplazado a EP Chachapoyas. Saldo vac. 00 días.'
        WHERE id_empleado = 10 AND tipo_movimiento = 'BAJA_SALIDA'
    """)

    # Pag 7: REG. N° 002-2026: Guevara Castillo Michael Estefany (id 26)
    cur.execute("""
        UPDATE desplazamientos_personal
        SET numero_constancia_oficial = 'REG. N° 002-2026-INPE/ORNOSM-EPA-IQT-RRHH',
            documento_oficial = 'RD N° 144-2026-INPE/OGA-URH',
            nombre_destino_ext = 'EP. VIRGEN DE FÁTIMA (LIMA)',
            fecha_desplazamiento = '2026-02-17',
            vacaciones_periodo = '2024-2025',
            vacaciones_saldo_origen = 0,
            comp_gozadas_origen = 0,
            observaciones = 'Constancia REG. N° 002-2026. Franco 18-19 feb. Desplazado a EP Virgen de Fátima. Saldo vac. 00 días.'
        WHERE id_empleado = 26 AND tipo_movimiento = 'BAJA_SALIDA'
    """)

    # Pag 6: REG. N° 003-2026: Zapata Roque Santos Delcia (id 1)
    cur.execute("""
        UPDATE desplazamientos_personal
        SET numero_constancia_oficial = 'REG. N° 003-2026-INPE/ORNOSM-EPA-IQT-RRHH',
            documento_oficial = 'RESOLUCIÓN PRESIDENCIAL N° 089-2026-INPE/P',
            nombre_destino_ext = 'EP. MOYOBAMBA',
            fecha_desplazamiento = '2026-03-06',
            vacaciones_periodo = '2024-2025',
            vacaciones_saldo_origen = 30,
            observaciones = 'Constancia REG. N° 003-2026. Retorna a plaza origen EP Moyobamba (presentación en EP Mujeres Virgen de Fátima Lima). Saldo vac. 2024-2025: 30 días.'
        WHERE id_empleado = 1 AND tipo_movimiento = 'BAJA_SALIDA'
    """)

    # Pag 5: REG. N° 004-2026: López Tamani Blanca Carina (id 3)
    cur.execute("""
        UPDATE desplazamientos_personal
        SET numero_constancia_oficial = 'REG. N° 004-2026-INPE/ORNOSM-EPA-IQT-RRHH',
            documento_oficial = 'RD N° 122-2026-INPE/ORNOSM',
            nombre_destino_ext = 'EP. IQUITOS (VARONES)',
            fecha_desplazamiento = '2026-04-10',
            vacaciones_periodo = '2024-2025',
            vacaciones_saldo_origen = 23,
            observaciones = 'Constancia REG. N° 004-2026. Retorna a plaza de origen EP Iquitos Varones. Saldo vac. 2024-2025: 23 días.'
        WHERE id_empleado = 3 AND tipo_movimiento = 'BAJA_SALIDA'
    """)

    # Pag 4: REG. N° 005-2026: Núñez Góngora Ralf Francois (id 27)
    cur.execute("""
        UPDATE desplazamientos_personal
        SET numero_constancia_oficial = 'REG. N° 005-2026-INPE/ORNOSM-EPA-IQT-RRHH',
            documento_oficial = 'RD N° 189-2026-INPE/ORNOSM',
            nombre_destino_ext = 'EP. IQUITOS (VARONES)',
            fecha_desplazamiento = '2026-06-12',
            vacaciones_periodo = '2024-2025',
            vacaciones_saldo_origen = 0,
            comp_ganadas_origen = 4,
            observaciones = 'Constancia REG. N° 005-2026. Rotado a EP Iquitos Varones. Pendiente 24x48 (2025): 02 días. Ha generado 4 días compensación 2026 para 2027.'
        WHERE id_empleado = 27 AND tipo_movimiento = 'BAJA_SALIDA'
    """)

    # Pag 3: REG. N° 006-2026: Canales Paredes Adela Isabel (id 13)
    cur.execute("""
        UPDATE desplazamientos_personal
        SET numero_constancia_oficial = 'REG. N° 006-2026-INPE/ORNOSM-EPA-IQT-RRHH',
            documento_oficial = 'RD N° 189-2026-INPE/ORNOSM',
            nombre_destino_ext = 'EP. IQUITOS (VARONES)',
            fecha_desplazamiento = '2026-06-12',
            vacaciones_periodo = '2024-2025',
            vacaciones_saldo_origen = 48,
            comp_saldo_origen = 7,
            observaciones = 'Constancia REG. N° 006-2026. Rotado a EP Iquitos Varones. Saldo vac: 18 días (23-24) + 30 días (24-25). Pendiente 24x48 (2025): 07 días. Generó 6 días 2026 para 2027.'
        WHERE id_empleado = 13 AND tipo_movimiento = 'BAJA_SALIDA'
    """)

    # Pag 2: REG. N° 007-2026: Lomas Romero Mónica (id 16)
    cur.execute("""
        UPDATE desplazamientos_personal
        SET numero_constancia_oficial = 'REG. N° 007-2026-INPE/ORNOSM-EPA-IQT-RRHH',
            documento_oficial = 'RD N° 189-2026-INPE/ORNOSM',
            nombre_destino_ext = 'EP. IQUITOS (VARONES)',
            fecha_desplazamiento = '2026-06-12',
            vacaciones_periodo = '2024-2025',
            vacaciones_saldo_origen = 30,
            observaciones = 'Constancia REG. N° 007-2026. Rotado a EP Iquitos Varones. Saldo vac: 30 días (24-25). Pendiente 24x48 (2025): 00 días. Generó 6 días 2026 para 2027.'
        WHERE id_empleado = 16 AND tipo_movimiento = 'BAJA_SALIDA'
    """)

    # Pag 1: REG. N° 008-2026: De Loayza Torres Ambar Cristina (id 101)
    cur.execute("""
        SELECT id_desplazamiento FROM desplazamientos_personal 
        WHERE id_empleado = 101 AND tipo_movimiento = 'BAJA_SALIDA'
    """)
    row_loayza = cur.fetchone()
    if not row_loayza:
        cur.execute("""
            INSERT INTO desplazamientos_personal (
                id_empleado, tipo_movimiento, fecha_desplazamiento, fecha_presentacion_eepp,
                documento_oficial, nombre_destino_ext, numero_constancia_oficial,
                vacaciones_periodo, vacaciones_saldo_origen, comp_saldo_origen,
                observaciones
            ) VALUES (
                101, 'BAJA_SALIDA', '2026-10-09', '2026-10-10',
                'RESOLUCIÓN PRESIDENCIAL N° 0652-2026-INPE/P', 'EP. IQUITOS (VARONES)', 'REG. N° 008-2026-INPE/ORNOSM-EPA-IQT-RRHH',
                '2025-2026', 0, 0,
                'Constancia REG. N° 008-2026. Técnico Administrativo rotado a EP Iquitos Varones. Horario 24x48. Récord vac. saldo 0 días. Ingreso nueva ley 01/10/2026.'
            )
        """)
        print("Registrada Baja por Desplazamiento REG. N° 008-2026 para Ambar De Loayza Torres")

    # Actualizar estado laboral de Ambar De Loayza Torres a DESPLAZADO
    cur.execute("""
        UPDATE empleados
        SET estado_laboral = 'DESPLAZADO',
            fecha_ingreso_inpe = '2026-10-01'
        WHERE id_empleado = 101
    """)

    # Actualizar fechas exactas de ingreso al INPE de los otros servidores según las constancias oficiales
    # Cavero Diaz: 27/12/2017
    cur.execute("UPDATE empleados SET fecha_ingreso_inpe = '2017-12-27' WHERE id_empleado = 10")
    # Guevara Castillo: 29/08/2024
    cur.execute("UPDATE empleados SET fecha_ingreso_inpe = '2024-08-29' WHERE id_empleado = 26")
    # Zapata Roque: 07/05/1987
    cur.execute("UPDATE empleados SET fecha_ingreso_inpe = '1987-05-07' WHERE id_empleado = 1")
    # Lopez Tamani: 12/09/2012
    cur.execute("UPDATE empleados SET fecha_ingreso_inpe = '2012-09-12' WHERE id_empleado = 3")
    # Nuñez Gongora: 22/12/2014
    cur.execute("UPDATE empleados SET fecha_ingreso_inpe = '2014-12-22' WHERE id_empleado = 27")
    # Canales Paredes: 31/12/2008
    cur.execute("UPDATE empleados SET fecha_ingreso_inpe = '2008-12-31' WHERE id_empleado = 13")
    # Lomas Romero: 01/09/2024
    cur.execute("UPDATE empleados SET fecha_ingreso_inpe = '2024-09-01' WHERE id_empleado = 16")

    conn.commit()
    print("Sincronización de constancias oficiales del PDF culminada exitosamente.")
    conn.close()

if __name__ == '__main__':
    sincronizar_constancias_pdf()
