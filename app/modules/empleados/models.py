from pydantic import BaseModel, Field
from typing import Optional

class EmpleadoBase(BaseModel):
    codigo_servidor: str = Field(..., min_length=4, max_length=20, description="Código de servidor (ej: 099132)")
    dni: Optional[str] = Field(None, min_length=8, max_length=15, description="Número de DNI")
    apellidos_nombres: str = Field(..., min_length=3, max_length=200, description="Apellidos y Nombres completos")

class EmpleadoCreate(EmpleadoBase):
    pass

class EmpleadoOut(EmpleadoBase):
    id_empleado: int
    created_at: Optional[str] = None
    regimen_codigo: Optional[str] = None
    cargo: Optional[str] = None
