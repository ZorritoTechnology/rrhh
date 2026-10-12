import sqlite3

def run_db_update():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    # 1. Agregar columna 'estado' a reportes_cierre_mensual si no existe
    cur.execute("PRAGMA table_info(reportes_cierre_mensual)")
    cols = [r[1] for r in cur.fetchall()]
    if "estado" not in cols:
        cur.execute("ALTER TABLE reportes_cierre_mensual ADD COLUMN estado VARCHAR(20) DEFAULT 'ABIERTO'")
        print("Columna 'estado' agregada a reportes_cierre_mensual.")

    # Marcar Enero como CERRADO
    cur.execute("UPDATE reportes_cierre_mensual SET estado = 'CERRADO' WHERE anio = 2026 AND mes = 1")
    conn.commit()
    conn.close()
    print("Base de datos actualizada con estados ABIERTO/CERRADO.")

if __name__ == "__main__":
    run_db_update()
