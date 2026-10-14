import sqlite3

def init_sanciones():
    conn = sqlite3.connect('rrhh_control.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS empleados_sanciones (
        id_sancion_legajo INTEGER PRIMARY KEY AUTOINCREMENT,
        id_empleado INTEGER NOT NULL,
        tipo_sancion VARCHAR(100) NOT NULL,
        documento_resolucion VARCHAR(250) NOT NULL,
        fecha_resolucion DATE,
        fecha_inicio DATE,
        fecha_fin DATE,
        dias_sancion INTEGER DEFAULT 0,
        motivo_falta TEXT,
        estado_sancion VARCHAR(50) DEFAULT 'EJECUTADA',
        tiempo_que_resuelve VARCHAR(100),
        observaciones TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_empleado) REFERENCES empleados (id_empleado)
    )
    """)

    # Sincronizar las sanciones existentes en reporte_sanciones a empleados_sanciones si no están
    cur.execute("SELECT id_empleado, tipo_sancion, fecha_inicio, fecha_termino, dias, tiempo_que_resuelve, resolucion_documento, observaciones FROM reporte_sanciones")
    sanciones_existentes = cur.fetchall()

    registrados = 0
    for s in sanciones_existentes:
        e_id, tipo, f_ini, f_fin, dias, tiempo_res, resol, obs = s
        cur.execute("""
            SELECT id_sancion_legajo FROM empleados_sanciones
            WHERE id_empleado = ? AND documento_resolucion = ? AND fecha_inicio = ?
        """, (e_id, resol, f_ini))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO empleados_sanciones (
                    id_empleado, tipo_sancion, documento_resolucion,
                    fecha_inicio, fecha_fin, dias_sancion,
                    tiempo_que_resuelve, estado_sancion, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'EJECUTADA', ?)
            """, (e_id, tipo, resol, f_ini, f_fin, dias, tiempo_res, obs))
            registrados += 1

    conn.commit()
    print(f"Tabla empleados_sanciones inicializada. Sanciones sincronizadas: {registrados}")
    conn.close()

if __name__ == '__main__':
    init_sanciones()
