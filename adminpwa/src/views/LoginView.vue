<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <Shield :size="40" />
        </div>
        <h1>Admin COSTOS</h1>
        <p>Inicia sesión para continuar</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label class="form-label">Correo electrónico</label>
          <div class="input-icon">
            <Mail :size="18" />
            <input
              v-model="form.correo"
              type="email"
              class="form-input"
              :class="{ error: errors.correo }"
              placeholder="correo@ejemplo.com"
              required
            />
          </div>
          <p v-if="errors.correo" class="form-error">{{ errors.correo }}</p>
        </div>

        <div class="form-group">
          <label class="form-label">Contraseña</label>
          <div class="input-icon">
            <Lock :size="18" />
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ error: errors.password }"
              placeholder="••••••••"
              required
            />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <Eye v-if="!showPassword" :size="18" />
              <EyeOff v-else :size="18" />
            </button>
          </div>
          <p v-if="errors.password" class="form-error">{{ errors.password }}</p>
        </div>

        <p v-if="generalError" class="form-error text-center mb-2">{{ generalError }}</p>

        <button type="submit" class="btn btn--primary btn--full" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Iniciar sesión</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>¿No tienes cuenta? <router-link to="/register">Regístrate</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Shield, Mail, Lock, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  correo: '',
  password: ''
})

const errors = reactive({
  correo: '',
  password: ''
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

async function handleSubmit() {
  // Reset errors
  errors.correo = ''
  errors.password = ''
  generalError.value = ''

  // Validate
  if (!form.correo.trim()) {
    errors.correo = 'El correo es obligatorio'
    return
  }
  if (!form.password) {
    errors.password = 'La contraseña es obligatoria'
    return
  }

  loading.value = true
  try {
    await auth.login(form.correo, form.password)
    router.push('/')
  } catch (e: any) {
    const msg = e.response?.data?.detail || 'Error al iniciar sesión'
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

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
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
