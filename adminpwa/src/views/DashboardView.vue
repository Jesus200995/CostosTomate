<template>
  <AdminLayout>
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="top-bar__pattern"></div>
      <div class="top-bar__text">
        <h1 class="top-bar__title"><LayoutDashboard :size="22" /> Dashboard</h1>
        <p class="top-bar__desc">Bienvenido, {{ auth.user?.nombre }} — {{ currentDate }}</p>
      </div>
      <div class="top-bar__actions">
        <select v-model="filtros.corte" class="f-select" @change="loadDashboard">
          <option value="">Todos los cortes</option>
          <option value="matutino">Matutino</option>
          <option value="mediodia">Mediodía</option>
        </select>
        <input type="date" v-model="filtros.fecha" class="f-input" @change="loadDashboard" />
        <button class="btn-refresh" @click="loadDashboard" :disabled="loading">
          <RefreshCw :size="16" :class="{ spinning: loading }" />
        </button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card kpi--red">
        <div class="kpi-icon"><Building2 :size="24" /></div>
        <div><div class="kpi-value">{{ data?.cobertura?.con_reporte || 0 }} / {{ data?.cobertura?.total || 0 }}</div><div class="kpi-label">Cobertura centrales</div></div>
      </div>
      <div class="kpi-card kpi--blue">
        <div class="kpi-icon"><ClipboardList :size="24" /></div>
        <div><div class="kpi-value">{{ data?.total_reportes || 0 }}</div><div class="kpi-label">Reportes</div></div>
      </div>
      <div class="kpi-card kpi--orange">
        <div class="kpi-icon"><Clock :size="24" /></div>
        <div><div class="kpi-value">{{ data?.capturas_tardias || 0 }}</div><div class="kpi-label">Capturas tardías</div></div>
      </div>
      <div class="kpi-card kpi--amber">
        <div class="kpi-icon"><AlertTriangle :size="24" /></div>
        <div><div class="kpi-value">{{ data?.alertas_activas || 0 }}</div><div class="kpi-label">Alertas activas</div></div>
      </div>
    </div>

    <!-- Calidades -->
    <div class="section-grid">
      <div class="card">
        <h3 class="card-title">Precios por Calidad</h3>
        <div v-if="data?.calidades?.length" class="calidades-grid">
          <div v-for="c in data.calidades" :key="c.calidad" class="calidad-card" :class="'cal-' + c.calidad">
            <div class="cal-name">{{ c.calidad }}</div>
            <div class="cal-price">${{ c.promedio.toFixed(2) }}/kg</div>
            <div class="cal-range">Min ${{ c.minimo.toFixed(2) }} — Max ${{ c.maximo.toFixed(2) }}</div>
            <div class="cal-datos">{{ c.con_dato }} reportes · {{ c.sin_dato }} sin dato</div>
          </div>
        </div>
        <div v-else class="empty-state">Sin datos de precios aún</div>
      </div>

      <div class="card">
        <h3 class="card-title">Promedios por Estado</h3>
        <div v-if="data?.por_estado?.length" class="ranking-list">
          <div v-for="(e, i) in data.por_estado.slice(0, 15)" :key="e.estado" class="ranking-row">
            <span class="rank">#{{ i + 1 }}</span>
            <span class="rank-name">{{ e.estado }}</span>
            <span class="rank-price">${{ e.promedio.toFixed(2) }}</span>
            <span class="rank-count">{{ e.centrales_con_reporte }} centrales</span>
          </div>
        </div>
        <div v-else class="empty-state">Sin datos por estado</div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-grid" v-if="auth.isAdmin">
      <router-link to="/visor" class="action-card"><MapIcon :size="28" /><span>Mapa</span></router-link>
      <router-link to="/reportes" class="action-card"><ClipboardList :size="28" /><span>Reportes</span></router-link>
      <router-link to="/centrales" class="action-card"><Building2 :size="28" /><span>Centrales</span></router-link>
      <router-link to="/capturistas" class="action-card"><Users :size="28" /><span>Capturistas</span></router-link>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth.service'
import AdminLayout from '@/components/AdminLayout.vue'
import type { DashboardData } from '@/types'
import {
  LayoutDashboard, RefreshCw, Building2, ClipboardList, Clock,
  AlertTriangle, Map as MapIcon, Users
} from 'lucide-vue-next'

const auth = useAuthStore()
const loading = ref(false)
const data = ref<DashboardData | null>(null)
const filtros = reactive({ fecha: '', corte: '' })

const currentDate = computed(() =>
  new Date().toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
)

async function loadDashboard() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (filtros.fecha) params.fecha = filtros.fecha
    if (filtros.corte) params.corte = filtros.corte
    data.value = await authService.getDashboard(params)
  } catch (e) { console.error('Dashboard error:', e) }
  finally { loading.value = false }
}

onMounted(loadDashboard)
</script>

<style scoped>
.top-bar {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;
  background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px;
  padding: 1rem 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2);
  position: relative; overflow: hidden;
}
.top-bar__pattern {
  position: absolute; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cellipse cx='16' cy='20' rx='9' ry='8' fill='none' stroke='%239b0000' stroke-width='1.2' opacity='0.6'/%3E%3Cline x1='16' y1='12' x2='16' y2='8' stroke='%239b0000' stroke-width='1.1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C13,9 10,9.5 9.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C19,9 22,9.5 22.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,10.5 C15.5,7.5 15,5.5 16,4.5 C17,5.5 16.5,7.5 16,10.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3C/svg%3E");
  background-size: 32px 32px; background-repeat: repeat;
}
.top-bar__text { position: relative; z-index: 1; }
.top-bar__title { font-size: 1.3rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__desc { font-size: 0.82rem; color: rgba(255,255,255,0.8); margin: 0.1rem 0 0; text-transform: capitalize; }
.top-bar__actions { display: flex; align-items: center; gap: 0.5rem; position: relative; z-index: 1; }
.f-select, .f-input {
  padding: 6px 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px;
  font-size: 0.78rem; background: rgba(255,255,255,0.15); color: #fff;
}
.f-select option { color: #333; background: #fff; }
.btn-refresh {
  display: flex; align-items: center; padding: 6px; border: none; border-radius: 8px;
  background: rgba(255,255,255,0.2); color: #fff; cursor: pointer;
}
.spinning { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* KPIs */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.kpi-card {
  background: #fff; border-radius: 14px; padding: 1.1rem; display: flex; align-items: center; gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 4px solid #e0e0e0;
}
.kpi--red { border-left-color: #D32F2F; }
.kpi--blue { border-left-color: #1976D2; }
.kpi--orange { border-left-color: #E65100; }
.kpi--amber { border-left-color: #F9A825; }
.kpi-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.kpi--red .kpi-icon { background: #ffebee; color: #D32F2F; }
.kpi--blue .kpi-icon { background: #e3f2fd; color: #1976D2; }
.kpi--orange .kpi-icon { background: #fff3e0; color: #E65100; }
.kpi--amber .kpi-icon { background: #fff8e1; color: #F9A825; }
.kpi-value { font-size: 1.2rem; font-weight: 700; color: #333; }
.kpi-label { font-size: 0.78rem; color: #888; }

/* Sections */
.section-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.5rem; }
.card { background: #fff; border-radius: 14px; padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.card-title { font-size: 1rem; font-weight: 700; color: #B71C1C; margin: 0 0 1rem; }

.calidades-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.calidad-card { border-radius: 12px; padding: 1rem; text-align: center; }
.cal-primera { background: #e8f5e9; }
.cal-segunda { background: #fff8e1; }
.cal-tercera { background: #ffebee; }
.cal-name { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #555; margin-bottom: 0.3rem; }
.cal-price { font-size: 1.3rem; font-weight: 800; color: #333; }
.cal-range { font-size: 0.7rem; color: #777; margin-top: 0.2rem; }
.cal-datos { font-size: 0.65rem; color: #999; margin-top: 0.3rem; }

.ranking-list { max-height: 320px; overflow-y: auto; }
.ranking-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 1px solid #f5f5f5; font-size: 0.82rem; }
.rank { width: 28px; font-weight: 700; color: #D32F2F; text-align: center; }
.rank-name { flex: 1; color: #333; }
.rank-price { font-weight: 700; color: #2e7d32; }
.rank-count { font-size: 0.72rem; color: #999; }

.empty-state { text-align: center; padding: 2rem; color: #bbb; font-size: 0.9rem; }

/* Actions */
.actions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; }
.action-card {
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 1.25rem;
  background: #fff; border-radius: 12px; border: 2px solid transparent; text-decoration: none;
  color: #616161; box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: all 0.2s;
}
.action-card:hover { border-color: #D32F2F; color: #D32F2F; }
.action-card span { font-weight: 600; font-size: 0.85rem; }

@media (max-width: 768px) {
  .section-grid { grid-template-columns: 1fr; }
  .calidades-grid { grid-template-columns: 1fr; }
  .top-bar { flex-direction: column; align-items: flex-start; }
  .top-bar__actions { width: 100%; flex-wrap: wrap; }
}
</style>
