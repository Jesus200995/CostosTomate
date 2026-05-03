<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="historial-page">
        <!-- Header -->
        <div class="historial-top">
          <div class="section-header">
            <ClipboardList :size="24" />
            <h1>Historial de Precios</h1>
          </div>

          <!-- Filtros -->
          <div class="filtros-card">
            <div class="filtros-fechas">
              <div class="filtro-group">
                <label class="filtro-label"><Calendar :size="12" /> Desde</label>
                <input v-model="fechaDesde" type="date" class="input input--date" @change="loadHistorial" />
              </div>
              <div class="filtro-group">
                <label class="filtro-label"><Calendar :size="12" /> Hasta</label>
                <input v-model="fechaHasta" type="date" class="input input--date" @change="loadHistorial" />
              </div>
            </div>
            <div class="filtro-group">
              <label class="filtro-label">Central</label>
              <select v-model="filtroCentral" class="input input--select">
                <option value="">Todas las centrales</option>
                <option v-for="c in centralesUnicas" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="filtro-group">
              <label class="filtro-label">Corte</label>
              <div class="toggle-pills">
                <button class="toggle-pill" :class="{ 'toggle-pill--active': filtroCorte === '' }" @click="filtroCorte = ''">Todos</button>
                <button class="toggle-pill" :class="{ 'toggle-pill--active': filtroCorte === 'matutino' }" @click="filtroCorte = 'matutino'">Matutino</button>
                <button class="toggle-pill" :class="{ 'toggle-pill--active': filtroCorte === 'mediodia' }" @click="filtroCorte = 'mediodia'">Mediodía</button>
              </div>
            </div>
            <button v-if="fechaDesde || fechaHasta || filtroCentral || filtroCorte" class="btn-clear" @click="clearFilters">
              <X :size="14" /> Limpiar
            </button>
          </div>

          <!-- Resumen -->
          <div v-if="!loading && reportesFiltrados.length > 0" class="resumen-bar">
            <span class="resumen-item"><strong>{{ reportesFiltrados.length }}</strong> reportes</span>
            <span class="resumen-sep">·</span>
            <span class="resumen-item"><strong>{{ centralesCount }}</strong> centrales</span>
          </div>
        </div>

        <!-- Resultados -->
        <div class="historial-results">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Cargando historial...</p>
          </div>

          <div v-else-if="reportesFiltrados.length === 0" class="empty-state">
            <ClipboardList :size="48" />
            <p>{{ historial.length === 0 ? 'No hay reportes registrados' : 'Sin resultados con estos filtros' }}</p>
            <p class="empty-state__hint">{{ historial.length === 0 ? 'Captura precios en la sección Capturar' : 'Prueba cambiando los filtros' }}</p>
          </div>

          <div v-else class="historial-groups">
            <div v-for="group in groupedByDate" :key="group.fecha" class="historial-group">
              <div class="group-date">
                <Calendar :size="14" />
                <span>{{ formatFecha(group.fecha) }}</span>
                <span class="group-count">{{ group.reportes.length }}</span>
              </div>
              <div class="group-items">
                <div v-for="reporte in group.reportes" :key="reporte.key" class="reporte-card">
                  <div class="reporte-card__header">
                    <div class="reporte-info">
                      <Building2 :size="14" />
                      <span class="reporte-central">{{ reporte.central_nombre }}</span>
                      <span v-if="reporte.central_estado" class="reporte-estado">{{ reporte.central_estado }}</span>
                    </div>
                    <div class="reporte-badges">
                      <span class="corte-badge" :class="reporte.corte === 'matutino' ? 'badge--morning' : 'badge--noon'">
                        {{ reporte.corte === 'matutino' ? 'Matutino' : 'Mediodía' }}
                      </span>
                      <span v-if="reporte.captura_tardia" class="late-badge">Tardío</span>
                    </div>
                  </div>
                  <div class="precios-row">
                    <div v-for="cal in (['primera', 'segunda', 'tercera'] as const)" :key="cal" class="precio-col">
                      <span class="cal-label">{{ calLabel(cal) }}</span>
                      <template v-if="reporte.precios[cal]">
                        <span v-if="reporte.precios[cal].sin_dato" class="precio-nd">S/D</span>
                        <span v-else-if="reporte.precios[cal].precio !== undefined" class="precio-val">
                          ${{ reporte.precios[cal].precio!.toFixed(2) }}
                        </span>
                        <span v-else class="precio-nd">—</span>
                      </template>
                      <span v-else class="precio-nd">—</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <AppToast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import { jitomateService } from '@/services/jitomate.service'
import type { HistorialJitomateItem } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import { ClipboardList, Calendar, Building2, X } from 'lucide-vue-next'

type Calidad = 'primera' | 'segunda' | 'tercera'

interface PrecioInfo {
  precio: number | undefined
  sin_dato: boolean
}

interface ReporteAgrupado {
  key: string
  central_id: number
  central_nombre: string
  central_estado?: string
  corte: string
  captura_tardia: boolean
  precios: Partial<Record<Calidad, PrecioInfo>>
}

interface DateGroup {
  fecha: string
  reportes: ReporteAgrupado[]
}

const ui = useUiStore()

const loading = ref(false)
const historial = ref<HistorialJitomateItem[]>([])
const fechaDesde = ref('')
const fechaHasta = ref('')
const filtroCentral = ref('')
const filtroCorte = ref('')

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

function calLabel(cal: Calidad): string {
  return { primera: '1a', segunda: '2a', tercera: '3a' }[cal]
}

async function loadHistorial() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (fechaDesde.value) params.fecha_desde = fechaDesde.value
    if (fechaHasta.value) params.fecha_hasta = fechaHasta.value
    historial.value = await jitomateService.getHistorial(params)
  } catch {
    ui.showToast('Error al cargar historial', 'error')
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  fechaDesde.value = ''
  fechaHasta.value = ''
  filtroCentral.value = ''
  filtroCorte.value = ''
  loadHistorial()
}

const centralesUnicas = computed(() => {
  const set = new Set(historial.value.map(h => h.central_nombre))
  return Array.from(set).sort()
})

// Agrupa filas individuales en reportes (una fila por calidad → un reporte con 3 calidades)
const reportesFiltrados = computed<ReporteAgrupado[]>(() => {
  const map = new Map<string, ReporteAgrupado>()

  for (const item of historial.value) {
    if (filtroCentral.value && item.central_nombre !== filtroCentral.value) continue
    if (filtroCorte.value && item.corte !== filtroCorte.value) continue

    const key = `${item.fecha}|${item.central_id}|${item.corte}`
    if (!map.has(key)) {
      map.set(key, {
        key,
        central_id: item.central_id,
        central_nombre: item.central_nombre,
        central_estado: item.central_estado,
        corte: item.corte,
        captura_tardia: item.captura_tardia,
        precios: {},
      })
    }
    const reporte = map.get(key)!
    reporte.precios[item.calidad as Calidad] = {
      precio: item.precio,
      sin_dato: item.sin_dato,
    }
  }

  return Array.from(map.values())
})

const centralesCount = computed(() => new Set(reportesFiltrados.value.map(r => r.central_id)).size)

const groupedByDate = computed<DateGroup[]>(() => {
  const map = new Map<string, ReporteAgrupado[]>()
  for (const r of reportesFiltrados.value) {
    const fecha = r.key.split('|')[0]
    const list = map.get(fecha) || []
    list.push(r)
    map.set(fecha, list)
  }
  return Array.from(map.entries())
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([fecha, reportes]) => ({ fecha, reportes }))
})

function formatFecha(fecha: string): string {
  const d = new Date(fecha + 'T12:00:00')
  return d.toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => {
  loadHistorial()
})
</script>

<style scoped>
/* ── Layout ── */
.historial-page {
  max-width: 640px;
  width: 100%;
  margin: 0 auto;
  padding: 1rem 1rem 0.5rem;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  height: calc(100dvh - 60px);
  overflow: hidden;
}
.historial-top { flex-shrink: 0; }

/* ── Header ── */
.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  color: #b71c1c;
}
.section-header h1 {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0;
}

/* ── Filtros ── */
.filtros-card {
  background: #fff;
  border: 1.5px solid #e0e0e0;
  border-radius: 14px;
  padding: 0.85rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.filtros-fechas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}
.filtro-group { min-width: 0; }
.filtro-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #b71c1c;
  margin-bottom: 0.25rem;
}
.input {
  width: 100%;
  padding: 0.5rem 0.65rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.85rem;
  color: #333;
  background: #fff;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
  min-width: 0;
  -webkit-appearance: none;
  appearance: none;
}
.input:focus {
  border-color: #b71c1c;
  outline: none;
  box-shadow: 0 0 0 2px rgba(183,28,28,0.1);
}
.input--date {
  min-height: 38px;
  color-scheme: light;
}
.input--date::-webkit-calendar-picker-indicator { opacity: 0.6; cursor: pointer; }
.input--select {
  min-height: 38px;
  background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23b71c1c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E") no-repeat right 0.55rem center;
  padding-right: 1.9rem;
}
.toggle-pills { display: flex; gap: 0.3rem; }
.toggle-pill {
  flex: 1;
  padding: 0.45rem 0.5rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
  text-align: center;
  white-space: nowrap;
}
.toggle-pill--active {
  background: #b71c1c;
  color: #fff;
  border-color: #b71c1c;
}
.btn-clear {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.6rem;
  border: none;
  background: #ffebee;
  color: #c62828;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  align-self: flex-start;
}

/* ── Resumen ── */
.resumen-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.82rem;
  color: #b71c1c;
  margin-bottom: 1rem;
  background: #ffebee;
  border-radius: 10px;
  font-weight: 500;
}
.resumen-sep { color: #ef9a9a; }

/* ── Resultados scroll ── */
.historial-results {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  background: #fff;
  border: 1.5px solid #e0e0e0;
  border-radius: 14px;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ── Loading / Empty ── */
.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #bbb;
}
.loading-state p,
.empty-state p {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #999;
}
.empty-state__hint {
  font-weight: 400 !important;
  font-size: 0.82rem !important;
  color: #bbb !important;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #b71c1c;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin: 0 auto 0.5rem;
}
@keyframes spin { to { transform: rotate(360deg) } }

/* ── Grupos por fecha ── */
.historial-groups {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.group-date {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #b71c1c;
  margin-bottom: 0.5rem;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid #ffebee;
}
.group-count {
  margin-left: auto;
  background: #ffebee;
  color: #b71c1c;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
}
.group-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* ── Reporte card ── */
.reporte-card {
  background: #fff;
  border: 1.5px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.reporte-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}
.reporte-info {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
  color: #555;
  flex: 1;
}
.reporte-central {
  font-size: 0.85rem;
  font-weight: 700;
  color: #222;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.reporte-estado {
  font-size: 0.72rem;
  color: #999;
  white-space: nowrap;
  flex-shrink: 0;
}
.reporte-badges {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-shrink: 0;
}
.corte-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.18rem 0.45rem;
  border-radius: 6px;
}
.badge--morning {
  background: #fff8e1;
  color: #f57f17;
}
.badge--noon {
  background: #e3f2fd;
  color: #1565c0;
}
.late-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.35rem;
  border-radius: 5px;
  background: #ffebee;
  color: #c62828;
}

/* ── Precios row ── */
.precios-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  divide: 1px solid #f0f0f0;
}
.precio-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.6rem 0.4rem;
  border-right: 1px solid #f0f0f0;
}
.precio-col:last-child { border-right: none; }
.cal-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.2rem;
}
.precio-val {
  font-size: 1rem;
  font-weight: 700;
  color: #b71c1c;
}
.precio-nd {
  font-size: 0.82rem;
  font-weight: 600;
  color: #ccc;
}

/* ── Responsive 480px ── */
@media (max-width: 480px) {
  .historial-page {
    padding: 0.75rem 0.75rem 0.35rem;
  }
  .section-header { margin-bottom: 0.85rem; }
  .section-header h1 { font-size: 1.15rem; }
  .filtros-card {
    padding: 0.65rem;
    border-radius: 11px;
    gap: 0.45rem;
    margin-bottom: 0.75rem;
  }
  .filtros-fechas { gap: 0.35rem; }
  .filtro-label { font-size: 0.7rem; }
  .input--date,
  .input--select {
    padding: 0.4rem 0.5rem;
    font-size: 0.8rem;
    min-height: 36px;
    border-radius: 8px;
  }
  .input--select { padding-right: 1.7rem; }
  .toggle-pill {
    padding: 0.35rem 0.35rem;
    font-size: 0.75rem;
    border-radius: 7px;
  }
  .btn-clear { font-size: 0.7rem; padding: 0.28rem 0.45rem; }
  .resumen-bar { font-size: 0.72rem; padding: 0.35rem 0.5rem; margin-bottom: 0.75rem; }
  .historial-results { padding: 0.5rem; border-radius: 11px; }
  .historial-groups { gap: 1rem; }
  .group-date { font-size: 0.78rem; }
  .group-count { font-size: 0.65rem; }
  .reporte-card__header { padding: 0.5rem 0.6rem; }
  .reporte-central { font-size: 0.8rem; }
  .reporte-estado { font-size: 0.66rem; }
  .corte-badge { font-size: 0.65rem; padding: 0.14rem 0.35rem; }
  .precio-col { padding: 0.5rem 0.3rem; }
  .precio-val { font-size: 0.9rem; }
  .cal-label { font-size: 0.62rem; }
}

/* ── Responsive 360px ── */
@media (max-width: 360px) {
  .historial-page { padding: 0.5rem 0.5rem 0.25rem; }
  .section-header h1 { font-size: 1rem; }
  .filtros-card { padding: 0.5rem; gap: 0.35rem; }
  .filtros-fechas { grid-template-columns: 1fr; }
  .toggle-pill { font-size: 0.68rem; padding: 0.28rem 0.2rem; }
  .precio-val { font-size: 0.82rem; }
  .cal-label { font-size: 0.58rem; }
}
</style>
