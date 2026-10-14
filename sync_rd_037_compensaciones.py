import sqlite3

def sync_rd_037():
    conn = sqlite3.connect('rrhh_control.db')
    c = conn.cursor()

    # 1. Registrar o actualizar la Resolución Directoral N° 037-2026-INPE/ORNOSM
    c.execute("""
        INSERT INTO resoluciones_compensacion (
            numero_resolucion, anio_generado, anio_goce, dias_maximos_anual, descripcion, fecha_emision
        ) VALUES (
            'RD N° 037-2026-INPE/ORNOSM', 2025, 2026, 16,
            'Aprobación con eficacia anticipada del consolidado de programación anual de uso físico de compensación 24x48 (Anexo N° 01) - ORNOSM',
            '2026-02-06'
        )
    """)
    id_resolucion = c.lastrowid
    print(f"Resolución N° 037-2026 registrada con ID: {id_resolucion}")

    # 2. Lista oficial de los 23 servidores de EP Mujeres de Iquitos según el Anexo N° 01 (págs. 19-20 de la RD N° 037-2026)
    rd_037_personal = [
        ("BARDALES LOZANO AMBAR GRECIA TAMARA", 10),
        ("CANALES PAREDES ADELA ISABEL", 10),
        ("CARO SILVA FRANK REDI", 7),
        ("CASTILLO SOLIS DALIA MILAGROS", 11),
        ("CAVERO DIAZ ANGEL GABRIEL", 12),
        ("CHUQUIVAL RODRIGUEZ EDINSON", 9),
        ("CULQUI RENGIFO CLARA URSULA PATRICIA", 11),
        ("FLORES CARDENAS FRANCO CHRISTOPHER", 12),
        ("GOLAC ICAHUATE VICTOR ELVIS", 2),
        ("GUEVARA CASTILLO MICHAEL STEFANNY", 4),
        ("LOMAS ROMERO MONICA ANGELICA", 14),
        ("MANIHUARI VASQUEZ ALEXANDER", 12),
        ("MELENDEZ AMASIFUEN MAILITH", 8),
        ("MENDOZA ROJAS JORGE ENRIQUE", 4),
        ("NUÑEZ GONGORA RALF FRANCOIS", 8),
        ("OLANO SALAZAR CARLOS ALBERTO", 5),
        ("PANDURO PARANA LLOYSI LLERLITA", 12),
        ("PARANO OROCHE BRIGITTE", 14),
        ("PIÑA GONGORA CRISTIAN", 14),
        ("SANDY DEL CASTILLO DELIA ANITA", 10),
        ("SOLSOL FONSECA ADRIAN ALFREDO", 9),
        ("TEJADA ZUÑIGA CELIA YENNI", 11),
        ("VALLE SANCHEZ EYLIN", 14)
    ]

    # Verificar si GOLAC y MENDOZA existen en empleados, si no, insertarlos
    for nom, dias in [("GOLAC ICAHUATE VICTOR ELVIS", 2), ("MENDOZA ROJAS JORGE ENRIQUE", 4)]:
        c.execute("SELECT id_empleado FROM empleados WHERE apellidos_nombres LIKE ?", (f"%{nom}%",))
        row = c.fetchone()
        if not row:
            # Insertar empleado básico
            cip_placeholder = "919901" if "GOLAC" in nom else "919902"
            c.execute("""
                INSERT INTO empleados (
                    codigo_servidor, apellidos_nombres, area_clasificacion, cargo_funcion,
                    horario_laboral, estado_laboral, regimen_nombre, nivel
                ) VALUES (?, ?, 'SEG', 'AGENTE DE SEGURIDAD', '24 x 48', 'ACTIVO', 'Ley N° 29709', 'T1')
            """, (cip_placeholder, nom))
            print(f"Insertado nuevo servidor en EP Mujeres Iquitos: {nom} (CIP provisional {cip_placeholder})")

    # 3. Limpiar saldos previos de 2026 para reasignar con la resolución oficial
    c.execute("DELETE FROM saldos_compensacion WHERE anio_goce = 2026")

    # 4. Asignar los saldos exactos de la RD N° 037-2026
    c.execute("SELECT id_empleado, codigo_servidor, apellidos_nombres FROM empleados")
    todos = c.fetchall()

    asignados_count = 0
    for nom_oficial, dias_rd in rd_037_personal:
        id_emp = None
        for id_e, cip, nom_e in todos:
            # Comparación robusta
            if nom_oficial in nom_e or nom_e in nom_oficial:
                id_emp = id_e
                break
            # Match por los dos primeros apellidos
            partes = nom_oficial.split()
            if len(partes) >= 2 and f"{partes[0]} {partes[1]}" in nom_e:
                id_emp = id_e
                break

        if id_emp:
            # Calcular si ya tiene solicitudes aprobadas en 2026
            c.execute("""
                SELECT COALESCE(SUM(COALESCE(dias_solicitados, dias_compensados, 1)), 0)
                FROM solicitudes_compensacion
                WHERE id_empleado = ? AND anio_goce = 2026 AND estado = 'APROBADO'
            """, (id_emp,))
            utilizados = c.fetchone()[0]
            disponibles = max(0, dias_rd - utilizados)

            c.execute("""
                INSERT INTO saldos_compensacion (
                    id_empleado, id_resolucion, anio_goce, dias_asignados, dias_utilizados, dias_disponibles, observaciones
                ) VALUES (?, ?, 2026, ?, ?, ?, 'Asignado según RD N° 037-2026-INPE/ORNOSM')
            """, (id_emp, id_resolucion, dias_rd, utilizados, disponibles))
            asignados_count += 1
            print(f"  [OK] {nom_oficial}: {dias_rd} días asignados (utilizados: {utilizados}, disponibles: {disponibles})")
        else:
            print(f"  [ALERTA] No se encontró en DB: {nom_oficial}")

    print(f"\nTotal servidores con saldo RD N° 037-2026 asignado: {asignados_count} de {len(rd_037_personal)}")

    # 5. Asegurar que NINGÚN empleado de Tratamiento o Administrativo tenga saldo en saldos_compensacion
    c.execute("""
        DELETE FROM saldos_compensacion 
        WHERE id_empleado IN (
            SELECT id_empleado FROM empleados 
            WHERE area_clasificacion IN ('TRA', 'ADM') 
               OR horario_laboral NOT LIKE '%24%'
        )
    """)
    print("Limpieza completada: Ningún trabajador de TRA o ADM posee saldos_compensacion.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    sync_rd_037()
