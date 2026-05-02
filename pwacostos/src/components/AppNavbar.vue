<template>
  <div class="navbar-wrapper">
    <header class="navbar">
      <button class="navbar__burger" @click="ui.toggleSidebar()" aria-label="Menú">
        <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
        <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
        <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
      </button>
      <div class="navbar__brand">
        <Wheat :size="22" />
        <span>COSTOS</span>
      </div>
      <button class="navbar__action" @click="$emit('search')" aria-label="Buscar">
        <Bell :size="22" />
      </button>
    </header>

    <!-- Barra de conexión -->
    <div
      class="conn-bar"
      :class="isOnline ? 'conn-bar--on' : 'conn-bar--off'"
      @click="pendingCount > 0 && (showPending = !showPending)"
      :style="pendingCount > 0 ? 'cursor:pointer' : ''"
    >
      <span class="conn-left">
        <span class="conn-dot"></span>
        <span class="conn-label">{{ isOnline ? 'En línea' : 'Sin conexión' }}</span>
      </span>
      <span v-if="pendingCount > 0" class="conn-badge">
        <UploadCloud :size="13" />
        {{ pendingCount }} pendiente{{ pendingCount > 1 ? 's' : '' }}
        <ChevronDown :size="13" :class="{ 'chevron-open': showPending }" />
      </span>
    </div>

    <!-- Panel de pendientes -->
    <transition name="slide-pending">
      <div v-if="showPending && pendingCount > 0" class="pending-panel">
        <div class="pending-header">
          <span>Operaciones por sincronizar</span>
          <button class="pending-close" @click="showPending = false">&times;</button>
        </div>
        <ul class="pending-list">
          <li v-for="item in pendingItems" :key="item.id" class="pending-item">
            <span class="pending-icon" :class="item.type === 'precio' ? 'pi-precio' : 'pi-propuesta'">
              {{ item.type === 'precio' ? '$' : '📍' }}
            </span>
            <div class="pending-info">
              <span class="pending-type">{{ item.type === 'precio' ? 'Precio' : 'Propuesta mercado' }}</span>
              <span class="pending-detail">
                <template v-if="item.type === 'precio'">
                  ${{ item.payload.precio }} · {{ item.payload.unidad }}
                </template>
                <template v-else>
                  {{ item.payload.nombre_mercado }}
                </template>
              </span>
            </div>
            <span class="pending-time">{{ timeAgo(item.createdAt) }}</span>
          </li>
        </ul>
        <div class="pending-footer" v-if="isOnline">
          <button class="pending-sync-btn" @click="doSync">
            <RefreshCw :size="13" :class="{ spinning: syncing }" /> Sincronizar ahora
          </button>
        </div>
        <div class="pending-footer" v-else>
          <span class="pending-note">Se subirán automáticamente al reconectar</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import { Wheat, Bell, UploadCloud, ChevronDown, RefreshCw } from 'lucide-vue-next'
import { useOnlineStatus, usePendingCount, syncAll } from '@/services/offline'

defineEmits<{ search: [] }>()

const ui = useUiStore()
const { isOnline } = useOnlineStatus()
const { pendingCount, pendingItems } = usePendingCount()
const showPending = ref(false)
const syncing = ref(false)

async function doSync() {
  syncing.value = true
  const { synced } = await syncAll()
  syncing.value = false
  if (synced > 0) {
    ui.showToast(`${synced} operación${synced > 1 ? 'es' : ''} sincronizada${synced > 1 ? 's' : ''}`, 'success')
  }
  if (pendingCount.value === 0) showPending.value = false
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'ahora'
  if (mins < 60) return `${mins}m`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h`
  return `${Math.floor(hrs / 24)}d`
}
</script>

<style scoped>
.navbar-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.conn-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  width: 100%;
  padding: 4px 14px;
  font-size: .78rem;
  font-weight: 600;
  letter-spacing: .03em;
  transition: background .3s, color .3s;
  user-select: none;
}
.conn-bar--on { background: linear-gradient(90deg, #22c55e, #16a34a); color: #fff; }
.conn-bar--off { background: linear-gradient(90deg, #ef4444, #dc2626); color: #fff; }
.conn-dot { width: 7px; height: 7px; border-radius: 50%; background: #fff; flex-shrink: 0; }
.conn-bar--on .conn-dot { box-shadow: 0 0 6px rgba(255,255,255,.6); }
.conn-bar--off .conn-dot { animation: blink-dot 1.2s infinite; }
@keyframes blink-dot { 0%,100%{opacity:1} 50%{opacity:.3} }
.conn-left {
  display: flex; align-items: center; gap: 6px;
}
.conn-label { white-space: nowrap; }
.conn-badge {
  display: flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,.22);
  font-size: .68rem; padding: 2px 9px; border-radius: 8px;
}
.conn-badge .chevron-open { transform: rotate(180deg); }

/* Panel de pendientes */
.pending-panel {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 4px 16px rgba(0,0,0,.12);
  max-height: 280px;
  overflow-y: auto;
}
.pending-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 14px 4px;
  font-size: .75rem; font-weight: 700; color: #374151;
}
.pending-close {
  background: none; border: none; font-size: 1.2rem; color: #9ca3af;
  cursor: pointer; line-height: 1; padding: 0 4px;
}
.pending-list {
  list-style: none; margin: 0; padding: 0 10px 6px;
}
.pending-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 4px;
  border-bottom: 1px solid #f3f4f6;
}
.pending-item:last-child { border-bottom: none; }
.pending-icon {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: .8rem; flex-shrink: 0;
}
.pi-precio { background: #dbeafe; color: #2563eb; font-weight: 700; }
.pi-propuesta { background: #fef3c7; }
.pending-info { flex: 1; min-width: 0; }
.pending-type { display: block; font-size: .72rem; font-weight: 600; color: #374151; }
.pending-detail {
  display: block; font-size: .65rem; color: #6b7280;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.pending-time { font-size: .6rem; color: #9ca3af; white-space: nowrap; }
.pending-footer {
  padding: 6px 14px 8px;
  display: flex; justify-content: center;
}
.pending-sync-btn {
  display: flex; align-items: center; gap: 5px;
  background: #22c55e; color: #fff; border: none;
  padding: 5px 14px; border-radius: 8px;
  font-size: .7rem; font-weight: 600; cursor: pointer;
}
.pending-sync-btn:active { background: #16a34a; }
.pending-note { font-size: .65rem; color: #9ca3af; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { animation: spin .8s linear infinite; }

/* Transición */
.slide-pending-enter-active, .slide-pending-leave-active {
  transition: max-height .25s ease, opacity .2s ease;
  overflow: hidden;
}
.slide-pending-enter-from, .slide-pending-leave-to {
  max-height: 0; opacity: 0;
}
.slide-pending-enter-to, .slide-pending-leave-from {
  max-height: 280px; opacity: 1;
}
</style>
