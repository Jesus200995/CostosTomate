<template>
  <AdminLayout>
    <div class="top-bar">
      <div class="top-bar__pattern"></div>
      <div class="top-bar__text">
        <h1 class="top-bar__title"><Shield :size="22" /> Administradores</h1>
        <span class="top-bar__subtitle">Usuarios con acceso al panel de administración</span>
      </div>
      <span class="top-bar__count">{{ usuarios.length }} usuarios</span>
    </div>
    <div class="filters-bar">
      <input type="text" v-model="busqueda" class="fi fi-wide" placeholder="Buscar..." />
    </div>
    <div v-if="loading" class="loading-center"><span class="spinner"></span></div>
    <div v-else class="table-container">
      <table class="table">
        <thead><tr><th>Nombre</th><th>Correo</th><th>CURP</th><th>Rol</th><th>Estatus</th><th>Registro</th><th>Acciones</th></tr></thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td class="td-name">{{ u.nombre }} {{ u.apellido_paterno }} {{ u.apellido_materno }}</td>
            <td>{{ u.correo }}</td>
            <td class="td-mono">{{ u.curp }}</td>
            <td><span class="badge" :class="u.rol === 'administrador' ? 'badge--primary' : 'badge--default'">{{ u.rol }}</span></td>
            <td><span class="badge" :class="u.estatus === 'activo' ? 'badge--success' : 'badge--danger'">{{ u.estatus }}</span></td>
            <td>{{ formatDate(u.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button v-if="u.estatus === 'activo'" class="btn-action btn-no" @click="toggleEstatus(u, 'inactivo')"><X :size="14" /></button>
                <button v-else class="btn-action btn-ok" @click="toggleEstatus(u, 'activo')"><Check :size="14" /></button>
              </div>
            </td>
          </tr>
          <tr v-if="!filtered.length"><td colspan="7" class="empty-state">Sin administradores</td></tr>
        </tbody>
      </table>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { authService } from '@/services/auth.service'
import AdminLayout from '@/components/AdminLayout.vue'
import type { AdminUser } from '@/types'
import { Shield, Check, X } from 'lucide-vue-next'

const loading = ref(false)
const usuarios = ref<AdminUser[]>([])
const busqueda = ref('')

const filtered = computed(() => {
  if (!busqueda.value) return usuarios.value
  const q = busqueda.value.toLowerCase()
  return usuarios.value.filter(u => u.nombre.toLowerCase().includes(q) || u.correo.toLowerCase().includes(q) || u.curp.toLowerCase().includes(q))
})

function formatDate(iso?: string) {
  if (!iso) return '\u2014'
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function toggleEstatus(u: AdminUser, estatus: string) {
  try { const updated = await authService.updateEstatus(u.id, estatus); Object.assign(u, updated) }
  catch (e) { console.error(e) }
}

async function load() {
  loading.value = true
  try { usuarios.value = await authService.getUsuarios() }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.top-bar { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px; padding: 1rem 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2); position: relative; overflow: hidden; }
.top-bar__pattern { position: absolute; inset: 0; pointer-events: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cellipse cx='16' cy='20' rx='9' ry='8' fill='none' stroke='%239b0000' stroke-width='1.2' opacity='0.6'/%3E%3Cline x1='16' y1='12' x2='16' y2='8' stroke='%239b0000' stroke-width='1.1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C13,9 10,9.5 9.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,11 C19,9 22,9.5 22.5,11.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3Cpath d='M16,10.5 C15.5,7.5 15,5.5 16,4.5 C17,5.5 16.5,7.5 16,10.5' fill='none' stroke='%239b0000' stroke-width='1' stroke-linecap='round' opacity='0.6'/%3E%3C/svg%3E"); background-size: 32px 32px; background-repeat: repeat; }
.top-bar__text { position: relative; z-index: 1; display: flex; flex-direction: column; gap: 2px; }
.top-bar__title { font-size: 1.2rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__subtitle { font-size: 0.75rem; color: rgba(255,255,255,0.75); font-weight: 400; }
.top-bar__count { font-size: 0.85rem; color: rgba(255,255,255,0.8); background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 8px; position: relative; z-index: 1; }
.filters-bar { display: flex; gap: 0.5rem; margin-bottom: 1rem; background: #fff; padding: 0.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.fi { padding: 6px 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 0.82rem; }
.fi-wide { flex: 1; }
.loading-center { display: flex; justify-content: center; padding: 3rem; }
.empty-state { text-align: center; padding: 2rem; color: #bbb; }
.td-name { font-weight: 600; }
.td-mono { font-family: monospace; font-size: 0.8rem; }
.badge--default { background: #f5f5f5; color: #616161; }
.action-btns { display: flex; gap: 4px; }
.btn-action { width: 26px; height: 26px; border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-ok { background: #e8f5e9; color: #2e7d32; }
.btn-ok:hover { background: #c8e6c9; }
.btn-no { background: #ffebee; color: #c62828; }
.btn-no:hover { background: #ffcdd2; }
</style>
