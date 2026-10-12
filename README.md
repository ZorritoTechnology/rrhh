# RRHH NexGen - Control de Asistencia y Compensaciones (INPE)

Sistema modular desarrollado en **FastAPI** y **Jinja2** para la gestión de recursos humanos, control de asistencia mensual conforme a la **Directiva DI-003-2023-INPE-OGA**, saldos de vacaciones y compensación de jornada especial 24x48 según el **Lineamiento LI-001-2023-INPE-OGA** para el **Establecimiento Penitenciario Mujeres Iquitos (Sede 722)**.

---

## Características Principales
- **Módulo de Compensación 24x48:**
  - Matriz anual mensualizada oficial (**Anexo N° 03**).
  - Formulario de solicitud y papeleta oficial (**Anexo N° 01**).
  - Control de tope anual de 16 días (no fraccionables) y regla de 5 días de anticipación.
- **Módulo de Asistencia Mensual:**
  - Reportes de cierre mensualizados y desglose de 12 hojas de incidencias.
  - Registro de asistencia para personal de seguridad, tratamiento y administración.
- **Módulo de Vacaciones:**
  - Saldos acumulados y alertas de días excedidos por régimen laboral.
- **Panel Ejecutivo (Dashboard):**
  - Métricas clave, indicadores de servicio y alertas de personal.

---

## Documentación para Desarrolladores y Agentes IA
- [docs/SYSTEM_DOCUMENTATION.md](file:///c:/Users/Ander/Documents/Aplicaciones/rrhh/docs/SYSTEM_DOCUMENTATION.md): Arquitectura, modelo de datos relacional y reglas normativas institucionales.
- [AGENTS.md](file:///c:/Users/Ander/Documents/Aplicaciones/rrhh/AGENTS.md): Reglas, convenciones y directrices para agentes de IA para dar continuidad a las tareas del proyecto.

---

## Cómo Iniciar la Aplicación

1. **Instalar dependencias necesarias:**
   ```powershell
   pip install fastapi uvicorn jinja2
   ```

2. **Ejecutar el servidor local:**
   ```powershell
   python -m uvicorn app.main:app --reload --port 8000
   ```

3. **Acceso Web:**
   - Panel Principal: [http://localhost:8000](http://localhost:8000)
   - Módulo de Compensaciones: [http://localhost:8000/compensacion](http://localhost:8000/compensacion)
   - API Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
