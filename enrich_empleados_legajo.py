import sqlite3
from datetime import datetime

def parse_date(d_str):
    if not d_str or str(d_str).strip() in ["", "-", "None"]:
        return None
    d_str = str(d_str).strip()
    if d_str == "18-feb":
        return "2026-02-18"
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
        try:
            return datetime.strptime(d_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None

DATA_PERSONAL = [
    {
        "codigo": "909794", "dni": "45568033", "nombres": "AYASTA AGAPITO SEGUNDO CRISTIAN", "sexo": "M",
        "fecha_nac": "1/2/1989", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "27 x 48",
        "fecha_ingreso_eepp": "12/6/2026", "resolucion": "RD N°189-2026-INPE/ORNOSM", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "913371", "dni": "70185836", "nombres": "BARDALES LOZANO AMBAR GRECIA TAMARA", "sexo": "F",
        "fecha_nac": "19/10/1992", "correo": "ambar.lozano@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "29/12/2023", "resolucion": "RP N°339-2023-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "102595", "dni": "42714779", "nombres": "BARDALES LOZANO CARMEN ROSA", "sexo": "F",
        "fecha_nac": "3/10/1984", "correo": "cbardalesl@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "S1",
        "cargo_estructural": "DOCENTE DE AULA (PROFESIONAL EN TRATAMIENTO)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "TRATAMIENTO", "jefatura": "EDUCACION",
        "cargo_funcion": "COORDINADORA DE EDUCACION", "area": "TRA", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "5/12/2024", "resolucion": "RD N°303-2024-INPE-P", "observaciones": "",
        "fecha_ingreso_inpe": "5/12/2024"
    },
    {
        "codigo": "103097", "dni": "43574815", "nombres": "CACERES RIOS JAXSON CHARLES", "sexo": "M",
        "fecha_nac": "24/11/1985", "correo": "jcaceres@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "GESTOR DE BASE DE DATOS", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "REGISTRO", "jefatura": "REGISTRO PENITENCIARIO",
        "cargo_funcion": "JEFE DE REGISTRO PENITENCIARIO", "area": "ADM", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "1/4/2021", "resolucion": "RD 42-2021-INPE/ORNOSM", "observaciones": "",
        "fecha_ingreso_inpe": "1/7/2016"
    },
    {
        "codigo": "910490", "dni": "61101713", "nombres": "CAHUAZA CHOTA ROY JUNIOR", "sexo": "M",
        "fecha_nac": "15/6/1993", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "31 x 48",
        "fecha_ingreso_eepp": "9/7/2026", "resolucion": "RD N°131", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "102747", "dni": "15864987", "nombres": "CANALES PAREDES ADELA ISABEL", "sexo": "F",
        "fecha_nac": "22/6/1978", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "11/4/2025", "resolucion": "RD N°057-2025-INPE/ORNOSM", "observaciones": "",
        "fecha_ingreso_inpe": "31/12/2014"
    },
    {
        "codigo": "911381", "dni": "74576560", "nombres": "CARO SILVA FRANK REDI", "sexo": "M",
        "fecha_nac": "18/7/1994", "correo": "frank.caro@inpe.gob.pe", "regimen": "DL N° 1057", "id_regimen": 3, "nivel": "SNR",
        "cargo_estructural": "AGENTE DE SEGURIDAD PENITENCIARIA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "6/7/2023", "resolucion": "MEMORANDO N°116-2023-INPE/ORNOSM-ERRHH", "observaciones": "",
        "fecha_ingreso_inpe": "1/6/2017"
    },
    {
        "codigo": "910668", "dni": "44687160", "nombres": "CASTILLO SOLIS DALIA MILAGROS", "sexo": "F",
        "fecha_nac": "23/11/1987", "correo": "dalia.castillo@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "6/9/2024", "resolucion": "RP. N°203-2024-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "1/9/2024"
    },
    {
        "codigo": "911664", "dni": "76210282", "nombres": "CAVERO DIAZ ANGEL GABRIEL", "sexo": "M",
        "fecha_nac": "22/4/1995", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "30/12/2023", "resolucion": "", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "912244", "dni": "70929943", "nombres": "CHUQUIVAL RODRIGUEZ EDINSON", "sexo": "M",
        "fecha_nac": "4/6/1992", "correo": "echuquival@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "18/1/2024", "resolucion": "RP N°339-2023-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "911117", "dni": "45765846", "nombres": "CUEVA RODRIGUEZ JUAN CARLOS", "sexo": "M",
        "fecha_nac": "5/4/1988", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "14/6/2026", "resolucion": "RD N°189-2026-INPE/ORNOSM", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "911382", "dni": "42036844", "nombres": "CULQUI RENGIFO CLARA URSULA PATRICIA", "sexo": "F",
        "fecha_nac": "26/3/1982", "correo": "cculqui@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "29/12/2023", "resolucion": "RP N°339-2023-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "103986", "dni": "45810415", "nombres": "DAVALOS LAZARO ELIZABETH ISABEL", "sexo": "F",
        "fecha_nac": "12/7/1989", "correo": "", "regimen": "DL N° 276", "id_regimen": 2, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "25 x 48",
        "fecha_ingreso_eepp": "15/6/2026", "resolucion": "RD N°189-2026-INPE/ORNOSM", "observaciones": "",
        "fecha_ingreso_inpe": "17/9/2012"
    },
    {
        "codigo": "910717", "dni": "43818009", "nombres": "DAVILA FLORES MARISSA ISABEL", "sexo": "F",
        "fecha_nac": "4/10/1984", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "STF",
        "cargo_estructural": "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "26 x 48",
        "fecha_ingreso_eepp": "15/6/2026", "resolucion": "RD N°189-2026-INPE/ORNOSM", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "910721", "dni": "71851435", "nombres": "DE LOAYZA TORRES AMBAR CRISTINA", "sexo": "F",
        "fecha_nac": "29/5/1994", "correo": "", "regimen": "DL N° 1057", "id_regimen": 3, "nivel": "SNR",
        "cargo_estructural": "AGENTE DE SEGURIDAD PENITENCIARIA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "21/10/2015", "resolucion": "", "observaciones": "",
        "fecha_ingreso_inpe": "21/10/2015"
    },
    {
        "codigo": "910748", "dni": "46187186", "nombres": "FLORES CARDENAS FRANCO CHRISTOPHER", "sexo": "M",
        "fecha_nac": "24/11/1989", "correo": "franco.flores@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "29/12/2023", "resolucion": "RP N°339-2023-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "913429", "dni": "72362380", "nombres": "GUEVARA CASTILLO MICHAEL STEFANNY", "sexo": "F",
        "fecha_nac": "6/2/1998", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "1/9/2024", "resolucion": "", "observaciones": "",
        "fecha_ingreso_inpe": "1/9/2024"
    },
    {
        "codigo": "914591", "dni": "44306146", "nombres": "HIDALGO NASHNATE LEIDY VANESSA", "sexo": "F",
        "fecha_nac": "28/2/1987", "correo": "leidyhidalgo0102@gmail.com", "regimen": "DL N° 1057", "id_regimen": 3, "nivel": "SNR",
        "cargo_estructural": "TECNICO EN ENFERMERIA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "TRATAMIENTO", "jefatura": "SALUD PENITENCIARIA",
        "cargo_funcion": "TECNICO EN ENFERMERIA", "area": "TRA", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "1/4/2021", "resolucion": "CONTRATO", "observaciones": "",
        "fecha_ingreso_inpe": "1/4/2021"
    },
    {
        "codigo": "912503", "dni": "48566494", "nombres": "LOMAS ROMERO MONICA ANGELICA", "sexo": "F",
        "fecha_nac": "6/11/1990", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "8/9/2024", "resolucion": "RP N°203-2024-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "1/9/2024"
    },
    {
        "codigo": "103913", "dni": "43945591", "nombres": "LOPEZ TAMANI BLANCA CARINA", "sexo": "F",
        "fecha_nac": "27/5/1986", "correo": "", "regimen": "DL N° 276", "id_regimen": 2, "nivel": "STF",
        "cargo_estructural": "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "ADMINISTRATIVO", "jefatura": "SEGURIDAD",
        "cargo_funcion": "JEFE DE DIVISION DE SEGURIDAD", "area": "ADM", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "30/12/2020", "resolucion": "RD 260-2020-INPE/ORNOSM", "observaciones": "",
        "fecha_ingreso_inpe": "17/9/2012"
    },
    {
        "codigo": "909967", "dni": "45519121", "nombres": "MANIHUARI VASQUEZ ALEXANDER", "sexo": "M",
        "fecha_nac": "24/5/1986", "correo": "alexander.manihuari@inpe.gob.pe", "regimen": "DL N° 1057", "id_regimen": 3, "nivel": "SNR",
        "cargo_estructural": "AGENTE DE SEGURIDAD PENITENCIARIA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "6/1/2025", "resolucion": "MEMORANDO N°01-2025-INPE/ORNOSM-ERRHH", "observaciones": "",
        "fecha_ingreso_inpe": "1/8/2014"
    },
    {
        "codigo": "910465", "dni": "48009378", "nombres": "MELENDEZ AMASIFUEN MAILITH", "sexo": "F",
        "fecha_nac": "14/9/1993", "correo": "mailith.melendez@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "6/8/2025", "resolucion": "RD N°607-2025-INPE/OGA-URH", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "910854", "dni": "46370605", "nombres": "MOZOMBITE AHUANARI DAVID ALBERTO", "sexo": "M",
        "fecha_nac": "2/6/1990", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "28 x 48",
        "fecha_ingreso_eepp": "9/7/2026", "resolucion": "RD N°131", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "913148", "dni": "42208613", "nombres": "NOVOA MIÑOPE EMILIA KATHERINE", "sexo": "F",
        "fecha_nac": "24/12/1983", "correo": "enovoam@inpe.gob.pe", "regimen": "DL N° 1057", "id_regimen": 3, "nivel": "SNR",
        "cargo_estructural": "OBSTETRA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "TRATAMIENTO", "jefatura": "SALUD PENITENCIARIA",
        "cargo_funcion": "OBSTETRIZ", "area": "TRA", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "10/9/2019", "resolucion": "CONTRATO", "observaciones": "",
        "fecha_ingreso_inpe": "6/9/2019"
    },
    {
        "codigo": "910332", "dni": "45857066", "nombres": "NUÑEZ GONGORA RALF FRANCOIS", "sexo": "M",
        "fecha_nac": "10/7/1989", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "20/6/2024", "resolucion": "MEMORANDO N°125-2024-INPE/ORNOSM-ERRHH", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "104449", "dni": "40869121", "nombres": "OLANO SALAZAR CARLOS ALBERTO", "sexo": "M",
        "fecha_nac": "3/2/1979", "correo": "colano@inpe.gob.pe", "regimen": "DL N° 276", "id_regimen": 2, "nivel": "STF",
        "cargo_estructural": "ESPECIALISTA EN SEGURIDAD PENITENCIARIA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "5/8/2025", "resolucion": "RD N°607-2025-INPE/OGA-URH", "observaciones": "",
        "fecha_ingreso_inpe": "19/12/2012"
    },
    {
        "codigo": "910869", "dni": "43908245", "nombres": "PANDURO PARANA LLOYSI LLERLITA", "sexo": "F",
        "fecha_nac": "20/2/1986", "correo": "lloysi.panduro@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "7/9/2024", "resolucion": "RP N°203-2024-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "1/9/2024"
    },
    {
        "codigo": "908917", "dni": "46051088", "nombres": "PARANO OROCHE BRIGITTE", "sexo": "F",
        "fecha_nac": "4/4/1989", "correo": "brigitte.parano@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "LICENCIA MATERNIDAD", "modalidad": "NO APLICA",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "29/12/2023", "resolucion": "RP N°339-2023-INPE/P", "observaciones": "Licencia por maternidad 02/01/2026 al 09/04/2026",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "911387", "dni": "46188189", "nombres": "PIÑA GONGORA CRISTIAN", "sexo": "M",
        "fecha_nac": "23/6/1989", "correo": "cristian.pina@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "13/9/2024", "resolucion": "RP N°203-2024-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "1/9/2024"
    },
    {
        "codigo": "910524", "dni": "72556894", "nombres": "RIOS ANGELES JULIO CESAR", "sexo": "M",
        "fecha_nac": "29/4/1991", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "30 x 48",
        "fecha_ingreso_eepp": "9/7/2026", "resolucion": "RD N°131", "observaciones": "",
        "fecha_ingreso_inpe": "1/9/2024"
    },
    {
        "codigo": "911755", "dni": "45675819", "nombres": "SALDAÑA TUANAMA JARRIN TUNNER", "sexo": "M",
        "fecha_nac": "10/3/1989", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "29 x 48",
        "fecha_ingreso_eepp": "9/7/2026", "resolucion": "RD N°131", "observaciones": "",
        "fecha_ingreso_inpe": "17/7/2025"
    },
    {
        "codigo": "910940", "dni": "45481934", "nombres": "SANCHEZ PIZANGO MAYRA SOVEYDA", "sexo": "F",
        "fecha_nac": "11/11/1988", "correo": "mayra.sanchez@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "1/1/2026", "resolucion": "RP N° 534-2025-INPE/P", "observaciones": "INCORPORACIÓN A LEY 29709",
        "fecha_ingreso_inpe": "1/1/2026"
    },
    {
        "codigo": "910945", "dni": "42341212", "nombres": "SANDY DEL CASTILLO DELIA ANITA", "sexo": "F",
        "fecha_nac": "23/3/1984", "correo": "delia.sandy@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "29/12/2023", "resolucion": "RP N°339-2023-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "910396", "dni": "46783856", "nombres": "SOLSOL FONSECA ADRIAN ALFREDO", "sexo": "M",
        "fecha_nac": "25/1/1992", "correo": "adrian.solsol@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "AGENTE DE SEGURIDAD I (TÉCNICO EN SEGURIDAD)", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "6/9/2024", "resolucion": "RP N°203-2024-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "1/9/2024"
    },
    {
        "codigo": "9881", "dni": "29557455", "nombres": "TEJADA ZUÑIGA CELIA YENNI", "sexo": "F",
        "fecha_nac": "4/10/1970", "correo": "ctejadz@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T3",
        "cargo_estructural": "SUPERVISOR DE GRUPO", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "9/11/2014", "resolucion": "RD N°251-2014-INPE/21", "observaciones": "",
        "fecha_ingreso_inpe": "31/12/2014"
    },
    {
        "codigo": "9889", "dni": "9756696", "nombres": "TORRES OBREGON EDITH MODESTA", "sexo": "F",
        "fecha_nac": "19/10/1971", "correo": "Edith.torres@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T3",
        "cargo_estructural": "DIRECTORA", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "DIRECCION", "jefatura": "DIRECCION",
        "cargo_funcion": "DIRECTORA", "area": "ADM", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "20/2/2026", "resolucion": "RP N° 089-2026-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "23/12/2013"
    },
    {
        "codigo": "911662", "dni": "46924524", "nombres": "VALLE SANCHEZ EYLIN", "sexo": "M",
        "fecha_nac": "16/10/1991", "correo": "eylin.valle@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "TÉCNICO EN SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "29/1/2024", "resolucion": "RP N°339-2023-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "30/12/2023"
    },
    {
        "codigo": "103793", "dni": "41616632", "nombres": "VALLEJOS LEYVA ERIC JHON", "sexo": "M",
        "fecha_nac": "8/10/1979", "correo": "", "regimen": "DL N° 276", "id_regimen": 2, "nivel": "STF",
        "cargo_estructural": "ESPECIALISTA DE SEGURIDAD PENITENCIARIA", "estado": "ABANDONO", "modalidad": "NO APLICA",
        "direccion": "SEGURIDAD PENITENCIARIA", "jefatura": "SEGURIDAD PENITENCIARIA",
        "cargo_funcion": "AGENTE DE SEGURIDAD", "area": "SEG", "horario": "24 x 48",
        "fecha_ingreso_eepp": "2/7/2017", "resolucion": "RD N°461-2016-INPE/P", "observaciones": "abandono laboral desde el 10/05/2021",
        "fecha_ingreso_inpe": "17/9/2012"
    },
    {
        "codigo": "103095", "dni": "42916467", "nombres": "VELA VILLENA JHULY ANGELA", "sexo": "F",
        "fecha_nac": "27/3/1985", "correo": "jvela@inpe.gob.pe", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T1",
        "cargo_estructural": "JEFA DE SEGURIDAD", "estado": "ACTIVO", "modalidad": "PRESENCIAL",
        "direccion": "ADMINISTRATIVO", "jefatura": "SEGURIDAD",
        "cargo_funcion": "JEFE DE SECCION DE SEGURIDAD", "area": "ADM", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "18/2/2026", "resolucion": "RP N° 089-2026-INPE/P", "observaciones": "",
        "fecha_ingreso_inpe": "1/7/2016"
    },
    {
        "codigo": "99132", "dni": "7032370", "nombres": "ZAPATA ROQUE SANTOS DELCIA", "sexo": "F",
        "fecha_nac": "2/5/1962", "correo": "", "regimen": "Ley N° 29709", "id_regimen": 1, "nivel": "T2",
        "cargo_estructural": "AGENTE DE SEGURIDAD II", "estado": "DESPLAZADO", "modalidad": "PRESENCIAL",
        "direccion": "DIRECCION", "jefatura": "DIRECCION",
        "cargo_funcion": "DIRECTORA", "area": "ADM", "horario": "08:00 - 17:00",
        "fecha_ingreso_eepp": "29/12/2023", "resolucion": "RP N°325-2023-INPE/P", "observaciones": "Desplazado EP. Moyobamba",
        "fecha_ingreso_inpe": "31/12/2014"
    }
]

def main():
    conn = sqlite3.connect("rrhh_control.db")
    cur = conn.cursor()

    # 1. Asegurar nuevas columnas en tabla empleados
    columnas_nuevas = [
        ("sexo", "TEXT"),
        ("fecha_nacimiento", "DATE"),
        ("correo", "TEXT"),
        ("id_regimen", "INTEGER"),
        ("regimen_nombre", "TEXT"),
        ("nivel", "TEXT"),
        ("cargo_estructural", "TEXT"),
        ("estado_laboral", "TEXT"),
        ("modalidad_laboral", "TEXT"),
        ("direccion_oficina", "TEXT"),
        ("jefatura_area", "TEXT"),
        ("cargo_funcion", "TEXT"),
        ("area_clasificacion", "TEXT"),
        ("horario_laboral", "TEXT"),
        ("fecha_ingreso_eepp", "DATE"),
        ("resolucion_documento", "TEXT"),
        ("observaciones", "TEXT"),
        ("fecha_ingreso_inpe", "DATE"),
    ]

    cur.execute("PRAGMA table_info(empleados)")
    cols_existentes = [r[1] for r in cur.fetchall()]

    for col, col_type in columnas_nuevas:
        if col not in cols_existentes:
            print(f"Agregando columna {col} a empleados...")
            cur.execute(f"ALTER TABLE empleados ADD COLUMN {col} {col_type}")

    conn.commit()

    # 2. Insertar o actualizar empleados con datos completos
    for p in DATA_PERSONAL:
        f_nac = parse_date(p["fecha_nac"])
        f_eepp = parse_date(p["fecha_ingreso_eepp"])
        f_inpe = parse_date(p["fecha_ingreso_inpe"])

        # Buscar si existe por DNI o código
        cur.execute("SELECT id_empleado FROM empleados WHERE dni = ? OR codigo_servidor = ?", (p["dni"], p["codigo"]))
        row = cur.fetchone()

        if row:
            id_emp = row[0]
            cur.execute("""
                UPDATE empleados SET
                    codigo_servidor = ?,
                    dni = ?,
                    apellidos_nombres = ?,
                    sexo = ?,
                    fecha_nacimiento = ?,
                    correo = ?,
                    id_regimen = ?,
                    regimen_nombre = ?,
                    nivel = ?,
                    cargo_estructural = ?,
                    estado_laboral = ?,
                    modalidad_laboral = ?,
                    direccion_oficina = ?,
                    jefatura_area = ?,
                    cargo_funcion = ?,
                    area_clasificacion = ?,
                    horario_laboral = ?,
                    fecha_ingreso_eepp = ?,
                    resolucion_documento = ?,
                    observaciones = ?,
                    fecha_ingreso_inpe = ?
                WHERE id_empleado = ?
            """, (
                p["codigo"], p["dni"], p["nombres"], p["sexo"], f_nac, p["correo"],
                p["id_regimen"], p["regimen"], p["nivel"], p["cargo_estructural"],
                p["estado"], p["modalidad"], p["direccion"], p["jefatura"],
                p["cargo_funcion"], p["area"], p["horario"], f_eepp,
                p["resolucion"], p["observaciones"], f_inpe, id_emp
            ))
            print(f"Actualizado emp {id_emp}: {p['nombres']}")
        else:
            cur.execute("""
                INSERT INTO empleados (
                    codigo_servidor, dni, apellidos_nombres, sexo, fecha_nacimiento,
                    correo, id_regimen, regimen_nombre, nivel, cargo_estructural,
                    estado_laboral, modalidad_laboral, direccion_oficina, jefatura_area,
                    cargo_funcion, area_clasificacion, horario_laboral, fecha_ingreso_eepp,
                    resolucion_documento, observaciones, fecha_ingreso_inpe
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["codigo"], p["dni"], p["nombres"], p["sexo"], f_nac, p["correo"],
                p["id_regimen"], p["regimen"], p["nivel"], p["cargo_estructural"],
                p["estado"], p["modalidad"], p["direccion"], p["jefatura"],
                p["cargo_funcion"], p["area"], p["horario"], f_eepp,
                p["resolucion"], p["observaciones"], f_inpe
            ))
            id_emp = cur.lastrowid
            print(f"Insertado nuevo emp {id_emp}: {p['nombres']}")

    conn.commit()
    print("¡Base de datos enriquecida exitosamente con 40 servidores penitenciarios!")

if __name__ == "__main__":
    main()
