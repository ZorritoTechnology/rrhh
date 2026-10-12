import sqlite3
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.asistencia_service import get_personal_activo
from app.core.database import get_connection

router = APIRouter(prefix="/vacaciones", tags=["Vacaciones"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/saldos", response_class=HTMLResponse)
async def ver_saldos(request: Request):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.id_empleado, e.codigo_servidor, e.apellidos_nombres,
               COALESCE(SUM(v.dias), 0) as dias_consumidos_2025,
               GROUP_CONCAT(v.periodo || ' (' || v.dias || 'd)', ', ') as desglose_periodos,
               GROUP_CONCAT(v.observaciones, ' | ') as observaciones
        FROM empleados e
        LEFT JOIN reporte_vacaciones v ON e.id_empleado = v.id_empleado
        GROUP BY e.id_empleado
        ORDER BY dias_consumidos_2025 DESC
    """)
    resultados = cur.fetchall()
    
    empleados_stats = []
    for r in resultados:
        dias = r["dias_consumidos_2025"]
        
        excedido = False
        if dias > 30:
            excedido = True
            
        if dias == 0:
            estado = "SIN SALIDAS"
        elif dias <= 15:
            estado = "FRACCIONADO"
        elif dias <= 30:
            estado = "REGULAR"
        else:
            estado = "EXCEDIDO"
            
        empleados_stats.append({
            "codigo_servidor": r["codigo_servidor"],
            "apellidos_nombres": r["apellidos_nombres"],
            "dias_consumidos": dias,
            "desglose": r["desglose_periodos"] if r["desglose_periodos"] else "-",
            "estado": estado,
            "excedido": excedido,
            "observaciones": r["observaciones"] if r["observaciones"] else ""
        })
        
    conn.close()
    
    return templates.TemplateResponse(
        request=request,
        name="vacaciones_saldos.html",
        context={
            "empleados_stats": empleados_stats
        }
    )

