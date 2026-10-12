from app.core.database import get_connection

def get_personal_activo():
    """Retorna la lista de empleados registrados con su código y DNI."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_empleado, codigo_servidor, dni, apellidos_nombres FROM empleados ORDER BY apellidos_nombres")
    personal = cur.fetchall()
    conn.close()
    return personal

def registrar_o_obtener_reporte_mensual(anio: int, mes: int, id_establecimiento: int = 722, id_responsable: int = 1, obs: str = ""):
    """Crea o retorna el ID del reporte mensual para el año y mes indicados."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_reporte, total_trabajadores, observaciones_generales 
        FROM reportes_cierre_mensual 
        WHERE anio = ? AND mes = ? AND id_establecimiento = ?
    """, (anio, mes, id_establecimiento))
    fila = cur.fetchone()
    
    if fila:
        reporte_id = fila["id_reporte"]
    else:
        # Contar empleados actuales
        cur.execute("SELECT COUNT(*) FROM empleados")
        total = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO reportes_cierre_mensual (anio, mes, id_establecimiento, id_responsable, total_trabajadores, observaciones_generales)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (anio, mes, id_establecimiento, id_responsable, total, obs or f"Reporte de Asistencia {mes:02d}/{anio}"))
        conn.commit()
        reporte_id = cur.lastrowid
        
    conn.close()
    return reporte_id

def registrar_novedad(tipo_novedad: str, id_reporte: int, id_empleado: int, datos: dict):
    """
    Registra una novedad de asistencia para el mes en curso.
    tipo_novedad: 'tardanza', 'permiso', 'inasistencia', 'licencia', 'vacacion'
    """
    conn = get_connection()
    cur = conn.cursor()
    
    if tipo_novedad == "tardanza":
        cur.execute("""
            INSERT INTO reporte_tardanzas (id_reporte, id_empleado, minutos, observaciones)
            VALUES (?, ?, ?, ?)
        """, (id_reporte, id_empleado, datos.get("minutos", 0), datos.get("observaciones", "")))
        
    elif tipo_novedad == "permiso":
        cur.execute("""
            INSERT INTO reporte_permisos (id_reporte, id_empleado, minutos, observaciones)
            VALUES (?, ?, ?, ?)
        """, (id_reporte, id_empleado, datos.get("minutos", 0), datos.get("observaciones", "")))
        
    elif tipo_novedad == "inasistencia":
        cur.execute("""
            INSERT INTO reporte_inasistencias (id_reporte, id_empleado, dias, fechas_detalle, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (id_reporte, id_empleado, datos.get("dias", 1), datos.get("fechas_detalle", ""), datos.get("observaciones", "")))
        
    elif tipo_novedad == "licencia":
        cur.execute("""
            INSERT INTO reporte_licencias (id_reporte, id_empleado, tipo, entidad, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_reporte, id_empleado, datos.get("tipo", "ENFERMEDAD"), datos.get("entidad", "ESSALUD"),
              datos.get("fecha_inicio"), datos.get("fecha_termino"), datos.get("dias", 1), datos.get("observaciones", "")))
              
    elif tipo_novedad == "vacacion":
        cur.execute("""
            INSERT INTO reporte_vacaciones (id_reporte, id_empleado, periodo, fecha_inicio, fecha_termino, dias, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_reporte, id_empleado, datos.get("periodo", "2026"),
              datos.get("fecha_inicio"), datos.get("fecha_termino"), datos.get("dias", 1), datos.get("observaciones", "")))
              
    elif tipo_novedad == "desplazamiento":
        cur.execute("""
            INSERT INTO reporte_desplazamientos (id_reporte, id_empleado, area, cargo_funcion, fecha_desplazamiento, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_reporte, id_empleado, datos.get("area", ""), datos.get("cargo_funcion", ""),
              datos.get("fecha_inicio"), datos.get("observaciones", "")))
              
    conn.commit()
    conn.close()
    return True

def obtener_resumen_mes(anio: int, mes: int, id_establecimiento: int = 722):
    """Retorna todas las novedades cargadas para un mes específico."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_reporte FROM reportes_cierre_mensual WHERE anio=? AND mes=? AND id_establecimiento=?", (anio, mes, id_establecimiento))
    rep = cur.fetchone()
    if not rep:
        conn.close()
        return None
    
    rep_id = rep["id_reporte"]
    
    # Tardanzas
    cur.execute("""
        SELECT e.apellidos_nombres, e.codigo_servidor, t.minutos, t.observaciones 
        FROM reporte_tardanzas t JOIN empleados e ON t.id_empleado = e.id_empleado
        WHERE t.id_reporte = ?
    """, (rep_id,))
    tardanzas = [dict(r) for r in cur.fetchall()]
    
    # Permisos
    cur.execute("""
        SELECT e.apellidos_nombres, e.codigo_servidor, p.minutos, p.observaciones 
        FROM reporte_permisos p JOIN empleados e ON p.id_empleado = e.id_empleado
        WHERE p.id_reporte = ?
    """, (rep_id,))
    permisos = [dict(r) for r in cur.fetchall()]
    
    # Licencias
    cur.execute("""
        SELECT e.apellidos_nombres, e.codigo_servidor, l.tipo, l.entidad, l.fecha_inicio, l.fecha_termino, l.dias, l.observaciones 
        FROM reporte_licencias l JOIN empleados e ON l.id_empleado = e.id_empleado
        WHERE l.id_reporte = ?
    """, (rep_id,))
    licencias = [dict(r) for r in cur.fetchall()]
    
    # Vacaciones
    cur.execute("""
        SELECT e.apellidos_nombres, e.codigo_servidor, v.periodo, v.fecha_inicio, v.fecha_termino, v.dias, v.observaciones 
        FROM reporte_vacaciones v JOIN empleados e ON v.id_empleado = e.id_empleado
        WHERE v.id_reporte = ?
    """, (rep_id,))
    vacaciones = [dict(r) for r in cur.fetchall()]
    
    # Desplazamientos
    cur.execute("""
        SELECT e.apellidos_nombres, e.codigo_servidor, d.area, d.cargo_funcion, d.fecha_desplazamiento, d.observaciones
        FROM reporte_desplazamientos d JOIN empleados e ON d.id_empleado = e.id_empleado
        WHERE d.id_reporte = ?
    """, (rep_id,))
    desplazamientos = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return {
        "anio": anio,
        "mes": mes,
        "tardanzas": tardanzas,
        "permisos": permisos,
        "licencias": licencias,
        "vacaciones": vacaciones,
        "desplazamientos": desplazamientos
    }

