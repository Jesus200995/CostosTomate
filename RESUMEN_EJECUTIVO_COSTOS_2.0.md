# COSTOS 2.0 - RESUMEN EJECUTIVO RÁPIDO

## 🎯 OBJETIVO
Convertir COSTOS de sistema general de precios → Monitor especializado de **jitomate Saladette/huaje** en centrales de abasto

## 📋 VALORES FIJOS DEL SISTEMA
- **Producto:** Jitomate
- **Variedad:** Saladette/huaje  
- **Unidad:** kg
- **Tipo Precio:** Reparto en bodega
- **Cortes:** Matutino, Mediodía (2 diarios)
- **Calidades:** Primera, Segunda, Tercera
- **Usuario:** CAPTURISTA (único rol operativo)
- **Lugar:** Centrales de abasto autorizadas

---

## 📊 CAMBIO CENTRAL: DE MERCADOS A CENTRALES

```
ANTES                          AHORA
─────────────────────────────────────────────────────────
Múltiples productos      →     Jitomate solo
Mercados DENUE           →     Centrales autorizadas
1 precio por producto    →     1 reporte + 3 calidades
Tipos de capturista      →     CAPTURISTA (único)
KPIs genéricos           →     Central, reportes, capturas, último corte
```

---

## 🗄️ MODELO DE DATOS (5 TABLAS NUEVAS)

| Tabla | Descripción | PK | Unique |
|-------|-------------|-----|--------|
| **catalogo_centrales** | Catálogo oficial | id | - |
| **capturista_centrales** | Mis Centrales por usuario | id | (usuario_id, central_id) |
| **propuestas_centrales** | Propuestas autorizables | id | - |
| **reportes_jitomate** | Cabecera de reportes | id | **(central_id, fecha, corte)** ⚠️ |
| **precios_jitomate_calidad** | Detalle 3 calidades | id | (reporte_jitomate_id, calidad) |

**⚠️ CRÍTICO:** `UNIQUE(central_id, fecha, corte)` en reportes_jitomate previene duplicados

---

## 🔌 ENDPOINTS PRINCIPALES

### Catálogo (PWA)
```
GET  /api/centrales              → Lista de centrales visibles
GET  /api/centrales/:id          → Detalles
POST /api/capturista/centrales   → Agregar a Mis Centrales
GET  /api/capturista/centrales   → Mis Centrales
DELETE /api/capturista/centrales/:id
```

### Captura (PWA)
```
POST /api/jitomate/reportes      → Crear reporte + 3 calidades (transacción)
GET  /api/jitomate/historial     → Historial de usuario
```

### Admin
```
POST /api/centrales/propuestas                    → Usuario propone central
GET  /api/admin/propuestas-centrales              → Admin lista
POST /api/admin/propuestas-centrales/:id/autorizar
POST /api/admin/propuestas-centrales/:id/rechazar

GET  /api/admin/jitomate/reportes   → Tabla filtrable
GET  /api/admin/jitomate/dashboard  → KPIs
GET  /api/admin/jitomate/mapa       → Puntos para mapeo
GET  /api/admin/jitomate/alertas    → Alertas activas
GET  /api/admin/jitomate/exportar   → CSV/Excel
```

---

## ✅ VALIDACIONES CRÍTICAS (Backend)

1. **Central autorizada:** estatus='autorizado' Y visible_pwa=true
2. **No duplicados:** UNIQUE(central_id, fecha, corte)
3. **Precio >= 0:** No permitir negativos
4. **sin_dato:** Si true → precio=NULL; si false → precio >= 0
5. **3 Calidades:** Primera, Segunda, Tercera obligatorias (marcadas sin_dato si no hay valor)
6. **Captura tardía:** Marcar si hora > rango esperado
7. **Transacción:** Cabecera + 3 detalles atómica

---

## 🎨 CAMBIOS PWA (Usuario)

### Navegación
```
ANTES                    AHORA
─────────────────────────────────────────
Mercados                 Mis Centrales ⭐
Perfil con rol selector  Perfil (CAPTURISTA fijo)
Sin captura jitomate     + Capturar Jitomate
```

### Vistas Principales
1. **HomeView** → KPIs: Centrales, Reportes Hoy, Capturas Hoy, Último Corte
2. **CentralesView** (MercadosView) → Tabs: Principal, Favoritos, Propuestas
3. **CapturaJitomateView** (NUEVA) → Formulario: Central, Fecha, Corte + 3 calidades
4. **HistorialView** → Reportes de jitomate, filtrable
5. **ProfileView** → Rol CAPTURISTA fijo (sin selector)

### Formulario Captura
```
[ENCABEZADO]
Central (dropdown Mis Centrales)        ← Requerido
Fecha (picker)                          ← Requerido  
Corte (radio: Matutino/Mediodía)        ← Requerido
Hora Real (auto + editable)

[VALORES FIJOS - Solo Lectura]
Producto: Jitomate
Variedad: Saladette/huaje
Unidad: kg
Tipo Precio: Reparto en bodega

[3 CALIDADES]
Primera:  Precio [__] ☐ Sin Dato
Segunda:  Precio [__] ☐ Sin Dato
Tercera:  Precio [__] ☐ Sin Dato

[ACCIONES]
[Guardar] [Cancelar]
```

### Offline
- Guardar en IndexedDB si sin internet
- Sincronizar al reconectar
- Detectar conflictos (central+fecha+corte duplicado)

---

## 👨‍💼 CAMBIOS ADMIN WEB

### Módulos
1. **Catálogo Centrales** → Importar Excel/CSV, editar, activar/inactivar, coordenadas
2. **Propuestas** → Autorizar/rechazar propuestas de centrales
3. **Reportes** → Tabla filtrable: Fecha, Corte, Central, Primera, Segunda, Tercera, Capturista, Hora
4. **Dashboard** → KPIs: Cobertura, Promedios, Variación, Alertas (Chart.js)
5. **Mapa** → Centrales visibles con colores por estado (Mapbox)
6. **Alertas** → Sube >10%, Baja >10%, Sin reporte, Captura tardía, etc.
7. **Exportables** → CSV/Excel de catálogo y reportes

### Filtros Admin
- Fecha inicio/fin
- Corte (Matutino, Mediodía)
- Central (dropdown)
- Calidad (Primera, Segunda, Tercera)
- Capturista (usuario_id)
- Captura Tardía (sí/no)

---

## ⚠️ VARIACIONES Y ALERTAS

### Cálculo de Variación
```
variación (%) = ((precio_actual - precio_anterior) / precio_anterior) * 100

Clasificación:
- Sube:         > 1%
- Baja:         < -1%
- Se mantiene:  -1% a 1%
```

### Comparaciones (Orden)
1. Mismo corte día anterior (ej: lunes mat vs domingo mat)
2. Corte anterior disponible (ej: mediodía vs matutino hoy)
3. Promedio móvil 7 días (si datos suficientes)

### Tipos de Alertas
| Tipo | Condición | Descripción |
|------|-----------|-------------|
| Sube > 10% | var > 10% | Presión al alza |
| Baja > 10% | var < -10% | Caída fuerte |
| Sin Reporte | Falta esperada | Central pendiente |
| Captura Tardía | Fuera rango hora | Reporte atrasado |
| Diferencia Alta | Gap inusual | Brecha entre centrales/calidades |
| Fuera Promedio 7D | > 2σ | Dato atípico |

---

## 🚀 PLAN DE IMPLEMENTACIÓN (5 FASES)

| Fase | Nombre | Duración | Archivos Clave |
|------|--------|----------|-----------------|
| 1 | Modelo BD + API | 3-5 días | migrations, jitomate.py, schemas.py |
| 2 | PWA especializada | 4-6 días | MercadosView, CapturaJitomateView, tipos |
| 3 | Offline | 3-4 días | offline.ts, sync logic |
| 4 | Admin operativo | 5-7 días | PropuestasView, RegistrosPreciosView, admin routes |
| 5 | Analítica | 5-7 días | Dashboard, Mapa, Alertas, variaciones |

**Total: ~20-30 días de trabajo**

---

## 📁 ARCHIVOS CRÍTICOS A MODIFICAR

### Backend (`backend/`)
```
NEW: backend/app/routes/jitomate.py          ← Todos endpoints jitomate
UPD: backend/app/routes/mercados.py          ← Cambiar a centrales
UPD: backend/app/routes/catalogos.py         ← Cambiar a catalogo_centrales
UPD: backend/app/routes/admin_auth.py        ← Admin jitomate
UPD: backend/app/schemas.py                  ← Nuevos Pydantic models
UPD: backend/app/database.py                 ← ORM para nuevas tablas
NEW: backend/migrations/00X_jitomate.sql     ← Tablas + migraciones
```

### PWA (`pwacostos/src/`)
```
NEW: views/CapturaJitomateView.vue           ← Captura jitomate
UPD: views/HomeView.vue                      ← KPIs nuevos
UPD: views/MercadosView.vue                  ← Renombrar a Centrales
UPD: views/HistorialView.vue                 ← Historial jitomate
UPD: views/ProfileView.vue                   ← Sin selector rol
UPD: services/mercados.service.ts            ← Actualizaciones centrales
UPD: services/offline.ts                     ← Nuevas entidades
UPD: types/index.ts                          ← Tipos nuevos
UPD: router/index.ts                         ← Rutas nuevas
```

### Admin (`adminpwa/src/`)
```
NEW: views/AlertasView.vue                   ← Vista de alertas
NEW: views/CatalogoCentralesView.vue         ← Catálogo de centrales
UPD: views/DashboardView.vue                 ← KPIs + charts
UPD: views/VisorView.vue                     ← Mapa de centrales
UPD: views/RegistrosPreciosView.vue          ← Reportes jitomate
UPD: views/PropuestasView.vue                ← Propuestas centrales
UPD: services/api.ts                         ← Endpoints nuevos
```

---

## ✨ CHECKLIST PRE-ENTREGA

### Backend ✓
- [ ] Tablas creadas (catalogo_centrales, capturista_centrales, propuestas_centrales, reportes_jitomate, precios_jitomate_calidad)
- [ ] UNIQUE(central_id, fecha, corte) en BD
- [ ] Endpoints funcionando
- [ ] Validaciones críticas activas
- [ ] Transacciones atómicas

### PWA ✓
- [ ] Usuario registra/asume CAPTURISTA
- [ ] Navegación Mercados → Centrales
- [ ] Solo consume centrales visibles
- [ ] Captura = 1 reporte + 3 calidades
- [ ] Sin duplicados (validación lado cliente)
- [ ] Offline funcional, syncronización activa
- [ ] Indicador visual offline

### Admin ✓
- [ ] Autoriza propuestas a catalogo_centrales
- [ ] Importa Excel/CSV
- [ ] Reportes filtrables
- [ ] Dashboard con KPIs correctas
- [ ] Mapa con colores por estado
- [ ] Variaciones calculadas
- [ ] Alertas generadas
- [ ] Exportables (CSV/Excel)

### Datos ✓
- [ ] Migraciones reversibles
- [ ] Test data cargado
- [ ] Script importación funcional

---

## 🔗 REFERENCIAS

**Documento completo:** `ESPECIFICACION_COMPLETA_COSTOS_2.0.md`

**Pasos iniciales:**
1. Leer análisis de proyecto actual (archivos backend/PWA/admin)
2. Crear migraciones SQL (Fase 1)
3. Crear endpoints jitomate.py (Fase 1)
4. Actualizar PWA views (Fase 2)
5. Integrar offline (Fase 3)
6. Admin Web (Fase 4)
7. Dashboard + Alertas (Fase 5)

---

**Última actualización:** 2 de mayo de 2026  
**Versión:** COSTOS 2.0 - Especialización Jitomate Saladette/Huaje
