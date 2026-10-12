from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.modules.reportes.service import ReportesService

router = APIRouter(prefix="/reportes", tags=["Reportes"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def catalogo_anexos(request: Request):
    anexos = ReportesService.get_catalogo_anexos()
    return templates.TemplateResponse(
        request=request,
        name="reportes/anexos.html",
        context={
            "anexos": anexos
        }
    )

@router.get("/anexo/{id_anexo}", response_class=HTMLResponse)
async def ver_anexo(request: Request, id_anexo: int, anio: int = 2026, mes: int = 1):
    catalogo = ReportesService.get_catalogo_anexos()
    anexo_info = next((a for a in catalogo if a["id"] == id_anexo), None)
    detalle = ReportesService.obtener_datos_anexo(id_anexo=id_anexo, anio=anio, mes=mes)
    
    return templates.TemplateResponse(
        request=request,
        name="reportes/detalle_anexo.html",
        context={
            "anexo": anexo_info,
            "detalle": detalle,
            "anio": anio,
            "mes": mes
        }
    )
