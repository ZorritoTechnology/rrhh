# Documentación Técnica del Sistema RRHH NexGen
**Establecimiento Penitenciario Mujeres Iquitos (Sede 722) - INPE**

---

## 1. Información General
- **Nombre:** Sistema de Recursos Humanos y Control de Asistencia (RRHH NexGen)
- **Ámbito:** Establecimiento Penitenciario Mujeres Iquitos (UBIC 722), Oficina Regional Nor Oriente (700), Instituto Nacional Penitenciario (INPE).
- **Objetivo:** Automatizar y gestionar de forma fidedigna la planilla de asistencia, el control mensualizado de novedades, el control de saldos vacacionales y la compensación de jornadas especiales de seguridad 24x48 en estricto cumplimiento de la normativa institucional vigente.

---

## 2. Marco Normativo Institucional

### 2.1. Directiva DI-003-2023-INPE-OGA
*Lineamientos para el control de asistencia, permanencia y desplazamiento de los servidores del INPE.*
- Regula los cierres mensuales de asistencia (enero a diciembre).
- Establece la generación de **12 reportes y hojas de incidencias**:
  1. Asistencia mensual y plantilla general del personal.
  2. Funcionarios y personal directivo.
  3. Sanciones disciplinarias ejecutadas en el mes.
  4. Licencias con y sin goce de haber (maternidad, enfermedad, capacitación, etc.).
  5. Goce y adelanto de vacaciones.
  6. Tardanzas acumuladas en minutos.
  7. Permisos particulares en minutos.
  8. Inasistencias injustificadas con detalle exacto de días y fechas.
  9. Comisiones de servicio y desplazamientos.
  10. Personal no registrado o en proceso de alta/baja.

### 2.2. Lineamiento LI-001-2023-INPE-OGA y RD N° 146-2023-INPE/OGA
*Compensación de la jornada laboral atípica de 24x48 horas del personal de seguridad penitenciaria.*
- **Universo:** Servidores penitenciarios asignados a la jornada de 24 horas continuas de servicio por 48 horas de descanso.
- **Tope Anual:** Hasta un máximo computable de **16 días de 24 horas por año fiscal**.
- **Indivisibilidad:** Los días a compensar son estrictamente **no fraccionables** (jornadas completas de 24 horas).
- **Anticipación de Solicitud:** Mínimo **5 días calendario antes** del turno de guardia a compensar, presentando el **Formato Anexo N° 01 (REG-010-URH)** con el visto bueno del Jefe Inmediato y Especialista de Personal.
- **Reporte Oficial:** La administración consolida anualmente el **Anexo N° 03: Reporte Mensualizado de Compensación**.

### 2.3. Regímenes Laborales
- **Ley N° 29709:** Ley de la Carrera Especial Pública Penitenciaria (servidores penitenciarios de seguridad y tratamiento).
- **Decreto Legislativo N° 276:** Régimen administrativo clásico de la administración pública.
- **Decreto Legislativo N° 1057 (CAS):** Contratos administrativos de servicios.

---

## 3. Arquitectura del Software

```
rrhh/
├── app/
│   ├── core/
│   │   ├── config.py           # Configuración general y rutas de base de datos
│   │   └── database.py         # Conexión SQLite con row_factory y contexto transaccional
│   ├── modules/
│   │   ├── asistencia/         # Registro de asistencias, cierres mensuales, plantillas
│   │   │   ├── router.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── models.py
│   │   ├── compensacion/       # Módulo 24x48 (Anexo 01 y Anexo 03)
│   │   │   ├── router.py       # Endpoints Web (GET/POST /compensacion/...)
│   │   │   ├── repository.py   # Consultas SQL y agregación de matriz anual
│   │   │   └── service.py      # Validaciones normativas (saldo, anticipación, etc.)
│   │   ├── vacaciones/         # Saldos y solicitudes de descanso físico anual
│   │   ├── empleados/          # Catálogo de personal, CIP, DNI, cargos, regímenes
│   │   ├── dashboard/          # Estadísticas globales y métricas clave
│   │   └── reportes/           # Exportación consolidada
│   ├── static/
│   │   └── premium.css         # Sistema de diseño (Glassmorphism, Dark UI, badges)
│   ├── templates/              # Vistas renderizadas con Jinja2
│   │   ├── base.html           # Estructura maestra con navegación lateral
│   │   ├── compensacion/       # Plantillas del módulo de compensaciones
│   │   │   ├── matriz_anexo3.html         # Vista oficial del Anexo 03
│   │   │   ├── form_solicitud.html        # Formulario oficial Anexo 01
│   │   │   ├── historial_solicitudes.html # Histórico y seguimiento
│   │   │   └── papeleta_anexo1.html       # Papeleta oficial apta para imprimir
│   │   ├── asistencia/
│   │   └── vacaciones/
│   └── main.py                 # Instancia FastAPI y registro de routers
├── docs/                       # Documentación técnica y manuales
├── rrhh_control.db             # Base de datos SQLite activa
├── schema.sql                  # Definición del esquema relacional
├── init_compensaciones.py      # Inicializador y seed del módulo de compensaciones
├── AGENTS.md                   # Instrucciones para agentes de IA
└── README.md                   # Resumen del proyecto
```

---

## 4. Base de Datos Relacional

### Tablas Principales
1. **`empleados`**: Maestro de personal (`id_empleado`, `codigo_servidor`, `dni`, `apellidos_nombres`).
2. **`establecimientos`** y **`oficinas_regionales`**: Ubicación institucional (EP Mujeres Iquitos 722, OR Nor Oriente 700).
3. **`regimenes_laborales`**: Catálogo de regímenes (Ley 29709, D.L. 276, D.L. 1057).
4. **`reportes_cierre_mensual`**: Encabezados de cierres por mes/año.
5. **`asistencia_mensual_personal`**: Detalle del personal en cada mes (cargo, nivel, horario `24 x 48`, área `SEG`, `ADM`, `TRA`).
6. **`resoluciones_compensacion`**: Resoluciones que autorizan compensaciones anuales (ej. RD N° 146-2023-INPE/OGA).
7. **`saldos_compensacion`**: Saldo individual por servidor por año fiscal (tope de 16 días, consumidos, disponibles).
8. **`solicitudes_compensacion`**: Registro de solicitudes (Anexo 01) con fecha de solicitud, fecha del turno a compensar de 24h, estado y observaciones.

---

## 5. Reglas de Negocio Clave

### Compensación de Jornada 24x48 (`app/modules/compensacion/service.py`)
1. **Verificación de Saldo:** Antes de autorizar una solicitud, el sistema consulta `saldos_compensacion` para el año fiscal (`dias_disponibles > 0`).
2. **Anticipación de Solicitud:** La directiva exige un mínimo de 5 días de diferencia entre `fecha_solicitud` y `fecha_compensacion`. Si se registra con menor antelación, el sistema registra una observación automática para regularización.
3. **Prevención de Duplicidad:** No se permite duplicar solicitudes para el mismo servidor en la misma fecha de compensación.
4. **Actualización Automática:** Al aprobarse una solicitud, el saldo utilizado se incrementa y el saldo disponible se recalcula atómicamente.

---

## 6. Convenciones de Frontend y Estilo
- **Diseño:** Dark Mode con Glassmorphism (`rgba(255, 255, 255, 0.05)`, bordes sutiles y acentos cromáticos).
- **Separación Limpia de Lógica y Estilos:**
  - Evitar colocar lógica Jinja dentro de propiedades CSS en atributos `style=""`.
  - Utilizar clases CSS dedicadas (`.cell-mes-active`, `.cell-mes-empty`) y aplicar Jinja condicional en el atributo `class="..."`.

---

## 7. Ejecución y Despliegue Local
Para iniciar el servidor en modo desarrollo:
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
La aplicación estará disponible en:
- Panel General: `http://127.0.0.1:8000/`
- Módulo de Compensaciones (Anexo 03): `http://127.0.0.1:8000/compensacion`
- Nueva Solicitud (Anexo 01): `http://127.0.0.1:8000/compensacion/solicitud`
- Documentación Interactiva de la API: `http://127.0.0.1:8000/docs`
