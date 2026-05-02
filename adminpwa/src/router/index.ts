import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guest: true }
    },
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/usuarios',
      name: 'Usuarios',
      component: () => import('@/views/UsuariosView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/usuarios-pwa',
      name: 'UsuariosPWA',
      component: () => import('@/views/UsuariosPWAView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/propuestas',
      name: 'Propuestas',
      component: () => import('@/views/PropuestasView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/visor',
      name: 'Visor',
      component: () => import('@/views/VisorView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/registros-precios',
      name: 'RegistrosPrecios',
      component: () => import('@/views/RegistrosPreciosView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  // Si hay token pero no user, restaurar sesión
  if (auth.token && !auth.user) {
    try {
      await auth.init()
    } catch {
      // init ya llama logout internamente
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return next('/')
  }

  if (to.meta.requiresAdmin && auth.user?.rol !== 'administrador') {
    return next('/')
  }

  next()
})

export default router
