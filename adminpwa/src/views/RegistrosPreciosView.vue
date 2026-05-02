<template>
  <div class="dashboard-layout">
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
          <LayoutDashboard :size="18" /><span>Dashboard</span>
        </router-link>
        <router-link to="/usuarios" class="nav-item" :class="{ active: $route.path === '/usuarios' }">
          <Users :size="18" /><span>Administradores</span>
        </router-link>
        <router-link to="/usuarios-pwa" class="nav-item" :class="{ active: $route.path === '/usuarios-pwa' }">
          <Users :size="18" /><span>Usuarios</span>
        </router-link>
        <router-link to="/propuestas" class="nav-item" :class="{ active: $route.path === '/propuestas' }">
          <Store :size="18" /><span>Propuestas Mercados</span>
        </router-link>
        <router-link to="/visor" class="nav-item" :class="{ active: $route.path === '/visor' }">
          <Map :size="18" /><span>Visor de Mapa</span>
        </router-link>
        <router-link to="/registros-precios" class="nav-item" :class="{ active: $route.path === '/registros-precios' }">
          <ClipboardList :size="18" /><span>Registros Precios</span>
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

    <main class="main-content">
      <!-- Top bar -->
      <div class="top-bar">
        <div>
          <h1 class="top-bar__title"><ClipboardList :size="22" /> Registros de Precios</h1>
          <p class="top-bar__desc">Todos los precios registrados por los usuarios</p>
        </div>
      </div>

      <!-- Toolbar -->
      <div class="toolbar-card">
        <div class="toolbar-row toolbar-row--stats">
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--total"><ClipboardList :size="18" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ registros.length }}</span>
              <span class="stat-pill__label">Total registros</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--shown"><Eye :size="18" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ filteredRegistros.length }}</span>
              <span class="stat-pill__label">Mostrando</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--cac"><Users :size="18" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ uniqueUsers }}</span>
              <span class="stat-pill__label">Usuarios</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--com"><ShoppingCart :size="18" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ uniqueProducts }}</span>
              <span class="stat-pill__label">Productos</span>
            </div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill__icon stat-pill__icon--ofi"><MapPin :size="18" /></div>
            <div class="stat-pill__data">
              <span class="stat-pill__value">{{ uniqueMercados }}</span>
              <span class="stat-pill__label">Mercados</span>
            </div>
          </div>
        </div>

        <div class="toolbar-row toolbar-row--filters">
          <div class="search-box">
            <Search :size="16" class="search-box__icon" />
            <input
              v-model="searchQuery"
              class="search-box__input"
              placeholder="Buscar usuario, correo, producto, mercado…"
            />
            <button v-if="searchQuery" class="search-box__clear" @click="searchQuery = ''">
              <X :size="12" />
            </button>
          </div>

          <div class="filter-chips">
            <div class="filter-chip">
              <ListFilter :size="14" />
              <select v-model="filterTipoPrecio">
                <option value="">Tipo precio</option>
                <option value="CONSUMIDOR">Consumidor</option>
                <option value="PRODUCTOR">Productor</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Filtros de catálogos -->
        <div class="toolbar-row toolbar-row--filters">
          <div class="filter-chips">
            <div class="filter-chip">
              <MapPin :size="14" />
              <select v-model="filterEstado" @change="onEstadoChange">
                <option value="">Estado</option>
                <option v-for="e in catEstados" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
            <div class="filter-chip">
              <Building :size="14" />
              <select v-model="filterMunicipio" :disabled="!filterEstado">
                <option value="">Municipio</option>
                <option v-for="m in municipiosFiltrados" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="filter-chip">
              <MapPin :size="14" />
              <select v-model="filterMercado">
                <option value="">Mercado</option>
                <option v-for="m in mercadosFiltrados" :key="m.id" :value="m.id">{{ m.nombre }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="toolbar-row toolbar-row--filters">
          <div class="filter-chips">
            <div class="filter-chip">
              <FolderOpen :size="14" />
              <select v-model="filterCategoria" @change="onCategoriaChange">
                <option value="">Categoría</option>
                <option v-for="c in catCategorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
              </select>
            </div>
            <div class="filter-chip">
              <Layers :size="14" />
              <select v-model="filterSubcategoria" :disabled="!filterCategoria" @change="onSubcategoriaChange">
                <option value="">Subcategoría</option>
                <option v-for="s in subcategoriasFiltradas" :key="s.id" :value="s.id">{{ s.nombre }}</option>
              </select>
            </div>
            <div class="filter-chip">
              <ShoppingCart :size="14" />
              <select v-model="filterProducto" :disabled="!filterSubcategoria">
                <option value="">Producto</option>
                <option v-for="p in productosFiltrados" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
          </div>

          <button v-if="hasActiveFilters" class="btn-clear-filters" @click="clearAllFilters">
            <X :size="14" /> Limpiar filtros
          </button>
        </div>

        <div class="toolbar-row toolbar-row--dates">
          <label class="date-label">
            <span>Desde</span>
            <input type="date" v-model="fechaDesde" class="date-input" />
          </label>
          <label class="date-label">
            <span>Hasta</span>
            <input type="date" v-model="fechaHasta" class="date-input" />
          </label>
          <button v-if="fechaDesde || fechaHasta" class="btn-clear-dates" @click="fechaDesde = ''; fechaHasta = ''; fetchData()">
            <X :size="14" /> Limpiar fechas
          </button>
          <button class="btn-apply-dates" @click="fetchData">
            <Search :size="14" /> Aplicar
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="table-card">
        <div v-if="loading" class="state-empty">
          <div class="spinner"></div>
          <p>Cargando registros…</p>
        </div>

        <template v-else-if="filteredRegistros.length">
          <div class="table-scroll">
            <table class="tbl">
              <thead>
                <tr>
                  <th @click="sortBy('user_name')" class="sortable">
                    Usuario
                    <ChevronDown v-if="sortField === 'user_name'" :size="12" :class="{ flipped: sortDir === 'asc' }" />
                  </th>
                  <th>Correo</th>
                  <th @click="sortBy('producto_nombre')" class="sortable">
                    Producto
                    <ChevronDown v-if="sortField === 'producto_nombre'" :size="12" :class="{ flipped: sortDir === 'asc' }" />
                  </th>
                  <th>Subcategoría</th>
                  <th @click="sortBy('precio')" class="sortable">
                    Precio
                    <ChevronDown v-if="sortField === 'precio'" :size="12" :class="{ flipped: sortDir === 'asc' }" />
                  </th>
                  <th>Unidad</th>
                  <th>Tipo</th>
                  <th @click="sortBy('mercado_nombre')" class="sortable">
                    Mercado
                    <ChevronDown v-if="sortField === 'mercado_nombre'" :size="12" :class="{ flipped: sortDir === 'asc' }" />
                  </th>
                  <th>Entidad</th>
                  <th @click="sortBy('fecha')" class="sortable">
                    Fecha
                    <ChevronDown v-if="sortField === 'fecha'" :size="12" :class="{ flipped: sortDir === 'asc' }" />
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in paginatedRegistros" :key="r.id">
                  <td>
                    <div class="cell-user">
                      <div class="cell-user__avatar" :style="{ background: avatarColor(r.user_name) }">
                        {{ getInitials(r.user_name) }}
                      </div>
                      <span>{{ r.user_name }}</span>
                    </div>
                  </td>
                  <td class="td-email">{{ r.user_email }}</td>
                  <td><strong>{{ r.producto_nombre }}</strong></td>
                  <td>{{ r.subcategoria_nombre }}</td>
                  <td class="td-precio">${{ r.precio.toFixed(2) }}</td>
                  <td>{{ r.unidad }}</td>
                  <td>
                    <span class="chip" :class="r.tipo_precio === 'CONSUMIDOR' ? 'chip--indigo' : 'chip--emerald'">
                      {{ r.tipo_precio }}
                    </span>
                  </td>
                  <td>{{ r.mercado_nombre }}</td>
                  <td>{{ r.mercado_entidad }}</td>
                  <td>{{ formatDate(r.fecha) }}</td>
                </tr>
              </tbody>
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
        </template>

        <div v-else class="state-empty">
          <ClipboardList :size="40" />
          <p>No se encontraron registros</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import {
  LayoutDashboard, Users, LogOut, Search, X,
  ChevronDown, ChevronLeft, ChevronRight, Layers,
  ListFilter, MapPin, ShoppingCart, Eye,
  ClipboardList, Map, Store, FolderOpen, Building
} from 'lucide-vue-next'

interface RegistroPrecio {
  id: number
  user_id: string
  user_name: string
  user_email: string
  mercado_id: number
  mercado_nombre: string
  mercado_entidad: string
  mercado_municipio: string
  producto_id: number
  producto_nombre: string
  subcategoria_nombre: string
  categoria_id: string
  precio: number
  unidad: string
  tipo_precio: string
  fecha: string
  created_at: string
}

const router = useRouter()
const auth = useAuthStore()

const registros = ref<RegistroPrecio[]>([])
const loading = ref(true)
const searchQuery = ref('')
const filterTipoPrecio = ref('')
const filterEstado = ref('')
const filterMunicipio = ref('')
const filterMercado = ref<number | string>('')
const filterCategoria = ref('')
const filterSubcategoria = ref('')
const filterProducto = ref<number | string>('')
const fechaDesde = ref('')
const fechaHasta = ref('')
const sortField = ref<string>('fecha')
const sortDir = ref<'asc' | 'desc'>('desc')
const currentPage = ref(1)
const perPage = 20

// Catálogos cargados desde la BD
const catEstados = ref<string[]>([])
const catMunicipiosMap = ref<Record<string, string[]>>({})
const catCategorias = ref<{id: string; nombre: string}[]>([])
const catSubcategorias = ref<{id: string; categoria_id: string; nombre: string}[]>([])
const catProductos = ref<{id: number; subcategoria_id: string; nombre: string}[]>([])
const catMercados = ref<{id: number; nombre: string; entidad: string; municipio: string}[]>([])

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

const uniqueUsers = computed(() => new Set(registros.value.map(r => r.user_id)).size)
const uniqueProducts = computed(() => new Set(registros.value.map(r => r.producto_nombre)).size)
const uniqueMercados = computed(() => new Set(registros.value.map(r => r.mercado_nombre)).size)

// Filtros dependientes
const municipiosFiltrados = computed(() =>
  filterEstado.value ? (catMunicipiosMap.value[filterEstado.value] || []) : []
)

const mercadosFiltrados = computed(() => {
  let list = catMercados.value
  if (filterEstado.value) list = list.filter(m => m.entidad === filterEstado.value)
  if (filterMunicipio.value) list = list.filter(m => m.municipio === filterMunicipio.value)
  return list
})

const subcategoriasFiltradas = computed(() =>
  filterCategoria.value
    ? catSubcategorias.value.filter(s => s.categoria_id === filterCategoria.value)
    : []
)

const productosFiltrados = computed(() =>
  filterSubcategoria.value
    ? catProductos.value.filter(p => p.subcategoria_id === filterSubcategoria.value)
    : []
)

const hasActiveFilters = computed(() =>
  !!(filterTipoPrecio.value || filterEstado.value || filterMunicipio.value ||
     filterMercado.value || filterCategoria.value || filterSubcategoria.value ||
     filterProducto.value || fechaDesde.value || fechaHasta.value)
)

const filteredRegistros = computed(() => {
  let result = [...registros.value]
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(r =>
      r.user_name?.toLowerCase().includes(q) ||
      r.user_email?.toLowerCase().includes(q) ||
      r.producto_nombre?.toLowerCase().includes(q) ||
      r.mercado_nombre?.toLowerCase().includes(q)
    )
  }
  if (filterTipoPrecio.value) result = result.filter(r => r.tipo_precio === filterTipoPrecio.value)
  if (filterEstado.value) result = result.filter(r => r.mercado_entidad === filterEstado.value)
  if (filterMunicipio.value) result = result.filter(r => r.mercado_municipio === filterMunicipio.value)
  if (filterMercado.value) result = result.filter(r => r.mercado_id === Number(filterMercado.value))
  if (filterCategoria.value) result = result.filter(r => r.categoria_id === filterCategoria.value)
  if (filterSubcategoria.value) {
    const prodIds = new Set(catProductos.value.filter(p => p.subcategoria_id === filterSubcategoria.value).map(p => p.id))
    result = result.filter(r => prodIds.has(r.producto_id))
  }
  if (filterProducto.value) result = result.filter(r => r.producto_id === Number(filterProducto.value))

  result.sort((a: any, b: any) => {
    const aVal = a[sortField.value] ?? ''
    const bVal = b[sortField.value] ?? ''
    const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
    return sortDir.value === 'asc' ? cmp : -cmp
  })
  return result
})

const totalPages = computed(() => Math.ceil(filteredRegistros.value.length / perPage))
const paginatedRegistros = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredRegistros.value.slice(start, start + perPage)
})

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const t = totalPages.value, c = currentPage.value
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

watch([searchQuery, filterTipoPrecio, filterEstado, filterMunicipio, filterMercado,
       filterCategoria, filterSubcategoria, filterProducto], () => { currentPage.value = 1 })

function onEstadoChange() {
  filterMunicipio.value = ''
  filterMercado.value = ''
}

function onCategoriaChange() {
  filterSubcategoria.value = ''
  filterProducto.value = ''
}

function onSubcategoriaChange() {
  filterProducto.value = ''
}

function clearAllFilters() {
  filterTipoPrecio.value = ''
  filterEstado.value = ''
  filterMunicipio.value = ''
  filterMercado.value = ''
  filterCategoria.value = ''
  filterSubcategoria.value = ''
  filterProducto.value = ''
  fechaDesde.value = ''
  fechaHasta.value = ''
  fetchData()
}

function sortByField(field: string) {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDir.value = 'desc'
  }
}
// alias used in template
const sortBy = sortByField

function getInitials(name: string) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function avatarColor(name: string) {
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  const h = Math.abs(hash) % 360
  return `linear-gradient(135deg, hsl(${h},65%,52%), hsl(${(h + 40) % 360},55%,42%))`
}

function formatDate(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (fechaDesde.value) params.fecha_desde = fechaDesde.value
    if (fechaHasta.value) params.fecha_hasta = fechaHasta.value
    const { data } = await api.get('/admin/registros-precios', { params })
    registros.value = data
  } catch (e: any) {
    console.error('Error cargando registros:', e)
  } finally {
    loading.value = false
  }
}

async function fetchFiltros() {
  try {
    const { data } = await api.get('/admin/registros-precios/filtros', { params: {} })
    catEstados.value = data.estados || []
    catMunicipiosMap.value = data.municipios_map || {}
    catCategorias.value = data.categorias || []
    catSubcategorias.value = data.subcategorias || []
    catProductos.value = data.productos || []
    catMercados.value = data.mercados || []
  } catch (e: any) {
    console.error('Error cargando filtros:', e)
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  fetchFiltros()
  fetchData()
})
</script>

<style scoped>
.dashboard-layout { display: flex; min-height: 100vh; }

.sidebar {
  width: 260px; background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100;
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.35);
}
.sidebar-header { display: flex; align-items: center; gap: 0.75rem; padding: 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #fff; }
.sidebar-logo { width: 44px; height: 44px; background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.sidebar-brand { display: flex; flex-direction: column; }
.sidebar-brand__title { font-weight: 800; font-size: 1.15rem; letter-spacing: 0.04em; }
.sidebar-brand__sub { font-size: 0.68rem; font-weight: 500; color: rgba(255,255,255,0.6); text-transform: uppercase; }
.sidebar-nav { flex: 1; padding: 0.75rem 0.65rem; overflow-y: auto; }
.sidebar-nav-label { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.05em; padding: 0.5rem 0.85rem 0.35rem; }
.nav-item { display: flex; align-items: center; gap: 0.65rem; padding: 0.55rem 0.85rem; border-radius: 8px; color: rgba(255,255,255,0.75); text-decoration: none; font-weight: 500; font-size: 0.88rem; transition: all 0.2s; margin-bottom: 2px; }
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.active { background: rgba(99,102,241,0.25); color: #fff; font-weight: 600; }
.sidebar-footer { padding: 0.85rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; }
.user-info { display: flex; align-items: center; gap: 0.65rem; }
.user-avatar { width: 34px; height: 34px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 600; font-size: 0.78rem; }
.user-details { display: flex; flex-direction: column; }
.user-name { font-weight: 600; font-size: 0.82rem; color: #fff; }
.user-role { font-size: 0.7rem; color: rgba(255,255,255,0.5); text-transform: capitalize; }
.btn-logout { width: 32px; height: 32px; border: none; border-radius: 8px; background: transparent; color: rgba(255,255,255,0.5); cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-logout:hover { background: rgba(255,255,255,0.1); color: #fff; }

.main-content { flex: 1; margin-left: 260px; padding: 0.75rem 2rem 2rem; background: #f8fafc; min-height: 100vh; }

.top-bar { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 14px; padding: 1.15rem 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 4px 20px rgba(79,70,229,0.18); }
.top-bar__title { font-size: 1.35rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__desc { font-size: 0.85rem; color: rgba(255,255,255,0.75); margin: 0.15rem 0 0; }

.toolbar-card { background: #fff; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04); margin-bottom: 1.25rem; overflow: hidden; }
.toolbar-row { padding: 1rem 1.25rem; }
.toolbar-row--stats { display: flex; gap: 0.6rem; flex-wrap: wrap; border-bottom: 1px solid #f1f5f9; background: #fafbfd; }
.stat-pill { display: flex; align-items: center; gap: 0.55rem; padding: 0.5rem 0.85rem; border-radius: 10px; background: #fff; border: 1px solid #e2e8f0; flex: 1; min-width: 110px; transition: transform 0.15s, box-shadow 0.15s; }
.stat-pill:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.stat-pill__icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.stat-pill__icon--total { background: #ede9fe; color: #7c3aed; }
.stat-pill__icon--shown { background: #e0f2fe; color: #0284c7; }
.stat-pill__icon--cac { background: #fef3c7; color: #d97706; }
.stat-pill__icon--com { background: #eef2ff; color: #4f46e5; }
.stat-pill__icon--ofi { background: #d1fae5; color: #059669; }
.stat-pill__data { display: flex; flex-direction: column; }
.stat-pill__value { font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.stat-pill__label { font-size: 0.7rem; color: #94a3b8; font-weight: 500; }

.toolbar-row--filters { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; border-bottom: 1px solid #f1f5f9; }
.search-box { flex: 1; min-width: 220px; position: relative; }
.search-box__icon { position: absolute; left: 0.85rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-box__input { width: 100%; padding: 0.65rem 2.2rem 0.65rem 2.7rem; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.88rem; background: #f8fafc; box-sizing: border-box; }
.search-box__input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); background: #fff; }
.search-box__clear { position: absolute; right: 0.6rem; top: 50%; transform: translateY(-50%); background: #e2e8f0; border: none; width: 22px; height: 22px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }

.filter-chips { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.filter-chip { display: flex; align-items: center; gap: 0.35rem; padding: 0 0.1rem 0 0.7rem; border: 1.5px solid #e2e8f0; border-radius: 10px; background: #f8fafc; }
.filter-chip select { border: none; background: transparent; font-size: 0.84rem; padding: 0.6rem 0.5rem; min-width: 120px; cursor: pointer; }
.filter-chip select:focus { outline: none; }

.btn-clear-filters { display: flex; align-items: center; gap: 0.3rem; padding: 0.5rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 500; border: none; cursor: pointer; background: #fef2f2; color: #dc2626; transition: background 0.15s; white-space: nowrap; margin-left: auto; }
.btn-clear-filters:hover { background: #fee2e2; }

.toolbar-row--dates { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
.date-label { display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: #475569; font-weight: 500; }
.date-input { padding: 0.5rem 0.65rem; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 0.84rem; background: #f8fafc; }
.date-input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.btn-clear-dates, .btn-apply-dates { display: flex; align-items: center; gap: 0.3rem; padding: 0.5rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 500; border: none; cursor: pointer; transition: background 0.15s; }
.btn-clear-dates { background: #fef2f2; color: #dc2626; }
.btn-clear-dates:hover { background: #fee2e2; }
.btn-apply-dates { background: #4f46e5; color: #fff; }
.btn-apply-dates:hover { background: #4338ca; }

.table-card { background: #fff; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04); overflow: hidden; }
.table-scroll { overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl thead { background: #f8fafc; border-bottom: 1.5px solid #e2e8f0; }
.tbl th { padding: 0.75rem 1rem; font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; text-align: left; white-space: nowrap; }
.tbl th.sortable { cursor: pointer; user-select: none; }
.tbl th.sortable:hover { color: #4f46e5; }
.tbl th .flipped { transform: rotate(180deg); }
.tbl td { padding: 0.65rem 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.86rem; color: #334155; }
.tbl tbody tr:hover { background: #f8fafc; }
.td-email { color: #64748b; font-size: 0.8rem; }
.td-precio { font-weight: 700; color: #059669; }

.cell-user { display: flex; align-items: center; gap: 0.7rem; white-space: nowrap; }
.cell-user__avatar { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 0.7rem; flex-shrink: 0; }
.chip { padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.7rem; font-weight: 600; white-space: nowrap; }
.chip--indigo { background: #eef2ff; color: #3730a3; }
.chip--emerald { background: #d1fae5; color: #065f46; }

.pager { display: flex; align-items: center; justify-content: center; gap: 0.25rem; padding: 0.85rem 1rem; border-top: 1px solid #f1f5f9; }
.pager__btn { min-width: 34px; height: 34px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; color: #475569; font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.pager__btn:hover:not(:disabled) { border-color: #6366f1; color: #4f46e5; background: #eef2ff; }
.pager__btn--active { background: #4f46e5 !important; border-color: #4f46e5 !important; color: #fff !important; }
.pager__btn:disabled { opacity: 0.35; cursor: not-allowed; }
.pager__dots { padding: 0 0.2rem; color: #94a3b8; }
.pager__info { margin-left: 0.6rem; font-size: 0.78rem; color: #94a3b8; }

.state-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; color: #94a3b8; }
.spinner { width: 36px; height: 36px; border: 3px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .sidebar { width: 68px; }
  .sidebar-brand, .nav-item span, .user-details, .sidebar-nav-label { display: none; }
  .main-content { margin-left: 68px; }
}
@media (max-width: 600px) {
  .main-content { padding: 0.75rem 1rem 1.5rem; }
  .stat-pill { flex: 1 1 calc(50% - 0.4rem); }
  .toolbar-row--filters { flex-direction: column; }
  .toolbar-row--dates { flex-direction: column; align-items: stretch; }
}
</style>
