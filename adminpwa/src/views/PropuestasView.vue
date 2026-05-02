<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <Layers :size="30" />
        </div>
        <div class="sidebar-brand">
          <span class="sidebar-brand__title">COSTOS</span>
          <span class="sidebar-brand__sub">Panel Admin</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="sidebar-nav-label">Menú</div>
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <LayoutDashboard :size="18" />
          <span>Dashboard</span>
        </router-link>
        <router-link to="/usuarios" class="nav-item" :class="{ active: $route.path === '/usuarios' }">
          <Users :size="18" />
          <span>Administradores</span>
        </router-link>
        <router-link to="/usuarios-pwa" class="nav-item" :class="{ active: $route.path === '/usuarios-pwa' }">
          <Users :size="18" />
          <span>Usuarios</span>
        </router-link>
        <router-link to="/propuestas" class="nav-item" :class="{ active: $route.path === '/propuestas' }">
          <Store :size="18" />
          <span>Propuestas Mercados</span>
        </router-link>
        <router-link to="/visor" class="nav-item" :class="{ active: $route.path === '/visor' }">
          <Map :size="18" />
          <span>Visor de Mapa</span>
        </router-link>
        <router-link to="/registros-precios" class="nav-item" :class="{ active: $route.path === '/registros-precios' }">
          <ClipboardList :size="18" />
          <span>Registros Precios</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userInitials }}</div>
          <div class="user-details">
            <span class="user-name">{{ auth.user?.nombre }}</span>
            <span class="user-role">{{ auth.user?.rol }}</span>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout">
          <LogOut :size="18" />
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Top Bar -->
      <div class="top-bar">
        <div class="top-bar__info">
          <h1 class="top-bar__title"><Store :size="22" /> Propuestas de Mercados</h1>
          <p class="top-bar__desc">Mercados propuestos por los capturistas — revisar y autorizar</p>
        </div>
      </div>

      <!-- Stats + Filters -->
      <div class="toolbar-card">
        <div class="toolbar-row toolbar-row--stats">
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--total"><Store :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ propuestas.length }}</span>
              <span class="stat-pill__label">Total</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--pending"><Clock :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ countByStatus('pendiente_autorizacion') }}</span>
              <span class="stat-pill__label">Pendientes</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--approved"><CheckCircle :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ countByStatus('autorizado') }}</span>
              <span class="stat-pill__label">Autorizados</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--rejected"><XCircle :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ countByStatus('rechazado') }}</span>
              <span class="stat-pill__label">Rechazados</span>
            </div>
          </div>
        </div>
        <div class="toolbar-row toolbar-row--filters">
          <div class="search-box">
            <Search :size="18" class="search-box__icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar nombre, estado, municipio…"
              class="search-box__input"
            />
            <Transition name="fade">
              <button v-if="searchQuery" class="search-box__clear" @click="searchQuery = ''">
                <X :size="14" />
              </button>
            </Transition>
          </div>
          <div class="filter-chips">
            <div class="filter-chip">
              <ListFilter :size="14" />
              <select v-model="filterStatus">
                <option value="">Todos los estatus</option>
                <option value="pendiente_autorizacion">Pendiente</option>
                <option value="autorizado">Autorizado</option>
                <option value="rechazado">Rechazado</option>
              </select>
            </div>
            <div class="filter-chip">
              <MapPin :size="14" />
              <select v-model="filterEstado">
                <option value="">Todos los estados</option>
                <option v-for="edo in estadosUnicos" :key="edo" :value="edo">{{ edo }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="state-empty">
        <div class="spinner"></div>
        <p>Cargando propuestas…</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filtered.length === 0" class="state-empty">
        <Store :size="48" class="state-empty__icon" />
        <h3>No se encontraron propuestas</h3>
        <p v-if="searchQuery || filterStatus || filterEstado">Intenta con otros filtros de búsqueda</p>
        <p v-else>Aún no hay mercados propuestos</p>
      </div>

      <!-- Table -->
      <div v-else class="table-card">
        <div class="table-scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th>Mercado</th>
                <th>Tipo</th>
                <th class="hide-md">Estado / Municipio</th>
                <th class="hide-sm">Días</th>
                <th class="hide-sm">Propuesto por</th>
                <th>Estatus</th>
                <th class="th-actions">Acciones</th>
              </tr>
            </thead>
            <TransitionGroup name="list" tag="tbody">
              <tr v-for="p in paginated" :key="p.id">
                <td>
                  <div class="cell-user">
                    <div class="cell-user__avatar cell-user__avatar--market">
                      <Store :size="16" />
                    </div>
                    <div class="cell-user__text">
                      <span class="cell-user__name">{{ p.nombre_mercado }}</span>
                      <span class="cell-user__sub show-sm">{{ p.estado }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="chip" :class="tipoChipClass(p.tipo_mercado)">
                    {{ tipoLabel(p.tipo_mercado) }}
                  </span>
                </td>
                <td class="hide-md">
                  <div>{{ p.estado }}</div>
                  <span class="text-muted">{{ p.municipio }}</span>
                </td>
                <td class="hide-sm">{{ p.dias_operacion.join(', ') }}</td>
                <td class="hide-sm">
                  <span class="text-muted">{{ p.created_by_nombre || '—' }}</span>
                </td>
                <td>
                  <span class="chip" :class="statusChipClass(p.status)">
                    {{ statusLabel(p.status) }}
                  </span>
                </td>
                <td class="td-actions">
                  <button class="act-btn act-btn--view" title="Ver detalle" @click="openDetail(p)">
                    <Eye :size="15" />
                  </button>
                  <button
                    v-if="p.status === 'pendiente_autorizacion'"
                    class="act-btn act-btn--approve"
                    title="Autorizar"
                    @click="confirmAction(p, 'autorizar')"
                  >
                    <CheckCircle :size="15" />
                  </button>
                  <button
                    v-if="p.status === 'pendiente_autorizacion'"
                    class="act-btn act-btn--reject"
                    title="Rechazar"
                    @click="confirmAction(p, 'rechazar')"
                  >
                    <XCircle :size="15" />
                  </button>
                </td>
              </tr>
            </TransitionGroup>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button :disabled="page === 1" @click="page--">&laquo; Anterior</button>
          <span class="pagination__info">Página {{ page }} de {{ totalPages }}</span>
          <button :disabled="page === totalPages" @click="page++">Siguiente &raquo;</button>
        </div>
      </div>

      <!-- Detail Modal -->
      <Transition name="modal">
        <div v-if="detailProp" class="modal-backdrop" @click.self="detailProp = null">
          <div class="modal-card modal-card--detail">
            <div class="modal-header">
              <h2><Store :size="20" /> Detalle de Propuesta</h2>
              <button class="modal-close" @click="detailProp = null"><X :size="20" /></button>
            </div>
            <div class="modal-body">
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Nombre del mercado</label>
                  <p>{{ detailProp.nombre_mercado }}</p>
                </div>
                <div class="detail-item">
                  <label>Tipo</label>
                  <p>{{ tipoLabel(detailProp.tipo_mercado) }}
                    <template v-if="detailProp.tipo_mercado_otro"> — {{ detailProp.tipo_mercado_otro }}</template>
                  </p>
                </div>
                <div class="detail-item">
                  <label>Entidad / Municipio</label>
                  <p>{{ detailProp.estado }} — {{ detailProp.municipio }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.localidad_colonia">
                  <label>Localidad / Colonia</label>
                  <p>{{ detailProp.localidad_colonia }}</p>
                </div>
                <div class="detail-item">
                  <label>Coordenadas GPS</label>
                  <p>{{ detailProp.latitud.toFixed(6) }}, {{ detailProp.longitud.toFixed(6) }}</p>
                </div>
                <div class="detail-item">
                  <label>Días de operación</label>
                  <p>{{ detailProp.dias_operacion.join(', ') }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.horario">
                  <label>Horario</label>
                  <p>{{ detailProp.horario }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.referencia">
                  <label>Referencia</label>
                  <p>{{ detailProp.referencia }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.observaciones">
                  <label>Observaciones</label>
                  <p>{{ detailProp.observaciones }}</p>
                </div>
                <div class="detail-item">
                  <label>Propuesto por</label>
                  <p>{{ detailProp.created_by_nombre || detailProp.created_by }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.tipo_capturista">
                  <label>Tipo capturista</label>
                  <p>{{ detailProp.tipo_capturista }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.cac_nombre">
                  <label>CAC</label>
                  <p>{{ detailProp.cac_nombre }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.territorio">
                  <label>Territorio</label>
                  <p>{{ detailProp.territorio }}</p>
                </div>
                <div class="detail-item" v-if="detailProp.ruta">
                  <label>Ruta</label>
                  <p>{{ detailProp.ruta }}</p>
                </div>
                <div class="detail-item">
                  <label>Estatus</label>
                  <p><span class="chip" :class="statusChipClass(detailProp.status)">{{ statusLabel(detailProp.status) }}</span></p>
                </div>
                <div class="detail-item">
                  <label>Fecha de propuesta</label>
                  <p>{{ formatDate(detailProp.created_at) }}</p>
                </div>
              </div>

              <div v-if="detailProp.status === 'pendiente_autorizacion'" class="detail-actions">
                <button class="btn btn--success" @click="confirmAction(detailProp, 'autorizar'); detailProp = null">
                  <CheckCircle :size="16" /> Autorizar
                </button>
                <button class="btn btn--danger" @click="confirmAction(detailProp, 'rechazar'); detailProp = null">
                  <XCircle :size="16" /> Rechazar
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Confirm Modal -->
      <Transition name="modal">
        <div v-if="confirmData" class="modal-backdrop" @click.self="confirmData = null">
          <div class="modal-card modal-card--confirm" :class="confirmData.action === 'rechazar' ? 'modal-card--danger' : 'modal-card--success'">
            <div class="modal-header">
              <h2>
                <template v-if="confirmData.action === 'autorizar'">
                  <CheckCircle :size="20" /> Autorizar mercado
                </template>
                <template v-else>
                  <XCircle :size="20" /> Rechazar mercado
                </template>
              </h2>
              <button class="modal-close" @click="confirmData = null"><X :size="20" /></button>
            </div>
            <div class="modal-body">
              <p v-if="confirmData.action === 'autorizar'">
                ¿Autorizar <strong>{{ confirmData.prop.nombre_mercado }}</strong>?
                Se agregará al catálogo de mercados y estará disponible para todos los capturistas.
              </p>
              <p v-else>
                ¿Rechazar <strong>{{ confirmData.prop.nombre_mercado }}</strong>?
                La propuesta quedará marcada como rechazada.
              </p>
            </div>
            <div class="modal-footer">
              <button class="btn btn--ghost" @click="confirmData = null">Cancelar</button>
              <button
                class="btn"
                :class="confirmData.action === 'autorizar' ? 'btn--success' : 'btn--danger'"
                :disabled="actionLoading"
                @click="executeAction"
              >
                <div v-if="actionLoading" class="spinner spinner--sm"></div>
                {{ confirmData.action === 'autorizar' ? 'Sí, autorizar' : 'Sí, rechazar' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Toast -->
      <Transition name="toast">
        <div v-if="toast" class="toast" :class="'toast--' + toast.type">
          {{ toast.message }}
        </div>
      </Transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth.service'
import type { MercadoPropuesto } from '@/types'
import {
  Layers, LayoutDashboard, Users, Map, Store, LogOut,
  Search, X, ListFilter, MapPin, Eye, CheckCircle, XCircle, Clock, ClipboardList
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const token = auth.token!

const propuestas = ref<MercadoPropuesto[]>([])
const loading = ref(true)
const searchQuery = ref('')
const filterStatus = ref('')
const filterEstado = ref('')
const page = ref(1)
const perPage = 15

const detailProp = ref<MercadoPropuesto | null>(null)
const confirmData = ref<{ prop: MercadoPropuesto; action: 'autorizar' | 'rechazar' } | null>(null)
const actionLoading = ref(false)
const toast = ref<{ message: string; type: 'success' | 'error' } | null>(null)

// ── Computed ──

const estadosUnicos = computed(() => {
  const set = new Set(propuestas.value.map(p => p.estado))
  return [...set].sort()
})

const filtered = computed(() => {
  let list = propuestas.value
  if (filterStatus.value) list = list.filter(p => p.status === filterStatus.value)
  if (filterEstado.value) list = list.filter(p => p.estado === filterEstado.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p =>
      p.nombre_mercado.toLowerCase().includes(q) ||
      p.estado.toLowerCase().includes(q) ||
      p.municipio.toLowerCase().includes(q) ||
      (p.created_by_nombre || '').toLowerCase().includes(q)
    )
  }
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / perPage)))

const paginated = computed(() => {
  const start = (page.value - 1) * perPage
  return filtered.value.slice(start, start + perPage)
})

// ── Helpers ──

function countByStatus(s: string) {
  return propuestas.value.filter(p => p.status === s).length
}

function tipoLabel(t: string) {
  const map: Record<string, string> = {
    MERCADO_PUBLICO: 'Mercado Público',
    TIANGUIS: 'Tianguis',
    CENTRAL_ABASTO: 'Central de Abasto',
    OTRO: 'Otro',
  }
  return map[t] || t
}

function tipoChipClass(t: string) {
  const map: Record<string, string> = {
    MERCADO_PUBLICO: 'chip--blue',
    TIANGUIS: 'chip--green',
    CENTRAL_ABASTO: 'chip--purple',
    OTRO: 'chip--gray',
  }
  return map[t] || 'chip--gray'
}

function statusLabel(s: string) {
  const map: Record<string, string> = {
    pendiente_autorizacion: 'Pendiente',
    autorizado: 'Autorizado',
    rechazado: 'Rechazado',
  }
  return map[s] || s
}

function statusChipClass(s: string) {
  const map: Record<string, string> = {
    pendiente_autorizacion: 'chip--yellow',
    autorizado: 'chip--green',
    rechazado: 'chip--red',
  }
  return map[s] || 'chip--gray'
}

function formatDate(d?: string) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

function showToast(message: string, type: 'success' | 'error') {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3500)
}

const userInitials = computed(() => {
  const u = auth.user
  if (!u) return ''
  return (u.nombre[0] + u.apellido_paterno[0]).toUpperCase()
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}

// ── Actions ──

function openDetail(p: MercadoPropuesto) {
  detailProp.value = p
}

function confirmAction(p: MercadoPropuesto, action: 'autorizar' | 'rechazar') {
  confirmData.value = { prop: p, action }
}

async function executeAction() {
  if (!confirmData.value) return
  actionLoading.value = true
  const { prop, action } = confirmData.value
  try {
    if (action === 'autorizar') {
      await authService.autorizarPropuesta(prop.id, token)
      prop.status = 'autorizado'
      showToast(`"${prop.nombre_mercado}" autorizado y agregado al catálogo`, 'success')
    } else {
      await authService.rechazarPropuesta(prop.id, token)
      prop.status = 'rechazado'
      showToast(`"${prop.nombre_mercado}" rechazado`, 'success')
    }
    confirmData.value = null
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al procesar', 'error')
  } finally {
    actionLoading.value = false
  }
}

// ── Load ──

async function loadPropuestas() {
  loading.value = true
  try {
    propuestas.value = await authService.getPropuestas(token)
  } catch {
    showToast('Error al cargar propuestas', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(loadPropuestas)
</script>

<style scoped>
/* ── Layout (same as other views) ── */
.dashboard-layout { display: flex; min-height: 100vh; background: #f5f6fa; }

/* Sidebar */
.sidebar {
  width: 260px; min-height: 100vh; display: flex; flex-direction: column;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: #fff; position: fixed; left: 0; top: 0; z-index: 100;
  transition: width .25s cubic-bezier(.4,0,.2,1);
}
.sidebar-header { display: flex; align-items: center; gap: 12px; padding: 1.5rem 1.25rem 1rem; }
.sidebar-logo {
  width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
}
.sidebar-brand__title { font-size: 1.2rem; font-weight: 800; letter-spacing: 1px; display: block; }
.sidebar-brand__sub { font-size: .72rem; color: #94a3b8; display: block; }
.sidebar-nav { flex: 1; padding: 1rem .75rem; display: flex; flex-direction: column; gap: 2px; }
.sidebar-nav-label { font-size: .68rem; text-transform: uppercase; color: #64748b; padding: .5rem .75rem .25rem; letter-spacing: 1.2px; font-weight: 700; }
.nav-item {
  display: flex; align-items: center; gap: 10px; padding: .65rem .75rem; border-radius: 10px;
  color: #cbd5e1; text-decoration: none; font-size: .88rem; font-weight: 500;
  transition: all .18s;
}
.nav-item:hover { background: rgba(255,255,255,.06); color: #fff; }
.nav-item.active { background: rgba(79,70,229,.25); color: #a5b4fc; font-weight: 600; }
.sidebar-footer {
  display: flex; align-items: center; padding: 1rem 1.25rem; border-top: 1px solid rgba(255,255,255,.07);
  gap: 10px;
}
.user-info { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.user-avatar {
  width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #4f46e5, #7c3aed); font-weight: 700; font-size: .85rem;
}
.user-details { display: flex; flex-direction: column; min-width: 0; }
.user-name { font-size: .82rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: .68rem; color: #94a3b8; text-transform: capitalize; }
.btn-logout {
  background: rgba(255,255,255,.06); border: none; color: #94a3b8; width: 34px; height: 34px;
  border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer;
  transition: all .18s;
}
.btn-logout:hover { background: rgba(239,68,68,.18); color: #f87171; }

/* Main */
.main-content { flex: 1; margin-left: 260px; padding: 0.75rem 2rem 2rem; background: #f8fafc; min-height: 100vh; }

/* Top bar */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 14px;
  padding: 1.15rem 1.5rem; margin-bottom: 1.25rem;
  box-shadow: 0 4px 20px rgba(79,70,229,0.18); color: #fff;
}
.top-bar__title { font-size: 1.35rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem; margin: 0; }
.top-bar__desc { font-size: .85rem; color: rgba(255,255,255,0.75); margin: .15rem 0 0; }

/* Toolbar */
.toolbar-card {
  margin: 1rem 2rem; background: #fff; border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06); overflow: hidden;
}
.toolbar-row { display: flex; flex-wrap: wrap; align-items: center; padding: .75rem 1.25rem; gap: .5rem; }
.toolbar-row--stats { border-bottom: 1px solid #f1f1f1; }

/* Stat pills */
.stat-pill { display: flex; align-items: center; gap: 8px; padding: .35rem .75rem; border-radius: 10px; background: #f8f8fa; }
.stat-pill__icon { width: 30px; height: 30px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.stat-pill__icon--total { background: #e8eaf6; color: #3f51b5; }
.stat-pill__icon--pending { background: #fff8e1; color: #f9a825; }
.stat-pill__icon--approved { background: #e8f5e9; color: #2e7d32; }
.stat-pill__icon--rejected { background: #ffebee; color: #c62828; }
.stat-pill__data { display: flex; flex-direction: column; }
.stat-pill__value { font-size: .95rem; font-weight: 700; color: #1e293b; line-height: 1; }
.stat-pill__label { font-size: .66rem; color: #94a3b8; margin-top: 2px; }

/* Search */
.search-box { position: relative; flex: 1; min-width: 200px; }
.search-box__icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-box__input {
  width: 100%; padding: .55rem .75rem .55rem 38px; border: 1.5px solid #e5e7eb;
  border-radius: 10px; font-size: .88rem; outline: none; background: #fafafb;
  transition: border .2s;
}
.search-box__input:focus { border-color: #818cf8; background: #fff; }
.search-box__clear {
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
  background: #f1f1f1; border: none; border-radius: 50%; width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
}

.filter-chips { display: flex; gap: .5rem; flex-wrap: wrap; }
.filter-chip {
  display: flex; align-items: center; gap: 4px; background: #f8f8fa; border: 1.5px solid #e5e7eb;
  border-radius: 10px; padding: 0 .55rem; font-size: .82rem; color: #475569;
}
.filter-chip select {
  border: none; background: transparent; font-size: .82rem; color: #1e293b;
  padding: .45rem 0; outline: none; cursor: pointer;
}

/* States */
.state-empty { text-align: center; padding: 4rem 2rem; color: #94a3b8; }
.state-empty__icon { color: #cbd5e1; margin-bottom: .5rem; }
.state-empty h3 { color: #64748b; margin: .5rem 0 .25rem; }
.spinner {
  width: 36px; height: 36px; border: 3px solid #e5e7eb; border-top-color: #6366f1;
  border-radius: 50%; animation: spin .7s linear infinite; margin: 0 auto 1rem;
}
.spinner--sm { width: 18px; height: 18px; border-width: 2px; display: inline-block; vertical-align: middle; margin-right: 6px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Table */
.table-card {
  margin: 0 2rem 2rem; background: #fff; border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06); overflow: hidden;
}
.table-scroll { overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl th {
  text-align: left; padding: .75rem 1rem; font-size: .75rem; font-weight: 700;
  text-transform: uppercase; color: #64748b; background: #fafafb; letter-spacing: .5px;
  border-bottom: 1.5px solid #f1f1f1; white-space: nowrap;
}
.tbl td { padding: .7rem 1rem; font-size: .875rem; color: #334155; border-bottom: 1px solid #f5f5f5; }
.tbl tbody tr { transition: background .15s; }
.tbl tbody tr:hover { background: #f8f9ff; }
.th-actions { text-align: center; }
.td-actions { text-align: center; white-space: nowrap; }

/* Cell user */
.cell-user { display: flex; align-items: center; gap: 10px; }
.cell-user__avatar {
  width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: .78rem; color: #fff; flex-shrink: 0;
}
.cell-user__avatar--market { background: linear-gradient(135deg, #4f46e5, #7c3aed); }
.cell-user__text { display: flex; flex-direction: column; min-width: 0; }
.cell-user__name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cell-user__sub { font-size: .75rem; color: #94a3b8; display: none; }
.text-muted { font-size: .78rem; color: #94a3b8; }

/* Chips */
.chip {
  display: inline-block; padding: .18rem .55rem; border-radius: 6px;
  font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .3px;
}
.chip--green { background: #e8f5e9; color: #2e7d32; }
.chip--blue { background: #e3f2fd; color: #1565c0; }
.chip--purple { background: #f3e5f5; color: #7b1fa2; }
.chip--yellow { background: #fff8e1; color: #f57f17; }
.chip--red { background: #ffebee; color: #c62828; }
.chip--gray { background: #f5f5f5; color: #616161; }

/* Action buttons */
.act-btn {
  border: none; width: 30px; height: 30px; border-radius: 8px;
  display: inline-flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all .15s; margin: 0 2px;
}
.act-btn--view { background: #e8eaf6; color: #3f51b5; }
.act-btn--view:hover { background: #c5cae9; }
.act-btn--approve { background: #e8f5e9; color: #2e7d32; }
.act-btn--approve:hover { background: #c8e6c9; }
.act-btn--reject { background: #ffebee; color: #c62828; }
.act-btn--reject:hover { background: #ffcdd2; }

/* Pagination */
.pagination {
  display: flex; align-items: center; justify-content: center; gap: 1rem;
  padding: .75rem; border-top: 1px solid #f1f1f1;
}
.pagination button {
  padding: .4rem .85rem; border: 1.5px solid #e5e7eb; background: #fff;
  border-radius: 8px; font-size: .82rem; font-weight: 600; color: #475569;
  cursor: pointer; transition: all .15s;
}
.pagination button:hover:not(:disabled) { border-color: #818cf8; color: #4f46e5; }
.pagination button:disabled { opacity: .4; cursor: default; }
.pagination__info { font-size: .82rem; color: #94a3b8; }

/* Modals */
.modal-backdrop {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 500;
  background: rgba(15,23,42,.45); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.modal-card {
  background: #fff; border-radius: 16px; width: 100%; max-width: 540px;
  box-shadow: 0 20px 60px rgba(0,0,0,.18); overflow: hidden;
  max-height: 90vh; display: flex; flex-direction: column;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem; border-bottom: 1px solid #f1f1f1;
}
.modal-header h2 { font-size: 1.05rem; font-weight: 700; display: flex; align-items: center; gap: 8px; margin: 0; color: #1e293b; }
.modal-close {
  background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; cursor: pointer; color: #64748b;
}
.modal-close:hover { background: #e2e8f0; }
.modal-body { padding: 1.25rem; overflow-y: auto; flex: 1; }
.modal-footer {
  padding: .75rem 1.25rem; border-top: 1px solid #f1f1f1;
  display: flex; justify-content: flex-end; gap: .5rem;
}

.modal-card--success .modal-header { border-bottom-color: #c8e6c9; }
.modal-card--success .modal-header h2 { color: #2e7d32; }
.modal-card--danger .modal-header { border-bottom-color: #ffcdd2; }
.modal-card--danger .modal-header h2 { color: #c62828; }

/* Detail grid */
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }
.detail-item label { font-size: .72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; display: block; margin-bottom: .15rem; }
.detail-item p { font-size: .9rem; color: #1e293b; margin: 0; word-break: break-word; }
.detail-actions { display: flex; gap: .5rem; justify-content: center; margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid #f1f1f1; }

/* Buttons */
.btn {
  display: inline-flex; align-items: center; gap: 6px; padding: .55rem 1.1rem;
  border: none; border-radius: 10px; font-size: .88rem; font-weight: 600;
  cursor: pointer; transition: all .18s;
}
.btn--success { background: #2e7d32; color: #fff; }
.btn--success:hover { background: #1b5e20; }
.btn--danger { background: #c62828; color: #fff; }
.btn--danger:hover { background: #b71c1c; }
.btn--ghost { background: #f1f5f9; color: #475569; }
.btn--ghost:hover { background: #e2e8f0; }
.btn:disabled { opacity: .6; cursor: default; }

/* Toast */
.toast {
  position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%);
  padding: .75rem 1.5rem; border-radius: 12px; font-size: .88rem; font-weight: 600;
  box-shadow: 0 8px 24px rgba(0,0,0,.15); z-index: 999;
}
.toast--success { background: #1b5e20; color: #fff; }
.toast--error { background: #b71c1c; color: #fff; }

/* Transitions */
.modal-enter-active, .modal-leave-active { transition: all .25s cubic-bezier(.4,0,.2,1); }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-card, .modal-leave-to .modal-card { transform: translateY(20px) scale(.97); }
.toast-enter-active, .toast-leave-active { transition: all .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(16px); }
.fade-enter-active, .fade-leave-active { transition: opacity .2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.list-enter-active, .list-leave-active { transition: all .3s; }
.list-enter-from { opacity: 0; transform: translateY(-8px); }
.list-leave-to { opacity: 0; }

/* Responsive */
@media (max-width: 900px) {
  .sidebar { width: 68px; }
  .sidebar-brand, .sidebar-nav-label, .nav-item span, .user-details { display: none; }
  .sidebar-header { justify-content: center; padding: 1.25rem .5rem .75rem; }
  .nav-item { justify-content: center; padding: .65rem; }
  .sidebar-footer { justify-content: center; padding: .75rem .5rem; }
  .user-info { justify-content: center; }
  .btn-logout { display: none; }
  .main-content { margin-left: 68px; }
}
@media (max-width: 768px) {
  .hide-md { display: none; }
  .detail-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .hide-sm { display: none; }
  .show-sm { display: block !important; }
  .main-content { padding: 0.75rem 1rem 1.5rem; }
}
</style>
