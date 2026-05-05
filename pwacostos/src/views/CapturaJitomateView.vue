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
                <Sun :size="15" /> Matutino
              </button>
              <button
                type="button"
                class="corte-btn"
                :class="{ 'corte-btn--active': form.corte === 'mediodia' }"
                @click="form.corte = 'mediodia'"
              >
                <Cloud :size="15" /> Mediodía
              </button>
            </div>
          </div>
        </div>

        <!-- Ayuda de corte -->
        <div class="corte-ayuda">
          <Info :size="14" />
          <span v-if="form.corte === 'matutino'">Matutino: captura de referencia de 4:00 a 6:00 a.m.</span>
          <span v-else>Mediodía: captura de referencia a las 12:00 p.m.</span>
        </div>

        <!-- Hora real de captura -->
        <div class="hora-captura-info" :class="{ 'hora-captura-info--tardia': esTardia }">
          <Clock :size="14" />
          <span>Hora de captura: <strong>{{ horaActualStr }}</strong></span>
          <span v-if="esTardia" class="tardia-badge">Tardía</span>
        </div>

        <!-- Precios por calidad con disponibilidad -->
        <div class="calidades-section">
          <h3 class="calidades-title">
            <Tag :size="18" /> Precios por calidad
          </h3>

          <div v-for="cal in calidades" :key="cal.key" class="calidad-card">
            <div class="calidad-card__header">
              <span class="calidad-badge" :class="`calidad-badge--${cal.key}`">{{ cal.label }}</span>
              <span class="calidad-desc">{{ cal.desc }}</span>
            </div>

            <div class="calidad-card__body">
              <!-- Dropdown disponibilidad -->
              <div class="form-group-inline">
                <label class="form-label-sm">Disponibilidad</label>
                <select
                  v-model="precios[cal.key].disponibilidad"
                  class="form-select-sm"
                  @change="onDisponibilidadChange(cal.key)"
                >
                  <option value="alta">Alta — hay suficiente producto</option>
                  <option value="media">Media — hay pero no es abundante</option>
                  <option value="baja">Baja — poco producto disponible</option>
                  <option value="no_hay">No hay — sin producto en este corte</option>
                </select>
              </div>

              <!-- Precio (solo si hay disponibilidad) -->
              <div class="form-group-inline" v-if="precios[cal.key].disponibilidad !== 'no_hay'">
                <label class="form-label-sm">Precio $/kg *</label>
                <div class="precio-input-wrap">
                  <span class="precio-prefix">$</span>
                  <input
                    v-model.number="precios[cal.key].precio"
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    class="form-input precio-input"
                    required
                  />
                </div>
              </div>

              <!-- Sin dato visual cuando no hay -->
              <div v-else class="no-hay-info">
                <Ban :size="14" />
                <span>Sin precio — no hay producto disponible</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Observaciones -->
        <div class="form-group">
          <label class="form-label">Observaciones (opcional)</label>
          <textarea v-model="form.observaciones" class="form-textarea" rows="2" placeholder="Notas adicionales..."></textarea>
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
import type { MiCentral, ReporteJitomateOut, Corte, Disponibilidad } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  Salad, Sun, Cloud, Tag, Ban, Save,
  AlertCircle, CheckCircle, Building2, Clock, Info
} from 'lucide-vue-next'

const ui = useUiStore()

const hoy = new Date().toISOString().split('T')[0]
const horaActual = new Date().getHours()

// Hora real actualizada cada minuto
const ahora = ref(new Date())
const horaActualStr = computed(() => ahora.value.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }))

const loadingCentrales = ref(true)
const submitting = ref(false)
const error = ref('')

const misCentrales = ref<MiCentral[]>([])
const reportesHoy = ref<ReporteJitomateOut[]>([])

type CalidadKey = 'primera' | 'segunda' | 'tercera'

const calidades: { key: CalidadKey; label: string; desc: string }[] = [
  { key: 'primera', label: 'Primera', desc: 'Calidad exportación' },
  { key: 'segunda', label: 'Segunda', desc: 'Grandes buenos' },
  { key: 'tercera', label: 'Tercera', desc: 'Revueltos y maduros' },
]

const form = reactive({
  central_id: '' as number | '',
  fecha: hoy,
  corte: (horaActual < 11 ? 'matutino' : 'mediodia') as Corte,
  observaciones: '',
})

const precios = reactive<Record<CalidadKey, { precio?: number; disponibilidad: Disponibilidad; sin_dato: boolean }>>({
  primera: { precio: undefined, disponibilidad: 'alta', sin_dato: false },
  segunda: { precio: undefined, disponibilidad: 'alta', sin_dato: false },
  tercera: { precio: undefined, disponibilidad: 'alta', sin_dato: false },
})

const esTardia = computed(() => {
  const h = ahora.value.getHours()
  if (form.corte === 'matutino') return h > 11
  if (form.corte === 'mediodia') return h > 17
  return false
})

function onDisponibilidadChange(calidad: CalidadKey) {
  if (precios[calidad].disponibilidad === 'no_hay') {
    precios[calidad].precio = undefined
    precios[calidad].sin_dato = true
  } else {
    precios[calidad].sin_dato = false
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
    if (p.disponibilidad !== 'no_hay') {
      if (p.precio === undefined || p.precio === null) {
        error.value = `Ingresa el precio de ${cal.label}`
        return
      }
      if (p.precio < 0) {
        error.value = `El precio de ${cal.label} no puede ser negativo`
        return
      }
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
        precio: precios[c.key].disponibilidad === 'no_hay' ? undefined : precios[c.key].precio,
        sin_dato: precios[c.key].disponibilidad === 'no_hay',
        disponibilidad: precios[c.key].disponibilidad,
      })),
    })

    ui.showToast('Reporte guardado correctamente', 'success')

    // Reset precios
    for (const cal of calidades) {
      precios[cal.key].precio = undefined
      precios[cal.key].disponibilidad = 'alta'
      precios[cal.key].sin_dato = false
    }
    form.observaciones = ''
    ahora.value = new Date()

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
  // Actualizar reloj cada minuto
  setInterval(() => { ahora.value = new Date() }, 60_000)

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
.captura-header__icon { color: #c0392b; flex-shrink: 0; }
.captura-header h1 { font-size: 1.3rem; font-weight: 700; color: #1a1a1a; margin: 0; }
.captura-header__sub { font-size: 0.78rem; color: #888; margin: 0; }

.captura-form { display: flex; flex-direction: column; gap: 14px; }

.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 0.82rem; font-weight: 600; color: #444; }
.form-label-sm { font-size: 0.78rem; font-weight: 600; color: #555; min-width: 100px; }
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
.form-select-sm {
  flex: 1;
  padding: 8px 10px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.82rem;
  background: #fff;
  transition: border-color 0.2s;
}
.form-select-sm:focus { outline: none; border-color: #c0392b; }
.form-hint { font-size: 0.75rem; color: #888; }
.form-hint a { color: #c0392b; }
.form-textarea { resize: vertical; min-height: 60px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.corte-toggle { display: flex; gap: 8px; }
.corte-btn {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 5px;
  padding: 9px 8px;
  border: 1.5px solid #e0e0e0; border-radius: 10px;
  background: #fff; font-size: 0.8rem; font-weight: 600; color: #666;
  cursor: pointer; transition: all 0.2s;
}
.corte-btn--active { border-color: #c0392b; background: #fef5f5; color: #c0392b; }

.corte-ayuda {
  display: flex; align-items: center; gap: 6px;
  background: #f0f4ff; border-radius: 8px; padding: 8px 12px;
  font-size: 0.78rem; color: #3a5bd0;
  margin-top: -4px;
}

.hora-captura-info {
  display: flex; align-items: center; gap: 6px;
  background: #f8f8f8; border: 1px solid #e8e8e8;
  border-radius: 8px; padding: 8px 12px;
  font-size: 0.8rem; color: #555;
}
.hora-captura-info--tardia { background: #fff8e1; border-color: #ffe082; color: #e65100; }
.tardia-badge {
  margin-left: auto;
  font-size: 0.68rem; font-weight: 700;
  background: #ff9800; color: #fff;
  padding: 2px 8px; border-radius: 6px;
}

/* Calidades */
.calidades-section {
  background: #fafafa;
  border: 1.5px solid #ebebeb;
  border-radius: 14px;
  padding: 14px;
}
.calidades-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.85rem; font-weight: 700; color: #333;
  margin: 0 0 14px;
}

.calidad-card {
  background: #fff;
  border: 1.5px solid #ebebeb;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
}
.calidad-card:last-child { margin-bottom: 0; }

.calidad-card__header {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 10px;
}
.calidad-badge {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  flex-shrink: 0;
}
.calidad-badge--primera { background: #ffd700; color: #333; }
.calidad-badge--segunda { background: #c0c0c0; color: #333; }
.calidad-badge--tercera { background: #cd7f32; color: #fff; }
.calidad-desc { font-size: 0.75rem; color: #888; font-style: italic; }

.calidad-card__body { display: flex; flex-direction: column; gap: 8px; }

.form-group-inline {
  display: flex; align-items: center; gap: 8px;
}

.precio-input-wrap {
  display: flex; align-items: center; gap: 0; flex: 1;
  border: 1.5px solid #e0e0e0; border-radius: 8px; overflow: hidden;
  transition: border-color 0.2s;
}
.precio-input-wrap:focus-within { border-color: #c0392b; }
.precio-prefix {
  padding: 8px 10px;
  background: #f5f5f5;
  color: #666;
  font-size: 0.88rem;
  font-weight: 600;
  border-right: 1px solid #e0e0e0;
}
.precio-input {
  flex: 1; border: none !important; border-radius: 0 !important;
  padding: 8px 10px !important;
  font-size: 0.9rem;
}
.precio-input:focus { outline: none; }

.no-hay-info {
  display: flex; align-items: center; gap: 6px;
  background: #fff3e0; border-radius: 8px; padding: 8px 12px;
  font-size: 0.78rem; color: #e65100;
}

.alert {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 10px 12px; border-radius: 10px; font-size: 0.82rem;
}
.alert--error { background: #fce4ec; color: #c0392b; border: 1px solid #f48fb1; }

.btn--lg { padding: 14px; font-size: 1rem; margin-top: 4px; }
.btn--primary {
  background: #c0392b; color: #fff; border: none; border-radius: 12px;
  font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: background 0.2s;
}
.btn--primary:hover:not(:disabled) { background: #a93226; }
.btn--primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--full { width: 100%; }

.spinner-inline {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.7s linear infinite; display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

.reportes-hoy { margin-top: 24px; padding-top: 16px; border-top: 1px solid #ebebeb; }
.reportes-hoy__title {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.85rem; font-weight: 700; color: #2e7d32; margin: 0 0 10px;
}
.reporte-chip {
  display: flex; align-items: center; gap: 8px;
  background: #f1f8f1; border: 1px solid #c8e6c9;
  border-radius: 10px; padding: 8px 12px;
  font-size: 0.82rem; color: #333; margin-bottom: 6px;
}
.reporte-chip__corte { margin-left: auto; font-size: 0.72rem; color: #666; text-transform: capitalize; }
.reporte-chip__tardia {
  font-size: 0.65rem; color: #f57c00; background: #fff8e1;
  padding: 1px 6px; border-radius: 6px; font-weight: 700;
}

@media (max-width: 480px) {
  .captura-header h1 { font-size: 1.1rem; }
  .form-row { grid-template-columns: 1fr; }
  .form-group-inline { flex-direction: column; align-items: flex-start; }
  .form-label-sm { min-width: unset; }
  .form-select-sm { width: 100%; }
}
</style>
