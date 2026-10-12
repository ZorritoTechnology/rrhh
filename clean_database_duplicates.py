import sqlite3

def clean_duplicates(db_path="rrhh_control.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    tables = [
        ("reporte_vacaciones", "id_vacacion"),
        ("reporte_licencias", "id_licencia"),
        ("reporte_permisos", "id_permiso"),
        ("reporte_tardanzas", "id_tardanza"),
        ("reporte_inasistencias", "id_inasistencia"),
        ("reporte_funcionarios", "id_funcionario"),
        ("reporte_desplazamientos", "id_desplazamiento"),
        ("reporte_sanciones", "id_sancion"),
        ("reporte_renuncias", "id_renuncia"),
        ("reporte_reincorporaciones", "id_reincorporacion"),
        ("asistencia_mensual_personal", "id_asistencia"),
        ("reporte_no_registrados", "id_no_reg")
    ]

    total_eliminados = 0

    for table, pk in tables:
        # Obtener columnas excepto el ID primario
        cur.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cur.fetchall() if c[1] != pk]
        cols_str = ", ".join(cols)

        # Encontrar y eliminar duplicados manteniendo el ID más bajo
        sql_dedup = f"""
            DELETE FROM {table}
            WHERE {pk} NOT IN (
                SELECT MIN({pk})
                FROM {table}
                GROUP BY {cols_str}
            )
        """
        cur.execute(sql_dedup)
        eliminados = cur.rowcount
        if eliminados > 0:
            print(f"[{table}] Se eliminaron {eliminados} registros duplicados.")
            total_eliminados += eliminados

    conn.commit()
    conn.close()
    print(f"\nLimpieza completada. Total de registros duplicados depurados: {total_eliminados}")

if __name__ == "__main__":
    clean_duplicates()
