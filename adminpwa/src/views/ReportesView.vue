<template>
  <AdminLayout>

    <!-- ══ HEADER ══════════════════════════════════════════════════ -->
    <div class="page-header">
      <div class="page-header__pattern"></div>
      <div class="page-header__left">
        <div class="page-header__icon">
          <ClipboardList :size="20" />
        </div>
        <div>
          <h1 class="page-header__title">Reportes</h1>
          <p class="page-header__sub">Precios de jitomate capturados por central — {{ reportes.length }} registro{{ reportes.length !== 1 ? 's' : '' }}</p>
        </div>
      </div>
      <button class="btn-refresh" @click="load" :disabled="loading" title="Actualizar">
        <RefreshCw :size="16" :class="{ spinning: loading }" />
      </button>
    </div>

    <!-- ══ FILTROS ══════════════════════════════════════════════════ -->
    <div class="filters-card">
      <div class="filters-grid">
        <div class="filter-group">
          <label class="filter-label">Desde</label>
          <input type="date" v-model="filtros.fecha_desde" class="filter-input" />
        </div>
        <div class="filter-group">
          <label class="filter-label">Hasta</label>
          <input type="date" v-model="filtros.fecha_hasta" class="filter-input" />
        </div>
        <div class="filter-group">
          <label class="filter-label">Corte</label>
          <select v-model="filtros.corte" class="filter-input">
            <option value="">Todos</option>
            <option value="matutino">Matutino</option>
            <option value="mediodia">Mediodía</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">Estado</label>
          <select v-model="filtros.estado" class="filter-input">
            <option value="">Todos</option>
            <option v-for="e in estados" :key="e">{{ e }}</option>
          </select>
        </div>
        <div class="filter-group filter-group--wide">
          <label class="filter-label">Capturista</label>
          <input type="text" v-model="filtros.capturista" class="filter-input" placeholder="Nombre o correo..." />
        </div>
        <div class="filter-group filter-group--action">
          <button class="btn-search" @click="load">
            <Search :size="15" />
            Buscar
          </button>
        </div>
      </div>
    </div>

    <!-- ══ TABLA ══════════════════════════════════════════════════ -->
    <div class="table-card">

      <!-- Loading skeleton -->
      <div v-if="loading" class="loading-wrap">
        <div class="skeleton-row" v-for="i in 6" :key="i">
          <div class="skeleton-cell skeleton-cell--date"></div>
          <div class="skeleton-cell skeleton-cell--badge"></div>
          <div class="skeleton-cell skeleton-cell--text"></div>
          <div class="skeleton-cell skeleton-cell--sm"></div>
          <div class="skeleton-cell skeleton-cell--price"></div>
          <div class="skeleton-cell skeleton-cell--price"></div>
          <div class="skeleton-cell skeleton-cell--price"></div>
          <div class="skeleton-cell skeleton-cell--text"></div>
          <div class="skeleton-cell skeleton-cell--sm"></div>
          <div class="skeleton-cell skeleton-cell--btn"></div>
        </div>
      </div>

      <!-- Tabla real -->
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Corte</th>
              <th>Central</th>
              <th>Estado</th>
              <th class="th-price">1ra Calidad</th>
              <th class="th-price">2da Calidad</th>
              <th class="th-price">3ra Calidad</th>
              <th>Capturista</th>
              <th class="th-center">Tardía</th>
              <th v-if="auth.hasPermiso('reportes:acciones')" class="th-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="r in reportes"
              :key="r.id"
              :class="{ 'row--deleting': deletingIds.has(r.id) }"
            >
              <td class="td-date">
                <span class="date-pill">{{ formatFecha(r.fecha) }}</span>
              </td>
              <td>
                <span class="badge" :class="r.corte === 'matutino' ? 'badge--sunrise' : 'badge--noon'">
                  {{ r.corte === 'matutino' ? '☀ Matutino' : '⛅ Mediodía' }}
                </span>
              </td>
              <td class="td-central">
                <span class="central-name">{{ r.nombre_central }}</span>
              </td>
              <td class="td-estado">{{ r.estado }}</td>
              <td class="td-price">
                <span :class="r.sin_dato_primera ? 'price--nd' : 'price--val'">
                  {{ r.sin_dato_primera ? 'S/D' : r.precio_primera != null ? '$' + r.precio_primera.toFixed(2) : '—' }}
                </span>
              </td>
              <td class="td-price">
                <span :class="r.sin_dato_segunda ? 'price--nd' : 'price--val'">
                  {{ r.sin_dato_segunda ? 'S/D' : r.precio_segunda != null ? '$' + r.precio_segunda.toFixed(2) : '—' }}
                </span>
              </td>
              <td class="td-price">
                <span :class="r.sin_dato_tercera ? 'price--nd' : 'price--val'">
                  {{ r.sin_dato_tercera ? 'S/D' : r.precio_tercera != null ? '$' + r.precio_tercera.toFixed(2) : '—' }}
                </span>
              </td>
              <td class="td-capturista">
                <div class="capturista-wrap">
                  <span class="capturista-avatar">{{ iniciales(r.capturista_nombre) }}</span>
                  <span class="capturista-nombre">{{ r.capturista_nombre }}</span>
                </div>
              </td>
              <td class="td-center">
                <span v-if="r.captura_tardia" class="badge badge--late">Tardía</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td v-if="auth.hasPermiso('reportes:acciones')" class="td-center">
                <button
                  class="btn-action"
                  :disabled="deletingIds.has(r.id)"
                  @click="abrirModal(r)"
                  title="Eliminar reporte"
                >
                  <span v-if="deletingIds.has(r.id)" class="micro-spinner"></span>
                  <Trash2 v-else :size="15" />
                </button>
              </td>
            </tr>

            <!-- Empty state -->
            <tr v-if="!reportes.length">
              <td colspan="10">
                <div class="empty-state">
                  <div class="empty-state__icon">
                    <ClipboardList :size="36" />
                  </div>
                  <p class="empty-state__title">Sin reportes</p>
                  <p class="empty-state__sub">Ajusta los filtros o registra nuevas capturas.</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ MODAL CONFIRMAR ELIMINACIÓN ══════════════════════════════ -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.visible" class="modal-overlay" @click.self="cerrarModal">
          <div class="modal-card" role="dialog" aria-modal="true">

            <!-- Icono destructivo -->
            <div class="modal-icon-wrap">
              <div class="modal-icon">
                <Trash2 :size="26" />
              </div>
            </div>

            <h2 class="modal-title">Eliminar reporte</h2>
            <p class="modal-desc">
              Esta acción eliminará permanentemente el reporte de
              <strong>{{ modal.central }}</strong>
              del día
              <strong>{{ modal.fecha }}</strong>.
              No se puede deshacer.
            </p>

            <!-- Info pill -->
            <div class="modal-info">
              <div class="modal-info__row">
                <span class="modal-info__label">Central</span>
                <span class="modal-info__val">{{ modal.central }}</span>
              </div>
              <div class="modal-info__row">
                <span class="modal-info__label">Fecha</span>
                <span class="modal-info__val">{{ modal.fecha }}</span>
              </div>
              <div class="modal-info__row">
                <span class="modal-info__label">Corte</span>
                <span class="modal-info__val">{{ modal.corte }}</span>
              </div>
            </div>

            <!-- Acciones -->
            <div class="modal-actions">
              <button class="modal-btn modal-btn--cancel" @click="cerrarModal">
                Cancelar
              </button>
              <button
                class="modal-btn modal-btn--delete"
                :disabled="deletingIds.has(modal.id!)"
                @click="confirmarEliminar"
              >
                <span v-if="deletingIds.has(modal.id!)" class="micro-spinner micro-spinner--white"></span>
                <Trash2 v-else :size="15" />
                Eliminar
              </button>
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>

  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/components/AdminLayout.vue'
import type { ReporteJitomate } from '@/types'
import { ClipboardList, Trash2, Search, RefreshCw } from 'lucide-vue-next'

const auth = useAuthStore()

// ── State ──────────────────────────────────────────────────────────
const loading = ref(false)
const reportes = ref<ReporteJitomate[]>([])
const deletingIds = ref(new Set<number>())

const filtros = reactive({
  fecha_desde: '',
  fecha_hasta: '',
  corte: '',
  estado: '',
  capturista: '',
})

interface ModalState {
  visible: boolean
  id: number | null
  central: string
  fecha: string
  corte: string
}
const modal = reactive<ModalState>({
  visible: false,
  id: null,
  central: '',
  fecha: '',
  corte: '',
})

// ── Computed ───────────────────────────────────────────────────────
const estados = computed(() => {
  const s = new Set(reportes.value.map(r => r.estado).filter(Boolean))
  return [...s].sort()
})

// ── Helpers ────────────────────────────────────────────────────────
function formatFecha(fecha: string): string {
  if (!fecha) return '—'
  const [y, m, d] = fecha.split('-')
  return `${d}/${m}/${y}`
}

function iniciales(nombre: string): string {
  if (!nombre) return '?'
  return nombre
    .split(' ')
    .slice(0, 2)
    .map(n => n[0] || '')
    .join('')
    .toUpperCase()
}

// ── Data ───────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  try {
    const p: Record<string, string> = {}
    Object.entries(filtros).forEach(([k, v]) => { if (v) p[k] = v })
    reportes.value = await authService.getReportes(p)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// ── Modal ──────────────────────────────────────────────────────────
function abrirModal(r: ReporteJitomate) {
  modal.id = r.id
  modal.central = r.nombre_central
  modal.fecha = formatFecha(r.fecha)
  modal.corte = r.corte === 'matutino' ? 'Matutino' : 'Mediodía'
  modal.visible = true
}

function cerrarModal() {
  modal.visible = false
}

async function confirmarEliminar() {
  if (!modal.id) return
  const id = modal.id
  deletingIds.value.add(id)
  try {
    await authService.deleteReporte(id)
    reportes.value = reportes.value.filter(r => r.id !== id)
    cerrarModal()
  } catch (e) {
    console.error(e)
  } finally {
    deletingIds.value.delete(id)
  }
}

onMounted(load)
</script>

<style scoped>
/* ── Fuente base Apple ─────────────────────────────────────────── */
* {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
  box-sizing: border-box;
}

/* ══ HEADER ════════════════════════════════════════════════════════ */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #B71C1C 0%, #D32F2F 60%, #C62828 100%);
  border-radius: 20px;
  padding: 1.1rem 1.4rem;
  margin-bottom: 1rem;
  box-shadow: 0 8px 32px rgba(183, 28, 28, 0.28), 0 2px 8px rgba(183, 28, 28, 0.15);
  position: relative; overflow: hidden;
}
.page-header__pattern {
  position: absolute; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cellipse cx='16' cy='20' rx='9' ry='8' fill='none' stroke='%239b0000' stroke-width='1.2' opacity='0.6'/%3E%3Cline x1='16' y1='12' x2='16' y2='8' stroke='%239b0000' stroke-width='1.1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C13,9 10,9.5 9.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C19,9 22,9.5 22.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,10.5 C15.5,7.5 15,5.5 16,4.5 C17,5.5 16.5,7.5 16,10.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3C/svg%3E");
  background-size: 32px 32px; background-repeat: repeat;
}
.page-header__left {
  position: relative; z-index: 1;
}
.page-header__left {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}
.page-header__icon {
  width: 42px;
  height: 42px;
  background: rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.22);
  flex-shrink: 0;
}
.page-header__title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
}
.page-header__sub {
  margin: 0;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 400;
  margin-top: 1px;
}
.btn-refresh {
  position: relative; z-index: 1;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: none;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.22);
}
.btn-refresh:hover { background: rgba(255, 255, 255, 0.28); }
.btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }
.spinning { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ══ FILTROS ═══════════════════════════════════════════════════════ */
.filters-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(1.8);
  border-radius: 16px;
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.05);
}
.filters-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 120px;
}
.filter-group--wide { flex: 1; min-width: 160px; }
.filter-group--action { justify-content: flex-end; min-width: auto; }
.filter-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: #6E6E73;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.filter-input {
  padding: 7px 11px;
  border: 1.5px solid #E5E5EA;
  border-radius: 10px;
  font-size: 0.82rem;
  background: #fff;
  color: #1C1C1E;
  transition: border-color 0.15s, box-shadow 0.15s;
  outline: none;
  height: 36px;
}
.filter-input:focus {
  border-color: #B71C1C;
  box-shadow: 0 0 0 3px rgba(183, 28, 28, 0.12);
}
.btn-search {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 18px;
  height: 36px;
  background: linear-gradient(135deg, #B71C1C, #D32F2F);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
  white-space: nowrap;
  box-shadow: 0 2px 10px rgba(183, 28, 28, 0.35);
}
.btn-search:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-search:active { transform: translateY(0); }

/* ══ TABLA CARD ════════════════════════════════════════════════════ */
.table-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px) saturate(1.8);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* ── Loading skeleton ── */
.loading-wrap { padding: 0.5rem 1rem 1rem; }
.skeleton-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #F2F2F7;
}
.skeleton-cell {
  height: 14px;
  border-radius: 7px;
  background: linear-gradient(90deg, #F2F2F7 25%, #E5E5EA 50%, #F2F2F7 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease infinite;
}
@keyframes shimmer { to { background-position: -200% 0; } }
.skeleton-cell--date { width: 70px; }
.skeleton-cell--badge { width: 80px; height: 22px; border-radius: 11px; }
.skeleton-cell--text { width: 130px; }
.skeleton-cell--sm { width: 55px; }
.skeleton-cell--price { width: 60px; }
.skeleton-cell--btn { width: 30px; height: 30px; border-radius: 8px; }

/* ── Tabla ── */
.table-wrap { overflow-x: auto; }
.table {
  width: 100%;
  border-collapse: collapse;
  min-width: 780px;
}
.table thead th {
  padding: 11px 14px;
  font-size: 0.7rem;
  font-weight: 600;
  color: #6E6E73;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: #F9F9FB;
  border-bottom: 1px solid #E5E5EA;
  white-space: nowrap;
}
.th-price { text-align: right; }
.th-center { text-align: center; }
.table tbody tr {
  border-bottom: 1px solid #F2F2F7;
  transition: background 0.12s;
}
.table tbody tr:last-child { border-bottom: none; }
.table tbody tr:hover { background: rgba(183, 28, 28, 0.025); }
.table tbody tr.row--deleting { opacity: 0.45; pointer-events: none; }
.table tbody td {
  padding: 11px 14px;
  font-size: 0.82rem;
  color: #1C1C1E;
  vertical-align: middle;
}

/* Celda fecha */
.td-date { white-space: nowrap; }
.date-pill {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 7px;
  background: #F2F2F7;
  font-size: 0.78rem;
  font-weight: 600;
  color: #3A3A3C;
  letter-spacing: 0.01em;
}

/* Badges corte */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}
.badge--sunrise {
  background: rgba(255, 149, 0, 0.12);
  color: #9B5A00;
}
.badge--noon {
  background: rgba(0, 122, 255, 0.1);
  color: #0055B3;
}
.badge--late {
  background: rgba(255, 59, 48, 0.1);
  color: #C0392B;
}

/* Central */
.td-central { max-width: 180px; }
.central-name {
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.td-estado { color: #6E6E73; font-size: 0.78rem; white-space: nowrap; }

/* Precios */
.td-price { text-align: right; white-space: nowrap; }
.price--val {
  font-weight: 600;
  color: #1C1C1E;
  font-variant-numeric: tabular-nums;
}
.price--nd {
  font-size: 0.75rem;
  color: #AEAEB2;
  font-weight: 500;
}

/* Capturista */
.td-capturista { white-space: nowrap; }
.capturista-wrap {
  display: flex;
  align-items: center;
  gap: 7px;
}
.capturista-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #B71C1C, #D32F2F);
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}
.capturista-nombre {
  font-size: 0.8rem;
  font-weight: 500;
  color: #1C1C1E;
  max-width: 130px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Centrado */
.td-center { text-align: center; }
.text-muted { color: #AEAEB2; font-size: 0.8rem; }

/* Botón acción */
.btn-action {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  border: 1.5px solid #FFE0DE;
  background: #FFF5F5;
  color: #C62828;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.btn-action:hover:not(:disabled) {
  background: #B71C1C;
  border-color: #B71C1C;
  color: #fff;
  transform: scale(1.1);
  box-shadow: 0 4px 14px rgba(183, 28, 28, 0.35);
}
.btn-action:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

/* Empty state */
.empty-state {
  padding: 3.5rem 1rem;
  text-align: center;
  color: #AEAEB2;
}
.empty-state__icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: #F2F2F7;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: #C7C7CC;
}
.empty-state__title {
  font-size: 1rem;
  font-weight: 600;
  color: #3A3A3C;
  margin: 0 0 4px;
}
.empty-state__sub {
  font-size: 0.82rem;
  color: #AEAEB2;
  margin: 0;
}

/* Micro spinner */
.micro-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(183, 28, 28, 0.25);
  border-top-color: #B71C1C;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
.micro-spinner--white {
  border-color: rgba(255,255,255,0.3);
  border-top-color: #fff;
}

/* ══ MODAL ════════════════════════════════════════════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(12px) saturate(1.2);
  z-index: 9000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}
.modal-card {
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(40px) saturate(2);
  border-radius: 24px;
  padding: 2rem 1.8rem 1.6rem;
  max-width: 380px;
  width: 100%;
  box-shadow:
    0 40px 80px rgba(0, 0, 0, 0.22),
    0 8px 24px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
  text-align: center;
}
.modal-icon-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 1.1rem;
}
.modal-icon {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: linear-gradient(135deg, #FFEDED, #FFD6D6);
  color: #B71C1C;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(183, 28, 28, 0.2);
}
.modal-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #1C1C1E;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.modal-desc {
  font-size: 0.85rem;
  color: #6E6E73;
  line-height: 1.5;
  margin: 0 0 1.2rem;
}
.modal-desc strong { color: #1C1C1E; font-weight: 600; }

.modal-info {
  background: #F9F9FB;
  border-radius: 14px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.4rem;
  border: 1px solid #E5E5EA;
  text-align: left;
}
.modal-info__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 0;
}
.modal-info__row:not(:last-child) {
  border-bottom: 1px solid #F0F0F0;
}
.modal-info__label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #AEAEB2;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.modal-info__val {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1C1C1E;
  max-width: 200px;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
}
.modal-btn {
  flex: 1;
  height: 44px;
  border-radius: 14px;
  border: none;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.18s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-btn--cancel {
  background: #F2F2F7;
  color: #3A3A3C;
  border: 1.5px solid #E5E5EA;
}
.modal-btn--cancel:hover { background: #E5E5EA; transform: translateY(-1px); }
.modal-btn--delete {
  background: linear-gradient(135deg, #B71C1C, #D32F2F);
  color: #fff;
  box-shadow: 0 4px 14px rgba(183, 28, 28, 0.4);
}
.modal-btn--delete:hover:not(:disabled) {
  opacity: 0.92;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(183, 28, 28, 0.5);
}
.modal-btn--delete:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

/* ══ TRANSICIÓN MODAL ══════════════════════════════════════════════ */
.modal-enter-active {
  transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-leave-active {
  transition: all 0.18s cubic-bezier(0.4, 0, 1, 1);
}
.modal-enter-from {
  opacity: 0;
}
.modal-enter-from .modal-card {
  transform: scale(0.88) translateY(20px);
  opacity: 0;
}
.modal-leave-to {
  opacity: 0;
}
.modal-leave-to .modal-card {
  transform: scale(0.92) translateY(10px);
  opacity: 0;
}

/* ══ RESPONSIVE ════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  .page-header { border-radius: 16px; }
  .page-header__title { font-size: 1rem; }
  .filters-card { padding: 0.85rem 0.9rem; }
  .filter-group { min-width: calc(50% - 0.35rem); }
  .filter-group--wide { min-width: 100%; }
  .filter-group--action { min-width: 100%; }
  .btn-search { width: 100%; justify-content: center; }
  .table-card { border-radius: 16px; }
  .modal-card { padding: 1.6rem 1.3rem 1.4rem; border-radius: 20px; }
  .modal-title { font-size: 1rem; }
  .modal-btn { height: 48px; font-size: 0.92rem; }
}
</style>
