import sqlite3

def init_compensaciones_db():
    conn = sqlite3.connect('rrhh_control.db')
    c = conn.cursor()

    # 1. Tabla de resoluciones directorales que aprueban los días de compensación anual
    c.execute("""
        CREATE TABLE IF NOT EXISTS resoluciones_compensacion (
            id_resolucion INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_resolucion TEXT NOT NULL, -- ej. RD N° 146-2023-INPE/OGA o RD Anual 2026
            anio_generado INTEGER NOT NULL,  -- ej. 2025
            anio_goce INTEGER NOT NULL,      -- ej. 2026
            dias_maximos_anual INTEGER DEFAULT 16,
            descripcion TEXT,
            fecha_emision DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Saldos de compensación por servidor
    c.execute("""
        CREATE TABLE IF NOT EXISTS saldos_compensacion (
            id_saldo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empleado INTEGER NOT NULL,
            id_resolucion INTEGER,
            anio_goce INTEGER NOT NULL,          -- 2026
            dias_asignados INTEGER DEFAULT 16,   -- Máximo 16 según directiva
            dias_utilizados INTEGER DEFAULT 0,
            dias_disponibles INTEGER DEFAULT 16,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
            FOREIGN KEY (id_resolucion) REFERENCES resoluciones_compensacion(id_resolucion),
            UNIQUE (id_empleado, anio_goce)
        )
    """)

    # 3. Solicitudes y goce de compensación (Anexo 01)
    c.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_compensacion (
            id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empleado INTEGER NOT NULL,
            anio_goce INTEGER NOT NULL,
            mes INTEGER NOT NULL,                -- 1 a 12
            fecha_solicitud DATE,                -- Fecha de presentación (mínimo 5 días antes)
            fecha_compensacion DATE NOT NULL,    -- Día completo de 24 horas a compensar
            dias_compensados INTEGER DEFAULT 1,  -- Siempre 1 jornada completa (24 hrs)
            jefe_inmediato TEXT,                 -- Firma y sello del jefe inmediato
            especialista_personal TEXT,          -- V°B° del especialista
            estado TEXT DEFAULT 'APROBADO',      -- APROBADO, PENDIENTE, RECHAZADO
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
        )
    """)

    # Insertar Resolución Directoral de Compensación 2026 si no existe
    c.execute("SELECT id_resolucion FROM resoluciones_compensacion WHERE anio_goce = 2026")
    res = c.fetchone()
    if not res:
        c.execute("""
            INSERT INTO resoluciones_compensacion (
                numero_resolucion, anio_generado, anio_goce, dias_maximos_anual, descripcion, fecha_emision
            ) VALUES (
                'RD N° 146-2023-INPE/OGA', 2025, 2026, 16,
                'Compensación de la jornada laboral 24x48 - Lineamiento LI-001-2023-INPE-OGA',
                '2023-09-01'
            )
        """)
        id_resolucion = c.lastrowid
    else:
        id_resolucion = res[0]

    # Mapeo de empleados
    c.execute("SELECT codigo_servidor, id_empleado FROM empleados")
    emp_map = {r[0]: r[1] for r in c.fetchall()}

    # Data exacta del ANEXO 3 - REPORTE MENSUALIZADO 2026 (EP Mujeres Iquitos)
    # Formato: (CIP, DNI, APELLIDOS Y NOMBRES, {mes: dias}, obs)
    anexo3_data = [
        ("913371", {2: 1, 3: 2}, ""),
        ("102747", {2: 1, 3: 2, 4: 1}, ""),
        ("911381", {2: 1, 3: 1}, ""),
        ("910668", {4: 1}, ""),
        ("911664", {2: 1}, "DESPLAZADO A EP CHACHAPOYAS 13 DE FEBRERO"),
        ("912244", {}, ""),
        ("911382", {}, ""),
        ("910748", {2: 1, 3: 1, 4: 2}, ""),
        ("913429", {}, "DESPLAZADO EP VIRGEN DE FATIMA 17 DE FEBRERO"),
        ("912503", {2: 1, 3: 2, 4: 1}, ""),
        ("909967", {2: 1, 3: 1, 4: 1}, ""),
        ("910465", {2: 1, 3: 1, 4: 1}, ""),
        ("910332", {3: 1, 4: 2}, ""),
        ("104449", {2: 1, 3: 2, 4: 1}, ""),
        ("910869", {3: 1, 4: 1}, ""),
        ("908917", {}, ""),
        ("911387", {2: 1, 3: 1, 4: 2}, ""),
        ("910940", {2: 1, 3: 1, 4: 2}, ""),
        ("910945", {3: 1}, ""),
        ("910396", {4: 1}, ""),
        ("009881", {2: 1, 3: 1, 4: 2}, ""),
        ("911662", {2: 1, 3: 2, 4: 1}, "")
    ]

    print("Inicializando saldos y solicitudes históricas del Anexo 3...")

    # Limpiar solicitudes existentes si se reejecuta para evitar duplicados
    c.execute("DELETE FROM solicitudes_compensacion WHERE anio_goce = 2026")
    c.execute("DELETE FROM saldos_compensacion WHERE anio_goce = 2026")

    for cip, meses_dict, obs in anexo3_data:
        if cip not in emp_map:
            print(f"Alerta: CIP {cip} no encontrado.")
            continue
        emp_id = emp_map[cip]
        total_usados = sum(meses_dict.values())
        dias_asignados = 16
        dias_disponibles = dias_asignados - total_usados

        # Insertar saldo
        c.execute("""
            INSERT INTO saldos_compensacion (
                id_empleado, id_resolucion, anio_goce, dias_asignados, dias_utilizados, dias_disponibles, observaciones
            ) VALUES (?, ?, 2026, ?, ?, ?, ?)
        """, (emp_id, id_resolucion, dias_asignados, total_usados, dias_disponibles, obs))

        # Insertar solicitudes mes a mes (generando fechas representativas del mes según el anexo)
        for mes, cantidad in meses_dict.items():
            for i in range(cantidad):
                dia = 10 + (i * 5)
                fecha_comp = f"2026-{mes:02d}-{dia:02d}"
                c.execute("""
                    INSERT INTO solicitudes_compensacion (
                        id_empleado, anio_goce, mes, fecha_solicitud, fecha_compensacion,
                        dias_compensados, jefe_inmediato, especialista_personal, estado, observaciones
                    ) VALUES (?, 2026, ?, ?, ?, 1, 'AUTORIZADO', 'CONFORME', 'APROBADO', ?)
                """, (emp_id, mes, f"2026-{mes:02d}-01", fecha_comp, f"Anexo 3 Oficial - {obs}"))

    # También asegurar saldo para los demás empleados de seguridad 24x48 que no hayan gozado aún
    c.execute("""
        SELECT DISTINCT a.id_empleado 
        FROM asistencia_mensual_personal a
        WHERE a.horario_laboral LIKE '%24%'
          AND a.id_empleado NOT IN (SELECT id_empleado FROM saldos_compensacion WHERE anio_goce = 2026)
    """)
    otros_24x48 = c.fetchall()
    for row in otros_24x48:
        emp_id = row[0]
        c.execute("""
            INSERT INTO saldos_compensacion (
                id_empleado, id_resolucion, anio_goce, dias_asignados, dias_utilizados, dias_disponibles, observaciones
            ) VALUES (?, ?, 2026, 16, 0, 16, 'Jornada 24x48 sin consumos registrados')
        """, (emp_id, id_resolucion))

    conn.commit()
    conn.close()
    print("¡Base de datos de compensaciones (Lineamiento LI-001-2023-INPE-OGA) inicializada con éxito!")

if __name__ == "__main__":
    init_compensaciones_db()
