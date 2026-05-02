<template>
  <div class="auth-page">
    <div class="auth-card auth-card--wide">
      <div class="auth-header">
        <div class="auth-logo">
          <UserPlus :size="40" />
        </div>
        <h1>Crear cuenta</h1>
        <p>Completa tus datos para registrarte</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <!-- Nombre -->
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Nombre(s) *</label>
            <input
              v-model="form.nombre"
              type="text"
              class="form-input"
              :class="{ error: errors.nombre }"
              placeholder="JUAN CARLOS"
              maxlength="100"
              @input="form.nombre = toUpper(form.nombre)"
              required
            />
            <p v-if="errors.nombre" class="form-error">{{ errors.nombre }}</p>
          </div>
        </div>

        <div class="form-row form-row--2">
          <div class="form-group">
            <label class="form-label">Apellido paterno *</label>
            <input
              v-model="form.apellido_paterno"
              type="text"
              class="form-input"
              :class="{ error: errors.apellido_paterno }"
              placeholder="GARCIA"
              maxlength="100"
              @input="form.apellido_paterno = toUpper(form.apellido_paterno)"
              required
            />
            <p v-if="errors.apellido_paterno" class="form-error">{{ errors.apellido_paterno }}</p>
          </div>

          <div class="form-group">
            <label class="form-label">Apellido materno *</label>
            <input
              v-model="form.apellido_materno"
              type="text"
              class="form-input"
              :class="{ error: errors.apellido_materno }"
              placeholder="LOPEZ"
              maxlength="100"
              @input="form.apellido_materno = toUpper(form.apellido_materno)"
              required
            />
            <p v-if="errors.apellido_materno" class="form-error">{{ errors.apellido_materno }}</p>
          </div>
        </div>

        <!-- CURP -->
        <div class="form-group">
          <label class="form-label">CURP *</label>
          <input
            v-model="form.curp"
            type="text"
            class="form-input"
            :class="{ error: errors.curp }"
            placeholder="XXXX000000XXXXXX00"
            maxlength="18"
            @input="form.curp = toUpperCurp(form.curp)"
            required
          />
          <p class="form-hint">18 caracteres, se convertirá automáticamente a mayúsculas</p>
          <p v-if="errors.curp" class="form-error">{{ errors.curp }}</p>
        </div>

        <div class="form-row form-row--2">
          <!-- Correo -->
          <div class="form-group">
            <label class="form-label">Correo electrónico *</label>
            <input
              v-model="form.correo"
              type="email"
              class="form-input"
              :class="{ error: errors.correo }"
              placeholder="correo@ejemplo.com"
              required
            />
            <p v-if="errors.correo" class="form-error">{{ errors.correo }}</p>
          </div>

          <!-- Teléfono -->
          <div class="form-group">
            <label class="form-label">Teléfono *</label>
            <input
              v-model="form.telefono"
              type="tel"
              class="form-input"
              :class="{ error: errors.telefono }"
              placeholder="5512345678"
              maxlength="10"
              @input="form.telefono = onlyNumbers(form.telefono)"
              required
            />
            <p class="form-hint">10 dígitos sin espacios ni guiones</p>
            <p v-if="errors.telefono" class="form-error">{{ errors.telefono }}</p>
          </div>
        </div>

        <!-- Rol -->
        <div class="form-group">
          <label class="form-label">Tipo de usuario *</label>
          <select
            v-model="form.rol"
            class="form-input"
            required
          >
            <option value="usuario">Usuario</option>
            <option value="administrador">Administrador</option>
          </select>
        </div>

        <!-- Contraseña -->
        <div class="form-group">
          <label class="form-label">Contraseña *</label>
          <div class="input-icon">
            <Lock :size="18" />
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ error: errors.password }"
              placeholder="Mínimo 6 caracteres"
              required
            />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <Eye v-if="!showPassword" :size="18" />
              <EyeOff v-else :size="18" />
            </button>
          </div>
          <p v-if="errors.password" class="form-error">{{ errors.password }}</p>
        </div>

        <!-- Confirmar contraseña -->
        <div class="form-group">
          <label class="form-label">Confirmar contraseña *</label>
          <div class="input-icon">
            <Lock :size="18" />
            <input
              v-model="form.confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ error: errors.confirmPassword }"
              placeholder="Repite tu contraseña"
              required
            />
          </div>
          <p v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</p>
        </div>

        <p v-if="generalError" class="form-error text-center mb-2">{{ generalError }}</p>

        <button type="submit" class="btn btn--primary btn--full" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Crear cuenta</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>¿Ya tienes cuenta? <router-link to="/login">Inicia sesión</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserPlus, Lock, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  nombre: '',
  apellido_paterno: '',
  apellido_materno: '',
  curp: '',
  correo: '',
  telefono: '',
  password: '',
  confirmPassword: '',
  rol: 'usuario' as 'usuario' | 'administrador'
})

const errors = reactive({
  nombre: '',
  apellido_paterno: '',
  apellido_materno: '',
  curp: '',
  correo: '',
  telefono: '',
  password: '',
  confirmPassword: ''
})

const generalError = ref('')
const loading = ref(false)
const showPassword = ref(false)

onMounted(async () => {
  await auth.init()
  if (auth.isAuthenticated) {
    router.push('/')
  }
})

// Helpers
function toUpper(v: string): string {
  return v
    .toUpperCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

function toUpperCurp(v: string): string {
  return v.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 18)
}

function onlyNumbers(v: string): string {
  return v.replace(/\D/g, '').slice(0, 10)
}

function validateCurp(curp: string): boolean {
  const regex = /^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$/
  return regex.test(curp)
}

async function handleSubmit() {
  // Reset errors
  Object.keys(errors).forEach(k => (errors as any)[k] = '')
  generalError.value = ''

  let hasErrors = false

  // Validate fields
  if (form.nombre.trim().length < 2) {
    errors.nombre = 'El nombre debe tener al menos 2 caracteres'
    hasErrors = true
  }

  if (form.apellido_paterno.trim().length < 2) {
    errors.apellido_paterno = 'El apellido paterno debe tener al menos 2 caracteres'
    hasErrors = true
  }

  if (form.apellido_materno.trim().length < 2) {
    errors.apellido_materno = 'El apellido materno debe tener al menos 2 caracteres'
    hasErrors = true
  }

  if (form.curp.length !== 18) {
    errors.curp = 'La CURP debe tener exactamente 18 caracteres'
    hasErrors = true
  } else if (!validateCurp(form.curp)) {
    errors.curp = 'Formato de CURP inválido'
    hasErrors = true
  }

  if (!form.correo.includes('@')) {
    errors.correo = 'Correo electrónico inválido'
    hasErrors = true
  }

  if (form.telefono.length !== 10) {
    errors.telefono = 'El teléfono debe tener exactamente 10 dígitos'
    hasErrors = true
  }

  if (form.password.length < 6) {
    errors.password = 'La contraseña debe tener al menos 6 caracteres'
    hasErrors = true
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Las contraseñas no coinciden'
    hasErrors = true
  }

  if (hasErrors) return

  loading.value = true
  try {
    await auth.register({
      nombre: form.nombre,
      apellido_paterno: form.apellido_paterno,
      apellido_materno: form.apellido_materno,
      curp: form.curp,
      correo: form.correo,
      telefono: form.telefono,
      password: form.password,
      rol: form.rol
    })
    router.push('/')
  } catch (e: any) {
    const msg = e.response?.data?.detail || 'Error al crear cuenta'
    generalError.value = msg
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(27, 94, 32, 0.12);
}

.auth-card--wide {
  max-width: 520px;
}

.auth-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.auth-logo {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: #fff;
}

.auth-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1B5E20;
  margin: 0 0 0.35rem;
}

.auth-header p {
  color: #757575;
  font-size: 0.95rem;
}

.auth-form {
  margin-bottom: 1.5rem;
}

.form-row {
  margin-bottom: 1rem;
}

.form-row--2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 520px) {
  .form-row--2 {
    grid-template-columns: 1fr;
  }
}

.input-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon > svg:first-child {
  position: absolute;
  left: 1rem;
  color: #9e9e9e;
  pointer-events: none;
}

.input-icon .form-input {
  padding-left: 2.75rem;
  padding-right: 2.75rem;
}

.toggle-password {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  color: #9e9e9e;
  cursor: pointer;
  padding: 0;
  display: flex;
}

.toggle-password:hover {
  color: #1B5E20;
}

.auth-footer {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.auth-footer p {
  color: #757575;
  font-size: 0.9rem;
}

.auth-footer a {
  color: #1B5E20;
  font-weight: 600;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
