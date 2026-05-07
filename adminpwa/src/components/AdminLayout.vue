<template>
  <div class="admin-layout">
    <!-- Mobile top bar -->
    <div class="mobile-bar" v-if="isMobile">
      <button class="mobile-menu-btn" @click="sidebarOpen = !sidebarOpen">
        <Menu :size="22" />
      </button>
      <span class="mobile-title">
        <img src="/icono.png" alt="" class="mobile-title-img" />
        TOMATE Admin
      </span>
      <button class="mobile-logout" @click="handleLogout"><LogOut :size="18" /></button>
    </div>

    <!-- Overlay -->
    <div v-if="sidebarOpen && isMobile" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ open: sidebarOpen || !isMobile }">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <img src="/icono.png" alt="TOMATE" class="sidebar-logo-img" />
        </div>
        <div class="sidebar-brand">
          <span class="sidebar-brand__title">TOMATE</span>
          <span class="sidebar-brand__sub">Panel Admin</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="sidebar-nav-label">Monitoreo</div>
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }" @click="closeMobile">
          <LayoutDashboard :size="18" /><span>Dashboard</span>
        </router-link>
        <router-link to="/visor" class="nav-item" :class="{ active: $route.path === '/visor' }" @click="closeMobile">
          <MapIcon :size="18" /><span>Mapa</span>
        </router-link>
        <router-link to="/reportes" class="nav-item" :class="{ active: $route.path === '/reportes' }" @click="closeMobile">
          <ClipboardList :size="18" /><span>Reportes</span>
        </router-link>
        <router-link to="/alertas" class="nav-item" :class="{ active: $route.path === '/alertas' }" @click="closeMobile">
          <Bell :size="18" /><span>Alertas</span>
        </router-link>

        <div class="sidebar-nav-label">Gestión</div>
        <router-link to="/centrales" class="nav-item" :class="{ active: $route.path === '/centrales' }" @click="closeMobile">
          <Building2 :size="18" /><span>Centrales</span>
        </router-link>
        <router-link to="/propuestas" class="nav-item" :class="{ active: $route.path === '/propuestas' }" @click="closeMobile">
          <FileCheck :size="18" /><span>Propuestas</span>
        </router-link>

        <div class="sidebar-nav-label" v-if="auth.isAdmin">Usuarios</div>
        <router-link v-if="auth.isAdmin" to="/usuarios" class="nav-item" :class="{ active: $route.path === '/usuarios' }" @click="closeMobile">
          <Shield :size="18" /><span>Administradores</span>
        </router-link>
        <router-link v-if="auth.isAdmin" to="/capturistas" class="nav-item" :class="{ active: $route.path === '/capturistas' }" @click="closeMobile">
          <Users :size="18" /><span>Capturistas</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userInitials }}</div>
          <div class="user-details">
            <span class="user-name">{{ auth.user?.nombre }}</span>
            <span class="user-role">{{ auth.user?.rol }}</span>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout"><LogOut :size="18" /></button>
      </div>
    </aside>

    <!-- Main -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard, Map as MapIcon, ClipboardList, Bell, Building2,
  FileCheck, Shield, Users, LogOut, Menu
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)
const isMobile = ref(false)

const userInitials = computed(() => {
  if (!auth.user) return '?'
  return ((auth.user.nombre?.charAt(0) || '') + (auth.user.apellido_paterno?.charAt(0) || '')).toUpperCase()
})

function handleLogout() { auth.logout(); router.push('/login') }
function closeMobile() { if (isMobile.value) sidebarOpen.value = false }

function checkMobile() { isMobile.value = window.innerWidth <= 900 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onBeforeUnmount(() => { window.removeEventListener('resize', checkMobile) })
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; }

/* ── Mobile bar ── */
.mobile-bar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 200;
  display: flex; align-items: center; justify-content: space-between;
  background: #1a1a2e; color: #fff; padding: 0.6rem 1rem; height: 52px;
}
.mobile-menu-btn, .mobile-logout {
  background: none; border: none; color: #fff; cursor: pointer; display: flex; padding: 4px;
}
.mobile-title { font-weight: 700; font-size: 1rem; display: flex; align-items: center; gap: 6px; }
.mobile-title-img { width: 24px; height: 24px; object-fit: contain; border-radius: 6px; flex-shrink: 0; }

.sidebar-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 150;
}

/* ── Sidebar ── */
.sidebar {
  width: 250px; background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 160;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  box-shadow: 4px 0 24px rgba(0,0,0,0.3); transition: transform 0.3s ease;
}
.sidebar-header {
  display: flex; align-items: center; gap: 0.75rem; padding: 1.1rem 1.1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1); color: #fff;
}
.sidebar-logo {
  width: 42px; height: 42px; background: transparent;
  border-radius: 12px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.sidebar-logo-img { width: 42px; height: 42px; object-fit: contain; border-radius: 12px; display: block; }
.sidebar-brand { display: flex; flex-direction: column; line-height: 1.15; }
.sidebar-brand__title { font-weight: 800; font-size: 1.1rem; letter-spacing: 0.04em; color: #fff; }
.sidebar-brand__sub { font-size: 0.65rem; font-weight: 500; color: rgba(255,255,255,0.6); text-transform: uppercase; }
.sidebar-nav { flex: 1; padding: 0.5rem 0.5rem; overflow-y: auto; }
.sidebar-nav-label {
  font-size: 0.65rem; font-weight: 600; color: rgba(255,255,255,0.4);
  text-transform: uppercase; letter-spacing: 0.06em; padding: 0.6rem 0.75rem 0.25rem;
}
.nav-item {
  display: flex; align-items: center; gap: 0.6rem; padding: 0.5rem 0.75rem;
  border-radius: 8px; color: rgba(255,255,255,0.75); text-decoration: none;
  font-weight: 500; font-size: 0.85rem; transition: all 0.15s; margin-bottom: 1px;
}
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.active { background: rgba(211,47,47,0.3); color: #fff; font-weight: 600; }
.sidebar-footer {
  padding: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: space-between;
}
.user-info { display: flex; align-items: center; gap: 0.6rem; }
.user-avatar {
  width: 32px; height: 32px; background: rgba(211,47,47,0.4); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 600; font-size: 0.75rem;
}
.user-details { display: flex; flex-direction: column; }
.user-name { font-weight: 600; font-size: 0.8rem; color: #fff; }
.user-role { font-size: 0.68rem; color: rgba(255,255,255,0.5); text-transform: capitalize; }
.btn-logout {
  display: flex; align-items: center; justify-content: center; width: 30px; height: 30px;
  border: none; border-radius: 8px; background: transparent;
  color: rgba(255,255,255,0.5); cursor: pointer;
}
.btn-logout:hover { background: rgba(255,255,255,0.1); color: #fff; }

/* ── Main ── */
.main-content {
  flex: 1; margin-left: 250px; padding: 1rem 1.5rem 2rem;
  background: #f8f9fa; min-height: 100vh;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .main-content { margin-left: 0; padding-top: 60px; padding-left: 1rem; padding-right: 1rem; }
}
</style>
