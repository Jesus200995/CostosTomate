<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="auth-bg-shape auth-bg-shape--1"></div>
      <div class="auth-bg-shape auth-bg-shape--2"></div>
      <div class="auth-bg-shape auth-bg-shape--3"></div>
    </div>

    <div class="auth-container auth-container--register" :class="{ 'auth-container--visible': mounted }">
      <div class="auth-logo">
        <div class="auth-logo__icon">
          <UserPlus :size="32" />
        </div>
        <h1 class="auth-logo__title">Crear Cuenta</h1>
        <p class="auth-logo__subtitle">Únete a COSTOS</p>
      </div>

      <!-- Step indicator -->
      <div class="step-indicator">
        <div v-for="s in totalSteps" :key="s" class="step-dot" :class="{ 'step-dot--active': s === step, 'step-dot--done': s < step }"></div>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister" novalidate>

        <!-- PASO 1: Credenciales -->
        <Transition name="step-slide" mode="out-in">
          <div v-if="step === 1" key="step1" class="step-content">
            <h3 class="step-title">Credenciales de acceso</h3>

            <div class="form-group" :class="{ 'form-group--error': errors.email, 'form-group--focus': focused === 'email' }">
              <div class="form-input-wrapper">
                <Mail :size="20" class="form-icon" />
                <input v-model="form.email" type="email" placeholder="Correo electrónico" autocomplete="email" @focus="focused = 'email'" @blur="focused = ''" />
              </div>
              <Transition name="slide-error"><span v-if="errors.email" class="form-error">{{ errors.email }}</span></Transition>
            </div>

            <div class="form-group" :class="{ 'form-group--error': errors.password, 'form-group--focus': focused === 'password' }">
              <div class="form-input-wrapper">
                <Lock :size="20" class="form-icon" />
                <input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="Contraseña" autocomplete="new-password" @focus="focused = 'password'" @blur="focused = ''" />
                <button type="button" class="form-toggle-pass" @click="showPassword = !showPassword" tabindex="-1">
                  <EyeOff v-if="showPassword" :size="20" /><Eye v-else :size="20" />
                </button>
              </div>
              <Transition name="slide-error"><span v-if="errors.password" class="form-error">{{ errors.password }}</span></Transition>
            </div>

            <div class="form-group" :class="{ 'form-group--error': errors.confirmPassword, 'form-group--focus': focused === 'confirm' }">
              <div class="form-input-wrapper">
                <ShieldCheck :size="20" class="form-icon" />
                <input v-model="form.confirmPassword" :type="showConfirm ? 'text' : 'password'" placeholder="Confirmar contraseña" autocomplete="new-password" @focus="focused = 'confirm'" @blur="focused = ''" />
                <button type="button" class="form-toggle-pass" @click="showConfirm = !showConfirm" tabindex="-1">
                  <EyeOff v-if="showConfirm" :size="20" /><Eye v-else :size="20" />
                </button>
              </div>
              <Transition name="slide-error"><span v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</span></Transition>
            </div>

            <div v-if="form.password" class="password-strength">
              <div class="password-strength__bar">
                <div class="password-strength__fill" :style="{ width: strengthPercent + '%' }" :class="'password-strength__fill--' + strengthLevel"></div>
              </div>
              <span class="password-strength__label" :class="'password-strength__label--' + strengthLevel">{{ strengthText }}</span>
            </div>

            <button type="button" class="btn btn--primary btn--full" @click="nextStep">
              Siguiente <ChevronRight :size="20" />
            </button>
          </div>
        </Transition>

        <!-- PASO 2: Perfil común -->
        <Transition name="step-slide" mode="out-in">
          <div v-if="step === 2" key="step2" class="step-content">
            <h3 class="step-title">Datos de perfil</h3>

            <div class="form-group" :class="{ 'form-group--error': errors.tipo_capturista, 'form-group--focus': focused === 'tipo' }">
              <label class="form-label">Tipo de capturista</label>
              <div class="form-input-wrapper">
                <Briefcase :size="20" class="form-icon" />
                <select v-model="form.tipo_capturista" @focus="focused = 'tipo'" @blur="focused = ''">
                  <option value="" disabled>Selecciona tu tipo</option>
                  <option value="REPRESENTANTE_CAC">Representante CAC</option>
                  <option value="COM_COMERCIALIZACION">Miembro de comisión de comercialización</option>
                  <option value="OFICINAS">Personal de oficinas central</option>
                </select>
              </div>
              <Transition name="slide-error"><span v-if="errors.tipo_capturista" class="form-error">{{ errors.tipo_capturista }}</span></Transition>
            </div>

            <div class="form-group" :class="{ 'form-group--error': errors.name, 'form-group--focus': focused === 'name' }">
              <label class="form-label">Nombre completo</label>
              <div class="form-input-wrapper">
                <User :size="20" class="form-icon" />
                <input v-model="form.name" type="text" placeholder="Nombre y apellido" autocomplete="name" style="text-transform: uppercase" @input="form.name = toUpperNoTilde(form.name)" @focus="focused = 'name'" @blur="focused = ''" />
              </div>
              <Transition name="slide-error"><span v-if="errors.name" class="form-error">{{ errors.name }}</span></Transition>
            </div>

            <div class="form-group" :class="{ 'form-group--error': errors.curp, 'form-group--focus': focused === 'curp' }">
              <label class="form-label">CURP</label>
              <div class="form-input-wrapper">
                <Hash :size="20" class="form-icon" />
                <input v-model="form.curp" type="text" placeholder="CURP (18 caracteres)" maxlength="18" style="text-transform: uppercase" @input="form.curp = form.curp.toUpperCase().replace(/[^A-Z0-9]/g, '')" @focus="focused = 'curp'" @blur="focused = ''" />
              </div>
              <Transition name="slide-error"><span v-if="errors.curp" class="form-error">{{ errors.curp }}</span></Transition>
            </div>

            <div class="form-group" :class="{ 'form-group--error': errors.estado, 'form-group--focus': focused === 'estado' }">
              <label class="form-label">Estado</label>
              <div class="form-input-wrapper">
                <MapPin :size="20" class="form-icon" />
                <select v-model="form.estado" @change="onEstadoChange" @focus="focused = 'estado'" @blur="focused = ''">
                  <option value="" disabled>Selecciona estado</option>
                  <option v-for="e in estados" :key="e.cve_ent" :value="e.cve_ent">{{ e.nom_ent }}</option>
                </select>
              </div>
              <Transition name="slide-error"><span v-if="errors.estado" class="form-error">{{ errors.estado }}</span></Transition>
            </div>

            <div class="form-group" :class="{ 'form-group--error': errors.municipio, 'form-group--focus': focused === 'municipio' }">
              <label class="form-label">Municipio</label>
              <div class="form-input-wrapper">
                <MapPin :size="20" class="form-icon" />
                <select v-model="form.municipio" :disabled="!form.estado || loadingMunicipios" @change="onMunicipioChange" @focus="focused = 'municipio'" @blur="focused = ''">
                  <option :value="0" disabled>{{ loadingMunicipios ? 'Cargando...' : 'Selecciona municipio' }}</option>
                  <option v-for="m in municipios" :key="m.clave_mun" :value="m.clave_mun">{{ m.nomgeo }}</option>
                </select>
              </div>
              <Transition name="slide-error"><span v-if="errors.municipio" class="form-error">{{ errors.municipio }}</span></Transition>
            </div>

            <div class="form-group" :class="{ 'form-group--focus': focused === 'localidad' }">
              <label class="form-label">Localidad / Comunidad <span class="form-optional">(opcional)</span></label>
              <div class="form-input-wrapper">
                <Home :size="20" class="form-icon" />
                <input v-model="form.localidad" type="text" placeholder="Localidad" style="text-transform: uppercase" @input="form.localidad = toUpperNoTilde(form.localidad)" @focus="focused = 'localidad'" @blur="focused = ''" />
              </div>
            </div>

            <div class="form-group" :class="{ 'form-group--focus': focused === 'telefono' }">
              <label class="form-label">Teléfono <span class="form-optional">(opcional)</span></label>
              <div class="form-input-wrapper">
                <Phone :size="20" class="form-icon" />
                <input v-model="form.telefono" type="tel" placeholder="Ej. 7710000000" maxlength="10" @input="form.telefono = form.telefono.replace(/[^0-9]/g, '')" @focus="focused = 'telefono'" @blur="focused = ''" />
              </div>
            </div>

            <div class="step-nav">
              <button type="button" class="btn btn--outline" @click="step = 1">
                <ChevronLeft :size="20" /> Anterior
              </button>
              <button type="button" class="btn btn--primary" @click="nextStep">
                Siguiente <ChevronRight :size="20" />
              </button>
            </div>
          </div>
        </Transition>

        <!-- PASO 3: Campos por rol + consent -->
        <Transition name="step-slide" mode="out-in">
          <div v-if="step === 3" key="step3" class="step-content">

            <template v-if="form.tipo_capturista === 'REPRESENTANTE_CAC' || form.tipo_capturista === 'COM_COMERCIALIZACION'">
              <h3 class="step-title">{{ form.tipo_capturista === 'REPRESENTANTE_CAC' ? 'Datos de CAC' : 'Comisión de comercialización' }}</h3>

              <div class="form-group" :class="{ 'form-group--error': errors.cac_id, 'form-group--focus': focused === 'cac_id' }">
                <label class="form-label">CAC ID</label>
                <div class="form-input-wrapper">
                  <Hash :size="20" class="form-icon" />
                  <input v-model="form.cac_id" type="text" placeholder="CAC_123" @focus="focused = 'cac_id'" @blur="focused = ''" />
                </div>
                <Transition name="slide-error"><span v-if="errors.cac_id" class="form-error">{{ errors.cac_id }}</span></Transition>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.cac_nombre, 'form-group--focus': focused === 'cac_nombre' }">
                <label class="form-label">Nombre del CAC</label>
                <div class="form-input-wrapper">
                  <Building :size="20" class="form-icon" />
                  <input v-model="form.cac_nombre" type="text" placeholder="CAC SEMILLAS DEL FUTURO" style="text-transform: uppercase" @input="form.cac_nombre = toUpperNoTilde(form.cac_nombre)" @focus="focused = 'cac_nombre'" @blur="focused = ''" />
                </div>
                <Transition name="slide-error"><span v-if="errors.cac_nombre" class="form-error">{{ errors.cac_nombre }}</span></Transition>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.territorio, 'form-group--focus': focused === 'territorio' }">
                <label class="form-label">Territorio <span v-if="territorioFromCatalog" class="form-auto-tag">Automático</span></label>
                <div class="form-input-wrapper" :class="{ 'form-input-wrapper--readonly': territorioFromCatalog }">
                  <MapIcon :size="20" class="form-icon" />
                  <select v-model="form.territorio" :disabled="territorioFromCatalog" @focus="focused = 'territorio'" @blur="focused = ''">
                    <option value="">Selecciona territorio</option>
                    <option v-for="t in territorioOptions" :key="t" :value="t">{{ t }}</option>
                  </select>
                </div>
                <Transition name="slide-error"><span v-if="errors.territorio" class="form-error">{{ errors.territorio }}</span></Transition>
              </div>

              <div class="form-group" :class="{ 'form-group--error': errors.ruta, 'form-group--focus': focused === 'ruta' }">
                <label class="form-label">Ruta</label>
                <div class="form-input-wrapper">
                  <MapIcon :size="20" class="form-icon" />
                  <input v-model="form.ruta" type="text" placeholder="Ruta 05 / Nombre ruta" style="text-transform: uppercase" @input="form.ruta = toUpperNoTilde(form.ruta)" @focus="focused = 'ruta'" @blur="focused = ''" />
                </div>
                <Transition name="slide-error"><span v-if="errors.ruta" class="form-error">{{ errors.ruta }}</span></Transition>
              </div>
            </template>

            <template v-if="form.tipo_capturista === 'OFICINAS'">
              <h3 class="step-title">Datos de oficinas</h3>

              <div class="form-group" :class="{ 'form-group--focus': focused === 'correo_inst' }">
                <label class="form-label">Correo institucional <span class="form-optional">(recomendado)</span></label>
                <div class="form-input-wrapper">
                  <Mail :size="20" class="form-icon" />
                  <input v-model="form.correo_institucional" type="email" placeholder="nombre@bienestar.gob.mx" @focus="focused = 'correo_inst'" @blur="focused = ''" />
                </div>
              </div>

              <div class="form-group" :class="{ 'form-group--focus': focused === 'rol_interno' }">
                <label class="form-label">Rol interno <span class="form-optional">(opcional)</span></label>
                <div class="form-input-wrapper">
                  <Briefcase :size="20" class="form-icon" />
                  <select v-model="rolInternoSelect" @focus="focused = 'rol_interno'" @blur="focused = ''">
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
                  <input v-model="rolInternoOtro" type="text" placeholder="Escribe el rol" @focus="focused = 'rol_interno_otro'" @blur="focused = ''" />
                </div>
              </div>

              <div class="form-info-note">
                <Info :size="16" />
                <span>Este rol no captura precios en la PWA (solo consulta).</span>
              </div>
            </template>

            <div class="form-group form-group--consent" :class="{ 'form-group--error': errors.consent }">
              <label class="form-checkbox">
                <input type="checkbox" v-model="form.consent" />
                <span class="form-checkbox__mark"></span>
                <span class="form-checkbox__text">Acepto el aviso de privacidad y condiciones de uso</span>
              </label>
              <Transition name="slide-error"><span v-if="errors.consent" class="form-error">{{ errors.consent }}</span></Transition>
            </div>

            <Transition name="slide-error">
              <div v-if="serverError" class="form-server-error">
                <AlertCircle :size="18" />
                <span>{{ serverError }}</span>
              </div>
            </Transition>

            <div class="step-nav">
              <button type="button" class="btn btn--outline" @click="step = 2">
                <ChevronLeft :size="20" /> Anterior
              </button>
              <button type="submit" class="btn btn--primary" :disabled="authStore.loading || !canSubmit">
                <Loader2 v-if="authStore.loading" :size="20" class="spin" />
                <UserPlus v-else :size="20" />
                <span>{{ authStore.loading ? 'Creando...' : 'Registrarse' }}</span>
              </button>
            </div>
          </div>
        </Transition>
      </form>

      <div class="auth-footer">
        <p>¿Ya tienes cuenta?</p>
        <router-link to="/login" class="auth-link">
          <ArrowLeft :size="16" />
          Iniciar sesión
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { catalogoService } from '@/services/catalogo.service'
import type { Estado, Municipio } from '@/types'
import {
  UserPlus, User, Mail, Lock, ShieldCheck,
  Eye, EyeOff, ArrowLeft, Loader2, AlertCircle,
  ChevronRight, ChevronLeft, Briefcase, MapPin,
  Phone, Home, Hash, Building, Map as MapIcon, Info,
  Pencil
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const ui = useUiStore()

const mounted = ref(false)
const focused = ref('')
const showPassword = ref(false)
const showConfirm = ref(false)
const serverError = ref('')
const step = ref(1)
const totalSteps = 3

const estados = ref<Estado[]>([])
const municipios = ref<Municipio[]>([])
const loadingMunicipios = ref(false)
const territorioFromCatalog = ref(false)

// "Otro" logic
const rolInternoSelect = ref('')
const rolInternoOtro = ref('')

const territorioOptions = [
  'Acapulco - Centro - Norte - Tierra Caliente',
  'Acayucan',
  'Balancán',
  'Chihuahua / Sonora',
  'Colima',
  'Comalcalco',
  'Córdoba',
  'Costa Chica - Montaña',
  'Costa Grande - Sierra',
  'Durango / Zacatecas',
  'Hidalgo',
  'Istmo',
  'Michoacán',
  'Mixteca',
  'Morelos',
  'Nayarit / Jalisco',
  'Ocosingo',
  'Palenque',
  'Papantla',
  'Pichucalco',
  'Puebla',
  'San Luis Potosí',
  'Sinaloa',
  'Tamaulipas',
  'Tantoyuca',
  'Tapachula',
  'Teapa',
  'Tlaxcala / Estado de México',
  'Tzucacab / Opb',
  'Xpujil',
]

function toUpperNoTilde(val: string): string {
  return val
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
}

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  curp: '',
  tipo_capturista: '',
  estado: '',
  municipio: 0,
  localidad: '',
  telefono: '',
  consent: false,
  cac_id: '',
  cac_nombre: '',
  territorio: '',
  ruta: '',
  rol_comision: '',
  correo_institucional: '',
  rol_interno: ''
})

const errors = reactive<Record<string, string>>({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  curp: '',
  tipo_capturista: '',
  estado: '',
  municipio: '',
  consent: '',
  cac_id: '',
  cac_nombre: '',
  territorio: '',
  ruta: ''
})

const strengthPercent = computed(() => {
  const p = form.password
  if (!p) return 0
  let score = 0
  if (p.length >= 6) score += 25
  if (p.length >= 10) score += 15
  if (/[A-Z]/.test(p)) score += 20
  if (/[0-9]/.test(p)) score += 20
  if (/[^A-Za-z0-9]/.test(p)) score += 20
  return Math.min(score, 100)
})

const strengthLevel = computed(() => {
  if (strengthPercent.value < 30) return 'weak'
  if (strengthPercent.value < 60) return 'medium'
  if (strengthPercent.value < 85) return 'strong'
  return 'excellent'
})

const strengthText = computed(() => {
  const map: Record<string, string> = { weak: 'Débil', medium: 'Media', strong: 'Fuerte', excellent: 'Excelente' }
  return map[strengthLevel.value]
})

const canSubmit = computed(() => {
  // Common required fields
  if (!form.email.trim()) return false
  if (!form.password || form.password.length < 6) return false
  if (form.password !== form.confirmPassword) return false
  if (!form.tipo_capturista) return false
  if (!form.name.trim() || form.name.trim().length < 2) return false
  if (!form.curp.trim() || form.curp.trim().length !== 18) return false
  if (!form.estado) return false
  if (!form.municipio) return false
  if (!form.consent) return false
  // Role-specific required
  if (form.tipo_capturista === 'REPRESENTANTE_CAC' || form.tipo_capturista === 'COM_COMERCIALIZACION') {
    if (!form.cac_id.trim()) return false
    if (!form.cac_nombre.trim()) return false
    if (!form.territorio) return false
    if (!form.ruta.trim()) return false
  }
  return true
})

onMounted(async () => {
  setTimeout(() => { mounted.value = true }, 50)
  try {
    estados.value = await catalogoService.getEstados()
  } catch { /* se cargará al reintentar */ }
})

async function onEstadoChange() {
  form.municipio = 0
  form.territorio = ''
  territorioFromCatalog.value = false
  municipios.value = []
  if (!form.estado) return
  loadingMunicipios.value = true
  try {
    municipios.value = await catalogoService.getMunicipios(form.estado)
  } catch { /* silencioso */ }
  loadingMunicipios.value = false
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

function clearErrors() {
  Object.keys(errors).forEach(k => errors[k] = '')
}

function validateStep1(): boolean {
  let valid = true
  clearErrors()
  if (!form.email.trim()) { errors.email = 'El correo es obligatorio'; valid = false }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = 'Correo inválido'; valid = false }
  if (!form.password) { errors.password = 'La contraseña es obligatoria'; valid = false }
  else if (form.password.length < 6) { errors.password = 'Mínimo 6 caracteres'; valid = false }
  if (!form.confirmPassword) { errors.confirmPassword = 'Confirma tu contraseña'; valid = false }
  else if (form.password !== form.confirmPassword) { errors.confirmPassword = 'Las contraseñas no coinciden'; valid = false }
  return valid
}

function validateStep2(): boolean {
  let valid = true
  clearErrors()
  if (!form.tipo_capturista) { errors.tipo_capturista = 'Selecciona un tipo'; valid = false }
  if (!form.name.trim()) { errors.name = 'El nombre es obligatorio'; valid = false }
  else if (form.name.trim().length < 2) { errors.name = 'Mínimo 2 caracteres'; valid = false }
  if (!form.curp.trim()) { errors.curp = 'La CURP es obligatoria'; valid = false }
  else if (form.curp.trim().length !== 18) { errors.curp = 'La CURP debe tener 18 caracteres'; valid = false }
  if (!form.estado) { errors.estado = 'Selecciona un estado'; valid = false }
  if (!form.municipio) { errors.municipio = 'Selecciona un municipio'; valid = false }
  return valid
}

function validateStep3(): boolean {
  let valid = true
  clearErrors()
  if (form.tipo_capturista === 'REPRESENTANTE_CAC' || form.tipo_capturista === 'COM_COMERCIALIZACION') {
    if (!form.cac_id.trim()) { errors.cac_id = 'El CAC ID es obligatorio'; valid = false }
    if (!form.cac_nombre.trim()) { errors.cac_nombre = 'El nombre del CAC es obligatorio'; valid = false }
    if (!form.territorio) { errors.territorio = 'El territorio es obligatorio'; valid = false }
    if (!form.ruta.trim()) { errors.ruta = 'La ruta es obligatoria'; valid = false }
  }
  if (!form.consent) { errors.consent = 'Debes aceptar el aviso de privacidad'; valid = false }
  return valid
}

function nextStep() {
  if (step.value === 1 && validateStep1()) step.value = 2
  else if (step.value === 2 && validateStep2()) step.value = 3
}

async function handleRegister() {
  serverError.value = ''
  if (!validateStep3()) return

  // Compute final rol values
  form.rol_comision = ''
  form.rol_interno = rolInternoSelect.value === 'Otro'
    ? rolInternoOtro.value.trim()
    : rolInternoSelect.value

  try {
    await authStore.register(form)
    ui.showToast('¡Cuenta creada exitosamente!', 'success')
    router.push('/')
  } catch (err: unknown) {
    const error = err as { response?: { data?: { detail?: string; message?: string } } }
    serverError.value = error.response?.data?.detail || error.response?.data?.message || 'Error al registrarse'
  }
}
</script>

<style scoped>
.step-indicator {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 1.2rem;
}
.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e2e8f0;
  transition: all 0.3s ease;
}
.step-dot--active {
  background: var(--primary, #e67e00);
  transform: scale(1.3);
}
.step-dot--done {
  background: var(--accent, #16a34a);
}
.step-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  margin-bottom: 1rem;
  text-align: center;
}
.step-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.step-slide-enter-active,
.step-slide-leave-active {
  transition: all 0.3s ease;
}
.step-slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.step-slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
.step-nav {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}
.step-nav .btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.btn--outline {
  background: transparent;
  border: 2px solid var(--primary, #e67e00);
  color: var(--primary, #e67e00);
  padding: 0.7rem 1rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn--outline:hover {
  background: rgba(230, 126, 0, 0.08);
}
.form-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary, #475569);
  margin-bottom: 0.3rem;
}
.form-optional {
  font-weight: 400;
  color: #94a3b8;
  font-size: 0.76rem;
}
.form-input-wrapper select {
  width: 100%;
  background: none;
  border: none;
  outline: none;
  font-size: 0.95rem;
  color: var(--text-primary, #1e293b);
  padding: 0.35rem 0;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
}
.form-input-wrapper select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.form-input-wrapper--readonly {
  background: #f1f5f9;
  border-color: #e2e8f0 !important;
}
.form-input-wrapper--readonly input {
  color: #64748b;
  cursor: not-allowed;
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
.form-group--consent {
  margin-top: 1rem;
}
.form-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  cursor: pointer;
  font-size: 0.88rem;
  color: var(--text-secondary, #475569);
}
.form-checkbox input[type="checkbox"] {
  display: none;
}
.form-checkbox__mark {
  width: 20px;
  height: 20px;
  min-width: 20px;
  border: 2px solid #cbd5e1;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  margin-top: 1px;
}
.form-checkbox input:checked + .form-checkbox__mark {
  background: var(--accent, #16a34a);
  border-color: var(--accent, #16a34a);
}
.form-checkbox input:checked + .form-checkbox__mark::after {
  content: '\2713';
  color: white;
  font-size: 13px;
  font-weight: 700;
}
.form-checkbox__text {
  line-height: 1.3;
}
.form-info-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: #fef3c7;
  border-radius: 8px;
  font-size: 0.8rem;
  color: #92400e;
  margin-top: 0.5rem;
}
.auth-container--register {
  max-width: 420px;
}
</style>
