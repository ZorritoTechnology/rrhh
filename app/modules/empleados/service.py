from typing import List, Dict, Any, Optional
from app.modules.empleados.repository import EmpleadoRepository
from app.modules.empleados.models import EmpleadoCreate

class EmpleadoService:
    @staticmethod
    def listar_personal() -> List[Dict[str, Any]]:
        return EmpleadoRepository.get_all()

    @staticmethod
    def registrar_empleado(datos: EmpleadoCreate) -> int:
        existente = EmpleadoRepository.get_by_codigo(datos.codigo_servidor)
        if existente:
            raise ValueError(f"El servidor con código {datos.codigo_servidor} ya se encuentra registrado.")
        return EmpleadoRepository.create(datos)

    @staticmethod
    def contar_empleados() -> int:
        return EmpleadoRepository.count_total()
