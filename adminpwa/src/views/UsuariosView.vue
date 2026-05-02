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
          <div class="user-avatar">
            {{ userInitials }}
          </div>
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
          <h1 class="top-bar__title"><Shield :size="22" /> Gestión de Administradores</h1>
          <p class="top-bar__desc">Administra los usuarios del panel administrativo</p>
        </div>
      </div>

      <!-- Stats + Search — unified card -->
      <div class="toolbar-card">
        <div class="toolbar-row toolbar-row--stats">
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--total"><Users :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ usuarios.length }}</span>
              <span class="stat-pill__label">Total</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--active"><UserCheck :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ activeCount }}</span>
              <span class="stat-pill__label">Activos</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--inactive"><UserX :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ inactiveCount }}</span>
              <span class="stat-pill__label">Inactivos</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--admin"><ShieldCheck :size="16" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ adminCount }}</span>
              <span class="stat-pill__label">Admins</span>
            </div>
          </div>
        </div>
        <div class="toolbar-row toolbar-row--filters">
          <div class="search-box">
            <Search :size="18" class="search-box__icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar nombre, correo, CURP, teléfono…"
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
              <select v-model="filterRol">
                <option value="">Todos los roles</option>
                <option value="administrador">Administrador</option>
                <option value="usuario">Usuario</option>
              </select>
            </div>
            <div class="filter-chip">
              <CircleDot :size="14" />
              <select v-model="filterEstatus">
                <option value="">Todos los estatus</option>
                <option value="activo">Activo</option>
                <option value="inactivo">Inactivo</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="state-empty">
        <div class="spinner"></div>
        <p>Cargando administradores…</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredUsers.length === 0" class="state-empty">
        <Users :size="48" class="state-empty__icon" />
        <h3>No se encontraron administradores</h3>
        <p v-if="searchQuery || filterRol || filterEstatus">Intenta con otros filtros de búsqueda</p>
        <p v-else>Aún no hay usuarios registrados</p>
      </div>

      <!-- Users Table -->
      <div v-else class="table-card">
        <div class="table-scroll">
          <table class="tbl">
            <thead>
              <tr>
                <th @click="sortBy('nombre')" class="th-sort">
                  Nombre completo
                  <ChevronDown v-if="sortField === 'nombre'" :size="13" :class="{ 'sort-flip': sortDir === 'asc' }" />
                </th>
                <th class="hide-md">Correo</th>
                <th class="hide-sm">CURP</th>
                <th class="hide-sm">Teléfono</th>
                <th>Rol</th>
                <th>Estatus</th>
                <th class="hide-sm th-sort" @click="sortBy('created_at')">
                  Registro
                  <ChevronDown v-if="sortField === 'created_at'" :size="13" :class="{ 'sort-flip': sortDir === 'asc' }" />
                </th>
                <th class="th-actions">Acciones</th>
              </tr>
            </thead>
            <TransitionGroup name="list" tag="tbody">
              <tr v-for="u in paginatedUsers" :key="u.id">
                <td>
                  <div class="cell-user">
                    <div class="cell-user__avatar" :style="{ background: avatarColor(u.nombre) }">
                      {{ getInitials(u) }}
                    </div>
                    <div class="cell-user__text">
                      <span class="cell-user__name">{{ u.nombre }} {{ u.apellido_paterno }}</span>
                      <span class="cell-user__sub">{{ u.apellido_materno }}</span>
                      <span class="cell-user__sub show-sm">{{ u.correo }}</span>
                    </div>
                  </div>
                </td>
                <td class="hide-md td-ellipsis">{{ u.correo }}</td>
                <td class="hide-sm mono">{{ u.curp }}</td>
                <td class="hide-sm">{{ u.telefono }}</td>
                <td>
                  <span class="chip" :class="u.rol === 'administrador' ? 'chip--indigo' : 'chip--slate'">
                    {{ u.rol === 'administrador' ? 'Admin' : 'Usuario' }}
                  </span>
                </td>
                <td>
                  <button
                    class="chip chip--btn"
                    :class="u.estatus === 'activo' ? 'chip--emerald' : 'chip--red'"
                    :disabled="u.id === auth.user?.id"
                    @click="toggleEstatus(u)"
                  >
                    {{ u.estatus }}
                    <RefreshCw v-if="u.id !== auth.user?.id" :size="11" />
                  </button>
                </td>
                <td class="hide-sm">{{ formatDate(u.created_at) }}</td>
                <td class="td-actions">
                  <template v-if="u.id !== auth.user?.id">
                    <button class="act-btn act-btn--view" title="Ver detalle" @click="openDetail(u)">
                      <Eye :size="15" />
                    </button>
                    <button class="act-btn act-btn--edit" title="Editar" @click="openEdit(u)">
                      <Pencil :size="15" />
                    </button>
                    <button class="act-btn act-btn--del" title="Eliminar" @click="openDelete(u)">
                      <Trash2 :size="15" />
                    </button>
                  </template>
                  <span v-else class="self-tag">Tú</span>
                </td>
              </tr>
            </TransitionGroup>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pager">
          <button class="pager__btn" :disabled="currentPage === 1" @click="currentPage--">
            <ChevronLeft :size="16" />
          </button>
          <template v-for="p in visiblePages" :key="p">
            <button
              v-if="p !== '...'"
              class="pager__btn" :class="{ 'pager__btn--active': currentPage === p }"
              @click="currentPage = p as number"
            >{{ p }}</button>
            <span v-else class="pager__dots">…</span>
          </template>
          <button class="pager__btn" :disabled="currentPage === totalPages" @click="currentPage++">
            <ChevronRight :size="16" />
          </button>
          <span class="pager__info">{{ currentPage }} / {{ totalPages }}</span>
        </div>
      </div>

      <!-- ═══════ Detail Modal ═══════ -->
      <Transition name="modal">
        <div v-if="selectedUser" class="overlay" @click="selectedUser = null">
          <div class="sheet sheet--md" @click.stop>
            <div class="sheet__head">
              <div class="sheet__user">
                <div class="sheet__avatar" :style="{ background: avatarColor(selectedUser.nombre) }">
                  {{ getInitials(selectedUser) }}
                </div>
                <div>
                  <h3>{{ selectedUser.nombre }} {{ selectedUser.apellido_paterno }} {{ selectedUser.apellido_materno }}</h3>
                  <p class="sheet__sub">{{ selectedUser.rol === 'administrador' ? 'Administrador' : 'Usuario' }} · {{ selectedUser.estatus }}</p>
                </div>
              </div>
              <button class="sheet__close" @click="selectedUser = null"><X :size="20" /></button>
            </div>
            <div class="sheet__body">
              <div class="info-grid">
                <div class="info-cell"><label>Nombre</label><span>{{ selectedUser.nombre }}</span></div>
                <div class="info-cell"><label>Apellido paterno</label><span>{{ selectedUser.apellido_paterno }}</span></div>
                <div class="info-cell"><label>Apellido materno</label><span>{{ selectedUser.apellido_materno }}</span></div>
                <div class="info-cell"><label>CURP</label><span class="mono">{{ selectedUser.curp }}</span></div>
                <div class="info-cell"><label>Correo electrónico</label><span>{{ selectedUser.correo }}</span></div>
                <div class="info-cell"><label>Teléfono</label><span>{{ selectedUser.telefono }}</span></div>
                <div class="info-cell"><label>Rol</label><span>{{ selectedUser.rol === 'administrador' ? 'Administrador' : 'Usuario' }}</span></div>
                <div class="info-cell"><label>Estatus</label><span>{{ selectedUser.estatus }}</span></div>
                <div class="info-cell"><label>Fecha de registro</label><span>{{ formatDateFull(selectedUser.created_at) }}</span></div>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- ═══════ Edit Modal ═══════ -->
      <Transition name="modal">
        <div v-if="editUser" class="overlay" @click="editUser = null">
          <div class="sheet sheet--md" @click.stop>
            <div class="sheet__head">
              <div class="sheet__user">
                <div class="sheet__avatar sheet__avatar--edit">
                  <Pencil :size="20" />
                </div>
                <div>
                  <h3>Editar administrador</h3>
                  <p class="sheet__sub">{{ editForm.nombre }} {{ editForm.apellido_paterno }}</p>
                </div>
              </div>
              <button class="sheet__close" @click="editUser = null"><X :size="20" /></button>
            </div>
            <form class="sheet__body" @submit.prevent="submitEdit">
              <div class="edit-grid">
                <div class="fg"><label>Nombre</label><input v-model="editForm.nombre" class="fi" /></div>
                <div class="fg"><label>Apellido paterno</label><input v-model="editForm.apellido_paterno" class="fi" /></div>
                <div class="fg"><label>Apellido materno</label><input v-model="editForm.apellido_materno" class="fi" /></div>
                <div class="fg"><label>CURP</label><input v-model="editForm.curp" class="fi" maxlength="18" /></div>
                <div class="fg"><label>Correo</label><input v-model="editForm.correo" type="email" class="fi" /></div>
                <div class="fg"><label>Teléfono</label><input v-model="editForm.telefono" class="fi" maxlength="10" /></div>
                <div class="fg">
                  <label>Rol</label>
                  <select v-model="editForm.rol" class="fi">
                    <option value="administrador">Administrador</option>
                    <option value="usuario">Usuario</option>
                  </select>
                </div>
              </div>
              <div class="sheet__actions">
                <button type="button" class="btn-cancel" @click="editUser = null">Cancelar</button>
                <button type="submit" class="btn-save" :disabled="saving">
                  <Loader2 v-if="saving" :size="16" class="spin" />
                  <Save v-else :size="16" />
                  {{ saving ? 'Guardando…' : 'Guardar cambios' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>

      <!-- ═══════ Delete Modal ═══════ -->
      <Transition name="modal">
        <div v-if="deleteTarget" class="overlay" @click="deleteTarget = null">
          <div class="sheet sheet--sm" @click.stop>
            <div class="sheet__head sheet__head--danger">
              <div class="sheet__user">
                <div class="sheet__avatar sheet__avatar--danger">
                  <AlertTriangle :size="22" />
                </div>
                <div>
                  <h3>Eliminar administrador</h3>
                  <p class="sheet__sub">Esta acción no se puede deshacer</p>
                </div>
              </div>
              <button class="sheet__close" @click="deleteTarget = null"><X :size="20" /></button>
            </div>
            <div class="sheet__body sheet__body--center">
              <p class="del-msg">
                ¿Estás seguro de eliminar a <strong>{{ deleteTarget.nombre }} {{ deleteTarget.apellido_paterno }}</strong>?<br />
                Se eliminará toda su información permanentemente.
              </p>
            </div>
            <div class="sheet__actions sheet__actions--danger">
              <button class="btn-cancel" @click="deleteTarget = null">Cancelar</button>
              <button class="btn-del" :disabled="deleting" @click="submitDelete">
                <Loader2 v-if="deleting" :size="16" class="spin" />
                <Trash2 v-else :size="16" />
                {{ deleting ? 'Eliminando…' : 'Eliminar usuario' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Toast -->
      <Transition name="toast">
        <div v-if="toast.show" class="toast" :class="`toast--${toast.type}`">
          <CheckCircle v-if="toast.type === 'success'" :size="18" />
          <AlertTriangle v-else :size="18" />
          {{ toast.message }}
        </div>
      </Transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth.service'
import type { AdminUser } from '@/types'
import {
  Shield, LayoutDashboard, Users, LogOut, Trash2, RefreshCw, AlertTriangle,
  Layers, Search, X, ChevronDown, ChevronLeft, ChevronRight,
  ListFilter, CircleDot, UserCheck, UserX, ShieldCheck,
  Eye, Pencil, Save, Loader2, CheckCircle, Map, Store, ClipboardList
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const usuarios = ref<AdminUser[]>([])
const loading = ref(true)
const searchQuery = ref('')
const filterRol = ref('')
const filterEstatus = ref('')
const sortField = ref<'nombre' | 'created_at'>('created_at')
const sortDir = ref<'asc' | 'desc'>('desc')
const currentPage = ref(1)
const perPage = 15

// modals
const selectedUser = ref<AdminUser | null>(null)
const editUser = ref<AdminUser | null>(null)
const deleteTarget = ref<AdminUser | null>(null)
const saving = ref(false)
const deleting = ref(false)

const editForm = reactive({
  nombre: '',
  apellido_paterno: '',
  apellido_materno: '',
  curp: '',
  correo: '',
  telefono: '',
  rol: '',
})

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

const activeCount = computed(() => usuarios.value.filter(u => u.estatus === 'activo').length)
const inactiveCount = computed(() => usuarios.value.filter(u => u.estatus === 'inactivo').length)
const adminCount = computed(() => usuarios.value.filter(u => u.rol === 'administrador').length)

const filteredUsers = computed(() => {
  let result = [...usuarios.value]
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(u =>
      u.nombre?.toLowerCase().includes(q) ||
      u.apellido_paterno?.toLowerCase().includes(q) ||
      u.apellido_materno?.toLowerCase().includes(q) ||
      u.correo?.toLowerCase().includes(q) ||
      u.curp?.toLowerCase().includes(q) ||
      u.telefono?.includes(q)
    )
  }
  if (filterRol.value) result = result.filter(u => u.rol === filterRol.value)
  if (filterEstatus.value) result = result.filter(u => u.estatus === filterEstatus.value)
  result.sort((a, b) => {
    const aVal = a[sortField.value] || ''
    const bVal = b[sortField.value] || ''
    const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
    return sortDir.value === 'asc' ? cmp : -cmp
  })
  return result
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / perPage))

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredUsers.value.slice(start, start + perPage)
})

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const t = totalPages.value
  const c = currentPage.value
  if (t <= 7) { for (let i = 1; i <= t; i++) pages.push(i) }
  else {
    pages.push(1)
    if (c > 3) pages.push('...')
    for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) pages.push(i)
    if (c < t - 2) pages.push('...')
    pages.push(t)
  }
  return pages
})

watch([searchQuery, filterRol, filterEstatus], () => { currentPage.value = 1 })

function sortBy(field: 'nombre' | 'created_at') {
  if (sortField.value === field) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortField.value = field; sortDir.value = 'asc' }
}

function getInitials(u: AdminUser): string {
  const n = u.nombre?.charAt(0) || ''
  const ap = u.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
}

function avatarColor(name: string) {
  const colors = [
    'linear-gradient(135deg,#4f46e5,#6366f1)',
    'linear-gradient(135deg,#0891b2,#06b6d4)',
    'linear-gradient(135deg,#7c3aed,#8b5cf6)',
    'linear-gradient(135deg,#db2777,#ec4899)',
    'linear-gradient(135deg,#059669,#10b981)',
    'linear-gradient(135deg,#d97706,#f59e0b)',
    'linear-gradient(135deg,#dc2626,#ef4444)',
    'linear-gradient(135deg,#2563eb,#3b82f6)',
  ]
  let h = 0
  for (let i = 0; i < (name || '').length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return colors[Math.abs(h) % colors.length]
}

function formatDate(iso: string) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateFull(iso: string) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function openDetail(u: AdminUser) { selectedUser.value = u }

function openEdit(u: AdminUser) {
  editUser.value = u
  editForm.nombre = u.nombre || ''
  editForm.apellido_paterno = u.apellido_paterno || ''
  editForm.apellido_materno = u.apellido_materno || ''
  editForm.curp = u.curp || ''
  editForm.correo = u.correo || ''
  editForm.telefono = u.telefono || ''
  editForm.rol = u.rol || ''
}

function openDelete(u: AdminUser) { deleteTarget.value = u }

async function toggleEstatus(user: AdminUser) {
  const newEstatus = user.estatus === 'activo' ? 'inactivo' : 'activo'
  try {
    const updated = await authService.updateEstatus(user.id, newEstatus, auth.token!)
    const idx = usuarios.value.findIndex(u => u.id === user.id)
    if (idx !== -1) usuarios.value[idx] = updated
    showToast(`Usuario ${newEstatus === 'activo' ? 'activado' : 'desactivado'}`)
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al actualizar estatus', 'error')
  }
}

async function submitEdit() {
  if (!editUser.value) return
  saving.value = true
  try {
    const updated = await authService.updateUsuario(editUser.value.id, {
      nombre: editForm.nombre || undefined,
      apellido_paterno: editForm.apellido_paterno || undefined,
      apellido_materno: editForm.apellido_materno || undefined,
      curp: editForm.curp || undefined,
      correo: editForm.correo || undefined,
      telefono: editForm.telefono || undefined,
      rol: editForm.rol as 'usuario' | 'administrador' || undefined,
    } as Partial<AdminUser>, auth.token!)
    const idx = usuarios.value.findIndex(x => x.id === editUser.value!.id)
    if (idx !== -1) usuarios.value[idx] = updated
    editUser.value = null
    showToast('Administrador actualizado correctamente')
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al actualizar', 'error')
  } finally {
    saving.value = false
  }
}

async function submitDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await authService.deleteUsuario(deleteTarget.value.id, auth.token!)
    usuarios.value = usuarios.value.filter(x => x.id !== deleteTarget.value!.id)
    deleteTarget.value = null
    showToast('Administrador eliminado correctamente')
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al eliminar', 'error')
  } finally {
    deleting.value = false
  }
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3500)
}

async function loadUsuarios() {
  loading.value = true
  try {
    usuarios.value = await authService.getUsuarios(auth.token!)
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al cargar administradores', 'error')
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => { loadUsuarios() })
</script>

<style scoped>
/* ═══════════════════════════════════════════
   Layout
   ═══════════════════════════════════════════ */
.dashboard-layout { display: flex; min-height: 100vh; }

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.35);
}

.sidebar-header { display: flex; align-items: center; gap: 0.75rem; padding: 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #fff; }
.sidebar-logo { width: 44px; height: 44px; background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sidebar-brand { display: flex; flex-direction: column; line-height: 1.15; }
.sidebar-brand__title { font-weight: 800; font-size: 1.15rem; letter-spacing: 0.04em; }
.sidebar-brand__sub { font-size: 0.68rem; font-weight: 500; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.02em; }

.sidebar-nav { flex: 1; padding: 0.75rem 0.65rem; }
.sidebar-nav-label { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.05em; padding: 0.5rem 0.85rem 0.35rem; }

.nav-item { display: flex; align-items: center; gap: 0.65rem; padding: 0.55rem 0.85rem; border-radius: 8px; color: rgba(255,255,255,0.75); text-decoration: none; font-weight: 500; font-size: 0.88rem; transition: all 0.2s cubic-bezier(.4,0,.2,1); margin-bottom: 2px; }
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.active { background: rgba(99,102,241,0.25); color: #fff; font-weight: 600; }

.sidebar-footer { padding: 0.85rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; }
.user-info { display: flex; align-items: center; gap: 0.65rem; }
.user-avatar { width: 34px; height: 34px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 600; font-size: 0.78rem; }
.user-details { display: flex; flex-direction: column; }
.user-name { font-weight: 600; font-size: 0.82rem; color: #fff; }
.user-role { font-size: 0.7rem; color: rgba(255,255,255,0.5); text-transform: capitalize; }
.btn-logout { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; border-radius: 8px; background: transparent; color: rgba(255,255,255,0.5); cursor: pointer; transition: all 0.15s; }
.btn-logout:hover { background: rgba(255,255,255,0.1); color: #fff; }

/* ── Main Content ── */
.main-content { flex: 1; margin-left: 260px; padding: 0.75rem 2rem 2rem; background: #f8fafc; min-height: 100vh; }

/* ── Top Bar ── */
.top-bar { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 14px; padding: 1.15rem 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 4px 20px rgba(79,70,229,0.18); }
.top-bar__title { font-size: 1.35rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__desc { font-size: 0.85rem; color: rgba(255,255,255,0.75); margin: 0.15rem 0 0; }

/* ═══════════════════════════════════════════
   Toolbar Card
   ═══════════════════════════════════════════ */
.toolbar-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  margin-bottom: 1.25rem;
  overflow: hidden;
}

.toolbar-row { padding: 1rem 1.25rem; }

.toolbar-row--stats {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  border-bottom: 1px solid #f1f5f9;
  background: #fafbfd;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.5rem 0.85rem;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #e2e8f0;
  transition: all 0.25s cubic-bezier(.4,0,.2,1);
  flex: 1;
  min-width: 110px;
}

.stat-pill:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  border-color: #cbd5e1;
}

.stat-pill__icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-pill__icon--total { background: #ede9fe; color: #7c3aed; }
.stat-pill__icon--active { background: #d1fae5; color: #059669; }
.stat-pill__icon--inactive { background: #fef2f2; color: #dc2626; }
.stat-pill__icon--admin { background: #eef2ff; color: #4f46e5; }

.stat-pill__data { display: flex; flex-direction: column; line-height: 1.2; }
.stat-pill__value { font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.stat-pill__label { font-size: 0.7rem; color: #94a3b8; font-weight: 500; }

.toolbar-row--filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box { flex: 1; min-width: 240px; position: relative; }
.search-box__icon { position: absolute; left: 0.85rem; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; }
.search-box__input {
  width: 100%; padding: 0.65rem 2.2rem 0.65rem 2.7rem; border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.88rem; background: #f8fafc; transition: all 0.25s cubic-bezier(.4,0,.2,1); box-sizing: border-box;
}
.search-box__input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); background: #fff; }
.search-box__input::placeholder { color: #94a3b8; }
.search-box__clear { position: absolute; right: 0.6rem; top: 50%; transform: translateY(-50%); background: #e2e8f0; border: none; color: #64748b; cursor: pointer; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.search-box__clear:hover { background: #cbd5e1; color: #334155; }

.filter-chips { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.filter-chip {
  display: flex; align-items: center; gap: 0.35rem; padding: 0 0.1rem 0 0.7rem;
  border: 1.5px solid #e2e8f0; border-radius: 10px; background: #f8fafc; color: #64748b;
  transition: all 0.25s cubic-bezier(.4,0,.2,1);
}
.filter-chip:hover { border-color: #6366f1; }
.filter-chip select {
  border: none; background: transparent; font-size: 0.84rem; color: #334155; cursor: pointer;
  padding: 0.6rem 0.5rem; outline: none; -webkit-appearance: none; appearance: none;
  min-width: 130px;
}

/* ═══════════════════════════════════════════
   States
   ═══════════════════════════════════════════ */
.state-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; color: #94a3b8; text-align: center; }
.state-empty__icon { color: #cbd5e1; }
.state-empty h3 { margin: 1rem 0 0.25rem; color: #475569; font-size: 1.15rem; }
.state-empty p { margin: 0; font-size: 0.88rem; }
.spinner { width: 36px; height: 36px; border: 3px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin 0.7s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ═══════════════════════════════════════════
   Table
   ═══════════════════════════════════════════ */
.table-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  overflow: hidden;
}
.table-scroll { overflow-x: auto; }

.tbl { width: 100%; border-collapse: collapse; }
.tbl thead { background: #f8fafc; border-bottom: 1.5px solid #e2e8f0; }
.tbl th { padding: 0.75rem 1rem; text-align: left; font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; white-space: nowrap; user-select: none; }
.th-sort { cursor: pointer; transition: color 0.15s; }
.th-sort:hover { color: #4f46e5; }
.th-actions { text-align: center; width: 130px; }
.sort-flip { display: inline-block; transform: rotate(180deg); transition: transform 0.2s; }

.tbl td { padding: 0.65rem 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.86rem; color: #334155; vertical-align: middle; }
.tbl tbody tr { transition: background 0.2s cubic-bezier(.4,0,.2,1); }
.tbl tbody tr:hover { background: #f8fafc; }

.cell-user { display: flex; align-items: center; gap: 0.7rem; }
.cell-user__avatar { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 0.75rem; flex-shrink: 0; }
.cell-user__text { display: flex; flex-direction: column; }
.cell-user__name { font-weight: 600; color: #1e293b; font-size: 0.86rem; }
.cell-user__sub { font-size: 0.75rem; color: #94a3b8; }
.show-sm { display: none; }

.td-ellipsis { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mono { font-family: 'SF Mono','Fira Code','Consolas',monospace; font-size: 0.8rem; letter-spacing: 0.02em; }

/* Chips / badges */
.chip { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.7rem; font-weight: 600; white-space: nowrap; border: none; }
.chip--indigo { background: #eef2ff; color: #3730a3; }
.chip--slate { background: #f1f5f9; color: #475569; }
.chip--emerald { background: #d1fae5; color: #065f46; }
.chip--red { background: #fef2f2; color: #991b1b; }
.chip--btn { cursor: pointer; transition: all 0.2s cubic-bezier(.4,0,.2,1); text-transform: capitalize; }
.chip--btn:not(:disabled):hover { transform: scale(1.05); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.chip--btn:disabled { opacity: 0.6; cursor: default; }

.self-tag { font-size: 0.75rem; color: #94a3b8; font-style: italic; }

/* Action buttons */
.td-actions { text-align: center; white-space: nowrap; }
.act-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; border: none; border-radius: 8px; cursor: pointer;
  transition: all 0.2s cubic-bezier(.4,0,.2,1); margin: 0 2px;
}
.act-btn--view { background: #f1f5f9; color: #475569; }
.act-btn--view:hover { background: #e2e8f0; color: #1e293b; }
.act-btn--edit { background: #eef2ff; color: #4f46e5; }
.act-btn--edit:hover { background: #c7d2fe; color: #3730a3; transform: scale(1.08); }
.act-btn--del { background: #fef2f2; color: #dc2626; }
.act-btn--del:hover { background: #fecaca; color: #991b1b; transform: scale(1.08); }

/* ═══════════════════════════════════════════
   Pagination
   ═══════════════════════════════════════════ */
.pager { display: flex; align-items: center; justify-content: center; gap: 0.25rem; padding: 0.85rem 1rem; border-top: 1px solid #f1f5f9; }
.pager__btn { display: flex; align-items: center; justify-content: center; min-width: 34px; height: 34px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; color: #475569; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.pager__btn:hover:not(:disabled) { border-color: #6366f1; color: #4f46e5; background: #eef2ff; }
.pager__btn--active { background: #4f46e5 !important; border-color: #4f46e5 !important; color: #fff !important; }
.pager__btn:disabled { opacity: 0.35; cursor: not-allowed; }
.pager__dots { padding: 0 0.2rem; color: #94a3b8; }
.pager__info { margin-left: 0.6rem; font-size: 0.78rem; color: #94a3b8; }

/* ═══════════════════════════════════════════
   Modals (Apple sheet style)
   ═══════════════════════════════════════════ */
.overlay {
  position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem;
}

.sheet {
  background: #fff; border-radius: 20px; width: 100%; box-shadow: 0 25px 60px rgba(0,0,0,0.18), 0 0 0 1px rgba(0,0,0,0.04);
  max-height: 90vh; overflow-y: auto;
  animation: sheetIn 0.35s cubic-bezier(.32,.72,0,1);
}

.sheet--md { max-width: 560px; }
.sheet--sm { max-width: 440px; }

@keyframes sheetIn {
  from { opacity: 0; transform: scale(0.96) translateY(12px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.sheet__head {
  display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9;
}
.sheet__head--danger { border-bottom-color: #fecaca; }

.sheet__user { display: flex; align-items: center; gap: 0.85rem; }
.sheet__avatar { width: 46px; height: 46px; border-radius: 14px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 0.95rem; }
.sheet__avatar--edit { background: linear-gradient(135deg,#4f46e5,#6366f1); }
.sheet__avatar--danger { background: linear-gradient(135deg,#dc2626,#ef4444); }

.sheet__head h3 { margin: 0; font-size: 1.05rem; font-weight: 700; color: #1e293b; }
.sheet__sub { margin: 0.1rem 0 0; font-size: 0.8rem; color: #94a3b8; }

.sheet__close { background: #f1f5f9; border: none; color: #64748b; cursor: pointer; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.sheet__close:hover { background: #e2e8f0; color: #1e293b; }

.sheet__body { padding: 1.25rem 1.5rem; }
.sheet__body--center { text-align: center; }

/* Detail grid */
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.9rem; }
.info-cell { display: flex; flex-direction: column; gap: 0.15rem; }
.info-cell label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }
.info-cell span { font-size: 0.88rem; color: #1e293b; word-break: break-word; }

/* Edit form */
.edit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }
.fg { display: flex; flex-direction: column; gap: 0.25rem; }
.fg label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b; }
.fi {
  padding: 0.6rem 0.75rem; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.88rem;
  background: #f8fafc; transition: all 0.25s cubic-bezier(.4,0,.2,1); width: 100%; box-sizing: border-box;
}
.fi:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); background: #fff; }

.sheet__actions {
  display: flex; justify-content: flex-end; gap: 0.65rem; padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9;
}
.sheet__actions--danger { border-top-color: #fecaca; background: #fefefe; border-radius: 0 0 20px 20px; }

.btn-cancel {
  padding: 0.6rem 1.25rem; border: 1.5px solid #e2e8f0; border-radius: 10px; background: #fff; color: #475569;
  font-weight: 600; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;
}
.btn-cancel:hover { background: #f1f5f9; border-color: #cbd5e1; }

.btn-save {
  display: flex; align-items: center; gap: 0.4rem; padding: 0.6rem 1.25rem; border: none; border-radius: 10px;
  background: linear-gradient(135deg,#4f46e5,#6366f1); color: #fff; font-weight: 600; font-size: 0.88rem; cursor: pointer;
  transition: all 0.25s cubic-bezier(.4,0,.2,1); box-shadow: 0 2px 8px rgba(79,70,229,0.25);
}
.btn-save:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(79,70,229,0.35); }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-del {
  display: flex; align-items: center; gap: 0.4rem; padding: 0.6rem 1.25rem; border: none; border-radius: 10px;
  background: linear-gradient(135deg,#dc2626,#ef4444); color: #fff; font-weight: 600; font-size: 0.88rem; cursor: pointer;
  transition: all 0.25s cubic-bezier(.4,0,.2,1); box-shadow: 0 2px 8px rgba(220,38,38,0.25);
}
.btn-del:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(220,38,38,0.35); }
.btn-del:disabled { opacity: 0.6; cursor: not-allowed; }

.del-msg { font-size: 0.92rem; color: #475569; line-height: 1.6; margin: 0; }
.del-msg strong { color: #1e293b; }

.spin { animation: spin 0.7s linear infinite; }

/* ═══════════════════════════════════════════
   Toast
   ═══════════════════════════════════════════ */
.toast {
  position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1.3rem; border-radius: 12px; font-size: 0.88rem; font-weight: 500; z-index: 1100;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.toast--success { background: #065f46; color: #fff; }
.toast--error { background: #991b1b; color: #fff; }

/* ═══════════════════════════════════════════
   Transitions
   ═══════════════════════════════════════════ */
.modal-enter-active { transition: opacity 0.25s cubic-bezier(.4,0,.2,1); }
.modal-leave-active { transition: opacity 0.2s cubic-bezier(.4,0,.2,1); }
.modal-enter-from, .modal-leave-to { opacity: 0; }

.toast-enter-active { animation: toastIn 0.35s cubic-bezier(.32,.72,0,1); }
.toast-leave-active { animation: toastOut 0.25s cubic-bezier(.4,0,.2,1) forwards; }
@keyframes toastIn {
  from { opacity: 0; transform: translateX(-50%) translateY(16px) scale(0.95); }
  to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}
@keyframes toastOut {
  to { opacity: 0; transform: translateX(-50%) translateY(10px) scale(0.96); }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* List transition for table rows */
.list-enter-active { transition: all 0.3s cubic-bezier(.4,0,.2,1); }
.list-leave-active { transition: all 0.2s cubic-bezier(.4,0,.2,1); }
.list-enter-from { opacity: 0; transform: translateY(-8px); }
.list-leave-to { opacity: 0; transform: translateX(20px); }

/* ═══════════════════════════════════════════
   Responsive
   ═══════════════════════════════════════════ */
@media (max-width: 1024px) {
  .hide-md { display: none !important; }
  .show-sm { display: block; }
}

@media (max-width: 900px) {
  .sidebar { width: 68px; }
  .sidebar-brand, .nav-item span, .user-details, .sidebar-nav-label { display: none; }
  .sidebar-header { justify-content: center; padding: 1rem 0.5rem; }
  .sidebar-logo { width: 36px; height: 36px; }
  .nav-item { justify-content: center; padding: 0.6rem 0.5rem; }
  .sidebar-footer { flex-direction: column; gap: 0.5rem; }
  .user-info { display: none; }
  .main-content { margin-left: 68px; }
  .hide-sm { display: none !important; }
  .show-sm { display: block; }
}

@media (max-width: 600px) {
  .main-content { padding: 0.75rem 1rem 1.5rem; }
  .toolbar-row--stats { gap: 0.4rem; }
  .stat-pill { min-width: 0; flex: 1 1 calc(50% - 0.4rem); padding: 0.4rem 0.6rem; }
  .stat-pill__value { font-size: 0.95rem; }
  .toolbar-row--filters { flex-direction: column; }
  .search-box { min-width: unset; }
  .filter-chips { width: 100%; }
  .filter-chip { flex: 1; }
  .filter-chip select { min-width: 0; }
  .info-grid, .edit-grid { grid-template-columns: 1fr; }
  .sheet { border-radius: 16px; }
  .sheet--md, .sheet--sm { max-width: 100%; }
}
</style>
