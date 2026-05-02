<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="auth-bg-shape auth-bg-shape--1"></div>
      <div class="auth-bg-shape auth-bg-shape--2"></div>
      <div class="auth-bg-shape auth-bg-shape--3"></div>
    </div>

    <div class="auth-container" :class="{ 'auth-container--visible': mounted }">
      <div class="auth-logo">
        <div class="auth-logo__icon">
          <Wheat :size="32" />
        </div>
        <h1 class="auth-logo__title">COSTOS</h1>
        <p class="auth-logo__subtitle">Cultivos y Productos</p>
      </div>

      <form class="auth-form" @submit.prevent="handleLogin" novalidate>
        <div class="form-group" :class="{ 'form-group--error': errors.email, 'form-group--focus': focused === 'email' }">
          <div class="form-input-wrapper">
            <Mail :size="20" class="form-icon" />
            <input
              v-model="form.email"
              type="email"
              placeholder="Correo electrónico"
              autocomplete="email"
              @focus="focused = 'email'"
              @blur="focused = ''"
            />
          </div>
          <Transition name="slide-error">
            <span v-if="errors.email" class="form-error">{{ errors.email }}</span>
          </Transition>
        </div>

        <div class="form-group" :class="{ 'form-group--error': errors.password, 'form-group--focus': focused === 'password' }">
          <div class="form-input-wrapper">
            <Lock :size="20" class="form-icon" />
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Contraseña"
              autocomplete="current-password"
              @focus="focused = 'password'"
              @blur="focused = ''"
            />
            <button type="button" class="form-toggle-pass" @click="showPassword = !showPassword" tabindex="-1">
              <EyeOff v-if="showPassword" :size="20" />
              <Eye v-else :size="20" />
            </button>
          </div>
          <Transition name="slide-error">
            <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
          </Transition>
        </div>

        <Transition name="slide-error">
          <div v-if="serverError" class="form-server-error">
            <AlertCircle :size="18" />
            <span>{{ serverError }}</span>
          </div>
        </Transition>

        <button type="submit" class="btn btn--primary btn--full" :disabled="authStore.loading">
          <Loader2 v-if="authStore.loading" :size="20" class="spin" />
          <LogIn v-else :size="20" />
          <span>{{ authStore.loading ? 'Ingresando...' : 'Iniciar Sesión' }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>¿No tienes cuenta?</p>
        <router-link to="/register" class="auth-link">
          Crear cuenta
          <ArrowRight :size="16" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import {
  Wheat, Mail, Lock, Eye, EyeOff, LogIn,
  ArrowRight, Loader2, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const ui = useUiStore()

const mounted = ref(false)
const focused = ref('')
const showPassword = ref(false)
const serverError = ref('')

const form = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: ''
})

onMounted(() => {
  setTimeout(() => { mounted.value = true }, 50)
})

function validate(): boolean {
  let valid = true
  errors.email = ''
  errors.password = ''

  if (!form.email.trim()) {
    errors.email = 'El correo es obligatorio'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Correo inválido'
    valid = false
  }

  if (!form.password) {
    errors.password = 'La contraseña es obligatoria'
    valid = false
  } else if (form.password.length < 6) {
    errors.password = 'Mínimo 6 caracteres'
    valid = false
  }

  return valid
}

async function handleLogin() {
  serverError.value = ''
  if (!validate()) return

  try {
    await authStore.login({ email: form.email, password: form.password })
    ui.showToast('¡Bienvenido de vuelta!', 'success')
    router.push('/')
  } catch (err: unknown) {
    const error = err as { response?: { data?: { detail?: string; message?: string } } }
    serverError.value = error.response?.data?.detail || error.response?.data?.message || 'Error al iniciar sesión'
  }
}
</script>
