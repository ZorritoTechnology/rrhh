import sqlite3
from app.modules.compensacion.service import CompensacionService

def clean_fake_data():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    print("=== PASO 1: ELIMINAR REGISTRO ESPURIO DE DESPLAZAMIENTO ===")
    cur.execute("SELECT id_desplazamiento, id_empleado, tipo_movimiento, fecha_desplazamiento, observaciones FROM desplazamientos_personal WHERE id_desplazamiento = 1")
    row_desp = cur.fetchone()
    print("Registro a eliminar:", row_desp)
    cur.execute("DELETE FROM desplazamientos_personal WHERE id_desplazamiento = 1")
    print(f"Eliminado id_desplazamiento = 1. Filas afectadas: {cur.rowcount}")

    print("\n=== PASO 2: LIMPIAR SALDOS_COMPENSACION PARA VALLE SANCHEZ EYLIN ===")
    cur.execute("""
        UPDATE saldos_compensacion
        SET dias_asignados = 16,
            dias_utilizados = 0,
            dias_disponibles = 16,
            observaciones = ''
        WHERE id_empleado = 25 AND anio_goce = 2026
    """)
    print(f"Actualizado saldos_compensacion para empleado 25. Filas afectadas: {cur.rowcount}")

    print("\n=== PASO 3: CONFIRMAR DATOS DEL LEGAJO EN EMPLEADOS ===")
    cur.execute("""
        UPDATE empleados
        SET fecha_ingreso_eepp = '2024-01-29',
            fecha_ingreso_inpe = '2023-12-30',
            estado_laboral = 'ACTIVO'
        WHERE id_empleado = 25
    """)
    print("Legajo oficial confirmado para empleado 25 (Ingreso EEPP: 2024-01-29).")

    conn.commit()
    conn.close()

    print("\n=== PASO 4: RECALCULAR Y GUARDAR ENERO Y FEBRERO 2026 ===")
    for mes in [1, 2]:
        res = CompensacionService.calcular_anexo2_mes(2026, mes)
        CompensacionService.guardar_anexo2_en_db(2026, mes, res["grupos"])
        print(f"Mes {mes}/2026 recalculado y guardado en BD exitosamente.")

        # Verificar marcas de Valle Sanchez
        for g in res["grupos"]:
            for e in g["empleados"]:
                if "VALLE SANCHEZ" in e["apellidos_nombres"]:
                    marks = [e["dias_calculados"][d] for d in range(1, len(e["dias_calculados"]) + 1)]
                    print(f"  Mes {mes} - {e['apellidos_nombres']}: dias_exceso={e['dias_exceso']}, desp_texto='{e.get('desplazamiento_texto')}'")
                    print(f"    Primeros 15 días: {' '.join(marks[:15])}")
                    print(f"    Resto de días:    {' '.join(marks[15:])}")

if __name__ == "__main__":
    clean_fake_data()
