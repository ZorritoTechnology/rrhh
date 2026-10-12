from typing import List, Optional, Dict, Any
from app.core.database import get_connection, get_db_cursor
from app.modules.empleados.models import EmpleadoCreate, EmpleadoOut

class EmpleadoRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_empleado, codigo_servidor, dni, apellidos_nombres, created_at 
                FROM empleados 
                ORDER BY apellidos_nombres ASC
            """)
            return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def get_by_id(id_empleado: int) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_empleado, codigo_servidor, dni, apellidos_nombres, created_at 
                FROM empleados 
                WHERE id_empleado = ?
            """, (id_empleado,))
            row = cur.fetchone()
            return dict(row) if row else None

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
    def count_total() -> int:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM empleados")
            return cur.fetchone()[0]
