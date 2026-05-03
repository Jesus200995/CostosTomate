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
          <span class="profile-role-badge">Capturista</span>
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
        </template>

        <!-- EDIT MODE -->
        <template v-else>
          <form class="profile-edit-form" @submit.prevent="saveProfile" novalidate>
            <section class="profile-section">
              <h3 class="profile-section__title"><UserIcon :size="18" /> Datos personales</h3>

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
                  <select v-model="form.municipio" :disabled="!form.estado || loadingMunicipios" @change="() => {}">
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { catalogoService } from '@/services/catalogo.service'
import type { Estado, Municipio } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  ArrowLeft, Pencil, X, User as UserIcon, MapPin,
  Hash, Phone, Home, Save, Loader2, AlertCircle
} from 'lucide-vue-next'

const authStore = useAuthStore()
const ui = useUiStore()

const mounted = ref(false)
const editing = ref(false)
const serverError = ref('')

const estados = ref<Estado[]>([])
const municipios = ref<Municipio[]>([])
const loadingMunicipios = ref(false)

function toUpperNoTilde(val: string): string {
  return val.normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase()
}

const form = reactive({
  name: '',
  curp: '',
  estado: '',
  municipio: 0,
  localidad: '',
  telefono: '',
})

const errors = reactive<Record<string, string>>({
  name: '', curp: '', estado: '', municipio: ''
})

const initials = computed(() => {
  const name = authStore.user?.name || 'U'
  return name.split(' ').map((w: string) => w[0]).join('').toUpperCase().slice(0, 2)
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
  return true
})

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

async function startEdit() {
  const u = authStore.user
  if (!u) return
  form.name = u.name || ''
  form.curp = u.curp || ''
  form.estado = u.estado || ''
  form.municipio = u.municipio || 0
  form.localidad = u.localidad || ''
  form.telefono = u.telefono || ''
  serverError.value = ''
  Object.keys(errors).forEach(k => errors[k] = '')
  if (form.estado) await loadMunicipios(form.estado)
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
  municipios.value = []
  if (!form.estado) return
  await loadMunicipios(form.estado)
}

function validate(): boolean {
  let valid = true
  Object.keys(errors).forEach(k => errors[k] = '')
  if (!form.name.trim() || form.name.trim().length < 2) { errors.name = 'Mínimo 2 caracteres'; valid = false }
  if (!form.curp.trim() || form.curp.trim().length !== 18) { errors.curp = 'La CURP debe tener 18 caracteres'; valid = false }
  if (!form.estado) { errors.estado = 'Selecciona un estado'; valid = false }
  if (!form.municipio) { errors.municipio = 'Selecciona un municipio'; valid = false }
  return valid
}

async function saveProfile() {
  serverError.value = ''
  if (!validate()) return
  try {
    await authStore.updateProfile({
      name: form.name,
      curp: form.curp,
      tipo_capturista: 'CAPTURISTA',
      estado: form.estado,
      municipio: form.municipio,
      localidad: form.localidad || null,
      telefono: form.telefono || null,
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
    if (authStore.user?.estado) {
      await loadMunicipios(authStore.user.estado)
    }
  } catch { /* silent */ }
})
</script>
