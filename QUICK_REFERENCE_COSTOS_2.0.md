# COSTOS 2.0 - GUÍA DE CONSULTA RÁPIDA (Quick Reference)

## 📚 ÍNDICE DE CONSULTA RÁPIDA
- Estructura de tablas
- Endpoints por módulo
- Validaciones
- Tipos TypeScript
- Cambios visuales
- Palabras clave importantes

---

## 🗄️ TABLAS - ESTRUCTURA EXACTA

### catalogo_centrales
```sql
id (PK)
nombre_central VARCHAR
tipo VARCHAR
municipio VARCHAR
estado VARCHAR
latitud DECIMAL(10,8)
longitud DECIMAL(11,8)
estatus ENUM('autorizado','pendiente','inactivo')
visible_pwa BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
```

### capturista_centrales
```sql
id (PK)
usuario_id (FK) → usuarios
central_id (FK) → catalogo_centrales
es_favorita BOOLEAN
created_at TIMESTAMP
UNIQUE(usuario_id, central_id)
```

### propuestas_centrales
```sql
id (PK)
usuario_id (FK) → usuarios
nombre_central VARCHAR
tipo VARCHAR
municipio VARCHAR
estado VARCHAR
latitud DECIMAL(10,8)
longitud DECIMAL(11,8)
estatus ENUM('pendiente','aprobada','rechazada')
motivo_rechazo TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

### reportes_jitomate ⚠️ CRÍTICA
```sql
id (PK)
central_id (FK) → catalogo_centrales
usuario_id (FK) → usuarios
fecha DATE
corte ENUM('matutino','mediodía')
hora_captura TIMESTAMP
captura_tardia BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
UNIQUE(central_id, fecha, corte)  ← EVITA DUPLICADOS
```

### precios_jitomate_calidad
```sql
id (PK)
reporte_jitomate_id (FK) → reportes_jitomate
calidad ENUM('primera','segunda','tercera')
precio DECIMAL(10,2) [NULL si sin_dato=true]
sin_dato BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
UNIQUE(reporte_jitomate_id, calidad)
```

---

## 🔌 ENDPOINTS - MATRIZ COMPLETA

### 📦 CATÁLOGO (Públicos/PWA)

| Método | Endpoint | Descripción | Auth | Response |
|--------|----------|-------------|------|----------|
| GET | `/api/centrales` | Lista centrales visibles | ✓ | `[{id, nombre_central, tipo, municipio, estado, latitud, longitud, visible_pwa}]` |
| GET | `/api/centrales/:id` | Detalles central | ✓ | `{id, nombre_central, ...}` |
| POST | `/api/capturista/centrales` | Agregar a Mis Centrales | ✓ | `{id, central_id, usuario_id}` |
| GET | `/api/capturista/centrales` | Mis Centrales | ✓ | `[{id, central_id, es_favorita, central:{...}}]` |
| DELETE | `/api/capturista/centrales/:id` | Quitar de Mis Centrales | ✓ | `{success: true}` |

### 📊 REPORTES JITOMATE

| Método | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/api/jitomate/reportes` | `{central_id, fecha, corte, precios_por_calidad:{primera:{precio?, sin_dato}, ...}}` | `{reporte_id, precios_ids:[...]}` |
| GET | `/api/jitomate/historial?fecha_ini=&fecha_fin=&central_id=&corte=` | - | `[{id, central, fecha, corte, primera, segunda, tercera, capturista, hora_captura}]` |

### 💼 PROPUESTAS

| Método | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/api/centrales/propuestas` | `{nombre_central, tipo, municipio, estado, latitud, longitud}` | `{id, usuario_id, ...}` |
| GET | `/api/admin/propuestas-centrales` | - | `[{id, usuario, nombre_central, tipo, ...}]` |
| POST | `/api/admin/propuestas-centrales/:id/autorizar` | `{}` | `{central_id (nuevo en catalogo)}` |
| POST | `/api/admin/propuestas-centrales/:id/rechazar` | `{motivo_rechazo}` | `{id, estatus:'rechazada'}` |

### 📈 ADMIN ANALYTICS

| Método | Endpoint | Params | Response |
|--------|----------|--------|----------|
| GET | `/api/admin/jitomate/reportes` | `?fecha=&corte=&central_id=&calidad=&capturista_id=` | `[{fecha, corte, central, primera, segunda, tercera, capturista, hora}]` |
| GET | `/api/admin/jitomate/dashboard` | `?fecha_ini=&fecha_fin=&central_id=` | `{total_centrales, reportes_hoy, cobertura%, promedio_*, min_*, max_*, variacion_*, alertas:[...]}` |
| GET | `/api/admin/jitomate/mapa` | - | `[{id, nombre_central, latitud, longitud, tiene_reporte_hoy, color_alerta}]` |
| GET | `/api/admin/jitomate/alertas` | `?tipo=&fecha=&central_id=` | `[{tipo, descripcion, central, calidad, precio, fecha}]` |
| GET | `/api/admin/jitomate/exportar?formato=csv&fecha_ini=&fecha_fin=` | - | `(binary CSV/Excel)` |

---

## ✅ VALIDACIONES - CHECKLIST

### 🚫 Rechazar si:

1. **Central no visible**
   - `central.estatus !== 'autorizado'` ❌
   - `central.visible_pwa !== true` ❌

2. **Reporte duplicado**
   - `UNIQUE(central_id, fecha, corte)` violado ❌
   - Retornar: HTTP 409 Conflict + conflicto_detectado

3. **Precio inválido**
   - `precio < 0` ❌
   - `precio === 0 && sin_dato === false` ❌

4. **Calidades incompletas**
   - Faltan entradas para primera/segunda/tercera ❌
   - Mínimo debe existir entrada marcada `sin_dato=true` si no hay precio

5. **Transacción fallida**
   - Cabecera insertada pero no los 3 detalles ❌
   - Usar transacción para atomicidad

### ✅ Validar que:
- Hora_captura es TIMESTAMP válido
- Fecha está en rango aceptable (no futura ni muy antigua)
- Corte es 'matutino' | 'mediodía' exactamente
- Usuario tiene permiso CAPTURISTA

---

## 📱 TIPOS TYPESCRIPT

```typescript
// types/index.ts

type Corte = 'matutino' | 'mediodía';
type Calidad = 'primera' | 'segunda' | 'tercera';
type EstatusCentral = 'autorizado' | 'pendiente' | 'inactivo';
type EstatusAlerta = 'activa' | 'resuelta';
type TipoAlerta = 'sube' | 'baja' | 'sin_reporte' | 'captura_tardia' | 'diferencia_alta' | 'fuera_promedio_7d';
type SyncStatus = 'pendiente' | 'sincronizado' | 'error' | 'conflicto';

interface Central {
  id: number;
  nombre_central: string;
  tipo: string;
  municipio: string;
  estado: string;
  latitud: number;
  longitud: number;
  estatus: EstatusCentral;
  visible_pwa: boolean;
}

interface ReporteJitomate {
  id: number;
  central_id: number;
  central?: Central;
  usuario_id: number;
  fecha: string;        // YYYY-MM-DD
  corte: Corte;
  hora_captura: string; // ISO 8601
  captura_tardia: boolean;
  precios: PrecioJitomateCalidad[];
}

interface PrecioJitomateCalidad {
  id: number;
  reporte_jitomate_id: number;
  calidad: Calidad;
  precio?: number;      // null si sin_dato=true
  sin_dato: boolean;
}

interface PrecioPayload {
  central_id: number;
  fecha: string;
  corte: Corte;
  precios_por_calidad: {
    primera: { precio?: number; sin_dato: boolean };
    segunda: { precio?: number; sin_dato: boolean };
    tercera: { precio?: number; sin_dato: boolean };
  };
}

interface Alerta {
  id: number;
  tipo: TipoAlerta;
  descripcion: string;
  central: Central;
  calidad?: Calidad;
  precio?: number;
  fecha: string;
  estatus: EstatusAlerta;
}
```

---

## 🎨 CAMBIOS VISUALES (UI/UX)

### Navegación Cambios
```
ANTES                      AHORA
─────────────────────────────────────────
[Logo] Mercados           [Logo] Mis Centrales ⭐
       Mi Perfil                 Mi Perfil
       Mercados                  Mis Centrales
       Historial                 Historial
       Versión 1.0               Versión 2.0
       [tipo capturista select]  [ninguno - fijo CAPTURISTA]
```

### Tabs en Mis Centrales
```
ANTES                    AHORA
───────────────────────────────────
Principal                Principal
Favoritos                Favoritos
Propuestas               Propuestas
```

### Bottom Tabs (PWA)
```
Inicio | Centrales | Historial
(en lugar de Mercados)
```

### Formulario Captura (NUEVO)
```
┌──────────────────────────┐
│ CAPTURAR JITOMATE        │
├──────────────────────────┤
│ Central      [dropdown▼] │ ← Solo Mis Centrales, visible_pwa=true
│ Fecha        [picker]    │ ← Default hoy
│ Corte        ◎Mat ◎Med   │ ← Radio buttons
│ Hora Real    [HH:MM:SS]  │ ← Auto capturada
├──────────────────────────┤
│ PRODUCTO FIJO (Display):  │
│ • Jitomate                │
│ • Saladette/huaje         │
│ • kg                       │
│ • Reparto en bodega        │
├──────────────────────────┤
│ CALIDADES:                │
│ Primera:  $[___] ☐Sin D   │
│ Segunda:  $[___] ☐Sin D   │
│ Tercera:  $[___] ☐Sin D   │
├──────────────────────────┤
│ [🔴 Guardar]  [Cancelar] │
│ 📡 Online mode            │
└──────────────────────────┘
```

---

## 🔄 FLUJO OFFLINE (IndexedDB)

### Stores/Colas Necesarias
```
catalogo_centrales       ← Cache local de centrales
mis_centrales            ← Relación usuario-centrales
propuestas_centrales     ← Propuestas locales
reportes_jitomate        ← Cola de reportes pendientes
precios_jitomate_calidad ← Detalles de calidades
sync_status              ← Control de sincronización
```

### Ciclo de Sincronización
```
1. Usuario captura offline
   ↓
2. Guardar en IndexedDB (sync_status='pendiente')
   ↓
3. Internet disponible (detectar por window.navigator.onLine)
   ↓
4. Enviar reportes_jitomate + precios_jitomate_calidad
   ↓
5. Backend valida:
   - ¿Central visible?
   - ¿central_id+fecha+corte duplicado?
   - ¿Precios válidos?
   ↓
6. Si OK → sync_status='sincronizado'
   Si CONFLICTO → sync_status='conflicto' + mostrar UI
   Si ERROR → sync_status='error' + reintentar
```

---

## 🚀 COMANDOS Y SCRIPTS ÚTILES

### SQL - Crear Tablas
```sql
-- Migraciones en: backend/migrations/00X_jitomate.sql

-- 1. Renombrar catalogo_mercados → catalogo_centrales
ALTER TABLE catalogo_mercados RENAME TO catalogo_centrales;
ALTER TABLE catalogo_centrales ADD COLUMN estatus ENUM('autorizado','pendiente','inactivo');
ALTER TABLE catalogo_centrales ADD COLUMN visible_pwa BOOLEAN DEFAULT true;

-- 2. Nueva tabla capturista_centrales
CREATE TABLE capturista_centrales (...);

-- 3. Nueva tabla propuestas_centrales
CREATE TABLE propuestas_centrales (...);

-- 4. Nueva tabla reportes_jitomate
CREATE TABLE reportes_jitomate (...);
CREATE UNIQUE INDEX idx_reporte_unique ON reportes_jitomate(central_id, fecha, corte);

-- 5. Nueva tabla precios_jitomate_calidad
CREATE TABLE precios_jitomate_calidad (...);
```

### Python - Importar Excel a Catálogo
```python
import pandas as pd
import psycopg2

def importar_centrales_excel(ruta_excel, connection_string):
    df = pd.read_excel(ruta_excel)
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO catalogo_centrales 
            (nombre_central, tipo, municipio, estado, latitud, longitud, estatus, visible_pwa)
            VALUES (%s, %s, %s, %s, %s, %s, 'autorizado', true)
            ON CONFLICT DO NOTHING
        """, (row['nombre_central'], row['tipo'], row['municipio'], row['estado'],
              row['latitud'], row['longitud']))
    
    conn.commit()
    cursor.close()
    conn.close()
```

---

## 🎯 PALABRAS CLAVE Y ACRÓNIMOS

| Término | Significado | Contexto |
|---------|-------------|----------|
| **CAPTURISTA** | Usuario operativo único | Rol de usuario |
| **Central** | Mercado mayorista autorizado | Ubicación |
| **Jitomate** | Producto fijo | Siempre |
| **Saladette/huaje** | Variedad fija | Siempre |
| **Corte** | Matutino o Mediodía | 2 diarios |
| **Calidad** | Primera, Segunda, Tercera | 3 por reporte |
| **sin_dato** | Flag de precio vacío | Permite NULL |
| **visible_pwa** | Central disponible para capturistas | Filtro importante |
| **Transacción** | Cabecera + 3 detalles atómica | Atomicidad BD |
| **UNIQUE(central_id, fecha, corte)** | Previene duplicados | Crítica |
| **Variación** | % cambio respecto comparación | Cálculo |
| **Alerta** | Condición crítica detectada | Dashboard |
| **Sync** | Sincronización offline→online | IndexedDB |
| **Conflicto** | Reporte duplicado al sincronizar | Manejo especial |

---

## 🔗 MAPEO: ARCHIVOS ANTES → DESPUÉS

```
BACKEND
backend/app/routes/mercados.py          → mercados.py (ACTUALIZAR) + jitomate.py (NUEVO)
backend/app/routes/catalogos.py         → ACTUALIZAR (catalogo_centrales)
backend/app/routes/admin_auth.py        → ACTUALIZAR (agregar endpoints admin)
backend/app/schemas.py                  → ACTUALIZAR (nuevos Pydantic models)
backend/app/database.py                 → ACTUALIZAR (ORM)

PWA
pwacostos/src/views/MercadosView.vue          → MercadosView.vue (ACTUALIZAR a Centrales)
pwacostos/src/views/HistorialView.vue         → ACTUALIZAR (Historial de Jitomate)
pwacostos/src/views/HomeView.vue              → ACTUALIZAR (KPIs nuevos)
pwacostos/src/views/ProfileView.vue           → ACTUALIZAR (Sin selector rol)
pwacostos/src/views/CapturaJitomateView.vue   → NUEVO
pwacostos/src/services/mercados.service.ts    → ACTUALIZAR (centrales)
pwacostos/src/services/offline.ts             → ACTUALIZAR (nuevas entidades)
pwacostos/src/types/index.ts                  → ACTUALIZAR (tipos nuevos)

ADMIN
adminpwa/src/views/DashboardView.vue          → ACTUALIZAR (KPIs jitomate)
adminpwa/src/views/VisorView.vue              → ACTUALIZAR (Mapa centrales)
adminpwa/src/views/RegistrosPreciosView.vue   → ACTUALIZAR (Reportes jitomate)
adminpwa/src/views/PropuestasView.vue         → ACTUALIZAR (Propuestas centrales)
adminpwa/src/views/CatalogoCentralesView.vue  → NUEVO
adminpwa/src/views/AlertasView.vue            → NUEVO
adminpwa/src/services/api.ts                  → ACTUALIZAR (endpoints)
```

---

## 📞 CONTACTO Y SOPORTE RÁPIDO

| Pregunta | Respuesta |
|----------|-----------|
| "¿Cuántos productos?" | Uno: Jitomate |
| "¿Cuántos cortes?" | Dos: Matutino, Mediodía |
| "¿Cuántas calidades?" | Tres: Primera, Segunda, Tercera |
| "¿Roles de usuario?" | Uno: CAPTURISTA |
| "¿Puedo cambiar precio si sin_dato=true?" | No, debe ser NULL |
| "¿Puedo duplicar central+fecha+corte?" | No, UNIQUE constraint |
| "¿Qué paso con mercados?" | Se renombran a centrales, mismo dato |
| "¿Offline cómo funciona?" | IndexedDB local + sync al conectar |
| "¿Conflicto cuando?" | Si central+fecha+corte ya existe al sincronizar |
| "¿Dashboard es real-time?" | Filtrable, actualiza al refrescar/sincronizar |

---

**Última actualización:** 2 de mayo de 2026  
**Versión:** 1.0 - COSTOS 2.0 Quick Reference
