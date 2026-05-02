import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AdminUser } from '@/types'
import { authService } from '@/services/auth.service'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AdminUser | null>(null)
  const token = ref<string | null>(localStorage.getItem('admin_token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.rol === 'administrador')

  async function init() {
    if (token.value) {
      try {
        loading.value = true
        user.value = await authService.getMe(token.value)
      } catch {
        logout()
      } finally {
        loading.value = false
      }
    }
  }

  async function login(correo: string, password: string) {
    const res = await authService.login({ correo, password })
    user.value = res.user
    token.value = res.token
    localStorage.setItem('admin_token', res.token)
  }

  async function register(data: {
    nombre: string
    apellido_paterno: string
    apellido_materno: string
    curp: string
    correo: string
    telefono: string
    password: string
    rol: 'usuario' | 'administrador'
  }) {
    const res = await authService.register(data)
    user.value = res.user
    token.value = res.token
    localStorage.setItem('admin_token', res.token)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('admin_token')
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    isAdmin,
    init,
    login,
    register,
    logout
  }
})
