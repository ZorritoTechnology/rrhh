from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class TipoNovedad(str, Enum):
    TARDANZA = "tardanza"
    PERMISO = "permiso"
    INASISTENCIA = "inasistencia"
    LICENCIA = "licencia"
    VACACION = "vacacion"
    DESPLAZAMIENTO = "desplazamiento"

class NovedadCreate(BaseModel):
    anio: int = Field(..., ge=2020, le=2030)
    mes: int = Field(..., ge=1, le=12)
    id_empleado: int = Field(..., ge=1)
    tipo_novedad: TipoNovedad
    cantidad: int = Field(1, ge=0)
    fecha_inicio: Optional[str] = None
    fecha_termino: Optional[str] = None
    fechas_detalle: Optional[str] = None
    tipo_licencia: Optional[str] = None
    entidad: Optional[str] = None
    area_destino: Optional[str] = None
    cargo_funcion: Optional[str] = None
    observaciones: Optional[str] = None
    periodo: Optional[str] = "2025-2026"
