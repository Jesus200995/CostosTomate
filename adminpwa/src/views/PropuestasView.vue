<template>
  <AdminLayout>
    <div class="top-bar">
      <div class="top-bar__pattern"></div>
      <div class="top-bar__text">
        <h1 class="top-bar__title"><FileCheck :size="22" /> Propuestas</h1>
        <span class="top-bar__subtitle">Solicitudes de nuevas centrales de abasto</span>
      </div>
      <div class="top-bar__actions">
        <select v-model="filtroEstatus" class="f-select" @change="load">
          <option value="">Todas</option>
          <option value="pendiente">Pendientes</option>
          <option value="aprobada">Aprobadas</option>
          <option value="rechazada">Rechazadas</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-center"><span class="spinner"></span></div>

    <div v-else-if="!propuestas.length" class="empty-card">
      <FileCheck :size="48" class="empty-icon" />
      <p>Sin propuestas {{ filtroEstatus || '' }}</p>
    </div>

    <div v-else class="props-list">
      <div v-for="p in propuestas" :key="p.id" class="prop-card" :class="'prop-' + p.estatus">
        <div class="prop-header">
          <h3>{{ p.nombre_central }}</h3>
          <span class="badge" :class="p.estatus === 'pendiente' ? 'badge--warning' : p.estatus === 'aprobada' ? 'badge--success' : 'badge--danger'">{{ p.estatus }}</span>
        </div>
        <div class="prop-details">
          <span><MapPin :size="14" /> {{ p.estado }}, {{ p.municipio }}</span>
          <span v-if="p.tipo">{{ p.tipo }}</span>
          <span v-if="p.latitud">📍 {{ p.latitud?.toFixed(4) }}, {{ p.longitud?.toFixed(4) }}</span>
          <span><User :size="14" /> {{ p.usuario_nombre || p.usuario_email || '—' }}</span>
          <span>{{ formatDate(p.created_at) }}</span>
        </div>
        <div v-if="p.motivo_rechazo" class="prop-motivo">Motivo: {{ p.motivo_rechazo }}</div>
        <div v-if="p.estatus === 'pendiente' && auth.hasPermiso('propuestas:acciones')" class="prop-actions">
          <button class="btn btn--success btn--sm" @click="autorizar(p.id)" :disabled="actionLoading">Autorizar</button>
          <button class="btn btn--danger btn--sm" @click="rechazar(p.id)" :disabled="actionLoading">Rechazar</button>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/components/AdminLayout.vue'
import type { PropuestaCentral } from '@/types'
import { FileCheck, MapPin, User } from 'lucide-vue-next'

const auth = useAuthStore()

const loading = ref(false)
const actionLoading = ref(false)
const propuestas = ref<PropuestaCentral[]>([])
const filtroEstatus = ref('pendiente')

function formatDate(iso?: string) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function load() {
  loading.value = true
  try { propuestas.value = await authService.getPropuestasCentrales(filtroEstatus.value || undefined) }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function autorizar(id: number) {
  actionLoading.value = true
  try { await authService.autorizarPropuesta(id); await load() }
  catch (e) { console.error(e) }
  finally { actionLoading.value = false }
}

async function rechazar(id: number) {
  const motivo = prompt('Motivo de rechazo (opcional):')
  actionLoading.value = true
  try { await authService.rechazarPropuesta(id, motivo || undefined); await load() }
  catch (e) { console.error(e) }
  finally { actionLoading.value = false }
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
.f-select { padding: 6px 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; font-size: 0.8rem; background: rgba(255,255,255,0.15); color: #fff; }
.f-select option { color: #333; background: #fff; }
.loading-center { display: flex; justify-content: center; padding: 3rem; }
.empty-card { text-align: center; padding: 4rem 2rem; background: #fff; border-radius: 14px; color: #bbb; }
.empty-icon { color: #ddd; margin-bottom: 1rem; }
.props-list { display: flex; flex-direction: column; gap: 0.75rem; }
.prop-card {
  background: #fff; border-radius: 12px; padding: 1rem 1.25rem;
  border-left: 4px solid #F9A825; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.prop-pendiente { border-left-color: #F9A825; }
.prop-aprobada { border-left-color: #2e7d32; }
.prop-rechazada { border-left-color: #c62828; }
.prop-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.prop-header h3 { font-size: 1rem; font-weight: 700; color: #333; margin: 0; }
.prop-details { display: flex; flex-wrap: wrap; gap: 0.75rem; font-size: 0.78rem; color: #666; margin-bottom: 0.5rem; }
.prop-details span { display: flex; align-items: center; gap: 0.2rem; }
.prop-motivo { font-size: 0.8rem; color: #c62828; font-style: italic; margin-bottom: 0.5rem; }
.prop-actions { display: flex; gap: 0.5rem; }
.btn--success { background: #2e7d32; color: #fff; }
.btn--success:hover { background: #1b5e20; }
.btn--danger { background: #c62828; color: #fff; }
.btn--danger:hover { background: #b71c1c; }
.btn--sm { padding: 5px 12px; font-size: 0.78rem; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
</style>
