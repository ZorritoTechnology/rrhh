from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from app.modules.desplazamientos.repository import DesplazamientoRepository
from app.modules.desplazamientos.service import DesplazamientoService
from app.modules.empleados.service import EmpleadoService

router = APIRouter(prefix="/desplazamientos", tags=["Desplazamientos de Personal"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def ver_desplazamientos(request: Request, tipo: str = None):
    """
    Bandeja principal de Desplazamientos entre penales (Altas y Bajas).
    """
    movimientos = DesplazamientoRepository.listar_desplazamientos(tipo)
    total_altas = sum(1 for m in movimientos if m["tipo_movimiento"] == "ALTA_RECEPCION")
    total_bajas = sum(1 for m in movimientos if m["tipo_movimiento"] == "BAJA_SALIDA")

    return templates.TemplateResponse(
        request=request,
        name="desplazamientos/lista.html",
        context={
            "movimientos": movimientos,
            "tipo_filtro": tipo,
            "total_altas": total_altas,
            "total_bajas": total_bajas,
            "total_movimientos": len(movimientos)
        }
    )

@router.get("/alta", response_class=HTMLResponse)
async def form_alta(request: Request):
    """
    Formulario oficial para registrar personal recibido de otro penal con su Hoja de Desplazamiento.
    """
    empleados = EmpleadoService.listar_personal()
    establecimientos = DesplazamientoRepository.listar_establecimientos()
    
    return templates.TemplateResponse(
        request=request,
        name="desplazamientos/form_alta.html",
        context={
            "empleados": empleados,
            "establecimientos": establecimientos,
            "fecha_hoy": date.today().isoformat()
        }
    )

@router.post("/alta", response_class=HTMLResponse)
async def registrar_alta(
    request: Request,
    id_empleado: int = Form(...),
    id_establecimiento_origen: int = Form(None),
    nombre_origen_ext: str = Form(""),
    fecha_desplazamiento: str = Form(...),
    fecha_presentacion_eepp: str = Form(...),
    documento_oficial: str = Form(...),
    vacaciones_periodo: str = Form("2025-2026"),
    vacaciones_gozadas_origen: int = Form(0),
    vacaciones_saldo_origen: int = Form(30),
    comp_ganadas_origen: int = Form(0),
    comp_gozadas_origen: int = Form(0),
    comp_saldo_origen: int = Form(0),
    observaciones: str = Form("")
):
    resultado = DesplazamientoService.procesar_alta_desplazamiento(
        id_empleado=id_empleado,
        id_establecimiento_origen=id_establecimiento_origen,
        nombre_origen_ext=nombre_origen_ext,
        fecha_desplazamiento=fecha_desplazamiento,
        fecha_presentacion_eepp=fecha_presentacion_eepp,
        documento_oficial=documento_oficial,
        vacaciones_periodo=vacaciones_periodo,
        vacaciones_gozadas_origen=vacaciones_gozadas_origen,
        vacaciones_saldo_origen=vacaciones_saldo_origen,
        comp_anio_fiscal=2026,
        comp_ganadas_origen=comp_ganadas_origen,
        comp_gozadas_origen=comp_gozadas_origen,
        comp_saldo_origen=comp_saldo_origen,
        observaciones=observaciones
    )

    empleados = EmpleadoService.listar_personal()
    establecimientos = DesplazamientoRepository.listar_establecimientos()

    return templates.TemplateResponse(
        request=request,
        name="desplazamientos/form_alta.html",
        context={
            "empleados": empleados,
            "establecimientos": establecimientos,
            "fecha_hoy": fecha_presentacion_eepp,
            "success": resultado["message"] if resultado["success"] else None,
            "error": resultado["message"] if not resultado["success"] else None,
            "id_desplazamiento": resultado.get("id_desplazamiento")
        }
    )

@router.get("/baja", response_class=HTMLResponse)
async def form_baja(request: Request):
    """
    Formulario oficial para registrar la salida de un servidor trasladado a otro penal.
    """
    empleados = EmpleadoService.listar_personal()
    establecimientos = DesplazamientoRepository.listar_establecimientos()
    
    return templates.TemplateResponse(
        request=request,
        name="desplazamientos/form_baja.html",
        context={
            "empleados": empleados,
            "establecimientos": establecimientos,
            "fecha_hoy": date.today().isoformat()
        }
    )

@router.post("/baja", response_class=HTMLResponse)
async def registrar_baja(
    request: Request,
    id_empleado: int = Form(...),
    id_establecimiento_destino: int = Form(None),
    nombre_destino_ext: str = Form(""),
    fecha_desplazamiento: str = Form(...),
    documento_oficial: str = Form(...),
    observaciones: str = Form("")
):
    resultado = DesplazamientoService.procesar_baja_desplazamiento(
        id_empleado=id_empleado,
        id_establecimiento_destino=id_establecimiento_destino,
        nombre_destino_ext=nombre_destino_ext,
        fecha_desplazamiento=fecha_desplazamiento,
        documento_oficial=documento_oficial,
        observaciones=observaciones
    )

    empleados = EmpleadoService.listar_personal()
    establecimientos = DesplazamientoRepository.listar_establecimientos()

    return templates.TemplateResponse(
        request=request,
        name="desplazamientos/form_baja.html",
        context={
            "empleados": empleados,
            "establecimientos": establecimientos,
            "fecha_hoy": fecha_desplazamiento,
            "success": resultado["message"] if resultado["success"] else None,
            "error": resultado["message"] if not resultado["success"] else None,
            "id_desplazamiento": resultado.get("id_desplazamiento")
        }
    )

@router.get("/constancia/{id_desplazamiento}", response_class=HTMLResponse)
async def ver_constancia_anexo6(request: Request, id_desplazamiento: int):
    """
    Formato oficial de impresión: Anexo N° 06 (REG-006-URH) - Constancia por Desplazamiento.
    """
    desp = DesplazamientoRepository.obtener_desplazamiento_detalle(id_desplazamiento)
    if not desp:
        return HTMLResponse("Registro de desplazamiento no encontrado", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="desplazamientos/constancia_anexo6.html",
        context={
            "desp": desp
        }
    )

@router.get("/detalle/{id_desplazamiento}")
async def obtener_desplazamiento_json(id_desplazamiento: int):
    """
    Retorna los datos completos de un desplazamiento en formato JSON para el modal interactivo de edición.
    """
    desp = DesplazamientoRepository.obtener_desplazamiento_detalle(id_desplazamiento)
    if not desp:
        return JSONResponse({"error": "Desplazamiento no encontrado"}, status_code=404)
    return JSONResponse(desp)

@router.post("/editar/{id_desplazamiento}")
async def editar_desplazamiento(
    request: Request,
    id_desplazamiento: int,
    tipo_movimiento: str = Form(...),
    nombre_origen_ext: str = Form(""),
    nombre_destino_ext: str = Form(""),
    fecha_desplazamiento: str = Form(...),
    fecha_presentacion_eepp: str = Form(...),
    documento_oficial: str = Form(...),
    vacaciones_periodo: str = Form("2025-2026"),
    vacaciones_gozadas_origen: int = Form(0),
    vacaciones_saldo_origen: int = Form(30),
    comp_ganadas_origen: int = Form(0),
    comp_gozadas_origen: int = Form(0),
    comp_saldo_origen: int = Form(0),
    observaciones: str = Form("")
):
    """
    Procesa la modificación de una Hoja de Desplazamiento (Anexo 06) y actualiza saldos vinculados.
    """
    resultado = DesplazamientoService.procesar_modificacion_desplazamiento(
        id_desplazamiento=id_desplazamiento,
        tipo_movimiento=tipo_movimiento,
        nombre_origen_ext=nombre_origen_ext,
        nombre_destino_ext=nombre_destino_ext,
        fecha_desplazamiento=fecha_desplazamiento,
        fecha_presentacion_eepp=fecha_presentacion_eepp,
        documento_oficial=documento_oficial,
        vacaciones_periodo=vacaciones_periodo,
        vacaciones_gozadas_origen=vacaciones_gozadas_origen,
        vacaciones_saldo_origen=vacaciones_saldo_origen,
        comp_ganadas_origen=comp_ganadas_origen,
        comp_gozadas_origen=comp_gozadas_origen,
        comp_saldo_origen=comp_saldo_origen,
        observaciones=observaciones
    )
    return RedirectResponse(url="/desplazamientos", status_code=303)
