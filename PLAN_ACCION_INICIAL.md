# COSTOS 2.0 - PLAN DE ACCIÓN INICIAL (Step-by-Step)

## 🎯 OBJETIVO FINAL
Transformar COSTOS de sistema general de precios → Monitor especializado de jitomate en centrales

## 📋 PREREQUISITOS
- [ ] Backup de BD PostgreSQL actual
- [ ] Git en estado limpio (commits actuales)
- [ ] Python 3.8+ con FastAPI instalado
- [ ] Node.js 18+ con npm/yarn
- [ ] Postman o similar para testing de endpoints

---

## ⏱️ SEMANA 1: ANÁLISIS Y PREPARACIÓN (Días 1-2)

### Día 1: Análisis del Proyecto Actual
**Tiempo:** 4-6 horas

#### Tarea 1.1: Revisar Backend
- [ ] Leer `backend/app/routes/mercados.py`
  - Entender estructura de endpoints actuales
  - Identificar lógica a reutilizar
  - Documentar campos actuales de precios

- [ ] Leer `backend/app/routes/catalogos.py`
  - Estructura de catálogo_mercados
  - Cómo se cargan datos
  - Filtros y búsquedas

- [ ] Leer `backend/app/routes/auth.py`
  - Sistema de autenticación actual
  - Cómo se valida usuario
  - Roles/permisos

- [ ] Leer `backend/app/database.py`
  - ORM o queries directas
  - Estructura de conexiones
  - Modelos actuales

**Preguntas a responder:**
```
¿Cómo se estructuran actualmente los precios?
¿Qué campos tiene catalogo_mercados?
¿Cómo se maneja la autenticación?
¿FastAPI usa ORM o queries directas?
¿Hay validaciones actuales aprovechables?
```

#### Tarea 1.2: Revisar PWA
- [ ] Leer `pwacostos/src/views/MercadosView.vue`
  - Cómo lista mercados
  - Cómo se agregan a "Mis Mercados"
  - Estructura de componentes

- [ ] Leer `pwacostos/src/services/mercados.service.ts`
  - Llamadas API actuales
  - Estructura de respuestas
  - Filtros y búsquedas

- [ ] Leer `pwacostos/src/services/offline.ts`
  - Estructura IndexedDB
  - Qué datos se cachean
  - Cómo sincroniza

- [ ] Revisar `pwacostos/src/types/index.ts`
  - Tipos actuales
  - Interfaces de mercados/precios

**Preguntas a responder:**
```
¿Cómo se estructura MercadosView?
¿Qué datos cachea offline.ts?
¿Cómo es el flujo de guardado?
¿Qué tipos existen actualmente?
¿IndexedDB usa transacciones?
```

#### Tarea 1.3: Revisar Admin
- [ ] Leer `adminpwa/src/views/RegistrosPreciosView.vue`
  - Tabla de reportes/precios
  - Filtros disponibles
  - Acciones (editar, eliminar)

- [ ] Leer `adminpwa/src/views/DashboardView.vue`
  - KPIs actuales
  - Charts (Chart.js)
  - Filtros

- [ ] Leer `adminpwa/src/views/VisorView.vue`
  - Cómo dibuja mapa (Mapbox)
  - Qué datos muestra
  - Interacciones

**Preguntas a responder:**
```
¿Cómo filtra admin los reportes?
¿Qué KPIs tiene el dashboard?
¿Cómo se dibuja el mapa?
¿Hay búsqueda en tiempo real?
```

### Día 2: Diseño Técnico Detallado
**Tiempo:** 4-6 horas

#### Tarea 2.1: Diagrama de Base de Datos
- [ ] Crear diagrama ER con las 5 tablas nuevas
- [ ] Mostrar relaciones FK
- [ ] Marcar UNIQUE constraints
- [ ] Documentar campos por tabla

```sql
-- Plantilla
catalogo_centrales
├─ id (PK)
├─ nombre_central
├─ latitud, longitud
├─ estatus ENUM
├─ visible_pwa BOOLEAN
└─ (FK a usuarios vía capturista_centrales)

reportes_jitomate
├─ id (PK)
├─ central_id (FK)
├─ usuario_id (FK)
├─ fecha DATE
├─ corte ENUM
└─ hora_captura TIMESTAMP
   UNIQUE(central_id, fecha, corte) ⚠️

precios_jitomate_calidad
├─ id (PK)
├─ reporte_jitomate_id (FK)
├─ calidad ENUM
├─ precio DECIMAL
└─ sin_dato BOOLEAN
   UNIQUE(reporte_jitomate_id, calidad)
```

#### Tarea 2.2: Mapeo de Cambios por Archivo
- [ ] Para cada archivo a modificar, crear lista de cambios:

```
Archivo: backend/app/routes/mercados.py
Cambios:
  1. Renombrar función listar_mercados → listar_centrales
  2. Cambiar consulta a catalogo_centrales
  3. Agregar filtro visible_pwa=true
  4. Cambiar respuesta de campos
  5. Crear nuevo endpoint POST /api/jitomate/reportes
```

#### Tarea 2.3: Crear Script de Migración
- [ ] Script SQL para crear 5 tablas nuevas
- [ ] Migración para renombrar catalogo_mercados
- [ ] Migración reversible (rollback)

**Ejemplo:**
```sql
-- backend/migrations/001_jitomate_base.sql

BEGIN;

-- Crear catalogo_centrales (renombrar desde catalogo_mercados)
ALTER TABLE IF EXISTS catalogo_mercados RENAME TO catalogo_centrales;

-- Agregar campos nuevos
ALTER TABLE catalogo_centrales 
ADD COLUMN IF NOT EXISTS estatus VARCHAR(50) DEFAULT 'autorizado',
ADD COLUMN IF NOT EXISTS visible_pwa BOOLEAN DEFAULT true;

-- Crear capturista_centrales
CREATE TABLE IF NOT EXISTS capturista_centrales (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
  central_id INTEGER NOT NULL REFERENCES catalogo_centrales(id),
  es_favorita BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(usuario_id, central_id)
);

-- ... resto de tablas

COMMIT;
```

---

## ⏱️ SEMANA 1: IMPLEMENTACIÓN FASE 1 (Días 3-5)

### Día 3: Migraciones y Base de Datos
**Tiempo:** 6-8 horas

#### Tarea 3.1: Crear Migraciones SQL
- [ ] Crear archivo: `backend/migrations/001_jitomate_base.sql`
- [ ] Crear archivo: `backend/migrations/002_jitomate_rollback.sql`
- [ ] Ejecutar en BD local de testing

```bash
# En terminal PostgreSQL
\i backend/migrations/001_jitomate_base.sql
```

#### Tarea 3.2: Validar Estructura
- [ ] Conectar a BD y verificar tablas
```sql
\dt catalogo_centrales;
\dt reportes_jitomate;
\dt precios_jitomate_calidad;

-- Ver UNIQUE constraints
SELECT constraint_name FROM information_schema.table_constraints 
WHERE table_name='reportes_jitomate' AND constraint_type='UNIQUE';
```

- [ ] Insertar datos de prueba
```sql
INSERT INTO catalogo_centrales (nombre_central, tipo, municipio, estado, latitud, longitud) 
VALUES ('Central CDMX', 'mayorista', 'CDMX', 'CDMX', 19.4326, -99.1332);
```

#### Tarea 3.3: Crear Script de Importación Excel
- [ ] Archivo: `backend/import_centrales.py`
- [ ] Leer Excel con pandas
- [ ] Insertar a BD con validation

```python
# backend/import_centrales.py

import pandas as pd
from sqlalchemy import create_engine

# Config
DATABASE_URL = "postgresql://user:password@localhost/costos_db"
EXCEL_PATH = "centrales.xlsx"

# Leer Excel
df = pd.read_excel(EXCEL_PATH)

# Conectar BD
engine = create_engine(DATABASE_URL)

# Insertar
df.to_sql('catalogo_centrales', engine, if_exists='append', index=False)

print(f"✓ {len(df)} centrales importadas")
```

### Día 4: Backend Endpoints - Parte 1
**Tiempo:** 8 horas

#### Tarea 4.1: Crear Rutas Básicas
- [ ] Archivo: `backend/app/routes/jitomate.py` (NUEVO)

```python
# backend/app/routes/jitomate.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.database import get_db
from app.schemas import ReporteJitomateCreate, ReporteJitomateResponse

router = APIRouter(prefix="/api/jitomate", tags=["jitomate"])

@router.get("/reportes/{reporte_id}")
async def get_reporte(reporte_id: int, db=Depends(get_db)):
    """Obtener detalles de un reporte"""
    # Lógica
    pass

@router.post("/reportes")
async def create_reporte(payload: ReporteJitomateCreate, db=Depends(get_db)):
    """Crear nuevo reporte con 3 calidades"""
    # Lógica crítica:
    # 1. Validar central existe y visible_pwa=true
    # 2. Validar no existe reporte con mismo central_id+fecha+corte
    # 3. Crear transacción: reportes_jitomate + precios_jitomate_calidad
    # 4. Retornar IDs creados
    pass

@router.get("/historial")
async def get_historial(usuario_id: int, db=Depends(get_db)):
    """Historial de reportes del usuario"""
    pass
```

#### Tarea 4.2: Actualizar Schemas
- [ ] Archivo: `backend/app/schemas.py`
- [ ] Agregar esquemas Pydantic

```python
# backend/app/schemas.py

from pydantic import BaseModel, validator
from typing import Optional, List

class PrecioCalidadPayload(BaseModel):
    calidad: str  # 'primera', 'segunda', 'tercera'
    precio: Optional[float] = None
    sin_dato: bool = False
    
    @validator('precio')
    def precio_valido(cls, v, values):
        sin_dato = values.get('sin_dato')
        if not sin_dato and v is None:
            raise ValueError('precio requerido si sin_dato=false')
        if v is not None and v < 0:
            raise ValueError('precio no puede ser negativo')
        return v

class ReporteJitomateCreate(BaseModel):
    central_id: int
    fecha: str  # YYYY-MM-DD
    corte: str  # 'matutino' o 'mediodía'
    precios_por_calidad: dict[str, PrecioCalidadPayload]

class CentralResponse(BaseModel):
    id: int
    nombre_central: str
    tipo: str
    municipio: str
    estado: str
    latitud: float
    longitud: float
    estatus: str
    visible_pwa: bool
    
    class Config:
        from_attributes = True
```

#### Tarea 4.3: Actualizar Database ORM
- [ ] Archivo: `backend/app/database.py`
- [ ] Crear modelos SQLAlchemy

```python
# backend/app/database.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CatalogoCentral(Base):
    __tablename__ = "catalogo_centrales"
    
    id = Column(Integer, primary_key=True)
    nombre_central = Column(String)
    tipo = Column(String)
    municipio = Column(String)
    estado = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    estatus = Column(String, default='autorizado')
    visible_pwa = Column(Boolean, default=True)

class ReporteJitomate(Base):
    __tablename__ = "reportes_jitomate"
    
    id = Column(Integer, primary_key=True)
    central_id = Column(Integer, ForeignKey("catalogo_centrales.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha = Column(String)  # YYYY-MM-DD
    corte = Column(String)  # 'matutino' o 'mediodía'
    hora_captura = Column(DateTime)
    captura_tardia = Column(Boolean, default=False)

class PrecioJitomateCalidad(Base):
    __tablename__ = "precios_jitomate_calidad"
    
    id = Column(Integer, primary_key=True)
    reporte_jitomate_id = Column(Integer, ForeignKey("reportes_jitomate.id"))
    calidad = Column(String)  # 'primera', 'segunda', 'tercera'
    precio = Column(Float, nullable=True)
    sin_dato = Column(Boolean, default=False)
```

#### Tarea 4.4: Implementar Validaciones
- [ ] Crear función validar_central_visible
- [ ] Crear función validar_reporte_no_duplicado
- [ ] Crear función validar_precios

```python
# backend/app/validations.py

def validar_central_visible(central_id: int, db):
    """Validar que central esté autorizada y visible"""
    central = db.query(CatalogoCentral).filter(
        CatalogoCentral.id == central_id,
        CatalogoCentral.estatus == 'autorizado',
        CatalogoCentral.visible_pwa == True
    ).first()
    
    if not central:
        raise HTTPException(status_code=403, detail="Central no autorizada o no visible")
    
    return central

def validar_reporte_no_duplicado(central_id: int, fecha: str, corte: str, db):
    """UNIQUE(central_id, fecha, corte)"""
    existe = db.query(ReporteJitomate).filter(
        ReporteJitomate.central_id == central_id,
        ReporteJitomate.fecha == fecha,
        ReporteJitomate.corte == corte
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=409, 
            detail="Reporte duplicado para central, fecha y corte",
            headers={"X-Conflicto": "true"}
        )

def validar_precios(precios_por_calidad: dict):
    """Validar 3 calidades con precios válidos"""
    calidades_requeridas = {'primera', 'segunda', 'tercera'}
    
    if set(precios_por_calidad.keys()) != calidades_requeridas:
        raise HTTPException(
            status_code=400, 
            detail="Deben estar las 3 calidades: primera, segunda, tercera"
        )
    
    for calidad, precio_obj in precios_por_calidad.items():
        if precio_obj.sin_dato and precio_obj.precio is not None:
            raise HTTPException(
                status_code=400,
                detail=f"{calidad}: Si sin_dato=true, precio debe ser null"
            )
        if not precio_obj.sin_dato and precio_obj.precio is None:
            raise HTTPException(
                status_code=400,
                detail=f"{calidad}: Si sin_dato=false, precio es obligatorio"
            )
        if precio_obj.precio and precio_obj.precio < 0:
            raise HTTPException(
                status_code=400,
                detail=f"{calidad}: Precio no puede ser negativo"
            )
```

### Día 5: Backend Endpoints - Parte 2
**Tiempo:** 8 horas

#### Tarea 5.1: Implementar POST /api/jitomate/reportes
- [ ] Transacción: Cabecera + 3 detalles atómica
- [ ] Test local con Postman

```python
# backend/app/routes/jitomate.py

from sqlalchemy import text
from datetime import datetime

@router.post("/jitomate/reportes", response_model=dict)
async def create_reporte(
    payload: ReporteJitomateCreate, 
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Crear nuevo reporte jitomate con 3 calidades - TRANSACCIÓN ATÓMICA"""
    
    try:
        # Validación 1: Central visible
        central = validar_central_visible(payload.central_id, db)
        
        # Validación 2: No duplicado
        validar_reporte_no_duplicado(payload.central_id, payload.fecha, payload.corte, db)
        
        # Validación 3: Precios válidos
        validar_precios(payload.precios_por_calidad)
        
        # Crear transacción
        # 1. Crear cabecera reportes_jitomate
        nuevo_reporte = ReporteJitomate(
            central_id=payload.central_id,
            usuario_id=current_user.id,
            fecha=payload.fecha,
            corte=payload.corte,
            hora_captura=datetime.now(),
            captura_tardia=detectar_captura_tardia(payload.corte)
        )
        db.add(nuevo_reporte)
        db.flush()  # Para obtener el ID
        
        # 2. Crear 3 detalles precios_jitomate_calidad
        precios_ids = []
        for calidad, precio_obj in payload.precios_por_calidad.items():
            precio_detalle = PrecioJitomateCalidad(
                reporte_jitomate_id=nuevo_reporte.id,
                calidad=calidad,
                precio=precio_obj.precio,
                sin_dato=precio_obj.sin_dato
            )
            db.add(precio_detalle)
            db.flush()
            precios_ids.append(precio_detalle.id)
        
        # Commit de la transacción
        db.commit()
        
        return {
            "reporte_id": nuevo_reporte.id,
            "precios_ids": precios_ids,
            "status": "ok"
        }
        
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def detectar_captura_tardia(corte: str) -> bool:
    """Detectar si captura está fuera de horario"""
    hora_actual = datetime.now().hour
    
    if corte == 'matutino' and hora_actual > 14:
        return True
    if corte == 'mediodía' and hora_actual > 18:
        return True
    
    return False
```

#### Tarea 5.2: Implementar GET /api/centrales
- [ ] Listar centrales visibles

```python
@router.get("/api/centrales", response_model=List[CentralResponse])
async def listar_centrales(db=Depends(get_db)):
    """Listar centrales autorizadas y visibles para PWA"""
    centrales = db.query(CatalogoCentral).filter(
        CatalogoCentral.estatus == 'autorizado',
        CatalogoCentral.visible_pwa == True
    ).all()
    
    return centrales
```

#### Tarea 5.3: Implementar GET /api/capturista/centrales
- [ ] Mis Centrales por usuario

```python
@router.get("/api/capturista/centrales")
async def get_mis_centrales(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Obtener Mis Centrales del capturista"""
    mis_centrales = db.query(CapturistaCentral).filter(
        CapturistaCentral.usuario_id == current_user.id
    ).all()
    
    return mis_centrales
```

#### Tarea 5.4: Testing con Postman
- [ ] Crear colección Postman: `COSTOS_2.0_Endpoints.postman_collection.json`
- [ ] Tests para cada endpoint:
  ```
  ✓ POST /api/jitomate/reportes - Crear reporte válido
  ✓ POST /api/jitomate/reportes - Rechazar duplicado
  ✓ POST /api/jitomate/reportes - Rechazar central no visible
  ✓ POST /api/jitomate/reportes - Rechazar precio negativo
  ✓ GET /api/centrales - Listar visibles
  ✓ GET /api/capturista/centrales - Mis centrales
  ```

---

## ⏱️ SEMANA 2: PWA Y OFFLINE (Días 6-10)

### Día 6: Actualización PWA - Tipos y Servicios
**Tiempo:** 8 horas

#### Tarea 6.1: Actualizar types/index.ts
- [ ] Agregar tipos nuevos

```typescript
// pwacostos/src/types/index.ts

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

export interface ReporteJitomate {
  id: number;
  central_id: number;
  central?: Central;
  usuario_id: number;
  fecha: string;
  corte: 'matutino' | 'mediodía';
  hora_captura: string;
  captura_tardia: boolean;
  precios: PrecioJitomateCalidad[];
}

export interface PrecioJitomateCalidad {
  id: number;
  reporte_jitomate_id: number;
  calidad: 'primera' | 'segunda' | 'tercera';
  precio?: number;
  sin_dato: boolean;
}

export interface CapturistaCentral {
  id: number;
  usuario_id: number;
  central_id: number;
  es_favorita: boolean;
  central?: Central;
}

export interface PrecioPayload {
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

#### Tarea 6.2: Crear/Actualizar Servicios
- [ ] Archivo: `pwacostos/src/services/centrales.service.ts` (NUEVO o actualizar mercados)

```typescript
// pwacostos/src/services/centrales.service.ts

import { apiClient } from './api';
import type { Central, CapturistaCentral, ReporteJitomate, PrecioPayload } from '@/types';

export const centralesService = {
  // Catálogo
  async listarCentrales(): Promise<Central[]> {
    const response = await apiClient.get('/api/centrales');
    return response.data;
  },

  async obtenerCentral(id: number): Promise<Central> {
    const response = await apiClient.get(`/api/centrales/${id}`);
    return response.data;
  },

  // Mis Centrales
  async obtenerMisCentrales(): Promise<CapturistaCentral[]> {
    const response = await apiClient.get('/api/capturista/centrales');
    return response.data;
  },

  async agregarACentrales(centralId: number): Promise<CapturistaCentral> {
    const response = await apiClient.post('/api/capturista/centrales', {
      central_id: centralId
    });
    return response.data;
  },

  async quitarDeVentaCentrales(capturistaId: number): Promise<void> {
    await apiClient.delete(`/api/capturista/centrales/${capturistaId}`);
  },

  // Reportes
  async crearReporte(payload: PrecioPayload): Promise<any> {
    const response = await apiClient.post('/api/jitomate/reportes', payload);
    return response.data;
  },

  async obtenerHistorial(filtros?: any): Promise<ReporteJitomate[]> {
    const response = await apiClient.get('/api/jitomate/historial', { params: filtros });
    return response.data;
  }
};
```

#### Tarea 6.3: Actualizar offline.ts
- [ ] Agregar nuevas colas/stores

```typescript
// pwacostos/src/services/offline.ts

export class OfflineService {
  private dbName = 'costos_db';
  private db: IDBDatabase;

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 2);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Stores existentes
        if (!db.objectStoreNames.contains('catalogo_centrales')) {
          db.createObjectStore('catalogo_centrales', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('mis_centrales')) {
          db.createObjectStore('mis_centrales', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('reportes_jitomate')) {
          db.createObjectStore('reportes_jitomate', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('precios_jitomate_calidad')) {
          db.createObjectStore('precios_jitomate_calidad', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('sync_status')) {
          db.createObjectStore('sync_status', { keyPath: 'id' });
        }
      };

      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onerror = () => reject(request.error);
    });
  }

  // Almacenar
  async guardarCentrales(centrales: any[]) {
    const tx = this.db.transaction('catalogo_centrales', 'readwrite');
    centrales.forEach(c => tx.objectStore('catalogo_centrales').put(c));
    return tx.promise;
  }

  async guardarReporte(reporte: any) {
    const tx = this.db.transaction(
      ['reportes_jitomate', 'precios_jitomate_calidad', 'sync_status'],
      'readwrite'
    );

    tx.objectStore('reportes_jitomate').add(reporte);
    
    reporte.precios.forEach((p: any) => {
      tx.objectStore('precios_jitomate_calidad').add(p);
    });

    tx.objectStore('sync_status').add({
      tabla: 'reportes_jitomate',
      registro_id: reporte.id,
      estatus: 'pendiente',
      fecha_intento: new Date().toISOString()
    });

    return tx.promise;
  }

  // Recuperar
  async obtenerCentrales() {
    const tx = this.db.transaction('catalogo_centrales', 'readonly');
    return new Promise((resolve, reject) => {
      const request = tx.objectStore('catalogo_centrales').getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async obtenerReportesPendientes() {
    const tx = this.db.transaction('sync_status', 'readonly');
    return new Promise((resolve, reject) => {
      const request = tx.objectStore('sync_status').getAll();
      const pending = (request.result as any[]).filter(r => r.estatus === 'pendiente');
      resolve(pending);
    });
  }

  // Sincronizar
  async sincronizar(apiService: any) {
    const pendientes = await this.obtenerReportesPendientes();

    for (const item of pendientes) {
      try {
        // Obtener reporte completo
        const reporte = await this.obtenerReporte(item.registro_id);

        // Enviar al backend
        const response = await apiService.crearReporte(reporte);

        // Marcar como sincronizado
        await this.marcarSincronizado(item.id);
      } catch (error: any) {
        if (error.response?.status === 409) {
          // Conflicto: duplicado
          await this.marcarConflicto(item.id, error.response.data);
        } else {
          // Error general
          await this.marcarError(item.id, error.message);
        }
      }
    }
  }

  private async marcarSincronizado(syncId: number) {
    const tx = this.db.transaction('sync_status', 'readwrite');
    const os = tx.objectStore('sync_status');
    const item = await new Promise((r) => os.get(syncId).onsuccess = (e) => r((e.target as any).result));
    (item as any).estatus = 'sincronizado';
    os.put(item);
    return tx.promise;
  }

  private async marcarConflicto(syncId: number, conflictoData: any) {
    const tx = this.db.transaction('sync_status', 'readwrite');
    const item = await new Promise((r) => tx.objectStore('sync_status').get(syncId).onsuccess = (e) => r((e.target as any).result));
    (item as any).estatus = 'conflicto';
    (item as any).conflicto_data = conflictoData;
    tx.objectStore('sync_status').put(item);
    return tx.promise;
  }

  private async marcarError(syncId: number, error: string) {
    const tx = this.db.transaction('sync_status', 'readwrite');
    const item = await new Promise((r) => tx.objectStore('sync_status').get(syncId).onsuccess = (e) => r((e.target as any).result));
    (item as any).estatus = 'error';
    (item as any).error_msg = error;
    (item as any).intento = ((item as any).intento || 0) + 1;
    tx.objectStore('sync_status').put(item);
    return tx.promise;
  }
}

export const offlineService = new OfflineService();
```

### Día 7: Crear Vista de Captura
**Tiempo:** 8 horas

#### Tarea 7.1: Crear CapturaJitomateView.vue
- [ ] Nueva vista con formulario especializado

```vue
<!-- pwacostos/src/views/CapturaJitomateView.vue -->

<template>
  <div class="captura-jitomate">
    <h1>Capturar Jitomate</h1>

    <!-- ENCABEZADO -->
    <div class="encabezado">
      <div class="form-group">
        <label>Central *</label>
        <select v-model="form.central_id" required>
          <option value="">Seleccionar central...</option>
          <option v-for="c in misCentrales" :key="c.id" :value="c.id">
            {{ c.central.nombre_central }} - {{ c.central.municipio }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>Fecha *</label>
        <input v-model="form.fecha" type="date" required />
      </div>

      <div class="form-group">
        <label>Corte *</label>
        <div class="radios">
          <label>
            <input v-model="form.corte" type="radio" value="matutino" required />
            Matutino
          </label>
          <label>
            <input v-model="form.corte" type="radio" value="mediodía" required />
            Mediodía
          </label>
        </div>
      </div>

      <div class="form-group">
        <label>Hora Captura</label>
        <input v-model="form.hora" type="time" />
        <small>Auto-capturada a {{ new Date().toLocaleTimeString() }}</small>
      </div>
    </div>

    <!-- VALORES FIJOS -->
    <div class="valores-fijos">
      <p>✓ Producto: Jitomate</p>
      <p>✓ Variedad: Saladette/huaje</p>
      <p>✓ Unidad: kg</p>
      <p>✓ Tipo Precio: Reparto en bodega</p>
    </div>

    <!-- 3 CALIDADES -->
    <div class="calidades">
      <div v-for="calidad in ['primera', 'segunda', 'tercera']" :key="calidad" class="calidad-card">
        <h3 style="text-transform: capitalize;">{{ calidad }}</h3>

        <div class="form-group">
          <label>Precio ($/kg)</label>
          <input
            v-model.number="form.precios_por_calidad[calidad].precio"
            type="number"
            step="0.01"
            min="0"
            :disabled="form.precios_por_calidad[calidad].sin_dato"
            placeholder="Ej: 45.50"
          />
        </div>

        <div class="checkbox-group">
          <label>
            <input
              v-model="form.precios_por_calidad[calidad].sin_dato"
              type="checkbox"
            />
            Sin dato
          </label>
        </div>
      </div>
    </div>

    <!-- MENSAJES -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-if="success" class="success-message">
      ✓ Reporte guardado exitosamente
    </div>
    <div v-if="!isOnline" class="offline-message">
      📡 Modo offline - Se sincronizará al conectar
    </div>

    <!-- ACCIONES -->
    <div class="acciones">
      <button @click="guardarReporte" :disabled="guardando" class="btn-primary">
        {{ guardando ? 'Guardando...' : '🔴 Guardar Reporte' }}
      </button>
      <button @click="cancelar" class="btn-secondary">
        Cancelar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { centralesService } from '@/services/centrales.service';
import { offlineService } from '@/services/offline';
import type { CapturistaCentral, PrecioPayload } from '@/types';

const router = useRouter();

const misCentrales = ref<CapturistaCentral[]>([]);
const isOnline = ref(navigator.onLine);
const error = ref('');
const success = ref('');
const guardando = ref(false);

const form = reactive({
  central_id: null as number | null,
  fecha: new Date().toISOString().split('T')[0],
  corte: 'matutino' as 'matutino' | 'mediodía',
  hora: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
  precios_por_calidad: {
    primera: { precio: null, sin_dato: false },
    segunda: { precio: null, sin_dato: false },
    tercera: { precio: null, sin_dato: false }
  }
});

onMounted(async () => {
  // Cargar Mis Centrales
  try {
    misCentrales.value = await centralesService.obtenerMisCentrales();
  } catch (e) {
    error.value = 'Error al cargar centrales';
  }

  // Monitorear conectividad
  window.addEventListener('online', () => { isOnline.value = true; });
  window.addEventListener('offline', () => { isOnline.value = false; });

  // Sincronizar si online
  if (isOnline.value) {
    await offlineService.sincronizar(centralesService);
  }
});

async function guardarReporte() {
  error.value = '';
  success.value = '';

  try {
    guardando.value = true;

    // Validaciones locales
    if (!form.central_id) {
      throw new Error('Selecciona una central');
    }

    const payload: PrecioPayload = {
      central_id: form.central_id,
      fecha: form.fecha,
      corte: form.corte,
      precios_por_calidad: form.precios_por_calidad
    };

    if (isOnline.value) {
      // Enviar al backend
      await centralesService.crearReporte(payload);
      success.value = 'Reporte guardado ✓';
    } else {
      // Guardar en IndexedDB
      const reporte = {
        id: Date.now(),
        central_id: form.central_id,
        fecha: form.fecha,
        corte: form.corte,
        hora_captura: new Date().toISOString(),
        precios: [
          { calidad: 'primera', ...form.precios_por_calidad.primera },
          { calidad: 'segunda', ...form.precios_por_calidad.segunda },
          { calidad: 'tercera', ...form.precios_por_calidad.tercera }
        ]
      };

      await offlineService.guardarReporte(reporte);
      success.value = 'Reporte guardado offline (📡)';
    }

    // Limpiar formulario
    setTimeout(() => {
      form.central_id = null;
      form.fecha = new Date().toISOString().split('T')[0];
      form.corte = 'matutino';
      Object.keys(form.precios_por_calidad).forEach(c => {
        form.precios_por_calidad[c as keyof typeof form.precios_por_calidad] = { precio: null, sin_dato: false };
      });
      success.value = '';

      // Redirigir a historial
      setTimeout(() => router.push('/historial'), 1500);
    }, 2000);
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Error desconocido';
  } finally {
    guardando.value = false;
  }
}

function cancelar() {
  router.back();
}
</script>

<style scoped>
.captura-jitomate {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.encabezado,
.calidades {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.radios {
  display: flex;
  gap: 20px;
}

.calidades {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.calidad-card {
  border: 2px solid #f0f0f0;
  padding: 15px;
  border-radius: 8px;
  background: #fafafa;
}

.valores-fijos {
  background: #e8f5e9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.success-message {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.offline-message {
  background: #fff3e0;
  color: #f57c00;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 13px;
}

.acciones {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #d32f2f;
  color: white;
}

.btn-primary:disabled {
  background: #bdbdbd;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #424242;
}
</style>
```

### Día 8-10: Actualizar Vistas Existentes
**Tiempo:** 20 horas (distribuidas)

#### Tarea: Actualizar HomeView.vue
- [ ] Cambiar KPIs a: Total Centrales, Reportes Hoy, Capturas Hoy, Último Corte
- [ ] Agregar botones rápidos: "Mis Centrales", "Capturar Jitomate"

#### Tarea: Actualizar MercadosView.vue
- [ ] Cambiar "Mercados" por "Centrales"
- [ ] Cambiar consumo de API a `/api/capturista/centrales`
- [ ] Mantener estructura de tabs

#### Tarea: Actualizar HistorialView.vue
- [ ] Cambiar a historial de reportes jitomate
- [ ] Columnas: Central, Fecha, Corte, Primera, Segunda, Tercera, Capturista, Hora

#### Tarea: Actualizar ProfileView.vue
- [ ] Quitar selector de rol
- [ ] Mostrar "CAPTURISTA" como texto fijo

#### Tarea: Actualizar Router
- [ ] Agregar ruta: `/captura` → CapturaJitomateView
- [ ] Cambiar "/mercados" por "/centrales" (o mantener pero actualizar)

---

## PRÓXIMOS PASOS (Semanas 3-4)

### Semana 3: Admin Web
- Día 11-13: Actualizar vistas admin (Catálogo, Propuestas, Reportes)
- Día 14-15: Dashboard y Mapa

### Semana 4: Analítica y Pulido
- Día 16-18: Variaciones, alertas y exportables
- Día 19-20: Testing, bugfixes, documentación

---

## ✅ CHECKLIST POR COMPLETAR

### FASE 1 BACKEND
- [ ] Migraciones ejecutadas
- [ ] 5 tablas creadas correctamente
- [ ] UNIQUE constraints verificados
- [ ] Script importación Excel funcional
- [ ] Endpoints POST /api/jitomate/reportes funciona
- [ ] Validaciones backend activas
- [ ] Postman tests pasados

### FASE 2 PWA
- [ ] Tipos TypeScript definidos
- [ ] CapturaJitomateView creada
- [ ] offline.ts actualizado
- [ ] HomeView actualizado
- [ ] MercadosView → Centrales
- [ ] Router actualizado
- [ ] PWA funciona en navegador local

### ANTES DE ENTREGAR
- [ ] Backup de BD hecho
- [ ] Todos los tests pasados
- [ ] Git commits pequeños y claros
- [ ] README actualizado con cambios
- [ ] Especificaciones documentadas

---

**Versión:** 1.0
**Última actualización:** 2 de mayo de 2026
**Responsable:** Desarrollador COSTOS 2.0
