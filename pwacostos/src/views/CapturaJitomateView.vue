<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="captura-header">
        <Salad :size="26" class="captura-header__icon" />
        <div>
          <h1>Capturar Jitomate</h1>
          <p class="captura-header__sub">Saladette/huaje · kg · Reparto en bodega</p>
        </div>
      </div>

      <!-- Formulario -->
      <form class="captura-form" @submit.prevent="submitReporte">

        <!-- Central -->
        <div class="form-group">
          <label class="form-label">Central de Abasto *</label>
          <select v-model="form.central_id" class="form-select" required :disabled="loadingCentrales">
            <option value="" disabled>{{ loadingCentrales ? 'Cargando...' : 'Selecciona una central' }}</option>
            <option v-for="c in misCentrales" :key="c.central_id" :value="c.central_id">
              {{ c.nombre_central }} — {{ c.municipio }}, {{ c.estado }}
            </option>
          </select>
          <p v-if="misCentrales.length === 0 && !loadingCentrales" class="form-hint">
            <router-link to="/centrales">Agrega centrales</router-link> antes de capturar.
          </p>
        </div>

        <!-- Fecha y Corte -->
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Fecha *</label>
            <input v-model="form.fecha" type="date" class="form-input" required :max="hoy" />
          </div>
          <div class="form-group">
            <label class="form-label">Corte *</label>
            <div class="corte-toggle">
              <button
                type="button"
                class="corte-btn"
                :class="{ 'corte-btn--active': form.corte === 'matutino' }"
                @click="form.corte = 'matutino'"
              >
                <Sun :size="16" /> Matutino
              </button>
              <button
                type="button"
                class="corte-btn"
                :class="{ 'corte-btn--active': form.corte === 'mediodia' }"
                @click="form.corte = 'mediodia'"
              >
                <Cloud :size="16" /> Mediodía
              </button>
            </div>
          </div>
        </div>

        <!-- Precios por calidad -->
        <div class="calidades-section">
          <h3 class="calidades-title">
            <Tag :size="18" /> Precios por calidad ($/kg)
          </h3>

          <div v-for="cal in calidades" :key="cal.key" class="calidad-row">
            <div class="calidad-label">
              <span class="calidad-badge" :class="`calidad-badge--${cal.key}`">{{ cal.label }}</span>
            </div>
            <div class="calidad-input-group">
              <input
                v-if="!getPrecio(cal.key).sin_dato"
                v-model.number="getPrecio(cal.key).precio"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                class="form-input calidad-input"
                :required="!getPrecio(cal.key).sin_dato"
              />
              <span v-else class="sin-dato-label">Sin dato</span>
              <button
                type="button"
                class="sin-dato-btn"
                :class="{ 'sin-dato-btn--active': getPrecio(cal.key).sin_dato }"
                @click="toggleSinDato(cal.key)"
                :title="getPrecio(cal.key).sin_dato ? 'Ingresar precio' : 'Marcar sin dato'"
              >
                <Ban v-if="getPrecio(cal.key).sin_dato" :size="16" />
                <X v-else :size="16" />
              </button>
            </div>
          </div>
        </div>

        <!-- Observaciones -->
        <div class="form-group">
          <label class="form-label">Observaciones (opcional)</label>
          <textarea v-model="form.observaciones" class="form-textarea" rows="2" placeholder="Notas adicionales..."></textarea>
        </div>

        <!-- Alerta de captura tardía -->
        <div v-if="esTardia" class="alert alert--warning">
          <AlertTriangle :size="18" />
          <span>Esta captura se registrará como <strong>tardía</strong> según el horario del corte.</span>
        </div>

        <!-- Error -->
        <div v-if="error" class="alert alert--error">
          <AlertCircle :size="18" />
          <span>{{ error }}</span>
        </div>

        <button type="submit" class="btn btn--primary btn--full btn--lg" :disabled="submitting || misCentrales.length === 0">
          <template v-if="submitting">
            <span class="spinner-inline"></span> Guardando...
          </template>
          <template v-else>
            <Save :size="18" /> Guardar Reporte
          </template>
        </button>
      </form>

      <!-- Últimos reportes del día -->
      <section v-if="reportesHoy.length > 0" class="reportes-hoy">
        <h3 class="reportes-hoy__title">
          <CheckCircle :size="18" /> Capturas de hoy
        </h3>
        <div v-for="r in reportesHoy" :key="r.id" class="reporte-chip">
          <Building2 :size="14" />
          <span>{{ r.central_nombre }}</span>
          <span class="reporte-chip__corte">{{ r.corte }}</span>
          <span v-if="r.captura_tardia" class="reporte-chip__tardia">tardía</span>
        </div>
      </section>
    </main>

    <AppToast />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import { centralesService, jitomateService } from '@/services/jitomate.service'
import type { MiCentral, ReporteJitomateOut, PrecioCalidad, Corte } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  Salad, Sun, Cloud, Tag, Ban, X, Save, AlertTriangle,
  AlertCircle, CheckCircle, Building2
} from 'lucide-vue-next'

const ui = useUiStore()

const hoy = new Date().toISOString().split('T')[0]
const horaActual = new Date().getHours()

const loadingCentrales = ref(true)
const submitting = ref(false)
const error = ref('')

const misCentrales = ref<MiCentral[]>([])
const reportesHoy = ref<ReporteJitomateOut[]>([])

const calidades = [
  { key: 'primera' as const, label: 'Primera' },
  { key: 'segunda' as const, label: 'Segunda' },
  { key: 'tercera' as const, label: 'Tercera' },
]

const form = reactive({
  central_id: '' as number | '',
  fecha: hoy,
  corte: (horaActual < 11 ? 'matutino' : 'mediodia') as Corte,
  observaciones: '',
})

const precios = reactive<Record<string, PrecioCalidad>>({
  primera: { calidad: 'primera', precio: undefined, sin_dato: false },
  segunda: { calidad: 'segunda', precio: undefined, sin_dato: false },
  tercera: { calidad: 'tercera', precio: undefined, sin_dato: false },
})

const esTardia = computed(() => {
  const h = new Date().getHours()
  if (form.corte === 'matutino') return h > 11
  if (form.corte === 'mediodia') return h > 17
  return false
})

function getPrecio(calidad: string) {
  return precios[calidad]
}

function toggleSinDato(calidad: string) {
  precios[calidad].sin_dato = !precios[calidad].sin_dato
  if (precios[calidad].sin_dato) {
    precios[calidad].precio = undefined
  }
}

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

async function submitReporte() {
  if (!form.central_id) return
  error.value = ''

  for (const cal of calidades) {
    const p = precios[cal.key]
    if (!p.sin_dato && (p.precio === undefined || p.precio === null)) {
      error.value = `Ingresa el precio de ${cal.label} o márcalo como sin dato`
      return
    }
    if (!p.sin_dato && p.precio! < 0) {
      error.value = `El precio de ${cal.label} no puede ser negativo`
      return
    }
  }

  submitting.value = true
  try {
    await jitomateService.crearReporte({
      central_id: form.central_id as number,
      fecha: form.fecha,
      corte: form.corte,
      observaciones: form.observaciones || undefined,
      precios: calidades.map(c => ({
        calidad: c.key,
        precio: precios[c.key].sin_dato ? undefined : precios[c.key].precio,
        sin_dato: precios[c.key].sin_dato,
      })),
    })

    ui.showToast('Reporte guardado correctamente', 'success')

    // Reset precios
    for (const cal of calidades) {
      precios[cal.key].precio = undefined
      precios[cal.key].sin_dato = false
    }
    form.observaciones = ''

    // Recargar capturas del día
    await cargarReportesHoy()
  } catch (e: any) {
    const msg = e?.response?.data?.detail || 'Error al guardar el reporte'
    error.value = msg
    ui.showToast(msg, 'error')
  } finally {
    submitting.value = false
  }
}

async function cargarReportesHoy() {
  try {
    reportesHoy.value = await jitomateService.getReportes({ fecha_desde: hoy, fecha_hasta: hoy })
  } catch {
    // silent
  }
}

onMounted(async () => {
  try {
    misCentrales.value = await centralesService.getMisCentrales()
  } finally {
    loadingCentrales.value = false
  }
  await cargarReportesHoy()
})
</script>

<style scoped>
.captura-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.captura-header__icon {
  color: #c0392b;
  flex-shrink: 0;
}
.captura-header h1 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}
.captura-header__sub {
  font-size: 0.78rem;
  color: #888;
  margin: 0;
}

.captura-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #444;
}
.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.9rem;
  background: #fff;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #c0392b;
}
.form-hint {
  font-size: 0.75rem;
  color: #888;
}
.form-hint a {
  color: #c0392b;
}
.form-textarea {
  resize: vertical;
  min-height: 60px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.corte-toggle {
  display: flex;
  gap: 8px;
}
.corte-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 10px;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  background: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}
.corte-btn--active {
  border-color: #c0392b;
  background: #fef5f5;
  color: #c0392b;
}

.calidades-section {
  background: #fafafa;
  border: 1.5px solid #ebebeb;
  border-radius: 12px;
  padding: 14px;
}
.calidades-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 12px;
}
.calidad-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.calidad-row:last-child {
  margin-bottom: 0;
}
.calidad-label {
  width: 80px;
  flex-shrink: 0;
}
.calidad-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}
.calidad-badge--primera { background: #ffd700; color: #333; }
.calidad-badge--segunda { background: #c0c0c0; color: #333; }
.calidad-badge--tercera { background: #cd7f32; color: #fff; }

.calidad-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}
.calidad-input {
  flex: 1;
}
.sin-dato-label {
  flex: 1;
  font-size: 0.8rem;
  color: #999;
  font-style: italic;
  padding: 10px 12px;
}
.sin-dato-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1.5px solid #e0e0e0;
  background: #fff;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.sin-dato-btn--active {
  border-color: #c0392b;
  background: #fef5f5;
  color: #c0392b;
}

.alert {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 0.82rem;
}
.alert--warning {
  background: #fff8e1;
  color: #f57c00;
  border: 1px solid #ffe082;
}
.alert--error {
  background: #fce4ec;
  color: #c0392b;
  border: 1px solid #f48fb1;
}

.btn--lg {
  padding: 14px;
  font-size: 1rem;
  margin-top: 4px;
}
.btn--primary {
  background: #c0392b;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.2s;
}
.btn--primary:hover:not(:disabled) { background: #a93226; }
.btn--primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--full { width: 100%; }

.spinner-inline {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

.reportes-hoy {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebebeb;
}
.reportes-hoy__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #2e7d32;
  margin: 0 0 10px;
}
.reporte-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f1f8f1;
  border: 1px solid #c8e6c9;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 0.82rem;
  color: #333;
  margin-bottom: 6px;
}
.reporte-chip__corte {
  margin-left: auto;
  font-size: 0.72rem;
  color: #666;
  text-transform: capitalize;
}
.reporte-chip__tardia {
  font-size: 0.65rem;
  color: #f57c00;
  background: #fff8e1;
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 700;
}

@media (max-width: 480px) {
  .captura-header h1 { font-size: 1.1rem; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
