from pydantic import BaseModel, Field
from typing import Optional

class SaldoVacacional(BaseModel):
    id_empleado: int
    codigo_servidor: str
    apellidos_nombres: str
    dias_consumidos: int = 0
    dias_derecho: int = 30
    dias_saldo: int = 30
    desglose: str = "-"
    estado: str = "SIN SALIDAS"
    excedido: bool = False
    observaciones: str = ""

class SolicitudVacacionesCreate(BaseModel):
    id_empleado: int
    periodo: str = Field(..., example="2025-2026")
    fecha_inicio: str
    fecha_termino: str
    dias_solicitados: int = Field(..., ge=1, le=30)
    tipo_uso: str = "GOZADO"
    observaciones: Optional[str] = None
