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
      meta: { requiresAuth: true, permiso: 'dashboard' }
    },
    {
      path: '/visor',
      name: 'Visor',
      component: () => import('@/views/VisorView.vue'),
      meta: { requiresAuth: true, permiso: 'visor' }
    },
    {
      path: '/reportes',
      name: 'Reportes',
      component: () => import('@/views/ReportesView.vue'),
      meta: { requiresAuth: true, permiso: 'reportes' }
    },
    {
      path: '/alertas',
      name: 'Alertas',
      component: () => import('@/views/AlertasView.vue'),
      meta: { requiresAuth: true, permiso: 'alertas' }
    },
    {
      path: '/centrales',
      name: 'Centrales',
      component: () => import('@/views/CentralesView.vue'),
      meta: { requiresAuth: true, permiso: 'centrales' }
    },
    {
      path: '/propuestas',
      name: 'Propuestas',
      component: () => import('@/views/PropuestasView.vue'),
      meta: { requiresAuth: true, permiso: 'propuestas' }
    },
    {
      path: '/usuarios',
      name: 'Usuarios',
      component: () => import('@/views/UsuariosView.vue'),
      meta: { requiresAuth: true, permiso: 'administradores' }
    },
    {
      path: '/capturistas',
      name: 'Capturistas',
      component: () => import('@/views/CapturistasView.vue'),
      meta: { requiresAuth: true, permiso: 'capturistas' }
    },
    {
      path: '/permisos',
      name: 'Permisos',
      component: () => import('@/views/PermisosView.vue'),
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

  if (to.meta.permiso && to.meta.permiso !== 'dashboard' && auth.user?.rol !== 'administrador') {
    if (!auth.hasPermiso(to.meta.permiso as string)) {
      return next('/')
    }
  }

  next()
})

export default router
