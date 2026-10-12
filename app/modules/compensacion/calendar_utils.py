import calendar
from datetime import date, timedelta
from typing import Dict, List, Any

def generar_calendario_mes(anio: int, mes: int) -> Dict[str, Any]:
    """
    Genera la estructura de semanas (Lunes a Domingo) y días para el mes,
    conforme al diseño oficial del Anexo 02 de la Directiva DI-003-2023-INPE-OGA.
    """
    num_dias = calendar.monthrange(anio, mes)[1]
    dias_semana_abrev = ["L", "M", "M", "J", "V", "S", "D"]
    dias_semana_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Lista de todos los días del mes
    dias_del_mes = []
    for d in range(1, num_dias + 1):
        f = date(anio, mes, d)
        dias_del_mes.append({
            "dia": d,
            "fecha": f.isoformat(),
            "weekday": f.weekday(), # 0: Lunes ... 6: Domingo
            "dia_letra": dias_semana_abrev[f.weekday()],
            "dia_nombre": dias_semana_nombres[f.weekday()]
        })

    # Agrupar por semanas de Lunes a Domingo
    semanas = []
    semana_actual = {
        "numero": 1,
        "dias": []
    }
    
    for d_info in dias_del_mes:
        semana_actual["dias"].append(d_info)
        # Si es Domingo o es el último día del mes, cerramos la semana
        if d_info["weekday"] == 6 or d_info["dia"] == num_dias:
            semanas.append(semana_actual)
            semana_actual = {
                "numero": len(semanas) + 1,
                "dias": []
            }

    return {
        "anio": anio,
        "mes": mes,
        "num_dias": num_dias,
        "dias": dias_del_mes,
        "semanas": semanas
    }

if __name__ == "__main__":
    cal = generar_calendario_mes(2026, 1)
    print(f"Mes {cal['mes']}/{cal['anio']} tiene {len(cal['semanas'])} semanas en Anexo 02:")
    for s in cal['semanas']:
        rango = f"{s['dias'][0]['dia']} ({s['dias'][0]['dia_letra']}) al {s['dias'][-1]['dia']} ({s['dias'][-1]['dia_letra']})"
        print(f"  Semana {s['numero']}: {len(s['dias'])} días -> {rango}")
