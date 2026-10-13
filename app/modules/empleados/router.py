from typing import Optional
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.modules.empleados.service import EmpleadoService
from app.modules.empleados.models import EmpleadoCreate

router = APIRouter(prefix="/empleados", tags=["Empleados"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def padron_empleados(request: Request, mensaje: str = None, error: str = None):
    personal = EmpleadoService.listar_personal()
    total = len(personal)
    total_seg = sum(1 for p in personal if p.get("area_clasificacion") == "SEG")
    total_adm = sum(1 for p in personal if p.get("area_clasificacion") == "ADM")
    total_tra = sum(1 for p in personal if p.get("area_clasificacion") == "TRA")
    total_desp = sum(1 for p in personal if p.get("estado_laboral") == "DESPLAZADO")
    total_lic = sum(1 for p in personal if "LICENCIA" in str(p.get("estado_laboral", "")))

    return templates.TemplateResponse(
        request=request,
        name="empleados/padron.html",
        context={
            "personal": personal,
            "total": total,
            "total_seg": total_seg,
            "total_adm": total_adm,
            "total_tra": total_tra,
            "total_desp": total_desp,
            "total_lic": total_lic,
            "mensaje": mensaje,
            "error": error
        }
    )

@router.get("/{id_empleado}")
async def obtener_detalle_empleado(id_empleado: int):
    emp = EmpleadoService.obtener_empleado(id_empleado)
    if not emp:
        return JSONResponse(status_code=404, content={"error": "Servidor no encontrado"})
    return JSONResponse(content=emp)

@router.post("/editar/{id_empleado}")
async def editar_empleado(
    id_empleado: int,
    codigo_servidor: str = Form(...),
    dni: str = Form(""),
    apellidos_nombres: str = Form(...),
    sexo: str = Form("M"),
    fecha_nacimiento: Optional[str] = Form(None),
    correo: Optional[str] = Form(""),
    regimen_nombre: Optional[str] = Form("Ley N° 29709"),
    nivel: Optional[str] = Form("T1"),
    cargo_estructural: Optional[str] = Form(""),
    cargo_funcion: Optional[str] = Form(""),
    area_clasificacion: Optional[str] = Form("SEG"),
    horario_laboral: Optional[str] = Form("24 x 48"),
    estado_laboral: Optional[str] = Form("ACTIVO"),
    modalidad_laboral: Optional[str] = Form("PRESENCIAL"),
    direccion_oficina: Optional[str] = Form(""),
    jefatura_area: Optional[str] = Form(""),
    fecha_ingreso_inpe: Optional[str] = Form(None),
    fecha_ingreso_eepp: Optional[str] = Form(None),
    resolucion_documento: Optional[str] = Form(""),
    observaciones: Optional[str] = Form("")
):
    try:
        # Determinar id_regimen
        id_reg = 1
        if "276" in str(regimen_nombre):
            id_reg = 2
        elif "1057" in str(regimen_nombre) or "CAS" in str(regimen_nombre).upper():
            id_reg = 3

        datos = {
            "codigo_servidor": codigo_servidor.strip(),
            "dni": dni.strip() if dni else None,
            "apellidos_nombres": apellidos_nombres.strip().upper(),
            "sexo": sexo.strip().upper() if sexo else "M",
            "fecha_nacimiento": fecha_nacimiento if fecha_nacimiento else None,
            "correo": correo.strip().lower() if correo else "",
            "id_regimen": id_reg,
            "regimen_nombre": regimen_nombre.strip(),
            "nivel": nivel.strip() if nivel else "T1",
            "cargo_estructural": cargo_estructural.strip() if cargo_estructural else "",
            "cargo_funcion": cargo_funcion.strip() if cargo_funcion else "",
            "area_clasificacion": area_clasificacion.strip() if area_clasificacion else "SEG",
            "horario_laboral": horario_laboral.strip() if horario_laboral else "24 x 48",
            "estado_laboral": estado_laboral.strip() if estado_laboral else "ACTIVO",
            "modalidad_laboral": modalidad_laboral.strip() if modalidad_laboral else "PRESENCIAL",
            "direccion_oficina": direccion_oficina.strip() if direccion_oficina else "",
            "jefatura_area": jefatura_area.strip() if jefatura_area else "",
            "fecha_ingreso_inpe": fecha_ingreso_inpe if fecha_ingreso_inpe else None,
            "fecha_ingreso_eepp": fecha_ingreso_eepp if fecha_ingreso_eepp else None,
            "resolucion_documento": resolucion_documento.strip() if resolucion_documento else "",
            "observaciones": observaciones.strip() if observaciones else ""
        }

        EmpleadoService.actualizar_empleado(id_empleado, datos)
        return RedirectResponse(
            url=f"/empleados?mensaje=Legajo+de+{apellidos_nombres}+actualizado+correctamente",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(url=f"/empleados?error={str(e)}", status_code=303)

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
