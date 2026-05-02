<template>
  <!-- Overlay -->
  <Transition name="fade">
    <div v-if="ui.sidebarOpen" class="sidebar-overlay" @click="ui.closeSidebar()"></div>
  </Transition>

  <!-- Sidebar -->
  <Transition name="slide-sidebar">
    <aside v-if="ui.sidebarOpen" class="sidebar">
      <div class="sidebar__header">
        <div class="sidebar__user">
          <div class="sidebar__avatar">
            <span>{{ initials }}</span>
          </div>
          <div class="sidebar__user-info">
            <h3>{{ authStore.user?.name || 'Usuario' }}</h3>
            <p>{{ authStore.user?.email || '' }}</p>
          </div>
        </div>
        <button class="sidebar__close" @click="ui.closeSidebar()" aria-label="Cerrar menú">
          <X :size="22" />
        </button>
      </div>

      <nav class="sidebar__nav">
        <router-link to="/" class="sidebar__link" @click="ui.closeSidebar()">
          <Home :size="20" />
          <span>Inicio</span>
        </router-link>
        <router-link to="/perfil" class="sidebar__link" @click="ui.closeSidebar()">
          <UserCircle :size="20" />
          <span>Mi Perfil</span>
        </router-link>
        <router-link to="/mercados" class="sidebar__link" @click="ui.closeSidebar()">
          <ShoppingBag :size="20" />
          <span>Mercados</span>
        </router-link>
        <router-link to="/historial" class="sidebar__link" @click="ui.closeSidebar()">
          <ClipboardList :size="20" />
          <span>Historial</span>
        </router-link>
      </nav>

      <div class="sidebar__divider"></div>

      <div class="sidebar__footer">
        <button class="sidebar__link sidebar__link--danger" @click="handleLogout">
          <LogOut :size="20" />
          <span>Cerrar Sesión</span>
        </button>
        <p class="sidebar__version">COSTOS v1.0.0</p>
      </div>
    </aside>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import {
  X, Home, ShoppingBag, LogOut, UserCircle, ClipboardList
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const ui = useUiStore()

const initials = computed(() => {
  const name = authStore.user?.name || 'U'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
})

function handleLogout() {
  ui.closeSidebar()
  authStore.logout()
  ui.showToast('Sesión cerrada', 'info')
  router.push('/login')
}
</script>
