from typing import List, Dict, Any
from app.modules.vacaciones.repository import VacacionesRepository
from app.modules.vacaciones.models import SaldoVacacional

class VacacionesService:
    @staticmethod
    def obtener_resumen_saldos() -> Dict[str, Any]:
        filas = VacacionesRepository.get_consumo_consolidado()
        empleados_stats = []
        
        total_personal = len(filas)
        total_dias_gozados = 0
        total_excedidos = 0
        total_fraccionados = 0
        
        for r in filas:
            dias = r["dias_consumidos"]
            total_dias_gozados += dias
            
            excedido = dias > 30
            if excedido:
                total_excedidos += 1
                
            if dias == 0:
                estado = "SIN SALIDAS"
            elif dias <= 15:
                estado = "FRACCIONADO"
                total_fraccionados += 1
            elif dias <= 30:
                estado = "REGULAR"
            else:
                estado = "EXCEDIDO"
                
            empleados_stats.append({
                "id_empleado": r["id_empleado"],
                "codigo_servidor": r["codigo_servidor"],
                "apellidos_nombres": r["apellidos_nombres"],
                "dias_consumidos": dias,
                "dias_saldo": max(0, 30 - dias),
                "desglose": r["desglose_periodos"] if r["desglose_periodos"] else "-",
                "estado": estado,
                "excedido": excedido,
                "observaciones": r["observaciones"] if r["observaciones"] else ""
            })
            
        return {
            "stats": {
                "total_personal": total_personal,
                "total_dias_gozados": total_dias_gozados,
                "total_excedidos": total_excedidos,
                "total_fraccionados": total_fraccionados
            },
            "empleados": empleados_stats
        }
