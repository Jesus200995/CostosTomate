<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="profile-page" :class="{ 'profile-page--visible': mounted }">

        <!-- ── HERO ── -->
        <div class="profile-hero">
          <div class="profile-hero__bg"></div>
          <div class="profile-hero__content">
            <div class="profile-hero__avatar">
              <span>{{ initials }}</span>
              <div class="profile-hero__avatar-ring"></div>
            </div>
            <div class="profile-hero__info">
              <h1 class="profile-hero__name">{{ authStore.user?.name || 'Usuario' }}</h1>
              <p class="profile-hero__email">{{ authStore.user?.email }}</p>
              <span class="profile-hero__badge">
                <Salad :size="13" />
                Capturista jitomate
              </span>
            </div>
          </div>

          <!-- Botón editar flotante -->
          <div class="profile-hero__actions">
            <button v-if="!editing" class="hero-btn hero-btn--edit" @click="startEdit">
              <Pencil :size="16" />
              <span>Editar perfil</span>
            </button>
            <button v-else class="hero-btn hero-btn--cancel" @click="cancelEdit">
              <X :size="16" />
              <span>Cancelar</span>
            </button>
          </div>
        </div>

        <!-- ── STATS BAR ── -->
        <div class="profile-stats">
          <div class="profile-stats__item">
            <MapPin :size="16" />
            <span>{{ estadoNombre }}</span>
          </div>
          <div class="profile-stats__divider"></div>
          <div class="profile-stats__item">
            <Building2 :size="16" />
            <span>{{ municipioNombre }}</span>
          </div>
          <div class="profile-stats__divider"></div>
          <div class="profile-stats__item">
            <Calendar :size="16" />
            <span>{{ memberSince }}</span>
          </div>
        </div>

        <!-- ── VIEW MODE ── -->
        <Transition name="profile-fade" mode="out-in">
          <div v-if="!editing" key="view" class="profile-body">

            <div class="profile-card">
              <div class="profile-card__header">
                <div class="profile-card__icon-wrap">
                  <UserIcon :size="18" />
                </div>
                <h3 class="profile-card__title">Datos personales</h3>
              </div>

              <div class="profile-grid">
                <div class="profile-item">
                  <div class="profile-item__icon"><UserIcon :size="15" /></div>
                  <div class="profile-item__content">
                    <span class="profile-item__label">Nombre completo</span>
                    <span class="profile-item__value">{{ authStore.user?.name || '—' }}</span>
                  </div>
                </div>
                <div class="profile-item">
                  <div class="profile-item__icon"><Hash :size="15" /></div>
                  <div class="profile-item__content">
                    <span class="profile-item__label">CURP</span>
                    <span class="profile-item__value profile-item__value--mono">{{ authStore.user?.curp || '—' }}</span>
                  </div>
                </div>
                <div class="profile-item">
                  <div class="profile-item__icon"><Mail :size="15" /></div>
                  <div class="profile-item__content">
                    <span class="profile-item__label">Correo electrónico</span>
                    <span class="profile-item__value">{{ authStore.user?.email || '—' }}</span>
                  </div>
                </div>
                <div class="profile-item">
                  <div class="profile-item__icon"><Phone :size="15" /></div>
                  <div class="profile-item__content">
                    <span class="profile-item__label">Teléfono</span>
                    <span class="profile-item__value">{{ authStore.user?.telefono || '—' }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="profile-card">
              <div class="profile-card__header">
                <div class="profile-card__icon-wrap">
                  <MapPin :size="18" />
                </div>
                <h3 class="profile-card__title">Ubicación</h3>
              </div>

              <div class="profile-grid">
                <div class="profile-item">
                  <div class="profile-item__icon"><MapPin :size="15" /></div>
                  <div class="profile-item__content">
                    <span class="profile-item__label">Estado</span>
                    <span class="profile-item__value">{{ estadoNombre }}</span>
                  </div>
                </div>
                <div class="profile-item">
                  <div class="profile-item__icon"><Building2 :size="15" /></div>
                  <div class="profile-item__content">
                    <span class="profile-item__label">Municipio</span>
                    <span class="profile-item__value">{{ municipioNombre }}</span>
                  </div>
                </div>
                <div class="profile-item">
                  <div class="profile-item__icon"><Home :size="15" /></div>
                  <div class="profile-item__content">
                    <span class="profile-item__label">Localidad</span>
                    <span class="profile-item__value">{{ authStore.user?.localidad || '—' }}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- ── EDIT MODE ── -->
          <div v-else key="edit" class="profile-body">
            <form class="profile-form" @submit.prevent="saveProfile" novalidate>

              <div class="profile-card">
                <div class="profile-card__header">
                  <div class="profile-card__icon-wrap">
                    <UserIcon :size="18" />
                  </div>
                  <h3 class="profile-card__title">Datos personales</h3>
                </div>

                <div class="form-fields">
                  <div class="form-field" :class="{ 'form-field--error': errors.name }">
                    <label class="form-field__label">Nombre completo</label>
                    <div class="form-field__input">
                      <UserIcon :size="17" class="form-field__icon" />
                      <input
                        v-model="form.name" type="text"
                        placeholder="NOMBRE Y APELLIDO"
                        @input="form.name = toUpperNoTilde(form.name)"
                      />
                    </div>
                    <span v-if="errors.name" class="form-field__error">{{ errors.name }}</span>
                  </div>

                  <div class="form-field" :class="{ 'form-field--error': errors.curp }">
                    <label class="form-field__label">CURP</label>
                    <div class="form-field__input">
                      <Hash :size="17" class="form-field__icon" />
                      <input
                        v-model="form.curp" type="text"
                        placeholder="18 caracteres" maxlength="18"
                        @input="form.curp = form.curp.toUpperCase().replace(/[^A-Z0-9]/g, '')"
                      />
                      <span class="form-field__counter" :class="{ 'form-field__counter--ok': form.curp.length === 18 }">
                        {{ form.curp.length }}/18
                      </span>
                    </div>
                    <span v-if="errors.curp" class="form-field__error">{{ errors.curp }}</span>
                  </div>

                  <div class="form-field">
                    <label class="form-field__label">Teléfono <span class="form-field__opt">opcional</span></label>
                    <div class="form-field__input">
                      <Phone :size="17" class="form-field__icon" />
                      <input
                        v-model="form.telefono" type="tel"
                        placeholder="10 dígitos" maxlength="10"
                        @input="form.telefono = form.telefono.replace(/[^0-9]/g, '')"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="profile-card">
                <div class="profile-card__header">
                  <div class="profile-card__icon-wrap">
                    <MapPin :size="18" />
                  </div>
                  <h3 class="profile-card__title">Ubicación</h3>
                </div>

                <div class="form-fields">
                  <div class="form-field" :class="{ 'form-field--error': errors.estado }">
                    <label class="form-field__label">Estado</label>
                    <div class="form-field__input">
                      <MapPin :size="17" class="form-field__icon" />
                      <select v-model="form.estado" @change="onEstadoChange">
                        <option value="" disabled>Selecciona estado</option>
                        <option v-for="e in estados" :key="e.cve_ent" :value="e.cve_ent">{{ e.nom_ent }}</option>
                      </select>
                    </div>
                    <span v-if="errors.estado" class="form-field__error">{{ errors.estado }}</span>
                  </div>

                  <div class="form-field" :class="{ 'form-field--error': errors.municipio }">
                    <label class="form-field__label">Municipio</label>
                    <div class="form-field__input" :class="{ 'form-field__input--disabled': !form.estado }">
                      <Building2 :size="17" class="form-field__icon" />
                      <select v-model="form.municipio" :disabled="!form.estado || loadingMunicipios">
                        <option :value="0" disabled>
                          {{ loadingMunicipios ? 'Cargando...' : !form.estado ? 'Primero elige estado' : 'Selecciona municipio' }}
                        </option>
                        <option v-for="m in municipios" :key="m.clave_mun" :value="m.clave_mun">{{ m.nomgeo }}</option>
                      </select>
                      <Loader2 v-if="loadingMunicipios" :size="16" class="form-field__spin" />
                    </div>
                    <span v-if="errors.municipio" class="form-field__error">{{ errors.municipio }}</span>
                  </div>

                  <div class="form-field">
                    <label class="form-field__label">Localidad <span class="form-field__opt">opcional</span></label>
                    <div class="form-field__input">
                      <Home :size="17" class="form-field__icon" />
                      <input
                        v-model="form.localidad" type="text"
                        placeholder="Tu comunidad o colonia"
                        @input="form.localidad = toUpperNoTilde(form.localidad)"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <Transition name="slide-error">
                <div v-if="serverError" class="form-error-banner">
                  <AlertCircle :size="18" />
                  <span>{{ serverError }}</span>
                </div>
              </Transition>

              <button type="submit" class="btn-save" :disabled="authStore.loading || !canSave">
                <Loader2 v-if="authStore.loading" :size="20" class="spin" />
                <Save v-else :size="20" />
                <span>{{ authStore.loading ? 'Guardando...' : 'Guardar cambios' }}</span>
              </button>

            </form>
          </div>
        </Transition>

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
  Pencil, X, User as UserIcon, MapPin, Hash, Phone,
  Home, Mail, Save, Loader2, AlertCircle, Salad,
  Building2, Calendar
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

const form = reactive({ name: '', curp: '', estado: '', municipio: 0, localidad: '', telefono: '' })
const errors = reactive<Record<string, string>>({ name: '', curp: '', estado: '', municipio: '' })

const initials = computed(() => {
  const name = authStore.user?.name || 'U'
  return name.split(' ').map((w: string) => w[0]).join('').toUpperCase().slice(0, 2)
})

const estadoNombre = computed(() => {
  if (!authStore.user?.estado) return 'Sin estado'
  return estados.value.find(x => x.cve_ent === authStore.user!.estado)?.nom_ent || authStore.user.estado
})

const municipioNombre = computed(() => {
  if (!authStore.user?.municipio) return 'Sin municipio'
  return municipios.value.find(x => x.clave_mun === authStore.user!.municipio)?.nomgeo || String(authStore.user.municipio)
})

const memberSince = computed(() => {
  if (!authStore.user?.createdAt) return 'Nuevo'
  return new Date(authStore.user.createdAt).toLocaleDateString('es-MX', { month: 'short', year: 'numeric' })
})

const canSave = computed(() =>
  form.name.trim().length >= 2 &&
  form.curp.trim().length === 18 &&
  !!form.estado &&
  !!form.municipio
)

function closeSidebar() { if (ui.sidebarOpen) ui.closeSidebar() }

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

function cancelEdit() { editing.value = false }

async function loadMunicipios(estado: string) {
  loadingMunicipios.value = true
  try { municipios.value = await catalogoService.getMunicipios(estado) } catch { /* silent */ }
  loadingMunicipios.value = false
}

async function onEstadoChange() {
  form.municipio = 0
  municipios.value = []
  if (form.estado) await loadMunicipios(form.estado)
}

function validate(): boolean {
  let v = true
  Object.keys(errors).forEach(k => errors[k] = '')
  if (form.name.trim().length < 2) { errors.name = 'Mínimo 2 caracteres'; v = false }
  if (form.curp.trim().length !== 18) { errors.curp = 'Debe tener exactamente 18 caracteres'; v = false }
  if (!form.estado) { errors.estado = 'Selecciona un estado'; v = false }
  if (!form.municipio) { errors.municipio = 'Selecciona un municipio'; v = false }
  return v
}

async function saveProfile() {
  serverError.value = ''
  if (!validate()) return
  try {
    await authStore.updateProfile({
      name: form.name, curp: form.curp, tipo_capturista: 'CAPTURISTA',
      estado: form.estado, municipio: form.municipio,
      localidad: form.localidad || null, telefono: form.telefono || null,
    })
    editing.value = false
    ui.showToast('Perfil actualizado correctamente', 'success')
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    serverError.value = e.response?.data?.detail || 'Error al guardar'
  }
}

onMounted(async () => {
  setTimeout(() => { mounted.value = true }, 50)
  try {
    estados.value = await catalogoService.getEstados()
    if (authStore.user?.estado) await loadMunicipios(authStore.user.estado)
  } catch { /* silent */ }
})
</script>

<style scoped>
/* ── PAGE ── */
.profile-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 0 0 2rem;
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.profile-page--visible { opacity: 1; transform: none; }

/* ── HERO ── */
.profile-hero {
  position: relative;
  background: linear-gradient(135deg, #c0392b 0%, #922b21 60%, #7b241c 100%);
  border-radius: 0 0 28px 28px;
  padding: 3rem 1.5rem 2rem;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(192,57,43,0.25);
}
.profile-hero__bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(255,255,255,0.08) 0%, transparent 60%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.06) 0%, transparent 50%);
  pointer-events: none;
}
.profile-hero__content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.profile-hero__avatar {
  position: relative;
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -1px;
  border: 3px solid rgba(255,255,255,0.35);
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.profile-hero__avatar-ring {
  position: absolute;
  inset: -5px;
  border-radius: 50%;
  border: 2px dashed rgba(255,255,255,0.25);
  animation: spin-slow 20s linear infinite;
}
@keyframes spin-slow { to { transform: rotate(360deg); } }

.profile-hero__info { flex: 1; min-width: 0; }
.profile-hero__name {
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 0.2rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.profile-hero__email {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.75);
  margin: 0 0 0.6rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.profile-hero__badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(255,255,255,0.18);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.25);
  color: #fff;
  font-size: 0.73rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 100px;
  letter-spacing: 0.3px;
}
.profile-hero__actions {
  position: relative;
  display: flex;
  justify-content: flex-end;
  margin-top: 1.25rem;
}
.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 100px;
  font-size: 0.82rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.hero-btn--edit {
  background: rgba(255,255,255,0.95);
  color: #c0392b;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.hero-btn--edit:hover { background: #fff; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,0.2); }
.hero-btn--cancel {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.35);
}
.hero-btn--cancel:hover { background: rgba(255,255,255,0.25); }

/* ── STATS BAR ── */
.profile-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  background: #fff;
  border-radius: 16px;
  margin: 1rem 1rem 0;
  padding: 0.75rem 0.5rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
}
.profile-stats__item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 500;
  min-width: 0;
  padding: 0 4px;
}
.profile-stats__item svg { color: #c0392b; flex-shrink: 0; }
.profile-stats__item span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.profile-stats__divider { width: 1px; height: 24px; background: #e2e8f0; flex-shrink: 0; }

/* ── BODY ── */
.profile-body { padding: 1rem 1rem 0; display: flex; flex-direction: column; gap: 1rem; }

/* ── CARDS ── */
.profile-card {
  background: #fff;
  border-radius: 18px;
  padding: 1.25rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
  border: 1px solid rgba(0,0,0,0.04);
}
.profile-card__header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.1rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
}
.profile-card__icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #fff0ef, #ffe4e1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0392b;
  flex-shrink: 0;
}
.profile-card__title { font-size: 0.9rem; font-weight: 700; color: #1e293b; margin: 0; }

/* ── PROFILE GRID (view mode) ── */
.profile-grid { display: flex; flex-direction: column; gap: 0; }
.profile-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.65rem 0;
  border-bottom: 1px solid #f8fafc;
}
.profile-item:last-child { border-bottom: none; padding-bottom: 0; }
.profile-item__icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  flex-shrink: 0;
  margin-top: 1px;
}
.profile-item__content { flex: 1; min-width: 0; }
.profile-item__label { display: block; font-size: 0.72rem; color: #94a3b8; font-weight: 500; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.4px; }
.profile-item__value { display: block; font-size: 0.88rem; color: #1e293b; font-weight: 500; word-break: break-word; }
.profile-item__value--mono { font-family: 'Courier New', monospace; font-size: 0.82rem; letter-spacing: 0.5px; color: #374151; }

/* ── FORM FIELDS (edit mode) ── */
.form-fields { display: flex; flex-direction: column; gap: 0.85rem; }
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field__label { font-size: 0.78rem; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 5px; }
.form-field__opt { font-weight: 400; color: #94a3b8; font-size: 0.72rem; }
.form-field__input {
  position: relative;
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 0 12px 0 38px;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 44px;
}
.form-field__input:focus-within {
  border-color: #c0392b;
  box-shadow: 0 0 0 3px rgba(192,57,43,0.1);
  background: #fff;
}
.form-field__input--disabled { opacity: 0.55; pointer-events: none; }
.form-field__icon {
  position: absolute;
  left: 11px;
  color: #94a3b8;
  pointer-events: none;
}
.form-field__input input,
.form-field__input select {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 0.88rem;
  color: #1e293b;
  outline: none;
  padding: 0;
  min-width: 0;
  height: 44px;
  appearance: none;
  font-family: inherit;
}
.form-field__input input::placeholder { color: #cbd5e1; }
.form-field__counter {
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 600;
  white-space: nowrap;
  padding-left: 6px;
}
.form-field__counter--ok { color: #16a34a; }
.form-field__spin { color: #c0392b; animation: spin 1s linear infinite; margin-left: 4px; }
.form-field__error { font-size: 0.75rem; color: #dc2626; font-weight: 500; padding-left: 4px; }
.form-field--error .form-field__input { border-color: #dc2626; box-shadow: 0 0 0 3px rgba(220,38,38,0.08); }

/* ── ERROR BANNER ── */
.form-error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  color: #dc2626;
  font-size: 0.85rem;
  font-weight: 500;
}

/* ── SAVE BUTTON ── */
.btn-save {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 0.9rem;
  background: linear-gradient(135deg, #c0392b, #e74c3c);
  color: #fff;
  border: none;
  border-radius: 14px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(192,57,43,0.35);
  transition: all 0.2s;
  letter-spacing: 0.3px;
}
.btn-save:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(192,57,43,0.4); }
.btn-save:active:not(:disabled) { transform: translateY(0); }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── ANIMATIONS ── */
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; }

.profile-fade-enter-active,
.profile-fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.profile-fade-enter-from { opacity: 0; transform: translateY(6px); }
.profile-fade-leave-to { opacity: 0; transform: translateY(-6px); }

.slide-error-enter-active,
.slide-error-leave-active { transition: all 0.2s ease; }
.slide-error-enter-from,
.slide-error-leave-to { opacity: 0; transform: translateY(-4px); }

/* ── RESPONSIVE ── */
@media (min-width: 480px) {
  .profile-hero { padding: 3.5rem 2rem 2rem; }
  .profile-hero__avatar { width: 90px; height: 90px; font-size: 2rem; }
  .profile-hero__name { font-size: 1.3rem; }
  .profile-body { padding: 1.25rem 1.25rem 0; }
  .profile-stats { margin: 1.25rem 1.25rem 0; }
}

@media (min-width: 600px) {
  .profile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
  .profile-item { border-bottom: 1px solid #f8fafc; }
  .profile-item:nth-last-child(-n+2) { border-bottom: none; }
}
</style>
