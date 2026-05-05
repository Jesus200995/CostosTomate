<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="section-header">
        <Building2 :size="24" />
        <h1>Mis Centrales</h1>
      </div>

      <!-- Tabs -->
      <div class="mercados-tabs">
        <button class="mercados-tab" :class="{ 'mercados-tab--active': activeTab === 'principal' }" @click="activeTab = 'principal'">
          <Building2 :size="16" /> Principal
        </button>
        <button class="mercados-tab" :class="{ 'mercados-tab--active': activeTab === 'favoritas' }" @click="activeTab = 'favoritas'">
          <Star :size="16" /> Favoritas
        </button>
        <button class="mercados-tab" :class="{ 'mercados-tab--active': activeTab === 'propuestas' }" @click="activeTab = 'propuestas'">
          <MapPin :size="16" /> Propuestas
        </button>
      </div>

      <!-- ══ TAB PRINCIPAL ══ -->
      <div v-if="activeTab === 'principal'">
        <button class="btn btn--primary btn--full" @click="showCatalogo = true" style="margin-bottom:1.25rem;">
          <Search :size="18" />
          <span>Buscar y agregar central</span>
        </button>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando centrales...</p>
        </div>

        <div v-else-if="misCentrales.length === 0" class="empty-state">
          <Building2 :size="48" />
          <p>No tienes centrales registradas</p>
          <p class="empty-state__hint">Busca una central del catálogo para comenzar a capturar precios de jitomate</p>
        </div>

        <div v-else class="mercados-list">
          <div v-for="c in misCentrales" :key="c.id" class="mercado-card" @click="irACapturar(c.central_id)">
            <div class="mercado-card__info">
              <h3>{{ c.nombre_central }}</h3>
              <div class="mercado-card__meta">
                <span class="mercado-card__badge">{{ c.tipo || 'Central' }}</span>
                <span class="mercado-card__loc">
                  <MapPin :size="12" />
                  {{ c.municipio }}, {{ c.estado }}
                </span>
              </div>
            </div>
            <div class="mercado-card__actions">
              <button class="btn-icon btn-icon--danger" @click.stop="deleteCentral(c.id)" title="Quitar central">
                <Trash2 :size="18" />
              </button>
              <ChevronRight :size="20" class="mercado-card__arrow" />
            </div>
          </div>
        </div>
      </div>

      <!-- ══ TAB FAVORITAS ══ -->
      <div v-if="activeTab === 'favoritas'">
        <p class="tab-description">Centrales marcadas como favoritas</p>
        <div v-if="favoritas.length === 0" class="empty-state">
          <Star :size="48" />
          <p>Sin centrales favoritas aún</p>
          <p class="empty-state__hint">Agrega centrales desde el catálogo y márcalas como favoritas</p>
        </div>
        <div v-else class="mercados-list">
          <div v-for="c in favoritas" :key="'fav-' + c.id" class="mercado-card" @click="irACapturar(c.central_id)">
            <div class="mercado-card__info">
              <h3>{{ c.nombre_central }}</h3>
              <div class="mercado-card__meta">
                <span class="mercado-card__badge">{{ c.tipo || 'Central' }}</span>
                <span class="mercado-card__loc">
                  <MapPin :size="12" />
                  {{ c.municipio }}, {{ c.estado }}
                </span>
              </div>
            </div>
            <ChevronRight :size="20" class="mercado-card__arrow" />
          </div>
        </div>
      </div>

      <!-- ══ TAB PROPUESTAS ══ -->
      <div v-if="activeTab === 'propuestas'">
        <div class="propuestos-tab-header">
          <p class="tab-description">Centrales que has propuesto</p>
          <button class="btn btn--outline btn--sm" @click="showProponer = true">
            <Plus :size="16" /> Proponer nueva
          </button>
        </div>
        <div v-if="propuestas.length === 0" class="empty-state">
          <MapPin :size="48" />
          <p>No has propuesto centrales</p>
          <p class="empty-state__hint">Si no encuentras una central en el catálogo, puedes proponer una nueva</p>
        </div>
        <div v-else class="propuestos-list">
          <div v-for="p in propuestas" :key="p.id" class="propuesto-card">
            <div class="propuesto-card__info">
              <h4>{{ p.nombre_central }}</h4>
              <div class="propuesto-card__meta">
                <span class="propuesto-card__badge" :class="propStatusClass(p.estatus)">{{ propStatusLabel(p.estatus) }}</span>
                <span class="propuesto-card__loc">{{ p.municipio }}, {{ p.estado }}</span>
              </div>
              <span v-if="p.motivo_rechazo" class="propuesto-card__motivo">{{ p.motivo_rechazo }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ MODAL CATÁLOGO ═══ -->
      <div v-if="showCatalogo" class="modal-overlay" @click.self="showCatalogo = false">
        <div class="modal-catalogo">
          <div class="modal-header">
            <h2><Search :size="20" /> Buscar Central</h2>
            <button class="btn-icon" @click="showCatalogo = false"><X :size="22" /></button>
          </div>

          <div class="catalogo-filtros">
            <!-- Estado (obligatorio, primer filtro) -->
            <div class="filter-row">
              <label class="filter-label">Estado *</label>
              <select
                v-model="filtroEstado"
                class="input"
                @change="onEstadoChange"
              >
                <option value="">Selecciona un estado...</option>
                <option v-for="e in estadosDisponibles" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>

            <!-- Municipio (dependiente de estado) -->
            <div class="filter-row">
              <label class="filter-label">Municipio</label>
              <select
                v-model="filtroMunicipio"
                class="input"
                :disabled="!filtroEstado || loadingMunicipios"
                @change="onMunicipioChange"
              >
                <option value="">{{ filtroEstado ? 'Todos los municipios' : 'Elige estado primero' }}</option>
                <option v-for="m in municipiosDisponibles" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- Nombre (opcional, refina resultados) -->
            <div class="filter-row">
              <label class="filter-label">Nombre (opcional)</label>
              <input
                v-model="filtroNombre"
                type="text"
                class="input"
                placeholder="Refinar por nombre..."
                :disabled="!filtroEstado"
                @input="onNombreInput"
              />
            </div>
          </div>

          <div v-if="searchingCatalogo" class="loading-state" style="padding:2rem;">
            <div class="spinner"></div>
            <p>Buscando centrales...</p>
          </div>

          <div v-else-if="!filtroEstado" class="empty-state" style="padding:2rem;">
            <MapPin :size="36" />
            <p>Selecciona un estado para buscar centrales</p>
            <p class="empty-state__hint">Elige primero el estado, luego podrás filtrar por municipio o nombre.</p>
          </div>

          <div v-else-if="catalogoResults.length === 0 && filtroEstado" class="empty-state" style="padding:2rem;">
            <p>No se encontraron centrales en <strong>{{ filtroEstado }}</strong></p>
            <button class="btn btn--outline btn--wrap" style="margin-top:0.75rem;" @click="showCatalogo=false; showProponer=true">
              <Plus :size="16" />
              <span>Proponer central nueva</span>
            </button>
          </div>

          <div v-else class="catalogo-results">
            <div
              v-for="cm in catalogoResults"
              :key="cm.id"
              class="catalogo-item"
              :class="{ 'catalogo-item--added': isCentralAdded(cm.id) }"
              @click="addFromCatalogo(cm)"
            >
              <div class="catalogo-item__info">
                <h4>{{ cm.nombre_central }}</h4>
                <div class="catalogo-item__meta">
                  <span>{{ cm.tipo || 'Central' }}</span>
                  <span>{{ cm.municipio }}, {{ cm.estado }}</span>
                </div>
              </div>
              <div class="catalogo-item__action">
                <span v-if="isCentralAdded(cm.id)" class="added-label">
                  <CheckCircle :size="16" /> Agregada
                </span>
                <button v-else class="btn btn--primary btn--sm" :disabled="addingId === cm.id">
                  <Plus :size="16" />
                </button>
              </div>
            </div>
          </div>

          <div class="catalogo-footer">
            <button class="btn btn--outline btn--full btn--wrap" @click="showCatalogo=false; showProponer=true">
              <MapPin :size="16" />
              <span>¿No encuentras tu central? Proponer una nueva</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ═══ MODAL PROPONER CENTRAL ═══ -->
      <div v-if="showProponer" class="modal-overlay" @click.self="showProponer = false">
        <div class="modal-catalogo modal-proponer">
          <div class="modal-header">
            <h2><MapPin :size="20" /> Proponer Central</h2>
            <button class="btn-icon" @click="showProponer = false"><X :size="22" /></button>
          </div>

          <div class="proponer-form">
            <div class="form-group">
              <label class="form-label">Nombre de la central *</label>
              <input v-model="propForm.nombre_central" type="text" class="input" placeholder="Ej: Central de Abasto Oriente" />
            </div>

            <div class="form-group">
              <label class="form-label">Tipo</label>
              <select v-model="propForm.tipo" class="input">
                <option value="">Seleccionar...</option>
                <option value="Central de Abasto">Central de Abasto</option>
                <option value="Mercado Mayorista">Mercado Mayorista</option>
                <option value="Bodega">Bodega</option>
                <option value="Otro">Otro</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Estado *</label>
              <input v-model="propForm.estado" type="text" class="input" placeholder="Ej: Jalisco" />
            </div>

            <div class="form-group">
              <label class="form-label">Municipio *</label>
              <input v-model="propForm.municipio" type="text" class="input" placeholder="Ej: Guadalajara" />
            </div>

            <div class="gps-buttons">
              <button class="btn btn--outline btn--full btn--wrap" type="button" @click="captureGPS" :disabled="gpsStatus === 'loading'">
                <Navigation :size="16" />
                <span>{{ gpsStatus === 'success' ? 'Recapturar GPS' : 'Capturar mi ubicación' }}</span>
              </button>
            </div>

            <div v-if="gpsStatus === 'success'" class="gps-status gps-status--ok">
              <CheckCircle :size="16" />
              <span>GPS: {{ propForm.latitud.toFixed(5) }}, {{ propForm.longitud.toFixed(5) }}</span>
            </div>
            <div v-else-if="gpsStatus === 'error'" class="gps-status gps-status--error">
              <AlertCircle :size="16" />
              <span>{{ gpsError }}</span>
            </div>

            <div v-if="propError" class="alert-error">{{ propError }}</div>

            <button
              class="btn btn--primary btn--full"
              type="button"
              :disabled="submittingProp"
              @click="submitPropuesta"
            >
              <template v-if="submittingProp">
                <span class="spinner-sm"></span> Enviando...
              </template>
              <template v-else>
                <Send :size="18" /> Enviar propuesta
              </template>
            </button>
          </div>
        </div>
      </div>
    </main>

    <AppToast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { centralesService } from '@/services/jitomate.service'
import type { MiCentral, Central, PropuestaCentral } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  Building2, Star, MapPin, Search, Plus, X, Trash2, ChevronRight,
  CheckCircle, Navigation, AlertCircle, Send
} from 'lucide-vue-next'

const router = useRouter()
const ui = useUiStore()

const activeTab = ref('principal')
const loading = ref(true)
const showCatalogo = ref(false)
const showProponer = ref(false)
const searchingCatalogo = ref(false)
const addingId = ref<number | null>(null)
const submittingProp = ref(false)
const propError = ref('')
const gpsStatus = ref<'idle' | 'loading' | 'success' | 'error'>('idle')
const gpsError = ref('')

const misCentrales = ref<MiCentral[]>([])
const catalogoResults = ref<Central[]>([])
const propuestas = ref<PropuestaCentral[]>([])

const estadosDisponibles = ref<string[]>([])
const municipiosDisponibles = ref<string[]>([])
const loadingMunicipios = ref(false)

const filtroNombre = ref('')
const filtroEstado = ref('')
const filtroMunicipio = ref('')

const propForm = ref({
  nombre_central: '',
  tipo: '',
  estado: '',
  municipio: '',
  latitud: 0,
  longitud: 0,
})

let searchTimer: ReturnType<typeof setTimeout> | null = null

const favoritas = computed(() => misCentrales.value.filter(c => c.es_favorita))

const isCentralAdded = (id: number) => misCentrales.value.some(c => c.central_id === id)

function irACapturar(centralId: number) {
  router.push({ name: 'capturar', query: { central: centralId } })
}

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

function propStatusClass(s: string) {
  if (s === 'aprobada') return 'status--success'
  if (s === 'rechazada') return 'status--danger'
  return 'status--pending'
}

function propStatusLabel(s: string) {
  if (s === 'aprobada') return 'Aprobada'
  if (s === 'rechazada') return 'Rechazada'
  return 'Pendiente'
}

async function onEstadoChange() {
  filtroMunicipio.value = ''
  municipiosDisponibles.value = []
  catalogoResults.value = []
  if (!filtroEstado.value) return

  loadingMunicipios.value = true
  try {
    municipiosDisponibles.value = await centralesService.getMunicipiosDisponibles(filtroEstado.value)
  } catch {
    municipiosDisponibles.value = []
  } finally {
    loadingMunicipios.value = false
  }
  await searchCatalogo()
}

function onMunicipioChange() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(searchCatalogo, 150)
}

function onNombreInput() {
  if (!filtroEstado.value) return
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(searchCatalogo, 350)
}

async function searchCatalogo() {
  if (!filtroEstado.value) { catalogoResults.value = []; return }
  searchingCatalogo.value = true
  try {
    catalogoResults.value = await centralesService.getCentrales({
      nombre: filtroNombre.value || undefined,
      estado: filtroEstado.value || undefined,
      municipio: filtroMunicipio.value || undefined,
    })
  } catch {
    catalogoResults.value = []
  } finally {
    searchingCatalogo.value = false
  }
}

async function addFromCatalogo(c: Central) {
  if (isCentralAdded(c.id) || addingId.value) return
  addingId.value = c.id
  try {
    const nueva = await centralesService.addMiCentral(c.id)
    misCentrales.value.unshift(nueva)
    ui.showToast(`${c.nombre_central} agregada`, 'success')
  } catch (e: any) {
    const msg = e?.response?.data?.detail || 'Error al agregar'
    ui.showToast(msg, 'error')
  } finally {
    addingId.value = null
  }
}

async function deleteCentral(relacionId: number) {
  try {
    await centralesService.removeMiCentral(relacionId)
    misCentrales.value = misCentrales.value.filter(c => c.id !== relacionId)
    ui.showToast('Central eliminada de tu lista', 'info')
  } catch {
    ui.showToast('Error al eliminar', 'error')
  }
}

function captureGPS() {
  if (!navigator.geolocation) {
    gpsError.value = 'GPS no disponible en este dispositivo'
    gpsStatus.value = 'error'
    return
  }
  gpsStatus.value = 'loading'
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      propForm.value.latitud = pos.coords.latitude
      propForm.value.longitud = pos.coords.longitude
      gpsStatus.value = 'success'
    },
    (err) => {
      gpsError.value = err.message || 'No se pudo obtener la ubicación'
      gpsStatus.value = 'error'
    },
    { timeout: 10000, enableHighAccuracy: true }
  )
}

async function submitPropuesta() {
  const f = propForm.value
  if (!f.nombre_central.trim()) { propError.value = 'Ingresa el nombre'; return }
  if (!f.estado.trim() || !f.municipio.trim()) { propError.value = 'Ingresa estado y municipio'; return }
  if (gpsStatus.value !== 'success') { propError.value = 'Captura tu ubicación GPS'; return }

  propError.value = ''
  submittingProp.value = true
  try {
    const nueva = await centralesService.proponerCentral({
      nombre_central: f.nombre_central.trim(),
      tipo: f.tipo || undefined,
      estado: f.estado.trim(),
      municipio: f.municipio.trim(),
      latitud: f.latitud,
      longitud: f.longitud,
    })
    propuestas.value.unshift(nueva)
    showProponer.value = false
    ui.showToast('Propuesta enviada correctamente', 'success')
    propForm.value = { nombre_central: '', tipo: '', estado: '', municipio: '', latitud: 0, longitud: 0 }
    gpsStatus.value = 'idle'
    activeTab.value = 'propuestas'
  } catch (e: any) {
    propError.value = e?.response?.data?.detail || 'Error al enviar propuesta'
  } finally {
    submittingProp.value = false
  }
}

onMounted(async () => {
  try {
    const [centrales, props, estados] = await Promise.all([
      centralesService.getMisCentrales(),
      centralesService.getPropuestas(),
      centralesService.getEstadosDisponibles(),
    ])
    misCentrales.value = centrales
    propuestas.value = props
    estadosDisponibles.value = estados
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.section-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 16px;
}
.section-header h1 {
  font-size: 1.3rem; font-weight: 700; color: #1a1a1a; margin: 0;
}

.mercados-tabs {
  display: flex; gap: 8px; margin-bottom: 16px; overflow-x: auto; padding-bottom: 2px;
}
.mercados-tab {
  display: flex; align-items: center; gap: 6px; padding: 7px 14px;
  border: 1.5px solid #e0e0e0; border-radius: 20px; background: #fff;
  font-size: 0.82rem; font-weight: 600; color: #666; cursor: pointer; white-space: nowrap;
  transition: all 0.2s;
}
.mercados-tab--active {
  border-color: #c0392b; background: #fef5f5; color: #c0392b;
}

.loading-state {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 3rem 0; color: #999;
}
.spinner {
  width: 32px; height: 32px;
  border: 3px solid #e0e0e0; border-top-color: #c0392b;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  padding: 3rem 0; color: #bbb; text-align: center;
}
.empty-state p { margin: 0; font-size: 0.9rem; color: #666; }
.empty-state__hint { font-size: 0.78rem !important; color: #999 !important; }

.mercados-list { display: flex; flex-direction: column; gap: 10px; }
.mercado-card {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border: 1.5px solid #ebebeb; border-radius: 12px; padding: 12px 14px;
  cursor: pointer; transition: all 0.2s;
}
.mercado-card:hover { border-color: #c0392b; box-shadow: 0 2px 8px rgba(192,57,43,0.08); }
.mercado-card__info { min-width: 0; flex: 1; }
.mercado-card__info h3 {
  font-size: 0.92rem; font-weight: 600; color: #1a1a1a;
  margin: 0 0 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.mercado-card__meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.mercado-card__badge {
  font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;
  background: #fce4ec; color: #c0392b; text-transform: uppercase;
}
.mercado-card__loc {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.75rem; color: #888;
}
.mercado-card__actions { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.mercado-card__arrow { color: #ccc; }
.btn-icon { background: none; border: none; cursor: pointer; padding: 4px; border-radius: 6px; }
.btn-icon--danger { color: #e74c3c; }
.btn-icon--danger:hover { background: #fce4ec; }

.tab-description { font-size: 0.82rem; color: #888; margin: 0 0 12px; }
.propuestos-tab-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.propuestos-list { display: flex; flex-direction: column; gap: 10px; }
.propuesto-card {
  background: #fff; border: 1.5px solid #ebebeb; border-radius: 12px; padding: 12px 14px;
}
.propuesto-card__info h4 { font-size: 0.9rem; font-weight: 600; margin: 0 0 6px; color: #1a1a1a; }
.propuesto-card__meta { display: flex; align-items: center; gap: 8px; }
.propuesto-card__badge {
  font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;
}
.status--success { background: #e8f5e9; color: #2e7d32; }
.status--danger { background: #fce4ec; color: #c0392b; }
.status--pending { background: #fff8e1; color: #f57c00; }
.propuesto-card__loc { font-size: 0.75rem; color: #888; }
.propuesto-card__motivo { font-size: 0.72rem; color: #c0392b; display: block; margin-top: 4px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 200;
  display: flex; align-items: flex-end; justify-content: center;
}
.modal-catalogo {
  background: #fff; border-radius: 20px 20px 0 0; width: 100%; max-width: 500px;
  max-height: 90vh; overflow-y: auto; padding: 0 0 env(safe-area-inset-bottom);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 16px 8px; border-bottom: 1px solid #ebebeb; position: sticky; top: 0; background: #fff; z-index: 1;
}
.modal-header h2 { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 700; margin: 0; }

.catalogo-filtros { padding: 12px 16px; display: flex; flex-direction: column; gap: 10px; }
.filter-row { display: flex; flex-direction: column; gap: 4px; }
.filter-label { font-size: 0.75rem; font-weight: 600; color: #555; }
.filter-row .input {
  width: 100%; padding: 10px 12px; border: 1.5px solid #e0e0e0;
  border-radius: 10px; font-size: 0.88rem; box-sizing: border-box; background: #fff;
  transition: border-color 0.2s;
}
.filter-row .input:focus { outline: none; border-color: #c0392b; }
.filter-row .input:disabled { background: #f5f5f5; color: #aaa; cursor: not-allowed; }

.catalogo-results { padding: 0 16px; }
.catalogo-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer;
}
.catalogo-item--added { opacity: 0.5; cursor: default; }
.catalogo-item__info h4 { font-size: 0.88rem; font-weight: 600; margin: 0 0 4px; color: #1a1a1a; }
.catalogo-item__meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.catalogo-item__meta span { font-size: 0.72rem; color: #888; }
.catalogo-item__action { flex-shrink: 0; }
.added-label { display: flex; align-items: center; gap: 4px; font-size: 0.72rem; color: #2e7d32; font-weight: 600; }
.catalogo-footer { padding: 12px 16px 16px; }

/* Modal proponer */
.modal-proponer .proponer-form { padding: 16px; display: flex; flex-direction: column; gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 0.8rem; font-weight: 600; color: #444; }
.input {
  padding: 10px 12px; border: 1.5px solid #e0e0e0; border-radius: 10px;
  font-size: 0.88rem; background: #fff; transition: border-color 0.2s;
}
.input:focus { outline: none; border-color: #c0392b; }

.gps-buttons { display: flex; gap: 8px; }
.gps-status {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  border-radius: 10px; font-size: 0.78rem; font-weight: 600;
}
.gps-status--ok { background: #e8f5e9; color: #2e7d32; }
.gps-status--error { background: #fce4ec; color: #c0392b; }

.alert-error {
  padding: 8px 12px; background: #fce4ec; color: #c0392b;
  border-radius: 10px; font-size: 0.8rem;
}

/* Buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 10px 16px; border-radius: 10px; font-weight: 600; font-size: 0.88rem;
  cursor: pointer; border: none; transition: all 0.2s;
}
.btn--primary { background: #c0392b; color: #fff; }
.btn--primary:hover:not(:disabled) { background: #a93226; }
.btn--primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--outline { background: #fff; color: #c0392b; border: 1.5px solid #c0392b; }
.btn--full { width: 100%; }
.btn--sm { padding: 6px 12px; font-size: 0.78rem; }
.btn--wrap { white-space: normal; text-align: center; }

.spinner-sm {
  width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.7s linear infinite; display: inline-block;
}
</style>
