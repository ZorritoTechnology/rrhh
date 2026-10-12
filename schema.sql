-- =====================================================================
-- ESQUEMA DE BASE DE DATOS RELACIONAL: CONTROL DE RRHH / ASISTENCIA
-- Motor recomendado: PostgreSQL / SQLite / MySQL (ANSI SQL compatible)
-- =====================================================================

-- 1. TABLAS MAESTRAS / CATÁLOGOS BASE

-- Sedes y Oficinas Regionales (Ej: OR 700 - OFICINA REGIONAL NOR ORIENTE)
CREATE TABLE IF NOT EXISTS oficinas_regionales (
    id_or INTEGER PRIMARY KEY, -- Ej: 700
    nombre VARCHAR(150) NOT NULL
);

-- Establecimientos Penitenciarios / Sedes (Ej: Ubic 722 - EP. MUJERES IQUITOS)
CREATE TABLE IF NOT EXISTS establecimientos (
    id_establecimiento INTEGER PRIMARY KEY, -- Código UBIC, ej: 722
    id_or INTEGER NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    FOREIGN KEY (id_or) REFERENCES oficinas_regionales(id_or)
);

-- Regímenes Laborales (D.L. 276, Ley 29709, D.L. 1057 - CAS, etc.)
CREATE TABLE IF NOT EXISTS regimenes_laborales (
    id_regimen SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL, -- 'LEY_29709', 'DL_276', 'DL_1057'
    nombre VARCHAR(100) NOT NULL
);

-- Maestro de Empleados / Servidores
CREATE TABLE IF NOT EXISTS empleados (
    id_empleado SERIAL PRIMARY KEY,
    codigo_servidor VARCHAR(20) UNIQUE NOT NULL, -- Ej: '099132', '103097'
    dni VARCHAR(15) UNIQUE,                      -- DNI (8 dígitos)
    apellidos_nombres VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. REPORTES MENSUALES (ENCABEZADOS DE CIERRE)
CREATE TABLE IF NOT EXISTS reportes_cierre_mensual (
    id_reporte SERIAL PRIMARY KEY,
    anio INTEGER NOT NULL,                       -- Ej: 2025, 2026
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12), -- 1 al 12 (Setiembre=9, Octubre=10, etc.)
    id_establecimiento INTEGER NOT NULL,         -- 722
    id_responsable INTEGER NOT NULL,             -- Referencia a empleado (directora/encargada)
    total_trabajadores INTEGER DEFAULT 0,
    fecha_cierre DATE,
    observaciones_generales TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_reporte_mensual UNIQUE (anio, mes, id_establecimiento),
    FOREIGN KEY (id_establecimiento) REFERENCES establecimientos(id_establecimiento),
    FOREIGN KEY (id_responsable) REFERENCES empleados(id_empleado)
);

-- 3. DETALLE DE ASISTENCIA Y PLANTILLA DEL MES (HOJA PRINCIPAL 1)
CREATE TABLE IF NOT EXISTS asistencia_mensual_personal (
    id_asistencia SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    id_regimen INTEGER,
    nivel VARCHAR(20),                           -- Ej: 'T1', 'T2', 'S1', 'STF', 'SNR'
    cargo_estructural VARCHAR(200),              -- Ej: 'AGENTE DE SEGURIDAD II'
    estado_laboral VARCHAR(50) DEFAULT 'ACTIVO', -- 'ACTIVO', 'ABANDONO', 'EXTINCION CONTRATO'
    modalidad_laboral VARCHAR(50) DEFAULT 'PRESENCIAL', -- 'PRESENCIAL', 'NO APLICA'
    direccion_oficina VARCHAR(100),              -- Ej: 'DIRECCION', 'SEGURIDAD PENITENCIARIA'
    jefatura_area VARCHAR(100),                  -- Ej: 'SEGURIDAD PENITENCIARIA', 'TRATAMIENTO'
    cargo_funcion VARCHAR(100),                  -- Ej: 'DIRECTORA', 'AGENTE DE SEGURIDAD'
    area_clasificacion VARCHAR(10),              -- 'ADM', 'SEG', 'TRA'
    horario_laboral VARCHAR(50),                 -- '08:00 - 17:00', '24 x 48'
    fecha_ingreso_eepp DATE,
    resolucion_documento VARCHAR(250),
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_regimen) REFERENCES regimenes_laborales(id_regimen)
);

-- 4. SUB-REGISTROS DE NOVEDADES MENSUALES (HOJAS 2 a 11)

-- Hoja 2: Funcionarios y Directivos
CREATE TABLE IF NOT EXISTS reporte_funcionarios (
    id_funcionario SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    cargo_funcion VARCHAR(100) NOT NULL,
    nivel VARCHAR(20),                           -- Ej: 'S4', 'F-1'
    fecha_inicio_funciones DATE,
    resolucion_documento VARCHAR(250),
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Hoja 3: Sanciones disciplinarias
CREATE TABLE IF NOT EXISTS reporte_sanciones (
    id_sancion SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    tipo_sancion VARCHAR(100),
    fecha_inicio DATE,
    fecha_termino DATE,
    dias INTEGER,
    tiempo_que_resuelve VARCHAR(100),
    resolucion_documento VARCHAR(250),
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Hoja 4: Renuncias
CREATE TABLE IF NOT EXISTS reporte_renuncias (
    id_renuncia SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    a_partir_del DATE,
    carta_fecha DATE,
    fecha_recepcion DATE,
    motivos TEXT,
    ultimo_dia_laborado DATE,
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Hoja 5: Reincorporaciones
CREATE TABLE IF NOT EXISTS reporte_reincorporaciones (
    id_reincorporacion SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    fecha_inicio_inactividad DATE,
    motivo_inactividad TEXT,
    fecha_reincorporacion DATE,
    motivo_reincorporacion TEXT,
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Hojas 6-7: Desplazamientos / Rotaciones / Traslados
CREATE TABLE IF NOT EXISTS reporte_desplazamientos (
    id_desplazamiento SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    id_establecimiento_origen INTEGER,
    id_establecimiento_destino INTEGER,
    area VARCHAR(100),
    cargo_funcion VARCHAR(100),
    fecha_desplazamiento DATE,
    documento_resolucion VARCHAR(250),
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_establecimiento_origen) REFERENCES establecimientos(id_establecimiento),
    FOREIGN KEY (id_establecimiento_destino) REFERENCES establecimientos(id_establecimiento)
);

-- Licencias (Enfermedad, Onomástico, Particular, etc.)
CREATE TABLE IF NOT EXISTS reporte_licencias (
    id_licencia SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,                  -- 'ENFERMEDAD', 'ONOMASTICO', 'FALLECIMIENTO', etc.
    entidad VARCHAR(50),                        -- 'ESSALUD', 'PARTICULAR', 'INPE'
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE NOT NULL,
    dias INTEGER NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Vacaciones
CREATE TABLE IF NOT EXISTS reporte_vacaciones (
    id_vacacion SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    periodo VARCHAR(50),                        -- Ej: '2023-2024', '2024-2025', '2025'
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE NOT NULL,
    dias INTEGER NOT NULL,
    observaciones TEXT,                         -- Ej: 'Adelanto de vacaciones, le resta 29 dias'
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Tardanzas (en minutos)
CREATE TABLE IF NOT EXISTS reporte_tardanzas (
    id_tardanza SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    minutos INTEGER NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Permisos Particulares (en minutos)
CREATE TABLE IF NOT EXISTS reporte_permisos (
    id_permiso SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    minutos INTEGER NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Inasistencias Injustificadas (en días y detalle de fechas)
CREATE TABLE IF NOT EXISTS reporte_inasistencias (
    id_inasistencia SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    dias INTEGER NOT NULL,
    fechas_detalle VARCHAR(255),                -- Ej: '15, 28, 29, 30 y 31'
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Hoja 12: Trabajadores No Registrados / Observados
CREATE TABLE IF NOT EXISTS reporte_no_registrados (
    id_no_reg SERIAL PRIMARY KEY,
    id_reporte INTEGER NOT NULL,
    dni VARCHAR(15),
    apellidos_nombres VARCHAR(200),
    regimen VARCHAR(50),
    cargo_funcion VARCHAR(100),
    area VARCHAR(100),
    fecha_ingreso DATE,
    documento VARCHAR(250),
    observaciones TEXT,
    FOREIGN KEY (id_reporte) REFERENCES reportes_cierre_mensual(id_reporte) ON DELETE CASCADE
);

-- Índices recomendados para búsquedas rápidas por empleado y período
CREATE INDEX IF NOT EXISTS idx_asistencia_rep_emp ON asistencia_mensual_personal (id_reporte, id_empleado);
CREATE INDEX IF NOT EXISTS idx_licencias_rep_emp ON reporte_licencias (id_reporte, id_empleado);
CREATE INDEX IF NOT EXISTS idx_vacaciones_rep_emp ON reporte_vacaciones (id_reporte, id_empleado);
CREATE INDEX IF NOT EXISTS idx_tardanzas_rep_emp ON reporte_tardanzas (id_reporte, id_empleado);

