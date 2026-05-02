<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <Layers :size="30" />
        </div>
        <div class="sidebar-brand">
          <span class="sidebar-brand__title">COSTOS</span>
          <span class="sidebar-brand__sub">Panel Admin</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="sidebar-nav-label">Menú</div>
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <LayoutDashboard :size="18" />
          <span>Dashboard</span>
        </router-link>

        <router-link 
          v-if="auth.isAdmin"
          to="/usuarios" 
          class="nav-item" 
          :class="{ active: $route.path === '/usuarios' }"
        >
          <Users :size="18" />
          <span>Administradores</span>
        </router-link>

        <router-link 
          v-if="auth.isAdmin"
          to="/usuarios-pwa" 
          class="nav-item" 
          :class="{ active: $route.path === '/usuarios-pwa' }"
        >
          <Users :size="18" />
          <span>Usuarios</span>
        </router-link>

        <router-link
          v-if="auth.isAdmin"
          to="/propuestas"
          class="nav-item"
          :class="{ active: $route.path === '/propuestas' }"
        >
          <Store :size="18" />
          <span>Propuestas Mercados</span>
        </router-link>

        <router-link to="/visor" class="nav-item" :class="{ active: $route.path === '/visor' }">
          <Map :size="18" />
          <span>Visor de Mapa</span>
        </router-link>
        <router-link to="/registros-precios" class="nav-item" :class="{ active: $route.path === '/registros-precios' }">
          <ClipboardList :size="18" />
          <span>Registros Precios</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            {{ userInitials }}
          </div>
          <div class="user-details">
            <span class="user-name">{{ auth.user?.nombre }}</span>
            <span class="user-role">{{ auth.user?.rol }}</span>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout">
          <LogOut :size="18" />
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Top Bar -->
      <div class="top-bar">
        <div class="top-bar__info">
          <h1 class="top-bar__title"><LayoutDashboard :size="22" /> Dashboard</h1>
          <p class="top-bar__desc">Panel de control — Bienvenido, {{ auth.user?.nombre }} {{ auth.user?.apellido_paterno }}</p>
        </div>
        <div class="top-bar__right">
          <span class="top-bar__date">{{ currentDate }}</span>
        </div>
      </div>

      <div class="dashboard-grid">
        <!-- Stats Cards -->
        <div class="stat-card">
          <div class="stat-icon stat-icon--primary">
            <User :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ auth.user?.rol === 'administrador' ? 'Administrador' : 'Usuario' }}</span>
            <span class="stat-label">Tu rol</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon--success">
            <CheckCircle :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value stat-value--success">{{ auth.user?.estatus }}</span>
            <span class="stat-label">Tu estatus</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon--info">
            <Calendar :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatDate(auth.user?.created_at) }}</span>
            <span class="stat-label">Fecha de registro</span>
          </div>
        </div>
      </div>

      <!-- User Profile Card -->
      <div class="profile-card">
        <h2>
          <UserCircle :size="22" />
          Mi perfil
        </h2>
        <div class="profile-grid">
          <div class="profile-item">
            <label>Nombre completo</label>
            <p>{{ auth.user?.nombre }} {{ auth.user?.apellido_paterno }} {{ auth.user?.apellido_materno }}</p>
          </div>
          <div class="profile-item">
            <label>CURP</label>
            <p>{{ auth.user?.curp }}</p>
          </div>
          <div class="profile-item">
            <label>Correo electrónico</label>
            <p>{{ auth.user?.correo }}</p>
          </div>
          <div class="profile-item">
            <label>Teléfono</label>
            <p>{{ auth.user?.telefono }}</p>
          </div>
        </div>
      </div>

      <!-- Quick Actions for Admin -->
      <div v-if="auth.isAdmin" class="quick-actions">
        <h2>
          <Zap :size="22" />
          Acciones rápidas
        </h2>
        <div class="actions-grid">
          <router-link to="/usuarios" class="action-card">
            <Users :size="32" />
            <span>Gestionar usuarios</span>
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Layers, LayoutDashboard, Users, LogOut, User, CheckCircle,
  Calendar, UserCircle, Zap, Map, Store, ClipboardList
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const currentDate = computed(() => {
  return new Date().toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
})

onMounted(async () => {
  if (!auth.isAuthenticated) {
    await auth.init()
  }
})

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

function formatDate(iso?: string): string {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  border-right: none;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.35);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.18);
  color: #fff;
}

.sidebar-logo {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.sidebar-brand__title {
  font-weight: 800;
  font-size: 1.15rem;
  letter-spacing: 0.04em;
}

.sidebar-brand__sub {
  font-size: 0.68rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0.65rem;
}

.sidebar-nav-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.5rem 0.85rem 0.35rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.85rem;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.88rem;
  transition: all 0.15s ease;
  margin-bottom: 2px;
  letter-spacing: -0.01em;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.25);
  color: #fff;
  font-weight: 600;
}

.sidebar-footer {
  padding: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.user-avatar {
  width: 34px;
  height: 34px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 0.78rem;
  letter-spacing: 0.02em;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 0.82rem;
  color: #fff;
  letter-spacing: -0.01em;
}

.user-role {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: capitalize;
}

.btn-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* ── Main Content ── */
.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 0.75rem 2rem 2rem;
  background: #f5f5f5;
  min-height: 100vh;
}

/* ── Top Bar ── */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  border-radius: 14px;
  padding: 1.15rem 1.5rem;
  margin-bottom: 1.75rem;
  box-shadow: 0 2px 12px rgba(79, 70, 229, 0.2);
}

.top-bar__title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.top-bar__desc {
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0.15rem 0 0;
}

.top-bar__right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.top-bar__date {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.7);
  text-transform: capitalize;
  white-space: nowrap;
}

/* ── Stats Grid ── */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon--primary {
  background: #e3f2fd;
  color: #1565c0;
}

.stat-icon--success {
  background: #e8f5e9;
  color: #2e7d32;
}

.stat-icon--info {
  background: #fff3e0;
  color: #e65100;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  text-transform: capitalize;
}

.stat-value--success {
  color: #2e7d32;
}

.stat-label {
  font-size: 0.85rem;
  color: #888;
}

/* ── Profile Card ── */
.profile-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-bottom: 2rem;
}

.profile-card h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #4f46e5;
  margin: 0 0 1.25rem;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.profile-item label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #888;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
}

.profile-item p {
  font-size: 0.95rem;
  color: #333;
  margin: 0;
  word-break: break-word;
}

/* ── Quick Actions ── */
.quick-actions {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.quick-actions h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #4f46e5;
  margin: 0 0 1.25rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background: #f5f5f5;
  border-radius: 12px;
  border: 2px solid transparent;
  text-decoration: none;
  color: #616161;
  transition: all 0.2s;
}

.action-card:hover {
  background: #eef2ff;
  border-color: #4f46e5;
  color: #4f46e5;
}

.action-card span {
  font-weight: 600;
  font-size: 0.9rem;
  text-align: center;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .sidebar {
    width: 68px;
  }

  .sidebar-header span,
  .sidebar-brand,
  .nav-item span,
  .user-details,
  .sidebar-nav-label {
    display: none;
  }

  .sidebar-header {
    justify-content: center;
    padding: 1rem 0.5rem;
  }

  .sidebar-logo {
    width: 36px;
    height: 36px;
  }

  .nav-item {
    justify-content: center;
    padding: 0.6rem 0.5rem;
  }

  .sidebar-footer {
    flex-direction: column;
    gap: 0.5rem;
  }

  .user-info {
    display: none;
  }

  .main-content {
    margin-left: 68px;
  }
}

@media (max-width: 600px) {
  .main-content {
    padding: 1rem;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
