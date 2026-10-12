import sqlite3

def init_db(db_path="rrhh_control.db"):
    with open("schema.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    # Adaptar tipos PostgreSQL (SERIAL) a SQLite (INTEGER AUTOINCREMENT)
    sqlite_script = sql_script.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(sqlite_script)
    conn.commit()
    print(f"Base de datos inicializada exitosamente en '{db_path}'.")
    
    # Cargar datos base de ejemplo extraídos de los reportes
    cursor.execute("INSERT OR IGNORE INTO oficinas_regionales (id_or, nombre) VALUES (?, ?)", 
                   (700, "OFICINA REGIONAL NOR ORIENTE"))
    cursor.execute("INSERT OR IGNORE INTO establecimientos (id_establecimiento, id_or, nombre) VALUES (?, ?, ?)", 
                   (722, 700, "EP. MUJERES IQUITOS"))
    
    # Responsable predeterminado (Directora Santos Delcia Zapata Roque)
    cursor.execute("INSERT OR IGNORE INTO empleados (codigo_servidor, dni, apellidos_nombres) VALUES (?, ?, ?)",
                   ("099132", "07032370", "ZAPATA ROQUE SANTOS DELCIA"))
    
    conn.commit()
    conn.close()
    print("Datos maestros iniciales insertados.")

if __name__ == "__main__":
    init_db()

