<template>
  <AdminLayout>
    <div class="top-bar">
      <div class="top-bar__pattern"></div>
      <div class="top-bar__text">
        <h1 class="top-bar__title"><Bell :size="22" /> Alertas</h1>
        <span class="top-bar__subtitle">Notificaciones y alertas activas del sistema</span>
      </div>
      <div class="top-bar__actions">
        <select v-model="filtroEstatus" class="f-select" @change="load">
          <option value="activa">Activas</option>
          <option value="">Todas</option>
          <option value="resuelta">Resueltas</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-center"><span class="spinner"></span></div>

    <div v-else-if="!alertas.length" class="empty-card">
      <Bell :size="48" class="empty-icon" />
      <p>Sin alertas {{ filtroEstatus === 'activa' ? 'activas' : '' }}</p>
    </div>

    <div v-else class="alerts-list">
      <div v-for="a in alertas" :key="a.id" class="alert-card" :class="'alert-' + a.tipo">
        <div class="alert-header">
          <span class="alert-tipo">{{ a.tipo }}</span>
          <span class="badge" :class="a.estatus === 'activa' ? 'badge--danger' : 'badge--success'">{{ a.estatus }}</span>
        </div>
        <p class="alert-desc">{{ a.descripcion }}</p>
        <div class="alert-meta">
          <span><Building2 :size="14" /> {{ a.nombre_central }}</span>
          <span>{{ a.estado }} · {{ a.municipio }}</span>
          <span v-if="a.calidad">Calidad: {{ a.calidad }}</span>
          <span v-if="a.variacion_porcentaje">Variación: {{ a.variacion_porcentaje > 0 ? '+' : '' }}{{ a.variacion_porcentaje }}%</span>
          <span v-if="a.fecha_alerta">{{ a.fecha_alerta }}</span>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authService } from '@/services/auth.service'
import AdminLayout from '@/components/AdminLayout.vue'
import type { Alerta } from '@/types'
import { Bell, Building2 } from 'lucide-vue-next'

const loading = ref(false)
const alertas = ref<Alerta[]>([])
const filtroEstatus = ref('activa')

async function load() {
  loading.value = true
  try { alertas.value = await authService.getAlertas(filtroEstatus.value || undefined) }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.top-bar {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;
  background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px;
  padding: 1rem 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2);
  position: relative; overflow: hidden;
}
.top-bar__pattern {
  position: absolute; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cellipse cx='16' cy='20' rx='9' ry='8' fill='none' stroke='%239b0000' stroke-width='1.2' opacity='0.6'/%3E%3Cline x1='16' y1='12' x2='16' y2='8' stroke='%239b0000' stroke-width='1.1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C13,9 10,9.5 9.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C19,9 22,9.5 22.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,10.5 C15.5,7.5 15,5.5 16,4.5 C17,5.5 16.5,7.5 16,10.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3C/svg%3E");
  background-size: 32px 32px; background-repeat: repeat;
}
.top-bar__text { position: relative; z-index: 1; }
.top-bar__title { font-size: 1.2rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__subtitle { font-size: 0.75rem; color: rgba(255,255,255,0.75); font-weight: 400; }
.top-bar__actions { display: flex; gap: 0.5rem; position: relative; z-index: 1; }
.top-bar__count { position: relative; z-index: 1; }
.f-select { padding: 6px 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; font-size: 0.8rem; background: rgba(255,255,255,0.15); color: #fff; }
.f-select option { color: #333; background: #fff; }
.loading-center { display: flex; justify-content: center; padding: 3rem; }
.empty-card { text-align: center; padding: 4rem 2rem; background: #fff; border-radius: 14px; color: #bbb; }
.empty-icon { color: #ddd; margin-bottom: 1rem; }
.alerts-list { display: flex; flex-direction: column; gap: 0.75rem; }
.alert-card { background: #fff; border-radius: 12px; padding: 1rem 1.25rem; border-left: 4px solid #F9A825; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.alert-card.alert-escasez { border-left-color: #D32F2F; }
.alert-card.alert-variacion { border-left-color: #E65100; }
.alert-card.alert-sin_reporte { border-left-color: #757575; }
.alert-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem; }
.alert-tipo { font-weight: 700; font-size: 0.85rem; text-transform: uppercase; color: #555; }
.alert-desc { font-size: 0.88rem; color: #333; margin: 0 0 0.5rem; }
.alert-meta { display: flex; flex-wrap: wrap; gap: 0.75rem; font-size: 0.75rem; color: #888; }
.alert-meta span { display: flex; align-items: center; gap: 0.25rem; }
</style>
