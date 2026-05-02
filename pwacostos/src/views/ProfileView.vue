<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="profile-page" :class="{ 'profile-page--visible': mounted }">
        <div class="profile-header">
          <button class="profile-back" @click="$router.push('/')">
            <ArrowLeft :size="20" />
          </button>
          <h1 class="profile-header__title">Mi Perfil</h1>
          <button v-if="!editing" class="profile-edit-btn" @click="startEdit">
            <Pencil :size="18" />
            <span>Editar</span>
          </button>
          <button v-else class="profile-cancel-btn" @click="cancelEdit">
            <X :size="18" />
            <span>Cancelar</span>
          </button>
        </div>

        <!-- Avatar + Name -->
        <div class="profile-card">
          <div class="profile-avatar">
            <span>{{ initials }}</span>
          </div>
          <h2 class="profile-name">{{ authStore.user?.name }}</h2>
          <p class="profile-email">{{ authStore.user?.email }}</p>
          <span class="profile-role-badge">{{ rolLabel }}</span>
        </div>

        <!-- VIEW MODE -->
        <template v-if="!editing">
          <section class="profile-section">
            <h3 class="profile-section__title"><UserIcon :size="18" /> Datos personales</h3>
            <div class="profile-field">
              <span class="profile-field__label">Nombre</span>
              <span class="profile-field__value">{{ authStore.user?.name || '—' }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">CURP</span>
              <span class="profile-field__value">{{ authStore.user?.curp || '—' }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Correo</span>
              <span class="profile-field__value">{{ authStore.user?.email || '—' }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Teléfono</span>
              <span class="profile-field__value">{{ authStore.user?.telefono || '—' }}</span>
            </div>
          </section>

          <section class="profile-section">
            <h3 class="profile-section__title"><MapPin :size="18" /> Ubicación</h3>
            <div class="profile-field">
              <span class="profile-field__label">Estado</span>
              <span class="profile-field__value">{{ estadoNombre }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Municipio</span>
              <span class="profile-field__value">{{ municipioNombre }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Localidad</span>
              <span class="profile-field__value">{{ authStore.user?.localidad || '—' }}</span>
            </div>
          </section>

          <section v-if="authStore.user?.tipo_capturista === 'REPRESENTANTE_CAC' || authStore.user?.tipo_capturista === 'COM_COMERCIALIZACION'" class="profile-section">
            <h3 class="profile-section__title"><Building :size="18" /> {{ authStore.user?.tipo_capturista === 'REPRESENTANTE_CAC' ? 'Datos CAC' : 'Comisión de comercialización' }}</h3>
            <div class="profile-field">
              <span class="profile-field__label">CAC ID</span>
              <span class="profile-field__value">{{ authStore.user?.cac_id || '—' }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Nombre del CAC</span>
              <span class="profile-field__value">{{ authStore.user?.cac_nombre || '—' }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Territorio</span>
              <span class="profile-field__value">{{ authStore.user?.territorio || '—' }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Ruta</span>
              <span class="profile-field__value">{{ authStore.user?.ruta || '—' }}</span>
            </div>
          </section>

          <section v-if="authStore.user?.tipo_capturista === 'OFICINAS'" class="profile-section">
            <h3 class="profile-section__title"><Briefcase :size="18" /> Datos de oficinas</h3>
            <div class="profile-field">
              <span class="profile-field__label">Correo institucional</span>
              <span class="profile-field__value">{{ authStore.user?.correo_institucional || '—' }}</span>
            </div>
            <div class="profile-field">
              <span class="profile-field__label">Rol interno</span>
              <span class="profile-field__value">{{ authStore.user?.rol_interno || '—' }}</span>
            </div>
          </section>
        </template>

        <!-- EDIT MODE -->
        <template v-else>
          <form class="profile-edit-form" @submit.prevent="saveProfile" novalidate>
            <section class="profile-section">
              <h3 class="profile-section__title"><UserIcon :size="18" /> Datos personales</h3>

              <div class="form-group">
                <label class="form-label">Tipo de capturista</label>
                <div class="form-input-wrapper">
                  <Briefcase :size="20" class="form-icon" />
                  <select v-model="form.tipo_capturista">
                    <option value="REPRESENTANTE_CAC">Representante CAC</option>
                    <option value="COM_COMERCIALIZACION">Miembro de comisión de comercialización</option>
                    <option value="OFICINAS">Personal de oficinas central</option>
                  </select>
                </div>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.name }">
                <label class="form-label">Nombre completo</label>
                <div class="form-input-wrapper">
                  <UserIcon :size="20" class="form-icon" />
                  <input v-model="form.name" type="text" placeholder="Nombre y apellido" style="text-transform: uppercase" @input="form.name = toUpperNoTilde(form.name)" />
                </div>
                <span v-if="errors.name" class="form-error">{{ errors.name }}</span>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.curp }">
                <label class="form-label">CURP</label>
                <div class="form-input-wrapper">
                  <Hash :size="20" class="form-icon" />
                  <input v-model="form.curp" type="text" placeholder="CURP (18 caracteres)" maxlength="18" style="text-transform: uppercase" @input="form.curp = form.curp.toUpperCase().replace(/[^A-Z0-9]/g, '')" />
                </div>
                <span v-if="errors.curp" class="form-error">{{ errors.curp }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Teléfono <span class="form-optional">(opcional)</span></label>
                <div class="form-input-wrapper">
                  <Phone :size="20" class="form-icon" />
                  <input v-model="form.telefono" type="tel" placeholder="Ej. 7710000000" maxlength="10" @input="form.telefono = form.telefono.replace(/[^0-9]/g, '')" />
                </div>
              </div>
            </section>

            <section class="profile-section">
              <h3 class="profile-section__title"><MapPin :size="18" /> Ubicación</h3>

              <div class="form-group" :class="{ 'form-group--error': errors.estado }">
                <label class="form-label">Estado</label>
                <div class="form-input-wrapper">
                  <MapPin :size="20" class="form-icon" />
                  <select v-model="form.estado" @change="onEstadoChange">
                    <option value="" disabled>Selecciona estado</option>
                    <option v-for="e in estados" :key="e.cve_ent" :value="e.cve_ent">{{ e.nom_ent }}</option>
                  </select>
                </div>
                <span v-if="errors.estado" class="form-error">{{ errors.estado }}</span>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.municipio }">
                <label class="form-label">Municipio</label>
                <div class="form-input-wrapper">
                  <MapPin :size="20" class="form-icon" />
                  <select v-model="form.municipio" :disabled="!form.estado || loadingMunicipios" @change="onMunicipioChange">
                    <option :value="0" disabled>{{ loadingMunicipios ? 'Cargando...' : 'Selecciona municipio' }}</option>
                    <option v-for="m in municipios" :key="m.clave_mun" :value="m.clave_mun">{{ m.nomgeo }}</option>
                  </select>
                </div>
                <span v-if="errors.municipio" class="form-error">{{ errors.municipio }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Localidad <span class="form-optional">(opcional)</span></label>
                <div class="form-input-wrapper">
                  <Home :size="20" class="form-icon" />
                  <input v-model="form.localidad" type="text" placeholder="Localidad" style="text-transform: uppercase" @input="form.localidad = toUpperNoTilde(form.localidad)" />
                </div>
              </div>
            </section>

            <!-- REP_CAC + COM_COMERCIALIZACION fields (compartidos) -->
            <section v-if="form.tipo_capturista === 'REPRESENTANTE_CAC' || form.tipo_capturista === 'COM_COMERCIALIZACION'" class="profile-section">
              <h3 class="profile-section__title"><Building :size="18" /> {{ form.tipo_capturista === 'REPRESENTANTE_CAC' ? 'Datos CAC' : 'Comisión de comercialización' }}</h3>

              <div class="form-group" :class="{ 'form-group--error': errors.cac_id }">
                <label class="form-label">CAC ID</label>
                <div class="form-input-wrapper">
                  <Hash :size="20" class="form-icon" />
                  <input v-model="form.cac_id" type="text" placeholder="CAC_123" />
                </div>
                <span v-if="errors.cac_id" class="form-error">{{ errors.cac_id }}</span>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.cac_nombre }">
                <label class="form-label">Nombre del CAC</label>
                <div class="form-input-wrapper">
                  <Building :size="20" class="form-icon" />
                  <input v-model="form.cac_nombre" type="text" placeholder="CAC SEMILLAS DEL FUTURO" style="text-transform: uppercase" @input="form.cac_nombre = toUpperNoTilde(form.cac_nombre)" />
                </div>
                <span v-if="errors.cac_nombre" class="form-error">{{ errors.cac_nombre }}</span>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.territorio }">
                <label class="form-label">Territorio <span v-if="territorioFromCatalog" class="form-auto-tag">Automático</span></label>
                <div class="form-input-wrapper" :class="{ 'form-input-wrapper--readonly': territorioFromCatalog }">
                  <MapPinIcon :size="20" class="form-icon" />
                  <select v-model="form.territorio" :disabled="territorioFromCatalog">
                    <option value="">Selecciona territorio</option>
                    <option v-for="t in territorioOptions" :key="t" :value="t">{{ t }}</option>
                  </select>
                </div>
                <span v-if="errors.territorio" class="form-error">{{ errors.territorio }}</span>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.ruta }">
                <label class="form-label">Ruta</label>
                <div class="form-input-wrapper">
                  <MapPinIcon :size="20" class="form-icon" />
                  <input v-model="form.ruta" type="text" placeholder="Ruta 05 / Nombre ruta" style="text-transform: uppercase" @input="form.ruta = toUpperNoTilde(form.ruta)" />
                </div>
                <span v-if="errors.ruta" class="form-error">{{ errors.ruta }}</span>
              </div>
            </section>

            <!-- OFICINAS fields -->
            <section v-if="form.tipo_capturista === 'OFICINAS'" class="profile-section">
              <h3 class="profile-section__title"><Briefcase :size="18" /> Datos de oficinas</h3>

              <div class="form-group">
                <label class="form-label">Correo institucional <span class="form-optional">(recomendado)</span></label>
                <div class="form-input-wrapper">
                  <Mail :size="20" class="form-icon" />
                  <input v-model="form.correo_institucional" type="email" placeholder="nombre@bienestar.gob.mx" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Rol interno <span class="form-optional">(opcional)</span></label>
                <div class="form-input-wrapper">
                  <Briefcase :size="20" class="form-icon" />
                  <select v-model="rolInternoSelect">
                    <option value="">Selecciona rol</option>
                    <option value="Director General">Director General</option>
                    <option value="Director de Área">Director de Área</option>
                    <option value="Facilitador Comunitario">Facilitador Comunitario</option>
                    <option value="JUD">JUD</option>
                    <option value="Técnico Social">Técnico Social</option>
                    <option value="Técnico Productivo">Técnico Productivo</option>
                    <option value="Otro">Otro</option>
                  </select>
                </div>
              </div>
              <div v-if="rolInternoSelect === 'Otro'" class="form-group">
                <label class="form-label">Especifica el rol</label>
                <div class="form-input-wrapper">
                  <Pencil :size="20" class="form-icon" />
                  <input v-model="rolInternoOtro" type="text" placeholder="Escribe el rol" />
                </div>
              </div>
            </section>

            <div v-if="serverError" class="form-server-error">
              <AlertCircle :size="18" />
              <span>{{ serverError }}</span>
            </div>

            <button type="submit" class="btn btn--primary btn--full" :disabled="authStore.loading || !canSave">
              <Loader2 v-if="authStore.loading" :size="20" class="spin" />
              <Save v-else :size="20" />
              <span>{{ authStore.loading ? 'Guardando...' : 'Guardar cambios' }}</span>
            </button>
          </form>
        </template>
      </div>
    </main>
    <AppToast />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { catalogoService } from '@/services/catalogo.service'
import type { Estado, Municipio } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  ArrowLeft, Pencil, X, User as UserIcon, MapPin,
  Building, Briefcase, Hash, Phone, Home,
  Mail, Save, Loader2, AlertCircle,
  Map as MapPinIcon
} from 'lucide-vue-next'

const authStore = useAuthStore()
const ui = useUiStore()

const mounted = ref(false)
const editing = ref(false)
const serverError = ref('')

const estados = ref<Estado[]>([])
const municipios = ref<Municipio[]>([])
const loadingMunicipios = ref(false)
const territorioFromCatalog = ref(false)

// "Otro" logic
const rolInternoSelect = ref('')
const rolInternoOtro = ref('')

const knownRolInterno = ['Director General', 'Director de Área', 'Facilitador Comunitario', 'JUD', 'Técnico Social', 'Técnico Productivo']

const territorioOptions = [
  'Acapulco - Centro - Norte - Tierra Caliente', 'Acayucan', 'Balancán',
  'Chihuahua / Sonora', 'Colima', 'Comalcalco', 'Córdoba',
  'Costa Chica - Montaña', 'Costa Grande - Sierra', 'Durango / Zacatecas',
  'Hidalgo', 'Istmo', 'Michoacán', 'Mixteca', 'Morelos',
  'Nayarit / Jalisco', 'Ocosingo', 'Palenque', 'Papantla', 'Pichucalco',
  'Puebla', 'San Luis Potosí', 'Sinaloa', 'Tamaulipas', 'Tantoyuca',
  'Tapachula', 'Teapa', 'Tlaxcala / Estado de México', 'Tzucacab / Opb', 'Xpujil',
]

function toUpperNoTilde(val: string): string {
  return val.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase()
}

const form = reactive({
  name: '',
  curp: '',
  tipo_capturista: '',
  estado: '',
  municipio: 0,
  localidad: '',
  telefono: '',
  cac_id: '',
  cac_nombre: '',
  territorio: '',
  ruta: '',
  correo_institucional: '',
  rol_interno: ''
})

const errors = reactive<Record<string, string>>({
  name: '', curp: '', estado: '', municipio: '', cac_id: '', cac_nombre: '', territorio: '', ruta: ''
})

const initials = computed(() => {
  const name = authStore.user?.name || 'U'
  return name.split(' ').map((w: string) => w[0]).join('').toUpperCase().slice(0, 2)
})

const rolLabel = computed(() => {
  const map: Record<string, string> = {
    REPRESENTANTE_CAC: 'Representante CAC',
    COM_COMERCIALIZACION: 'Comisión de comercialización',
    OFICINAS: 'Personal de oficinas'
  }
  return map[authStore.user?.tipo_capturista || ''] || authStore.user?.tipo_capturista || '—'
})

const estadoNombre = computed(() => {
  if (!authStore.user?.estado) return '—'
  const e = estados.value.find(x => x.cve_ent === authStore.user!.estado)
  return e?.nom_ent || authStore.user.estado
})

const municipioNombre = computed(() => {
  if (!authStore.user?.municipio) return '—'
  const m = municipios.value.find(x => x.clave_mun === authStore.user!.municipio)
  return m?.nomgeo || String(authStore.user.municipio)
})

const canSave = computed(() => {
  if (!form.name.trim() || form.name.trim().length < 2) return false
  if (!form.curp.trim() || form.curp.trim().length !== 18) return false
  if (!form.estado) return false
  if (!form.municipio) return false
  if (form.tipo_capturista === 'REPRESENTANTE_CAC' || form.tipo_capturista === 'COM_COMERCIALIZACION') {
    if (!form.cac_id.trim()) return false
    if (!form.cac_nombre.trim()) return false
    if (!form.territorio) return false
    if (!form.ruta.trim()) return false
  }
  return true
})

// Watcher: limpiar campos del rol anterior al cambiar tipo_capturista en edición
watch(() => form.tipo_capturista, (newVal, oldVal) => {
  if (!editing.value || !oldVal) return
  if (newVal === 'OFICINAS') {
    // Limpia campos CAC/COM
    form.cac_id = ''
    form.cac_nombre = ''
    form.territorio = ''
    form.ruta = ''
    territorioFromCatalog.value = false
  } else if (newVal === 'REPRESENTANTE_CAC' || newVal === 'COM_COMERCIALIZACION') {
    // Limpia campos Oficinas
    form.correo_institucional = ''
    rolInternoSelect.value = ''
    rolInternoOtro.value = ''
  }
})

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

async function startEdit() {
  const u = authStore.user
  if (!u) return
  form.name = u.name || ''
  form.curp = u.curp || ''
  form.tipo_capturista = u.tipo_capturista || ''
  form.estado = u.estado || ''
  form.municipio = u.municipio || 0
  form.localidad = u.localidad || ''
  form.telefono = u.telefono || ''
  form.cac_id = u.cac_id || ''
  form.cac_nombre = u.cac_nombre || ''
  form.territorio = u.territorio || ''
  form.ruta = u.ruta || ''
  form.correo_institucional = u.correo_institucional || ''

  // Rol interno - detect "Otro"
  if (u.rol_interno && !knownRolInterno.includes(u.rol_interno)) {
    rolInternoSelect.value = 'Otro'
    rolInternoOtro.value = u.rol_interno
  } else {
    rolInternoSelect.value = u.rol_interno || ''
    rolInternoOtro.value = ''
  }

  serverError.value = ''
  Object.keys(errors).forEach(k => errors[k] = '')

  // Load municipios for current estado and detect territorio from catalog
  if (form.estado) {
    await loadMunicipios(form.estado)
    if (form.municipio) {
      const sel = municipios.value.find(m => m.clave_mun === form.municipio)
      if (sel?.territorio && sel.territorio === form.territorio) {
        territorioFromCatalog.value = true
      } else {
        territorioFromCatalog.value = false
      }
    }
  }

  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

async function loadMunicipios(estado: string) {
  loadingMunicipios.value = true
  try {
    municipios.value = await catalogoService.getMunicipios(estado)
  } catch { /* silent */ }
  loadingMunicipios.value = false
}

async function onEstadoChange() {
  form.municipio = 0
  form.territorio = ''
  territorioFromCatalog.value = false
  municipios.value = []
  if (!form.estado) return
  await loadMunicipios(form.estado)
}

function onMunicipioChange() {
  const selected = municipios.value.find(m => m.clave_mun === form.municipio)
  if (selected?.territorio) {
    form.territorio = selected.territorio
    territorioFromCatalog.value = true
  } else {
    form.territorio = ''
    territorioFromCatalog.value = false
  }
}

function validate(): boolean {
  let valid = true
  Object.keys(errors).forEach(k => errors[k] = '')
  if (!form.name.trim() || form.name.trim().length < 2) { errors.name = 'Mínimo 2 caracteres'; valid = false }
  if (!form.curp.trim() || form.curp.trim().length !== 18) { errors.curp = 'La CURP debe tener 18 caracteres'; valid = false }
  if (!form.estado) { errors.estado = 'Selecciona un estado'; valid = false }
  if (!form.municipio) { errors.municipio = 'Selecciona un municipio'; valid = false }
  if (form.tipo_capturista === 'REPRESENTANTE_CAC' || form.tipo_capturista === 'COM_COMERCIALIZACION') {
    if (!form.cac_id.trim()) { errors.cac_id = 'El CAC ID es obligatorio'; valid = false }
    if (!form.cac_nombre.trim()) { errors.cac_nombre = 'El nombre del CAC es obligatorio'; valid = false }
    if (!form.territorio) { errors.territorio = 'El territorio es obligatorio'; valid = false }
    if (!form.ruta.trim()) { errors.ruta = 'La ruta es obligatoria'; valid = false }
  }
  return valid
}

async function saveProfile() {
  serverError.value = ''
  if (!validate()) return

  // Compute final rol values
  const finalRolInterno = rolInternoSelect.value === 'Otro'
    ? rolInternoOtro.value.trim() || null
    : rolInternoSelect.value || null

  // Solo enviar campos relevantes al rol actual
  const isCAC = form.tipo_capturista === 'REPRESENTANTE_CAC' || form.tipo_capturista === 'COM_COMERCIALIZACION'
  const isOficinas = form.tipo_capturista === 'OFICINAS'

  try {
    await authStore.updateProfile({
      name: form.name,
      curp: form.curp,
      tipo_capturista: form.tipo_capturista,
      estado: form.estado,
      municipio: form.municipio,
      localidad: form.localidad || null,
      telefono: form.telefono || null,
      cac_id: isCAC ? (form.cac_id || null) : null,
      cac_nombre: isCAC ? (form.cac_nombre || null) : null,
      territorio: isCAC ? (form.territorio || null) : null,
      ruta: isCAC ? (form.ruta || null) : null,
      rol_comision: null,
      correo_institucional: isOficinas ? (form.correo_institucional || null) : null,
      rol_interno: isOficinas ? finalRolInterno : null,
    })
    editing.value = false
    ui.showToast('Perfil actualizado correctamente', 'success')
  } catch (err: unknown) {
    const error = err as { response?: { data?: { detail?: string } } }
    serverError.value = error.response?.data?.detail || 'Error al guardar'
  }
}

onMounted(async () => {
  setTimeout(() => { mounted.value = true }, 50)
  try {
    estados.value = await catalogoService.getEstados()
    // load municipios for current user estado
    if (authStore.user?.estado) {
      await loadMunicipios(authStore.user.estado)
    }
  } catch { /* silent */ }
})
</script>

<style scoped>
.profile-page {
  padding: 0 1rem 2rem;
  max-width: 600px;
  margin: 0 auto;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.4s ease;
}
.profile-page--visible {
  opacity: 1;
  transform: translateY(0);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 0;
}
.profile-header__title {
  flex: 1;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary, #1e293b);
}
.profile-back {
  padding: 8px;
  border-radius: 10px;
  color: var(--text-secondary, #475569);
  transition: all 0.2s;
}
.profile-back:hover {
  background: var(--bg-input, #f1f5f9);
}
.profile-edit-btn,
.profile-cancel-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.profile-edit-btn {
  color: var(--primary, #e67e00);
  background: rgba(230, 126, 0, 0.08);
  border: 1.5px solid var(--primary, #e67e00);
}
.profile-edit-btn:hover {
  background: rgba(230, 126, 0, 0.15);
}
.profile-cancel-btn {
  color: var(--danger, #ef4444);
  background: rgba(239, 68, 68, 0.08);
  border: 1.5px solid var(--danger, #ef4444);
}
.profile-cancel-btn:hover {
  background: rgba(239, 68, 68, 0.15);
}

.profile-card {
  text-align: center;
  padding: 1.5rem;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: var(--radius-xl, 16px);
  margin-bottom: 1.25rem;
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.08));
}
.profile-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary, #e67e00), var(--accent, #16a34a));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.75rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}
.profile-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary, #1e293b);
  margin-bottom: 2px;
}
.profile-email {
  font-size: 0.85rem;
  color: var(--text-secondary, #475569);
  margin-bottom: 0.6rem;
}
.profile-role-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 12px;
  border-radius: 20px;
  background: rgba(230, 126, 0, 0.1);
  color: var(--primary, #e67e00);
}

.profile-section {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: var(--radius-xl, 16px);
  padding: 1.25rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.08));
}
.profile-section__title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary, #1e293b);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border, #e2e8f0);
}

.profile-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0;
}
.profile-field + .profile-field {
  border-top: 1px solid #f1f5f9;
}
.profile-field__label {
  font-size: 0.82rem;
  color: var(--text-secondary, #475569);
  font-weight: 500;
}
.profile-field__value {
  font-size: 0.88rem;
  color: var(--text-primary, #1e293b);
  font-weight: 600;
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

/* Edit form reuses global .form-group, .form-input-wrapper, etc */
.profile-edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.profile-edit-form .profile-section {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.profile-edit-form .btn--full {
  margin-top: 0.5rem;
}

.form-auto-tag {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  color: #16a34a;
  background: #dcfce7;
  padding: 1px 6px;
  border-radius: 4px;
  margin-left: 4px;
}
.form-optional {
  font-weight: 400;
  color: #94a3b8;
  font-size: 0.76rem;
}
.form-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary, #475569);
  margin-bottom: 0.3rem;
}
.form-input-wrapper--readonly {
  background: #f1f5f9;
  border-color: #e2e8f0 !important;
}

/* ── Responsive: pantallas pequeñas ── */
@media (max-width: 480px) {
  .profile-page {
    padding: 0 0.5rem 1.5rem;
  }
  .profile-header {
    padding: 0.6rem 0;
    gap: 0.5rem;
  }
  .profile-header__title {
    font-size: 1.05rem;
  }
  .profile-edit-btn,
  .profile-cancel-btn {
    font-size: 0.76rem;
    padding: 5px 10px;
    gap: 3px;
  }
  .profile-card {
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 0.75rem;
  }
  .profile-avatar {
    width: 56px;
    height: 56px;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
  }
  .profile-name {
    font-size: 1rem;
  }
  .profile-email {
    font-size: 0.78rem;
  }
  .profile-role-badge {
    font-size: 0.68rem;
    padding: 2px 9px;
  }
  .profile-section {
    padding: 0.85rem;
    border-radius: 12px;
    margin-bottom: 0.65rem;
  }
  .profile-section__title {
    font-size: 0.8rem;
    gap: 0.3rem;
    margin-bottom: 0.65rem;
    padding-bottom: 0.35rem;
  }
  .profile-field {
    padding: 0.4rem 0;
  }
  .profile-field__label {
    font-size: 0.74rem;
  }
  .profile-field__value {
    font-size: 0.78rem;
  }
  .form-label {
    font-size: 0.74rem;
  }
  .form-optional {
    font-size: 0.68rem;
  }
  .form-auto-tag {
    font-size: 0.62rem;
  }
  .profile-edit-form .profile-section {
    gap: 0.6rem;
  }
  .btn--full {
    font-size: 0.82rem;
    padding: 10px;
  }
}

@media (max-width: 360px) {
  .profile-page {
    padding: 0 0.35rem 1rem;
  }
  .profile-header__title {
    font-size: 0.95rem;
  }
  .profile-edit-btn,
  .profile-cancel-btn {
    font-size: 0.7rem;
    padding: 4px 8px;
  }
  .profile-card {
    padding: 0.75rem;
  }
  .profile-avatar {
    width: 48px;
    height: 48px;
    font-size: 1rem;
  }
  .profile-name {
    font-size: 0.9rem;
  }
  .profile-email {
    font-size: 0.72rem;
  }
  .profile-section {
    padding: 0.65rem;
  }
  .profile-section__title {
    font-size: 0.74rem;
  }
  .profile-field__label {
    font-size: 0.68rem;
  }
  .profile-field__value {
    font-size: 0.72rem;
  }
  .form-label {
    font-size: 0.68rem;
  }
  .btn--full {
    font-size: 0.76rem;
    padding: 8px;
  }
}
</style>
