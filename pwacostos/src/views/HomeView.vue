<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <!-- Header -->
      <div class="home-header" :class="{ 'home-header--visible': mounted }">
        <div class="home-welcome">
          <h1 class="home-welcome__title">
            Hola, <span>{{ firstName }}</span> 👋
          </h1>
          <p class="home-welcome__subtitle">{{ greetingText }}</p>
        </div>
        <div class="home-avatar" @click.stop="showProfileModal = true">
          <span>{{ initials }}</span>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-grid" :class="{ 'stats-grid--visible': mounted }">
        <div class="stat-card stat-card--primary" @click="router.push('/mercados')">
          <div class="stat-card__icon">
            <Store :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">{{ stats.mercados }}</span>
            <span class="stat-card__label">Mercados</span>
          </div>
        </div>
        <div class="stat-card stat-card--accent" @click="router.push('/mercados')">
          <div class="stat-card__icon">
            <ClipboardList :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">{{ stats.reportes }}</span>
            <span class="stat-card__label">Reportes</span>
          </div>
        </div>
        <div class="stat-card stat-card--success" @click="router.push('/mercados')">
          <div class="stat-card__icon">
            <ShoppingBasket :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">{{ stats.productos }}</span>
            <span class="stat-card__label">Productos captados</span>
          </div>
        </div>
        <div class="stat-card stat-card--warning" @click="router.push('/mercados')">
          <div class="stat-card__icon">
            <Calendar :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">{{ stats.ultimoReporte || '—' }}</span>
            <span class="stat-card__label">Último reporte</span>
          </div>
        </div>
      </div>

      <!-- Acciones rápidas -->
      <section class="home-section" :class="{ 'home-section--visible': mounted }">
        <h2 class="home-section__title">
          <Zap :size="20" />
          Acciones rápidas
        </h2>
        <div class="quick-actions">
          <button class="quick-action" @click="router.push('/mercados')">
            <div class="quick-action__icon quick-action__icon--green">
              <Store :size="24" />
            </div>
            <span>Ir a Mercados</span>
          </button>
          <button class="quick-action" @click="router.push('/perfil')">
            <div class="quick-action__icon quick-action__icon--blue">
              <UserCircle :size="24" />
            </div>
            <span>Mi Perfil</span>
          </button>
        </div>
      </section>

      <!-- Últimos reportes -->
      <section class="home-section home-section--last" :class="{ 'home-section--visible': mounted }">
        <h2 class="home-section__title">
          <Clock :size="20" />
          Actividad reciente
        </h2>

        <div v-if="loadingActivity" class="dash-loading">
          <div class="dash-spinner"></div>
        </div>

        <div v-else-if="recentReportes.length === 0" class="empty-state">
          <div class="empty-state__icon">
            <Inbox :size="48" />
          </div>
          <p class="empty-state__text">Aún no hay reportes</p>
          <p class="empty-state__hint">Ve a Mercados y captura tu primer reporte de precios</p>
        </div>

        <div v-else class="activity-list">
          <div v-for="r in recentReportes" :key="r.id" class="activity-card" @click="router.push('/mercados')">
            <div class="activity-card__left">
              <div class="activity-card__icon">
                <FileText :size="18" />
              </div>
              <div class="activity-card__info">
                <span class="activity-card__mercado">{{ getMercadoNombre(r.mercado_id) }}</span>
                <span class="activity-card__meta">
                  {{ r.total_productos }} producto{{ r.total_productos !== 1 ? 's' : '' }}
                </span>
              </div>
            </div>
            <div class="activity-card__right">
              <span class="activity-badge" :class="r.tipo_precio === 'MENUDEO' ? 'activity-badge--blue' : 'activity-badge--orange'">
                {{ r.tipo_precio }}
              </span>
              <span class="activity-card__date">{{ formatDateShort(r.fecha) }}</span>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Profile Modal -->
    <AppModal :show="showProfileModal" @close="showProfileModal = false">
      <template #header>
        <UserCircle :size="24" />
        <span>Mi Perfil</span>
      </template>
      <template #body>
        <div class="profile-modal">
          <div class="profile-modal__avatar">
            <span>{{ initials }}</span>
          </div>
          <h3>{{ authStore.user?.name }}</h3>
          <p>{{ authStore.user?.email }}</p>
        </div>
      </template>
      <template #footer>
        <button class="btn btn--primary btn--full" style="margin-bottom: 0.5rem" @click="showProfileModal = false; router.push('/perfil')">
          <UserCircle :size="18" />
          <span>Ver perfil completo</span>
        </button>
        <button class="btn btn--danger btn--full" @click="handleLogout">
          <LogOut :size="18" />
          <span>Cerrar Sesión</span>
        </button>
      </template>
    </AppModal>

    <AppToast />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { mercadosService } from '@/services/mercados.service'
import type { Mercado, ReporteOut } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppModal from '@/components/AppModal.vue'
import AppToast from '@/components/AppToast.vue'
import {
  Store, ClipboardList, ShoppingBasket, Calendar,
  Zap, UserCircle, LogOut, Clock, Inbox, FileText
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const ui = useUiStore()

const mounted = ref(false)
const showProfileModal = ref(false)
const loadingActivity = ref(true)

const mercados = ref<Mercado[]>([])
const recentReportes = ref<ReporteOut[]>([])

const stats = reactive({
  mercados: 0,
  reportes: 0,
  productos: 0,
  ultimoReporte: ''
})

const firstName = computed(() => {
  const n = authStore.user?.name || 'Usuario'
  return n.split(' ')[0].charAt(0).toUpperCase() + n.split(' ')[0].slice(1).toLowerCase()
})

const initials = computed(() => {
  const name = authStore.user?.name || 'U'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
})

const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días'
  if (h < 19) return 'Buenas tardes'
  return 'Buenas noches'
})

function getMercadoNombre(id: number): string {
  return mercados.value.find(m => m.id === id)?.nombre || `Mercado #${id}`
}

function formatDateShort(iso: string): string {
  return new Date(iso + 'T00:00:00').toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })
}

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

function handleLogout() {
  showProfileModal.value = false
  authStore.logout()
  ui.showToast('Sesión cerrada', 'info')
  router.push('/login')
}

async function loadDashboard() {
  loadingActivity.value = true
  try {
    const [m, r] = await Promise.all([
      mercadosService.getMercados(),
      mercadosService.getReportes()
    ])
    mercados.value = m
    const allReportes = r

    stats.mercados = m.length
    stats.reportes = allReportes.length
    stats.productos = allReportes.reduce((sum, rep) => sum + rep.total_productos, 0)
    if (allReportes.length > 0) {
      stats.ultimoReporte = formatDateShort(allReportes[0].fecha)
    }

    recentReportes.value = allReportes.slice(0, 5)
  } catch {
    // silent — dashboard is best-effort
  } finally {
    loadingActivity.value = false
  }
}

onMounted(() => {
  setTimeout(() => { mounted.value = true }, 100)
  loadDashboard()
})
</script>

<style scoped>
.stats-grid .stat-card {
  cursor: pointer;
}

.dash-loading {
  display: flex;
  justify-content: center;
  padding: 2rem;
}
.dash-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e0e0e0;
  border-top-color: #1B5E20;
  border-radius: 50%;
  animation: dash-spin 0.7s linear infinite;
}
@keyframes dash-spin { to { transform: rotate(360deg); } }

/* Activity list */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.activity-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border, #e8f5e9);
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.activity-card:hover {
  border-color: #1B5E20;
  box-shadow: 0 2px 8px rgba(27,94,32,0.08);
}

.activity-card__left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1;
}

.activity-card__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(27,94,32,0.08);
  color: #1B5E20;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-card__info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.activity-card__mercado {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-card__meta {
  font-size: 0.78rem;
  color: #999;
}

.activity-card__right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
  margin-left: 8px;
}

.activity-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 5px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.activity-badge--blue {
  background: #e3f2fd;
  color: #1565c0;
}
.activity-badge--orange {
  background: #fff3e0;
  color: #e65100;
}

.activity-card__date {
  font-size: 0.75rem;
  color: #aaa;
}

/* ── Responsive: pantallas pequeñas ── */
@media (max-width: 480px) {
  .home-header {
    margin-bottom: 16px;
    padding-top: 4px;
  }
  .home-welcome__title {
    font-size: 1.1rem;
  }
  .home-welcome__subtitle {
    font-size: 0.72rem;
  }
  .home-avatar {
    width: 36px;
    height: 36px;
    font-size: 13px;
  }
  .stats-grid {
    gap: 8px;
    margin-bottom: 18px;
  }
  .stat-card {
    padding: 10px;
    gap: 8px;
    border-radius: 10px;
  }
  .stat-card__icon {
    width: 34px;
    height: 34px;
  }
  .stat-card__value {
    font-size: 1rem;
  }
  .stat-card__label {
    font-size: 0.65rem;
  }
  .home-section {
    margin-bottom: 18px;
  }
  .home-section__title {
    font-size: 0.85rem;
    gap: 6px;
    margin-bottom: 10px;
  }
  .quick-actions {
    gap: 8px;
  }
  .quick-action {
    padding: 14px 10px;
    gap: 8px;
    font-size: 0.76rem;
    border-radius: 10px;
  }
  .quick-action__icon {
    width: 38px;
    height: 38px;
  }
  .activity-card {
    padding: 9px 10px;
    border-radius: 10px;
  }
  .activity-card__icon {
    width: 30px;
    height: 30px;
    border-radius: 8px;
  }
  .activity-card__mercado {
    font-size: 0.78rem;
  }
  .activity-card__meta {
    font-size: 0.68rem;
  }
  .activity-badge {
    font-size: 0.58rem;
    padding: 2px 5px;
  }
  .activity-card__date {
    font-size: 0.67rem;
  }
  .empty-state {
    padding: 24px 14px;
  }
  .empty-state__text {
    font-size: 0.82rem;
  }
  .empty-state__hint {
    font-size: 0.72rem;
  }
  .profile-modal__avatar {
    width: 56px;
    height: 56px;
    font-size: 1.2rem;
  }
  .profile-modal h3 {
    font-size: 0.95rem;
  }
  .profile-modal p {
    font-size: 0.78rem;
  }
}

@media (max-width: 360px) {
  .home-welcome__title {
    font-size: 0.95rem;
  }
  .home-welcome__subtitle {
    font-size: 0.65rem;
  }
  .home-avatar {
    width: 32px;
    height: 32px;
    font-size: 11px;
  }
  .stats-grid {
    gap: 6px;
    margin-bottom: 14px;
  }
  .stat-card {
    padding: 8px;
    gap: 6px;
  }
  .stat-card__icon {
    width: 28px;
    height: 28px;
  }
  .stat-card__value {
    font-size: 0.88rem;
  }
  .stat-card__label {
    font-size: 0.6rem;
  }
  .home-section__title {
    font-size: 0.78rem;
  }
  .quick-action {
    padding: 10px 8px;
    gap: 6px;
    font-size: 0.7rem;
  }
  .quick-action__icon {
    width: 32px;
    height: 32px;
  }
  .activity-card {
    padding: 7px 8px;
  }
  .activity-card__icon {
    width: 26px;
    height: 26px;
  }
  .activity-card__mercado {
    font-size: 0.72rem;
  }
  .activity-card__meta {
    font-size: 0.62rem;
  }
  .activity-badge {
    font-size: 0.54rem;
    padding: 1px 4px;
  }
  .activity-card__date {
    font-size: 0.6rem;
  }
}
</style>
