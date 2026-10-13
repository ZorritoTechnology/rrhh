from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.core.database import get_connection, get_db_cursor
from app.modules.empleados.models import EmpleadoCreate, EmpleadoOut

def calcular_tiempo_servicio(fecha_str: Optional[str]) -> Dict[str, Any]:
    if not fecha_str:
        return {"texto": "Sin registro", "anios": 0, "meses": 0, "dias": 0}
    try:
        f_ing = datetime.strptime(str(fecha_str)[:10], "%Y-%m-%d").date()
        hoy = date.today()
        if f_ing > hoy:
            return {"texto": "Fecha futura", "anios": 0, "meses": 0, "dias": 0}

        anios = hoy.year - f_ing.year
        meses = hoy.month - f_ing.month
        dias = hoy.day - f_ing.day

        if dias < 0:
            meses -= 1
            dias += 30
        if meses < 0:
            anios -= 1
            meses += 12

        partes = []
        if anios > 0:
            partes.append(f"{anios} año{'s' if anios != 1 else ''}")
        if meses > 0:
            partes.append(f"{meses} mes{'es' if meses != 1 else ''}")
        if not partes:
            partes.append(f"{max(0, dias)} días")

        return {
            "texto": ", ".join(partes),
            "anios": anios,
            "meses": meses,
            "dias": dias
        }
    except Exception:
        return {"texto": "No calculable", "anios": 0, "meses": 0, "dias": 0}

def calcular_ciclo_vacacional(fecha_str: Optional[str]) -> Dict[str, Any]:
    """
    Calcula el periodo vacacional generado a partir de la fecha de ingreso al INPE.
    Cada 12 meses continuos de labor efectiva genera 30 dias de descanso vacacional.
    """
    if not fecha_str:
        return {"periodo": "No asignado", "proximo_ciclo": "-", "dias_derecho": 30}
    try:
        f_ing = datetime.strptime(str(fecha_str)[:10], "%Y-%m-%d").date()
        hoy = date.today()
        # Periodo actual
        anio_inicio = hoy.year - 1 if (hoy.month, hoy.day) < (f_ing.month, f_ing.day) else hoy.year
        periodo = f"{anio_inicio}-{anio_inicio + 1}"

        # Proximo ciclo en que cumple un nuevo periodo
        proximo_anio = hoy.year if (hoy.month, hoy.day) < (f_ing.month, f_ing.day) else hoy.year + 1
        try:
            proxima_fecha = date(proximo_anio, f_ing.month, f_ing.day)
        except ValueError:
            proxima_fecha = date(proximo_anio, f_ing.month, 28)

        return {
            "periodo": periodo,
            "proximo_ciclo": proxima_fecha.strftime("%d/%m/%Y"),
            "dias_derecho": 30
        }
    except Exception:
        return {"periodo": "2025-2026", "proximo_ciclo": "-", "dias_derecho": 30}


class EmpleadoRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    id_empleado, codigo_servidor, dni, apellidos_nombres,
                    sexo, fecha_nacimiento, correo, id_regimen, regimen_nombre,
                    nivel, cargo_estructural, estado_laboral, modalidad_laboral,
                    direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                    horario_laboral, fecha_ingreso_eepp, resolucion_documento,
                    observaciones, fecha_ingreso_inpe, grupo_guardia_default, created_at
                FROM empleados 
                ORDER BY apellidos_nombres ASC
            """)
            filas = [dict(row) for row in cur.fetchall()]

            for emp in filas:
                emp["tiempo_servicio"] = calcular_tiempo_servicio(emp.get("fecha_ingreso_inpe"))
                emp["vacaciones_info"] = calcular_ciclo_vacacional(emp.get("fecha_ingreso_inpe"))
            return filas

    @staticmethod
    def get_by_id(id_empleado: int) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    id_empleado, codigo_servidor, dni, apellidos_nombres,
                    sexo, fecha_nacimiento, correo, id_regimen, regimen_nombre,
                    nivel, cargo_estructural, estado_laboral, modalidad_laboral,
                    direccion_oficina, jefatura_area, cargo_funcion, area_clasificacion,
                    horario_laboral, fecha_ingreso_eepp, resolucion_documento,
                    observaciones, fecha_ingreso_inpe, grupo_guardia_default, created_at
                FROM empleados 
                WHERE id_empleado = ?
            """, (id_empleado,))
            row = cur.fetchone()
            if not row:
                return None
            emp = dict(row)
            emp["tiempo_servicio"] = calcular_tiempo_servicio(emp.get("fecha_ingreso_inpe"))
            emp["vacaciones_info"] = calcular_ciclo_vacacional(emp.get("fecha_ingreso_inpe"))
            return emp

    @staticmethod
    def get_by_codigo(codigo_servidor: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_empleado, codigo_servidor, dni, apellidos_nombres, created_at 
                FROM empleados 
                WHERE codigo_servidor = ?
            """, (codigo_servidor,))
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(empleado: EmpleadoCreate) -> int:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO empleados (codigo_servidor, dni, apellidos_nombres)
                VALUES (?, ?, ?)
            """, (empleado.codigo_servidor.strip(), empleado.dni.strip() if empleado.dni else None, empleado.apellidos_nombres.strip().upper()))
            return cur.lastrowid

    @staticmethod
    def update(id_empleado: int, datos: Dict[str, Any]) -> bool:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE empleados SET
                    codigo_servidor = COALESCE(?, codigo_servidor),
                    dni = COALESCE(?, dni),
                    apellidos_nombres = COALESCE(?, apellidos_nombres),
                    sexo = COALESCE(?, sexo),
                    fecha_nacimiento = COALESCE(?, fecha_nacimiento),
                    correo = COALESCE(?, correo),
                    id_regimen = COALESCE(?, id_regimen),
                    regimen_nombre = COALESCE(?, regimen_nombre),
                    nivel = COALESCE(?, nivel),
                    cargo_estructural = COALESCE(?, cargo_estructural),
                    estado_laboral = COALESCE(?, estado_laboral),
                    modalidad_laboral = COALESCE(?, modalidad_laboral),
                    direccion_oficina = COALESCE(?, direccion_oficina),
                    jefatura_area = COALESCE(?, jefatura_area),
                    cargo_funcion = COALESCE(?, cargo_funcion),
                    area_clasificacion = COALESCE(?, area_clasificacion),
                    horario_laboral = COALESCE(?, horario_laboral),
                    fecha_ingreso_eepp = COALESCE(?, fecha_ingreso_eepp),
                    resolucion_documento = COALESCE(?, resolucion_documento),
                    observaciones = COALESCE(?, observaciones),
                    fecha_ingreso_inpe = COALESCE(?, fecha_ingreso_inpe)
                WHERE id_empleado = ?
            """, (
                datos.get("codigo_servidor"),
                datos.get("dni"),
                datos.get("apellidos_nombres"),
                datos.get("sexo"),
                datos.get("fecha_nacimiento"),
                datos.get("correo"),
                datos.get("id_regimen"),
                datos.get("regimen_nombre"),
                datos.get("nivel"),
                datos.get("cargo_estructural"),
                datos.get("estado_laboral"),
                datos.get("modalidad_laboral"),
                datos.get("direccion_oficina"),
                datos.get("jefatura_area"),
                datos.get("cargo_funcion"),
                datos.get("area_clasificacion"),
                datos.get("horario_laboral"),
                datos.get("fecha_ingreso_eepp"),
                datos.get("resolucion_documento"),
                datos.get("observaciones"),
                datos.get("fecha_ingreso_inpe"),
                id_empleado
            ))
            conn.commit()
            return True

    @staticmethod
    def count_total() -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM empleados")
            return cur.fetchone()[0]
