# Contexto y Reglas para Agentes IA - Sistema RRHH NexGen

Este archivo proporciona contexto esencial para cualquier agente de inteligencia artificial que continúe el desarrollo o mantenimiento de este repositorio.

## 1. Visión General del Proyecto
- **Entidad:** Instituto Nacional Penitenciario (INPE) - Oficina Regional Nor Oriente (700).
- **Establecimiento:** EP Mujeres Iquitos (Código UBIC 722).
- **Nombre de la Aplicación:** RRHH NexGen - Sistema Modular de Gestión de Personal, Asistencia, Vacaciones y Compensaciones.
- **Stack Técnico:**
  - **Backend:** Python 3.12+ con FastAPI.
  - **Plantillas / Frontend:** Jinja2 con HTML5 semántico, diseño Glassmorphism / Dark Mode y CSS modular (archivo base `app/static/premium.css`).
  - **Base de Datos:** SQLite (`rrhh_control.db`), definida en `schema.sql` e inicializaciones modulares (`init_compensaciones.py`).

## 2. Marco Normativo Institucional Obligatorio
Cualquier cambio o extensión en la lógica de negocio debe respetar los siguientes reglamentos:
1. **Directiva DI-003-2023-INPE-OGA (Control de Asistencia y Permanencia):**
   - Rige el registro mensual de asistencia y las 12 hojas oficiales (asistencia general, directivos/funcionarios, sanciones disciplinarias, licencias, vacaciones, tardanzas en minutos, permisos particulares, inasistencias injustificadas, personal no registrado).
2. **Lineamiento LI-001-2023-INPE-OGA y RD N° 146-2023-INPE/OGA (Compensación de Jornada 24x48):**
   - **Personal:** Personal de Seguridad Penitenciaria bajo jornada atípica 24x48.
   - **Tope Anual:** Máximo computable de **16 días de 24 horas continuas** por año fiscal (ej. 2026).
   - **Regla de Indivisibilidad:** Los días son **no fraccionables** (se compensan turnos completos de 24 horas).
   - **Anticipación:** Las solicitudes (Anexo 01) deben presentarse con un mínimo de **5 días calendario de anticipación**.
   - **Reporte Oficial:** La matriz anual mes a mes corresponde al **Anexo 03**.
3. **Regímenes Laborales Reconocidos:**
   - Ley N° 29709 (Ley de la Carrera Especial Pública Penitenciaria).
   - D.L. 276 (Régimen de la Carrera Administrativa).
   - D.L. 1057 (Contratación Administrativa de Servicios - CAS).

## 3. Estructura de Módulos (`app/modules/`)
- `dashboard/`: Router y estadísticas globales del establecimiento.
- `asistencia/`: Cierres mensuales, plantillas de asistencia y reportes de incidencias.
- `vacaciones/`: Saldos y control de goce vacacional (30 días anuales según régimen).
- `compensacion/`: Módulo de Compensación 24x48:
  - `repository.py`: Consultas y matriz mensualizada (Anexo 03).
  - `service.py`: Validaciones de negocio (saldo disponible, 5 días de anticipación, jornada completa).
  - `router.py`: Endpoints para ver matriz (`/compensacion`), registrar solicitud (`/compensacion/solicitud`), ver historial (`/compensacion/solicitudes`) y generar papeleta imprimible (`/compensacion/papeleta/{id}`).
- `empleados/`: Padrón y gestión de servidores.
- `reportes/`: Vistas consolidadas para exportación.

## 4. Convenciones de Código y Buenas Prácticas
1. **Separación de CSS y Jinja2:**
   - **PROHIBIDO** incrustar bloques condicionales Jinja2 `{% if ... %}` dentro de los valores de propiedades de estilos en línea (ej. `style="color: {% if ... %}#fff{% endif %}"`). Esto causa errores de sintaxis en los analizadores CSS del IDE.
   - **CORRECTO:** Usar clases CSS condicionales en el atributo `class` (ej. `class="cell-mes {% if row.m_1 != '-' %}cell-mes-active{% else %}cell-mes-empty{% endif %}"`) y definir las clases en un bloque `<style>` o en `premium.css`.
2. **Consultas SQL Seguras:**
   - Utilizar siempre `get_connection()` o el context manager `get_db_cursor()` de `app.core.database`.
   - Parametrizar todas las consultas SQL con `?` para prevenir inyecciones SQL.
3. **Rutas y URLs:**
   - Mantener prefijos modulares en routers (`prefix="/compensacion"`, etc.).
   - Utilizar rutas relativas o absolutas consistentes con FastAPI.

## 5. Cómo Ejecutar el Proyecto
- **Servidor de Desarrollo:**
  ```powershell
  python -m uvicorn app.main:app --reload --port 8000
  ```
  O directamente:
  ```powershell
  python app/main.py
  ```
- **Documentación Completa:** Consultar [docs/SYSTEM_DOCUMENTATION.md](file:///c:/Users/Ander/Documents/Aplicaciones/rrhh/docs/SYSTEM_DOCUMENTATION.md).
