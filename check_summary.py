import sqlite3

def check_summary(db_path="rrhh_control.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("=== RESUMEN DE LA BASE DE DATOS RRHH ===")
    
    cur.execute("SELECT COUNT(*) FROM empleados")
    print(f"Total empleados registrados: {cur.fetchone()[0]}")
    
    cur.execute("SELECT anio, mes, total_trabajadores, observaciones_generales FROM reportes_cierre_mensual ORDER BY anio, mes")
    print("\nMeses Reportados:")
    meses_nombres = {9: "Setiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    for anio, mes, total, obs in cur.fetchall():
        print(f" - {meses_nombres.get(mes, mes)} {anio}: {total} trabajadores | {obs}")
        
    cur.execute("SELECT COUNT(*) FROM reporte_licencias")
    print(f"\nTotal licencias cargadas (2025): {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM reporte_vacaciones")
    print(f"Total vacaciones programadas/tomadas (2025): {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM reporte_permisos")
    print(f"Total permisos particulares registrados: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM reporte_tardanzas")
    print(f"Total tardanzas registradas: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM reporte_inasistencias")
    print(f"Total inasistencias injustificadas registradas: {cur.fetchone()[0]}")
    
    cur.execute("SELECT anio, estado, total_meses_reportados, fecha_cierre, observaciones FROM cierres_anuales")
    print("\nCierres Anuales Oficiales:")
    for row in cur.fetchall():
        print(f" - Año {row[0]}: Estado '{row[1]}' | Meses computados: {row[2]} | Obs: {row[4]}")
        
    conn.close()

if __name__ == "__main__":
    check_summary()

