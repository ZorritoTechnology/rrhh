from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.modules.empleados.service import EmpleadoService
from app.modules.empleados.models import EmpleadoCreate

router = APIRouter(prefix="/empleados", tags=["Empleados"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def padron_empleados(request: Request, mensaje: str = None, error: str = None):
    personal = EmpleadoService.listar_personal()
    total = EmpleadoService.contar_empleados()
    return templates.TemplateResponse(
        request=request,
        name="empleados/padron.html",
        context={
            "personal": personal,
            "total": total,
            "mensaje": mensaje,
            "error": error
        }
    )

@router.post("/nuevo")
async def nuevo_empleado(
    codigo_servidor: str = Form(...),
    dni: str = Form(""),
    apellidos_nombres: str = Form(...)
):
    try:
        nuevo = EmpleadoCreate(
            codigo_servidor=codigo_servidor,
            dni=dni if dni.strip() else None,
            apellidos_nombres=apellidos_nombres
        )
        EmpleadoService.registrar_empleado(nuevo)
        return RedirectResponse(url="/empleados?mensaje=Servidor+registrado+exitosamente", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/empleados?error={str(e)}", status_code=303)
