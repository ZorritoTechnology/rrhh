from app.core.database import get_connection

def init_vacaciones_tables():
    """Crea las tablas de saldos y solicitudes de vacaciones si no existen."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Saldo de vacaciones por período anual para cada servidor
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saldos_vacaciones (
            id_saldo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empleado INTEGER NOT NULL,
            periodo VARCHAR(50) NOT NULL,            -- Ej: '2025-2026'
            dias_derecho INTEGER DEFAULT 30,        -- Según directiva: 30 días calendario
            dias_consumidos INTEGER DEFAULT 0,
            dias_saldo INTEGER DEFAULT 30,
            estado VARCHAR(20) DEFAULT 'VIGENTE',   -- 'VIGENTE', 'AGOTADO', 'VENCIDO'
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
            UNIQUE (id_empleado, periodo)
        )
    """)
    
    # Solicitudes / Fraccionamiento de vacaciones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_vacaciones (
            id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empleado INTEGER NOT NULL,
            periodo VARCHAR(50) NOT NULL,
            fecha_inicio DATE NOT NULL,
            fecha_termino DATE NOT NULL,
            dias_solicitados INTEGER NOT NULL,
            estado VARCHAR(20) DEFAULT 'APROBADO',   -- 'PENDIENTE', 'APROBADO', 'RECHAZADO'
            tipo_uso VARCHAR(50) DEFAULT 'GOZADO',  -- 'GOZADO', 'ADELANTO', 'FRACCIONAMIENTO'
            observaciones TEXT,
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
        )
    """)
    conn.commit()
    conn.close()

def obtener_saldo_empleado(id_empleado: int, periodo: str = "2025-2026"):
    """Consulta el saldo de vacaciones ganado y consumido por un servidor."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT dias_derecho, dias_consumidos, dias_saldo, estado 
        FROM saldos_vacaciones 
        WHERE id_empleado = ? AND periodo = ?
    """, (id_empleado, periodo))
    saldo = cur.fetchone()
    
    if not saldo:
        # Inicializar en 30 días si es nuevo
        cur.execute("""
            INSERT INTO saldos_vacaciones (id_empleado, periodo, dias_derecho, dias_consumidos, dias_saldo)
            VALUES (?, ?, 30, 0, 30)
        """, (id_empleado, periodo))
        conn.commit()
        saldo = {"dias_derecho": 30, "dias_consumidos": 0, "dias_saldo": 30, "estado": "VIGENTE"}
    else:
        saldo = dict(saldo)
        
    conn.close()
    return saldo

init_vacaciones_tables()

