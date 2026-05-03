# COSTOS 2.0 - Especificación Completa de Desarrollo
## Sistema de Monitoreo Especializado de Jitomate Saladette/Huaje en Centrales de Abasto

---

## ÍNDICE
1. Objetivo y Alcance
2. Cambio Central del Modelo
3. Arquitectura Actual y Archivos Clave
4. Modelo de Datos y Migraciones
5. Cambios en el Backend (API)
6. Cambios en el Frontend (PWA)
7. Cambios en el Admin Web
8. Soporte Offline
9. Variaciones, Alertas y Criterios
10. Plan de Implementación por Fases
11. Checklist de Aceptación

---

## 1. OBJETIVO Y ALCANCE

### Transformación Principal
**De:** Sistema general de precios para múltiples productos agrícolas/pecuarios
**A:** Monitor especializado de jitomate Saladette/huaje en centrales de abasto

### Valores Fijos del Sistema
- **Producto:** Jitomate
- **Variedad:** Saladette/huaje
- **Unidad:** kg
- **Tipo de Precio:** Reparto en bodega
- **Cortes:** Matutino y Mediodía
- **Calidades:** Primera, Segunda, Tercera
- **Ubicación:** Centrales de abasto / mercados mayoristas autorizados
- **Tipo de Usuario Operativo:** CAPTURISTA (único)

### Salida Esperada
- Captura por central, fecha, corte y tres calidades
- Control administrativo: Catálogo, propuestas, reportes, mapa, dashboard, alertas, exportables
- Sistema offline con sincronización

---

## 2. CAMBIO CENTRAL DEL MODELO

| Elemento | ANTES | AHORA |
|----------|-------|-------|
| **Productos** | Múltiples agrícolas/pecuarios | Jitomate fijo Saladette/huaje |
| **Ubicación** | Mercados DENUE/locales/públicos | Centrales de abasto autorizadas |
| **Captura** | Un precio por producto | Un reporte con 3 calidades |
| **Estructura** | Precio individual | Central + Fecha + Corte + 3 Calidades |
| **Usuario** | Múltiples tipos capturista | Un solo tipo: CAPTURISTA |
| **Pantalla KPIs** | Mercados, productos, reportes | Centrales, reportes, capturas hoy, último corte |
| **Navegación** | Mercados / Mis Mercados | Centrales / Mis Centrales |

---

## 3. ESTRUCTURA DE BASE DE DATOS

### 3.1 TABLAS EXISTENTES A MODIFICAR
```sql
-- usuarios
-- Cambio: Mantener estructura existente pero asegurar rol = 'CAPTURISTA'
-- Sin selector de tipo de capturista en PWA

-- catalogo_mercados
-- RENOMBRAR A: catalogo_centrales
-- Cambios de campos:
--   - nombre_mercado → nombre_central
--   - tipo_mercado → tipo (tipo de central)
--   - Agregar: visible_pwa (boolean, default true)
--   - Agregar: estatus (enum: 'autorizado', 'pendiente', 'inactivo')
```

### 3.2 TABLAS NUEVAS REQUERIDAS

#### 3.2.1 catalogo_centrales (renombrada de catalogo_mercados)
```sql
CREATE TABLE catalogo_centrales (
  id SERIAL PRIMARY KEY,
  nombre_central VARCHAR(255) NOT NULL,
  tipo VARCHAR(100),
  municipio VARCHAR(100),
  estado VARCHAR(100),
  latitud DECIMAL(10, 8),
  longitud DECIMAL(11, 8),
  estatus ENUM('autorizado', 'pendiente', 'inactivo') DEFAULT 'autorizado',
  visible_pwa BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.2.2 capturista_centrales (Mis Centrales por usuario)
```sql
CREATE TABLE capturista_centrales (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
  central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id),
  es_favorita BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(usuario_id, central_id)
);
```

#### 3.2.3 propuestas_centrales (Propuestas autorizables)
```sql
CREATE TABLE propuestas_centrales (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
  nombre_central VARCHAR(255) NOT NULL,
  tipo VARCHAR(100),
  municipio VARCHAR(100),
  estado VARCHAR(100),
  latitud DECIMAL(10, 8),
  longitud DECIMAL(11, 8),
  estatus ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
  motivo_rechazo TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.2.4 reportes_jitomate (Cabecera de reportes)
```sql
CREATE TABLE reportes_jitomate (
  id SERIAL PRIMARY KEY,
  central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id),
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
  fecha DATE NOT NULL,
  corte ENUM('matutino', 'mediodía') NOT NULL,
  hora_captura TIMESTAMP NOT NULL,
  captura_tardia BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(central_id, fecha, corte)
);
```

**Restricción Crítica:** `UNIQUE(central_id, fecha, corte)` - Evita duplicados

#### 3.2.5 precios_jitomate_calidad (Detalles de las 3 calidades)
```sql
CREATE TABLE precios_jitomate_calidad (
  id SERIAL PRIMARY KEY,
  reporte_jitomate_id INTEGER NOT NULL REFERENCES reportes_jitomate(id),
  calidad ENUM('primera', 'segunda', 'tercera') NOT NULL,
  precio DECIMAL(10, 2),
  sin_dato BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(reporte_jitomate_id, calidad)
);
```

---

## 4. CAMBIOS EN EL BACKEND (API)

### 4.1 ARQUITECTURA
- Framework: FastAPI + PostgreSQL con psycopg2
- Base de código: `backend/app/routes/*.py`

### 4.2 NUEVOS ENDPOINTS

#### Catálogo de Centrales (Público/PWA)
```
GET /api/centrales
  - Retorna centrales con estatus='autorizado' Y visible_pwa=true
  - Filtros: municipio, estado, tipo
  - Response: [{ id, nombre_central, tipo, municipio, estado, latitud, longitud }]

GET /api/centrales/:id
  - Detalles de una central específica
  - Response: { id, nombre_central, tipo, municipio, estado, latitud, longitud }
```

#### Mis Centrales (Por Usuario Capturista)
```
GET /api/capturista/centrales
  - Retorna centrales asignadas al usuario actual
  - Response: [{ id, nombre_central, tipo, municipio, estado, es_favorita }]

POST /api/capturista/centrales
  - Agregar una central a "Mis Centrales"
  - Body: { central_id }
  - Validación: Solo centrales con estatus='autorizado' Y visible_pwa=true

DELETE /api/capturista/centrales/:id
  - Quitar una central de "Mis Centrales"
```

#### Reportes de Jitomate (Captura)
```
POST /api/jitomate/reportes
  - Crear reporte con 3 calidades
  - Body: {
      central_id,
      fecha,
      corte: 'matutino' | 'mediodía',
      precios_por_calidad: {
        primera: { precio, sin_dato },
        segunda: { precio, sin_dato },
        tercera: { precio, sin_dato }
      }
    }
  - Retorna: { id, reporte_jitomate_id, precios_jitomate_calidad_ids }

GET /api/jitomate/historial
  - Retorna reportes del usuario actual
  - Filtros: fecha_inicio, fecha_fin, central_id, corte
  - Response: [{ reporte_id, central, fecha, corte, primera, segunda, tercera, hora_captura }]

GET /api/admin/jitomate/reportes
  - Tabla filtrable para admin
  - Filtros: fecha, corte, central_id, calidad, capturista_id, captura_tardía
  - Retorna: columnas mínimas (ver tabla abajo)
```

#### Propuestas de Centrales
```
POST /api/centrales/propuestas
  - Usuario propone nueva central
  - Body: { nombre_central, tipo, municipio, estado, latitud, longitud }

GET /api/admin/propuestas-centrales
  - Admin lista propuestas
  - Response: [{ id, usuario, nombre_central, tipo, municipio, estado, estatus, fecha }]

POST /api/admin/propuestas-centrales/:id/autorizar
  - Admin autoriza y crea registro en catalogo_centrales
  - Body: { }
  - Acción: Inserta en catalogo_centrales con estatus='autorizado'

POST /api/admin/propuestas-centrales/:id/rechazar
  - Admin rechaza propuesta
  - Body: { motivo_rechazo }
```

#### Análisis y Dashboard (Admin)
```
GET /api/admin/jitomate/dashboard
  - Retorna KPIs para dashboard
  - Response: {
      total_centrales,
      reportes_hoy,
      cobertura: percentage,
      promedio_primera, min_primera, max_primera,
      promedio_segunda, min_segunda, max_segunda,
      promedio_tercera, min_tercera, max_tercera,
      variacion_promedio,
      alertas: [ { tipo, central, calidad, valor } ]
    }

GET /api/admin/jitomate/mapa
  - Retorna centrales para mapeo
  - Response: [{ id, nombre_central, latitud, longitud, 
      tiene_reporte_hoy, color_alerta, propuestas_pendientes }]

GET /api/admin/jitomate/alertas
  - Lista de alertas generadas
  - Filtros: tipo, fecha, central_id, calidad
  - Response: [{ tipo, descripcion, central, calidad, precio, fecha }]

GET /api/admin/jitomate/exportar
  - Exporta CSV/Excel
  - Filtros: fecha_inicio, fecha_fin, formato
  - Columnas: Fecha, Corte, Central, Primera, Segunda, Tercera, Capturista, Hora, Variación
```

### 4.3 VALIDACIONES BACKEND (CRÍTICAS)

1. **Central autorizada y visible_pwa:** Solo permitir captura en centrales con `estatus='autorizado'` Y `visible_pwa=true`

2. **Fecha + Corte no duplicados:** `UNIQUE(central_id, fecha, corte)` en DB

3. **Precio >= 0:** No permitir precios negativos

4. **Precio 0 solo con sin_dato:** Si `sin_dato=true`, precio debe ser NULL. Si `sin_dato=false`, precio debe ser >= 0

5. **3 Calidades presentes:** Cada reporte debe tener entrada para primera, segunda y tercera (con sin_dato=true si no hay precio)

6. **Captura tardía:** Marcar `captura_tardia=true` si la hora está fuera de horario esperado (ej: después de las 14:00 para matutino)

7. **Transacciones:** Crear cabecera + 3 detalles como transacción atómica

### 4.4 ARCHIVOS BACKEND A MODIFICAR

- `backend/app/routes/mercados.py` → Renombrar a `backend/app/routes/centrales.py` o mantener pero cambiar lógica
- `backend/app/routes/catalogos.py` → Actualizar para `catalogo_centrales`
- `backend/app/routes/admin_auth.py` → Agregar endpoints de admin para jitomate
- `backend/app/database.py` → Actualizar modelos ORM
- `backend/app/schemas.py` → Agregar esquemas Pydantic nuevos
- Crear: `backend/app/routes/jitomate.py` (nueva ruta)

### 4.5 NOTA DE COMPATIBILIDAD
Si se reutiliza `/api/mercados/precio` por compatibilidad, documentar que ahora representa un reporte de jitomate, no un precio individual.

---

## 5. CAMBIOS EN EL FRONTEND (PWA)

### 5.1 PANTALLA INICIO (HomeView.vue)

#### Cambios Principales:
1. **Header:** Conservar identidad COSTOS, iconografía y textos orientados a jitomate
2. **KPIs Nuevos:**
   - Total de Centrales
   - Reportes de Hoy
   - Capturas de Hoy
   - Último Corte (fecha, hora, promedio precios)
3. **Acciones Rápidas:** Botones para "Mis Centrales" y "Capturar Jitomate"
4. **Actividad Reciente:** Últimos reportes de jitomate con central, fecha, corte, calidades
5. **Empty State:** Si no hay datos, mostrar instrucción clara con CTA a capturar

### 5.2 NAVEGACIÓN

#### Menú Lateral (Drawer/Sidebar)
Cambiar de:
- Mercados → **Mis Centrales** (item activo por defecto)
- Perfil con selector de rol → **Perfil** (sin selector, rol fijo CAPTURISTA)
- Eliminar módulos no aplicables
- Mantener: Inicio, Mi Perfil, Mis Centrales, Historial
- Agregar: Versión 2.0 (visual/indicador)

#### Navegación Inferior (Bottom Tabs)
- Inicio
- Centrales
- Historial

### 5.3 MIS CENTRALES (MercadosView.vue → actualizar)

#### Cambios:
1. **Título:** "Mis Centrales" en lugar de "Mis Mercados"
2. **Tabs:** Principal, Favoritos, Propuestas (mantener estructura)
3. **Buscar y Agregar Central:**
   - Consumir `GET /api/centrales` (solo visible_pwa=true)
   - Filtrar por municipio, estado, tipo
   - Agregar con `POST /api/capturista/centrales`
4. **Tarjeta de Central:**
   - Mostrar: nombre_central, tipo, municipio, estado
   - Acciones: Quitar, Detalle, Capturar
   - No permitir captura en centrales inactivas
5. **Favoritos:** Persistir `es_favorita` en BD

### 5.4 CAPTURAR JITOMATE (Nueva Vista)

#### Estructura del Formulario
```
[Encabezado de Reporte]
  - Central (dropdown de Mis Centrales) [Requerido]
  - Fecha (picker, default hoy) [Requerido]
  - Corte (radio: Matutino / Mediodía) [Requerido]
  - Hora Real (auto-capturada o seleccionable)

[Valores Fijos - Solo Lectura]
  - Producto: Jitomate
  - Variedad: Saladette/huaje
  - Unidad: kg
  - Tipo Precio: Reparto en bodega

[Tres Calidades]
  Cada calidad en su propia fila/card:
  
  [Primera Calidad]
    - Precio (number input) [opcional si sin_dato]
    - ☐ Sin Dato (checkbox)
  
  [Segunda Calidad]
    - Precio (number input) [opcional si sin_dato]
    - ☐ Sin Dato (checkbox)
  
  [Tercera Calidad]
    - Precio (number input) [opcional si sin_dato]
    - ☐ Sin Dato (checkbox)

[Acciones]
  - [Guardar Reporte] (online u offline)
  - [Cancelar]
```

#### Validaciones PWA
- No permitir precio negativo
- Advertencia si central no está en visible_pwa=true
- Advertencia si ya existe reporte para central+fecha+corte
- Indicador visual de modo offline

#### Guardado Online/Offline
- **Online:** `POST /api/jitomate/reportes` → Éxito inmediato
- **Offline:** Guardar en IndexedDB, marcar en cola de sync

### 5.5 HISTORIAL (HistorialView.vue → actualizar)

#### Cambios:
1. **Título:** Historial de Reportes de Jitomate
2. **Filtros:** Fecha inicio/fin, Central, Corte, Calidad
3. **Tabla:**
   - Columnas: Central, Fecha, Corte, Primera, Segunda, Tercera, Capturista (si aplica), Hora
   - Ordenable por fecha descendente (más reciente primero)
4. **Detalle:** Al hacer clic, mostrar detalles completos del reporte
5. **Acciones:** Opción de eliminar (solo propio usuario, con confirmación)

### 5.6 PERFIL (ProfileView.vue → actualizar)

#### Cambios:
1. **Rol:** Mostrar "Capturista" como texto (no selector)
2. **No mostrar selector de tipo de capturista**
3. **Información Central:**
   - Email, Nombre, Teléfono (existente)
   - Agregar: Central asignada (si aplica)

### 5.7 ARCHIVOS A MODIFICAR

- `pwacostos/src/views/RegisterView.vue` - Ajustar lenguaje a centrales
- `pwacostos/src/views/ProfileView.vue` - Quitar selector de rol
- `pwacostos/src/views/MercadosView.vue` - Renombrar/actualizar a centrales
- `pwacostos/src/views/HistorialView.vue` - Cambiar a historial de jitomate
- **Crear:** `pwacostos/src/views/CapturaJitomateView.vue` - Nueva vista de captura
- `pwacostos/src/services/mercados.service.ts` - Actualizar a centrales.service.ts
- `pwacostos/src/services/offline.ts` - Agregar nuevas entidades
- `pwacostos/src/types/index.ts` - Nuevos tipos
- `pwacostos/src/router/index.ts` - Actualizar rutas
- `pwacostos/src/stores/auth.ts` - Actualizar store

### 5.8 TIPOS TYPESCRIPT A DEFINIR

```typescript
// types/index.ts

export interface Central {
  id: number;
  nombre_central: string;
  tipo: string;
  municipio: string;
  estado: string;
  latitud: number;
  longitud: number;
  estatus: 'autorizado' | 'pendiente' | 'inactivo';
  visible_pwa: boolean;
}

export interface CapturistaCentral {
  id: number;
  usuario_id: number;
  central_id: number;
  es_favorita: boolean;
  central: Central;
}

export interface PropuestaCentral {
  id: number;
  usuario_id: number;
  nombre_central: string;
  tipo: string;
  municipio: string;
  estado: string;
  latitud: number;
  longitud: number;
  estatus: 'pendiente' | 'aprobada' | 'rechazada';
  motivo_rechazo?: string;
}

export interface PrecioJitomateCalidad {
  id: number;
  reporte_jitomate_id: number;
  calidad: 'primera' | 'segunda' | 'tercera';
  precio?: number;
  sin_dato: boolean;
}

export interface ReporteJitomate {
  id: number;
  central_id: number;
  usuario_id: number;
  fecha: string;
  corte: 'matutino' | 'mediodía';
  hora_captura: string;
  captura_tardia: boolean;
  precios: PrecioJitomateCalidad[];
  central?: Central;
  usuario?: { id: number; nombre: string };
}

export interface PreciosJitomatePayload {
  central_id: number;
  fecha: string;
  corte: 'matutino' | 'mediodía';
  precios_por_calidad: {
    primera: { precio?: number; sin_dato: boolean };
    segunda: { precio?: number; sin_dato: boolean };
    tercera: { precio?: number; sin_dato: boolean };
  };
}
```

---

## 6. CAMBIOS EN EL ADMIN WEB (adminpwa)

### 6.1 MÓDULOS PRINCIPALES

#### 6.1.1 CATÁLOGO DE CENTRALES (Nueva/Actualizada)
**Vista:** `UsuariosView.vue` → Renombrar a `CatalogoCentralesView.vue` o actualizar

Funcionalidades:
1. **Importar Excel/CSV**
   - Campos esperados: nombre_central, tipo, municipio, estado, latitud, longitud
   - Crear o actualizar en catalogo_centrales
   
2. **Listar Centrales**
   - Tabla: nombre, tipo, municipio, estado, estatus, visible_pwa
   - Búsqueda por nombre, municipio, estado
   - Ordenable por cualquier columna
   
3. **Editar Central**
   - Modal/formulario inline
   - Permitir cambiar: nombre, tipo, municipio, estado, latitud, longitud, visible_pwa
   - Persistir cambios
   
4. **Activar/Inactivar**
   - Cambiar estatus entre 'autorizado', 'pendiente', 'inactivo'
   - Efecto visible en PWA (si visible_pwa=false, ocultar de capturistas)
   
5. **Corregir Coordenadas**
   - Mapa integrado para ajustar latitud/longitud
   - Validar límites

#### 6.1.2 PROPUESTAS DE CENTRALES (Nueva/Actualizada)
**Vista:** `PropuestasView.vue` → Actualizar para propuestas de centrales

Funcionalidades:
1. **Listar Propuestas**
   - Tabla: Usuario, Nombre Central, Tipo, Municipio, Municipio, Estatus, Fecha
   - Filtro por estatus (pendiente, aprobada, rechazada)
   
2. **Autorizar Propuesta**
   - Botón "Autorizar" → Crea registro en catalogo_centrales
   - Campo revisado: latitud, longitud, visible_pwa
   - Cambiar estatus a 'aprobada'
   
3. **Rechazar Propuesta**
   - Modal para ingresar motivo_rechazo
   - Cambiar estatus a 'rechazada'
   
4. **Guardar Motivo**
   - Persistir motivo_rechazo en BD

#### 6.1.3 REPORTES DE JITOMATE (Nueva/Actualizada)
**Vista:** `RegistrosPreciosView.vue` → Actualizar

Columnas Mínimas de Tabla:
| Fecha | Corte | Central | Estado | Primera | Segunda | Tercera | Capturista | Hora |
|-------|-------|---------|--------|---------|---------|---------|-----------|------|
| 01/05/26 | Matutino | Central de Abasto CDMX | CDMX | $50/kg | $36/kg | $23/kg | Jess | 07:32 |

Filtros:
- Fecha inicio/fin
- Corte (Matutino, Mediodía)
- Central (dropdown de catalogo_centrales)
- Calidad (Primera, Segunda, Tercera)
- Capturista (usuario_id)
- Captura Tardía (sí/no)

Funcionalidades:
1. **Vista Tabla:** Listado filtrable, ordenable, paginable
2. **Exportar:** CSV/Excel con formato
3. **Detalles:** Al hacer clic, mostrar datos completos + variación respecto a comparaciones
4. **Eliminar:** Solo si es captura propia (validar usuario)

#### 6.1.4 DASHBOARD (Nueva/Actualizada)
**Vista:** `DashboardView.vue` → Actualizar

Indicadores (KPIs):
1. **Total de Centrales Autorizadas**
2. **Reportes del Período** (filtrable por fecha)
3. **Cobertura:** % de centrales con reporte en corte esperado
4. **Estadísticas por Calidad:**
   - Promedio, Mínimo, Máximo (Primera, Segunda, Tercera)
5. **Variación Promedio:** % de cambio entre períodos
6. **Alertas Activas:** Cantidad de alertas triggeradas

Charts recomendados (Chart.js):
- Precio por Calidad (línea temporal)
- Distribución de Precios (histograma)
- Cobertura de Centrales (barras)
- Alertas por Tipo (pie)

Filtros:
- Fecha inicio/fin
- Corte
- Estado
- Municipio
- Central
- Calidad

#### 6.1.5 MAPA (Nueva/Actualizada)
**Vista:** `VisorView.vue` → Actualizar

Características (Mapbox):
1. **Puntos del Mapa:** Todos de catalogo_centrales (latitud, longitud)
2. **Color del Punto:**
   - Verde: Tiene reporte del día, sin alertas
   - Amarillo: Sin reporte del día (esperado)
   - Naranja: Captura tardía o variación leve
   - Rojo: Alerta crítica (variación > 10%)
   - Gris: Inactivo
3. **Hover/Click:** Mostrar datos del reporte más reciente
4. **Propuestas:** Marker diferenciado para centrales propuestas (pendientes)
5. **Filtros:** Mismo filtrado que dashboard

#### 6.1.6 ALERTAS (Nueva)
**Vista:** Sección en Dashboard o vista nueva `AlertasView.vue`

Tipos de Alertas:
1. **Sube > 10%:** Presión al alza
2. **Baja > 10%:** Caída fuerte
3. **Sin Reporte:** Central pendiente para corte esperado
4. **Captura Tardía:** Reporte fuera de horario
5. **Diferencia Alta:** Brecha inusual entre centrales o entre calidades
6. **Fuera Promedio 7 días:** Dato atípico

Tabla de Alertas:
- Tipo de alerta
- Central
- Calidad
- Valor detectado
- Fecha/Hora
- Estado (activa, resuelta)

#### 6.1.7 EXPORTABLES (Nueva)
Generar archivos CSV/Excel:

Reportes Exportables:
1. **Catálogo de Centrales:** nombre, tipo, municipio, estado, latitud, longitud, estatus, visible_pwa
2. **Reportes de Jitomate:** Fecha, Corte, Central, Primera, Segunda, Tercera, Capturista, Hora, Variación (%), Alerta
3. **Análisis Temporal:** Promedios diarios/semanales por central y calidad

### 6.2 ARCHIVOS ADMIN A MODIFICAR

- `adminpwa/src/views/UsuariosView.vue` → Adaptación/renombramiento
- `adminpwa/src/views/UsuariosPWAView.vue` → Si aplica, actualizar
- `adminpwa/src/views/PropuestasView.vue` → Actualizar a propuestas_centrales
- `adminpwa/src/views/RegistrosPreciosView.vue` → Actualizar a reportes_jitomate
- `adminpwa/src/views/VisorView.vue` → Actualizar mapa para centrales
- `adminpwa/src/views/DashboardView.vue` → Actualizar KPIs y charts
- **Crear:** `adminpwa/src/views/AlertasView.vue` - Vista de alertas
- `adminpwa/src/services/api.ts` - Agregar endpoints nuevos
- `adminpwa/src/types/index.ts` - Nuevos tipos de admin

---

## 7. SOPORTE OFFLINE (IndexedDB y Sincronización)

### 7.1 FLUJO OFFLINE

```
1. Usuario llena reporte de jitomate
       ↓
2. Sin internet → Guardar en IndexedDB
       ↓
3. Reconectar a internet
       ↓
4. Sincronizar al backend
       ↓
5. Backend valida duplicados y reglas
       ↓
6. Confirmación: Marcar como sincronizado
```

### 7.2 STORES/COLAS EN INDEXEDDB

Actualizar `offline.ts` para soportar:

1. **catalogo_centrales**
   - Cache local de centrales visibles
   - Refrescar al conectar internet
   - Campos: id, nombre_central, tipo, municipio, estado, latitud, longitud, estatus, visible_pwa

2. **mis_centrales**
   - Relación del capturista con sus centrales
   - Campos: id, usuario_id, central_id, es_favorita

3. **propuestas_centrales**
   - Cola de propuestas pendientes (aún no autorizadas)
   - Campos: idem tabla backend

4. **reportes_jitomate**
   - Cola de cabeceras de reporte
   - Campos: central_id, fecha, corte, hora_captura, sync_status

5. **precios_jitomate_calidad**
   - Detalle de tres calidades por reporte
   - Campos: reporte_jitomate_id, calidad, precio, sin_dato

6. **sync_status**
   - Control de sincronización
   - Estados: pendiente, sincronizado, error, conflicto
   - Campos: id, tabla, registro_id, estatus, intento, fecha_intento, error_msg

### 7.3 CONFLICTOS CRÍTICOS

**Escenario:** Usuario captura reporte offline central X + fecha Y + corte Z. Al sincronizar, backend ya tiene ese reporte.

**Resolución:**
1. Backend detecta `UNIQUE(central_id, fecha, corte)` violado
2. Retorna error con `conflicto=true`
3. PWA marca en IndexedDB como `sync_status='conflicto'`
4. Mostrar UI al usuario: "Reporte duplicado. ¿Descartar o revisar?"
5. Si usuario elige "revisar": Mostrar ambos datos, permitir seleccionar cuál mantener
6. Si usuario elige "descartar": Limpiar de IndexedDB

### 7.4 ARCHIVOS A MODIFICAR

- `pwacostos/src/services/offline.ts` - Agregar nuevas entidades y lógica de conflictos
- `pwacostos/src/services/mercados.service.ts` → Actualizar a centrales.service.ts o crear nuevo servicio
- Sincronización periódica (considerar Service Worker para background sync)

---

## 8. VARIACIONES, ALERTAS Y CRITERIOS DE LECTURA

### 8.1 CÁLCULO DE VARIACIÓN POR CALIDAD

```
Fórmula:
variación_porcentaje = ((precio_actual - precio_comparacion) / precio_comparacion) * 100

Clasificación:
- Sube:         > 1%
- Baja:         < -1%
- Se mantiene:  entre -1% y 1%
- Sin comparación: no hay dato anterior
```

### 8.2 COMPARACIONES OBLIGATORIAS (ORDEN DE PRIORIDAD)

1. **Mismo corte día anterior**
   - Ejemplo: Lunes matutino vs Domingo matutino
   - Mejor para tendencias corto plazo

2. **Corte anterior disponible**
   - Ejemplo: Mediodía vs Matutino del mismo día
   - Útil para detectar cambios intradiarios

3. **Promedio móvil 7 días**
   - Solo si existen datos suficientes para la calidad y central
   - Referencia de tendencia

### 8.3 TIPOS DE ALERTAS

| Tipo | Condición | Importancia | Descripción |
|------|-----------|-------------|-------------|
| **Sube > 10%** | variación > 10% | Media | Presión al alza significativa |
| **Baja > 10%** | variación < -10% | Media | Caída fuerte o normalización |
| **Sin Reporte** | Falta reporte esperado | Alta | Central pendiente para corte |
| **Captura Tardía** | Hora fuera de rango | Baja | Reporte registrado fuera de horario |
| **Diferencia Alta** | Brecha inusual | Media | Entre centrales o entre calidades |
| **Fuera Promedio 7D** | > 2σ respecto promedio | Media | Dato atípico contra tendencia |

### 8.4 EJEMPLO DE LECTURA

**Entrada de datos:**
- Primera calidad en Central de Abasto CDMX, corte matutino
- Precio hoy: $45/kg
- Precio mismo corte día anterior: $50/kg
- Variación: ((45 - 50) / 50) * 100 = -10%
- Segunda y tercera se mantienen

**Salida generada automáticamente:**
```
"Primera calidad en Central de Abasto CDMX bajó 10% contra el mismo corte anterior. 
Segunda y tercera se mantienen."
```

### 8.5 IMPLEMENTACIÓN EN BACKEND

- Calcular variaciones al recibir reporte en `/api/jitomate/reportes`
- Persistir variaciones en tabla auxiliar (opcional) o calcular on-demand
- Generar alertas basadas en umbrales
- Exponerlas en `/api/admin/jitomate/alertas`

---

## 9. PLAN DE IMPLEMENTACIÓN POR FASES

### FASE 1: Modelo de Datos y API Base
**Duración estimada:** 3-5 días

Tareas:
1. ✓ Crear tablas: catalogo_centrales, capturista_centrales, propuestas_centrales, reportes_jitomate, precios_jitomate_calidad
2. ✓ Escribir migraciones SQL
3. ✓ Crear script de importación de Excel/CSV a catalogo_centrales
4. ✓ Crear endpoints básicos:
   - GET /api/centrales
   - POST /api/jitomate/reportes
   - GET /api/admin/jitomate/reportes
5. ✓ Implementar validaciones backend (críticas)
6. ✓ Documentar cambios en requirements.txt (si hay nuevas dependencias)

Archivos:
- `backend/migrations/00X_jitomate_tables.sql`
- `backend/app/routes/jitomate.py` (nueva)
- `backend/app/schemas.py` (actualizar)
- `backend/app/database.py` (actualizar ORM)

**Criterio de Aceptación:** Endpoints funcionan localmente, validaciones activas, tests de endpoint básicos

---

### FASE 2: PWA Especializada
**Duración estimada:** 4-6 días

Tareas:
1. ✓ Renombrar/actualizar vistas:
   - MercadosView → CentralesView o actualizar MercadosView.vue
   - HistorialView → Cambiar a historial de jitomate
   - HomeView → KPIs nuevos
2. ✓ Crear CapturaJitomateView.vue
3. ✓ Actualizar ProfileView (quitar selector de rol)
4. ✓ Actualizar router y navegación
5. ✓ Crear centrales.service.ts o actualizar mercados.service.ts
6. ✓ Implementar tipos en types/index.ts
7. ✓ Conectar servicios a APIs nuevas
8. ✓ Formulario de captura con validaciones locales

Archivos:
- `pwacostos/src/views/CapturaJitomateView.vue` (nueva)
- `pwacostos/src/views/HomeView.vue` (actualizar)
- `pwacostos/src/views/ProfileView.vue` (actualizar)
- `pwacostos/src/services/mercados.service.ts` (actualizar)
- `pwacostos/src/types/index.ts` (actualizar)
- `pwacostos/src/router/index.ts` (actualizar)
- `pwacostos/src/stores/auth.ts` (actualizar si necesario)

**Criterio de Aceptación:** PWA funciona, captura localmente, navegación correcta, offline=false aún

---

### FASE 3: Soporte Offline
**Duración estimada:** 3-4 días

Tareas:
1. ✓ Actualizar offline.ts con nuevas entidades (catalogo_centrales, reportes_jitomate, precios_jitomate_calidad)
2. ✓ Implementar cola de sincronización
3. ✓ Detección de cambios de conectividad
4. ✓ Sincronización al reconectar
5. ✓ Manejo de conflictos (reporte duplicado)
6. ✓ UI de estado sync (indicador visual)

Archivos:
- `pwacostos/src/services/offline.ts` (actualizar)
- `pwacostos/src/services/mercados.service.ts` (integrar sync)

**Criterio de Aceptación:** Offline=true, captura funciona, sincronización ocurre al reconectar, conflictos detectados

---

### FASE 4: Admin Operativo
**Duración estimada:** 5-7 días

Tareas:
1. ✓ Actualizar PropuestasView para propuestas_centrales
2. ✓ Actualizar RegistrosPreciosView para reportes_jitomate
3. ✓ Crear/actualizar CatalogoCentralesView
4. ✓ Implementar importación Excel/CSV
5. ✓ Filtros y tabla dinámica en reportes
6. ✓ Exportar funcionalidad (CSV/Excel)
7. ✓ Endpoints admin en backend
8. ✓ Autorizar/rechazar propuestas con motivo

Archivos:
- `adminpwa/src/views/PropuestasView.vue` (actualizar)
- `adminpwa/src/views/RegistrosPreciosView.vue` (actualizar)
- `adminpwa/src/views/CatalogoCentralesView.vue` (crear o actualizar UsuariosView)
- `adminpwa/src/services/api.ts` (actualizar)
- `backend/app/routes/admin_auth.py` (actualizar)

**Criterio de Aceptación:** Admin puede gestionar catálogo, propuestas, reportes; exporta CSV/Excel

---

### FASE 5: Analítica
**Duración estimada:** 5-7 días

Tareas:
1. ✓ Implementar cálculo de variaciones y alertas en backend
2. ✓ Crear endpoints de análisis:
   - /api/admin/jitomate/dashboard
   - /api/admin/jitomate/mapa
   - /api/admin/jitomate/alertas
   - /api/admin/jitomate/exportar
3. ✓ Actualizar DashboardView con KPIs y charts (Chart.js)
4. ✓ Actualizar VisorView con mapa (Mapbox)
5. ✓ Crear AlertasView o sección de alertas
6. ✓ Implementar filtros en dashboard/mapa
7. ✓ Pruebas de variaciones (test data)

Archivos:
- `adminpwa/src/views/DashboardView.vue` (actualizar)
- `adminpwa/src/views/VisorView.vue` (actualizar)
- `adminpwa/src/views/AlertasView.vue` (crear)
- `backend/app/routes/jitomate.py` (agregar análisis)
- Test data SQL

**Criterio de Aceptación:** Dashboard muestra KPIs correctas, variaciones calculadas, alertas activas, exportación funciona

---

### CRITERIOS DE CONTROL POR FASE

**Regla de Trabajo Crítica:**
El programador debe responder primero con **análisis del proyecto**, **archivos exactos a modificar**, **modelo final**, **migraciones**, **endpoints** y **riesgos**. Después debe implementar fase por fase, con **diffs pequeños** y **pruebas por cada cambio**.

---

## 10. CHECKLIST DE ACEPTACIÓN FINAL

Antes de entregar, validar:

### Backend
- [ ] Tablas creadas: catalogo_centrales, capturista_centrales, propuestas_centrales, reportes_jitomate, precios_jitomate_calidad
- [ ] `UNIQUE(central_id, fecha, corte)` en reportes_jitomate
- [ ] Endpoints funcionan localmente
- [ ] Validaciones backend activas:
  - [ ] central autorizada y visible_pwa
  - [ ] fecha + corte no duplicados
  - [ ] precio >= 0
  - [ ] precio 0 solo con sin_dato
  - [ ] 3 calidades presentes
  - [ ] captura_tardia detectado
  - [ ] transacciones atómicas
- [ ] Migraciones reversibles

### PWA
- [ ] Registra o asume solo CAPTURISTA como usuario operativo
- [ ] Navegación cambia de Mercados a Centrales
- [ ] PWA consume solo centrales con estatus='autorizado' Y visible_pwa=true
- [ ] Captura crea 1 reporte_jitomate + 3 precios_jitomate_calidad
- [ ] No se duplican reportes por central_id + fecha + corte
- [ ] offline.ts soporta catalogo_centrales, propuestas_centrales, reportes_jitomate, sincronización
- [ ] Indicador visual de modo offline
- [ ] Sincronización al reconectar internet

### Admin Web
- [ ] Admin autoriza propuestas hacia catalogo_centrales
- [ ] Catálogo importable desde Excel/CSV
- [ ] Reportes filtrables por fecha, corte, central, calidad, capturista
- [ ] Dashboard muestra KPIs: total centrales, reportes hoy, cobertura, promedios, variación
- [ ] Mapa muestra centrales con colores según estado (reporte, alerta, sin dato)
- [ ] Variaciones calculadas bajo reglas definidas
- [ ] Alertas generadas: sube > 10%, baja > 10%, sin reporte, captura tardía, diferencia alta, fuera promedio 7d
- [ ] Exportables incluyen: central, calidad, precio, disponibilidad, variación, capturista, hora

### Base de Datos
- [ ] Datos de prueba cargados
- [ ] Migraciones documentadas
- [ ] Script de importación de Excel/CSV funcional

### Documentación
- [ ] Cambios en archivos listados con rutas exactas
- [ ] Endpoints documentados con payloads
- [ ] Validaciones documentadas
- [ ] Tipos Typescript documentados

---

## 11. ANEXO: INSTRUCCIÓN BASE PARA CODEX / DESARROLLADOR

```
Estoy trabajando sobre un proyecto web/PWA existente llamado COSTOS. Necesito convertirlo 
en una aplicación especializada para monitorear el precio del jitomate variedad 
Saladette/huaje en centrales de abasto y mercados mayoristas. No quiero rehacer la app 
desde cero. Quiero reutilizar la estructura actual, componentes, endpoints, stores, 
lógica offline y panel administrativo cuando sea razonable.

Antes de modificar código, primero analiza el proyecto y responde con un plan técnico 
por archivo exacto.

CONTEXTO REAL DEL PROYECTO ACTUAL:
- Backend: FastAPI + PostgreSQL directo con psycopg2
- PWA usuario: Vue 3 + Pinia + Vite PWA
- Admin Web: Vue 3 + Pinia + Mapbox + Chart.js

RUTAS BACKEND PRINCIPALES:
- backend/app/routes/auth.py
- backend/app/routes/catalogos.py
- backend/app/routes/mercados.py
- backend/app/routes/admin_auth.py

PWA PRINCIPAL:
- pwacostos/src/views/RegisterView.vue
- pwacostos/src/views/ProfileView.vue
- pwacostos/src/views/MercadosView.vue
- pwacostos/src/views/HistorialView.vue
- pwacostos/src/services/mercados.service.ts
- pwacostos/src/services/offline.ts
- pwacostos/src/types/index.ts

ADMIN PRINCIPAL:
- adminpwa/src/views/UsuariosView.vue
- adminpwa/src/views/UsuariosPWAView.vue
- adminpwa/src/views/PropuestasView.vue
- adminpwa/src/views/RegistrosPreciosView.vue
- adminpwa/src/views/VisorView.vue
- adminpwa/src/views/DashboardView.vue
- adminpwa/src/services/api.ts

OBJETIVO:
Transformar en sistema especializado para:
- Producto fijo: Jitomate
- Variedad fija: Saladette/huaje
- Unidad fija: kg
- Tipo de precio fijo: Reparto en bodega
- Captura solo en centrales de abasto / mercados mayoristas autorizados
- Dos cortes diarios: matutino y mediodía
- Tres calidades comerciales: primera, segunda, tercera
```

---

## RESUMEN FINAL

Este documento especifica la transformación de COSTOS de un sistema general de precios a un monitor especializado de jitomate. Los cambios son extensos pero metodológicos:

1. **Modelo:** 5 tablas nuevas, valores fijos, relaciones claras
2. **Backend:** Nuevos endpoints, validaciones críticas, análisis
3. **PWA:** Renombramientos, nueva captura, offline mejorado
4. **Admin:** Catálogo, propuestas, reportes, dashboard, alertas, exportación
5. **Fases:** 5 fases bien definidas con criterios de aceptación claros

**Próximo paso:** Implementar Fase 1 con análisis de archivos exactos y migraciones SQL.
