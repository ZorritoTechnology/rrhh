import sqlite3

def run_migration(db_path="rrhh_control.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Catálogos Normalizados
    cur.execute("""
    CREATE TABLE IF NOT EXISTS catalogo_tipos_sancion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) UNIQUE NOT NULL,
        descripcion TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS catalogo_tipos_licencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) UNIQUE NOT NULL,
        descripcion TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS catalogo_entidades_licencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(50) UNIQUE NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS catalogo_niveles_directivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo VARCHAR(10) UNIQUE NOT NULL,
        regimen VARCHAR(50) NOT NULL
    );
    """)

    # Sembrar catálogos oficiales
    sanciones = [
        ("SUSPENSIÓN", "Suspensión temporal de labores sin goce de haber"),
        ("AMONESTACIÓN ESCRITA", "Amonestación con llamada de atención escrita"),
        ("CESE TEMPORAL", "Cese temporal en el ejercicio de funciones"),
        ("DESTITUCIÓN", "Destitución definitiva de la institución"),
        ("INHABILITACIÓN", "Inhabilitación para el ejercicio de función pública")
    ]
    for s, desc in sanciones:
        cur.execute("INSERT OR IGNORE INTO catalogo_tipos_sancion (nombre, descripcion) VALUES (?, ?)", (s, desc))

    licencias = [
        ("ENFERMEDAD", "Licencia médica o descanso por salud"),
        ("MATERNIDAD", "Licencia por maternidad prenatal y postnatal (98 días)"),
        ("PATERNIDAD", "Licencia remunerada por paternidad"),
        ("ONOMÁSTICO", "Día libre por fecha de onomástico"),
        ("PARTICULAR", "Licencia por motivos estrictamente particulares"),
        ("FALLECIMIENTO", "Licencia por luto / fallecimiento de familiar directo"),
        ("SINDICAL", "Licencia por representación o dirigencia sindical"),
        ("D.U. 026-20", "Licencia excepcional Decreto de Urgencia 026-2020"),
        ("CAPACITACIÓN", "Licencia por capacitación o perfeccionamiento oficial")
    ]
    for l, desc in licencias:
        cur.execute("INSERT OR IGNORE INTO catalogo_tipos_licencia (nombre, descripcion) VALUES (?, ?)", (l, desc))

    entidades = ["ESSALUD", "PARTICULAR", "INPE", "MINSA", "CLINICA PRIVADA"]
    for ent in entidades:
        cur.execute("INSERT OR IGNORE INTO catalogo_entidades_licencia (nombre) VALUES (?)", (ent,))

    niveles_dir = [
        ("F-1", "D.L. 276"), ("F-2", "D.L. 276"), ("F-3", "D.L. 276"), ("F-4", "D.L. 276"),
        ("F-5", "D.L. 276"), ("F-6", "D.L. 276"),
        ("S3", "Ley 29709"), ("S4", "Ley 29709"), ("S5", "Ley 29709")
    ]
    for cod, reg in niveles_dir:
        cur.execute("INSERT OR IGNORE INTO catalogo_niveles_directivos (codigo, regimen) VALUES (?, ?)", (cod, reg))

    # Asegurar que todas las 12 tablas oficiales del libro mensual existan
    cur.execute("""
    CREATE TABLE IF NOT EXISTS asistencia_mensual_personal (
        id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        id_regimen INTEGER,
        nivel VARCHAR(20),
        cargo_estructural VARCHAR(200),
        estado_laboral VARCHAR(50) DEFAULT 'ACTIVO',
        modalidad_laboral VARCHAR(50) DEFAULT 'PRESENCIAL',
        direccion_oficina VARCHAR(100),
        jefatura_area VARCHAR(100),
        cargo_funcion VARCHAR(100),
        area_clasificacion VARCHAR(10),
        horario_laboral VARCHAR(50),
        fecha_ingreso_eepp DATE,
        resolucion_documento VARCHAR(250),
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
        FOREIGN KEY (id_regimen) REFERENCES regimenes_laborales(id_regimen)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_funcionarios (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        cargo_funcion VARCHAR(100) NOT NULL,
        nivel VARCHAR(20),
        fecha_inicio_funciones DATE,
        resolucion_documento VARCHAR(250),
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_sanciones (
        id_sancion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        tipo_sancion VARCHAR(100) NOT NULL,
        fecha_inicio DATE,
        fecha_termino DATE,
        dias INTEGER,
        tiempo_que_resuelve VARCHAR(100),
        resolucion_documento VARCHAR(250),
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_renuncias (
        id_renuncia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        a_partir_del DATE,
        carta_fecha DATE,
        fecha_recepcion DATE,
        motivos TEXT,
        ultimo_dia_laborado DATE,
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_reincorporaciones (
        id_reincorporacion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        fecha_inicio_inactividad DATE,
        motivo_inactividad TEXT,
        fecha_reincorporacion DATE,
        motivo_reincorporacion TEXT,
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_desplazamientos (
        id_desplazamiento INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        id_establecimiento_origen INTEGER,
        id_establecimiento_destino INTEGER,
        area VARCHAR(100),
        cargo_funcion VARCHAR(100),
        fecha_desplazamiento DATE,
        documento_resolucion VARCHAR(250),
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_licencias (
        id_licencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        entidad VARCHAR(50),
        fecha_inicio DATE NOT NULL,
        fecha_termino DATE NOT NULL,
        dias INTEGER NOT NULL,
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_vacaciones (
        id_vacacion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        periodo VARCHAR(50),
        fecha_inicio DATE NOT NULL,
        fecha_termino DATE NOT NULL,
        dias INTEGER NOT NULL,
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_tardanzas (
        id_tardanza INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        minutos INTEGER NOT NULL,
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_permisos (
        id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        minutos INTEGER NOT NULL,
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_inasistencias (
        id_inasistencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        id_empleado INTEGER NOT NULL,
        dias INTEGER NOT NULL,
        fechas_detalle VARCHAR(255),
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reporte_no_registrados (
        id_no_reg INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER NOT NULL,
        dni VARCHAR(15),
        apellidos_nombres VARCHAR(200),
        regimen VARCHAR(50),
        cargo_funcion VARCHAR(100),
        area VARCHAR(100),
        fecha_ingreso DATE,
        documento VARCHAR(250),
        observaciones TEXT,
        FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print("Migración de tablas y catálogos completada con éxito.")

if __name__ == "__main__":
    run_migration()
