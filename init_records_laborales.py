import sqlite3

def init_records_laborales():
    conn = sqlite3.connect('rrhh_control.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS empleados_records_laborales (
        id_record INTEGER PRIMARY KEY AUTOINCREMENT,
        id_empleado INTEGER NOT NULL,
        tipo_proceso VARCHAR(50) DEFAULT 'LIQUIDACION_CAS',
        regimen_laboral VARCHAR(100) DEFAULT 'DL Nº 1057 CAS',
        cargo_funcion VARCHAR(150),
        dependencia_region VARCHAR(150) DEFAULT 'EP MUJERES IQUITOS',
        numero_celular VARCHAR(50),
        fecha_ingreso_entidad DATE,
        ultimo_dia_laborado DATE,
        fecha_cese_laboral DATE,
        motivo_cese VARCHAR(250),
        documento_sustento VARCHAR(250),
        
        -- Sección A: Vacaciones generadas y truncas
        vacaciones_periodo_1_anio VARCHAR(50) DEFAULT '2024',
        vacaciones_periodo_1_ini VARCHAR(50) DEFAULT 'x',
        vacaciones_periodo_1_fin VARCHAR(50) DEFAULT 'x',
        vacaciones_periodo_1_gozadas REAL DEFAULT 0,
        vacaciones_periodo_1_pendientes REAL DEFAULT 0,

        vacaciones_periodo_2_anio VARCHAR(50) DEFAULT '2025',
        vacaciones_periodo_2_ini VARCHAR(50),
        vacaciones_periodo_2_fin VARCHAR(50),
        vacaciones_periodo_2_gozadas REAL DEFAULT 0,
        vacaciones_periodo_2_pendientes REAL DEFAULT 0,

        vacaciones_no_gozadas_truncas INTEGER DEFAULT 0,

        -- Sección B: Registro de Asistencia
        asistencia_rango_periodo VARCHAR(100),
        inasistencias_dias_minutos VARCHAR(100) DEFAULT '-',
        inasistencias_fechas VARCHAR(150) DEFAULT '',
        tardanzas_dias_minutos VARCHAR(100) DEFAULT '-',
        tardanzas_fechas VARCHAR(150) DEFAULT '',
        particulares_dias_minutos VARCHAR(100) DEFAULT '-',
        particulares_fechas VARCHAR(150) DEFAULT '',

        -- Sección C: Horas por compensar
        horas_compensar_total VARCHAR(100) DEFAULT '0',
        horas_compensar_detalle TEXT DEFAULT '',

        -- Sección D: Observaciones
        observaciones TEXT DEFAULT 'NINGUNA',

        responsable_rrhh VARCHAR(150) DEFAULT 'Jefe de Recursos Humanos y/o Responsable de Control de Personal',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_empleado) REFERENCES empleados (id_empleado)
    )
    """)

    # 1. Actualizar estado laboral de HIDALGO NASHNATE LEIDY VANESSA (id 30) a 'CESADO'
    cur.execute("""
        UPDATE empleados
        SET estado_laboral = 'CESADO',
            cargo_funcion = 'TECNICA ENFERMERIA',
            cargo_estructural = 'TECNICA ENFERMERIA',
            regimen_nombre = 'DL N° 1057 (CAS)',
            observaciones = 'Extinción de Contrato CAS al 31/12/2025. Carta N° D001999-2025-INPE-URH. Récord liquidación: 8 días vac. truncas.'
        WHERE id_empleado = 30
    """)

    # 2. Registrar el Récord Laboral oficial para Pago de Liquidación CAS
    cur.execute("SELECT id_record FROM empleados_records_laborales WHERE id_empleado = 30")
    row = cur.fetchone()

    if not row:
        cur.execute("""
            INSERT INTO empleados_records_laborales (
                id_empleado, tipo_proceso, regimen_laboral, cargo_funcion, dependencia_region,
                numero_celular, fecha_ingreso_entidad, ultimo_dia_laborado, fecha_cese_laboral,
                motivo_cese, documento_sustento,
                vacaciones_periodo_1_anio, vacaciones_periodo_1_ini, vacaciones_periodo_1_fin,
                vacaciones_periodo_1_gozadas, vacaciones_periodo_1_pendientes,
                vacaciones_periodo_2_anio, vacaciones_periodo_2_ini, vacaciones_periodo_2_fin,
                vacaciones_periodo_2_gozadas, vacaciones_periodo_2_pendientes,
                vacaciones_no_gozadas_truncas,
                asistencia_rango_periodo,
                inasistencias_dias_minutos, inasistencias_fechas,
                tardanzas_dias_minutos, tardanzas_fechas,
                particulares_dias_minutos, particulares_fechas,
                horas_compensar_total, horas_compensar_detalle,
                observaciones, responsable_rrhh
            ) VALUES (
                30, 'LIQUIDACION_CAS', 'D.L. Nº 1057 CAS', 'TECNICA ENFERMERIA', 'EP MUJERES IQUITOS',
                '', '2025-09-30', '2025-12-31', '2025-12-31',
                'EXTINCIÓN DE CONTRATO Carta N° D001999-2025-INPE-URH', 'Carta N° D001999-2025-INPE-URH',
                '2024', 'x', 'x', 0, 0,
                '2025', '30/09/2025', '31/12/2025', 0, 7.66,
                8,
                '01/12/2025 al 31/12/2025',
                '-', '',
                '-', '',
                '-', '',
                '0', '',
                'NINGUNA', 'Jefe de Recursos Humanos y/o Responsable de Control de Personal'
            )
        """)
        print("Récord laboral para liquidación de HIDALGO NASHNATE LEIDY VANESSA registrado con éxito.")
    else:
        print("El récord laboral ya existía, se mantiene.")

    # 3. Registrar el evento en el historial laboral de Hidalgo Nashnate
    cur.execute("""
        SELECT id_historial FROM empleados_historial_laboral 
        WHERE id_empleado = 30 AND tipo_evento = 'EXTINCION_CONTRATO_CAS'
    """)
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO empleados_historial_laboral (
                id_empleado, tipo_evento, fecha_evento, regimen_laboral,
                nivel_cargo, cargo_funcion, resolucion_documento, detalles
            ) VALUES (
                30, 'EXTINCION_CONTRATO_CAS', '2025-12-31', 'DL N° 1057 CAS',
                'CAS', 'TECNICA ENFERMERIA', 'Carta N° D001999-2025-INPE-URH',
                'Extinción de Contrato Administrativo de Servicios. Récord laboral de liquidación emitido con 8 días de vacaciones no gozadas / truncas.'
            )
        """)
        print("Hito de término de contrato registrado en historial laboral.")

    conn.commit()
    print("Tabla empleados_records_laborales inicializada y datos sincronizados.")
    conn.close()

if __name__ == '__main__':
    init_records_laborales()
