<template>
  <AdminLayout>
    <div class="top-bar">
      <h1 class="top-bar__title"><Building2 :size="22" /> Catálogo de Centrales</h1>
      <span class="top-bar__count">{{ centrales.length }} centrales</span>
    </div>

    <!-- Filtros -->
    <div class="filters-bar">
      <input type="text" v-model="busqueda" class="fi fi-wide" placeholder="Buscar central..." />
      <select v-model="filtroEstado" class="fi">
        <option value="">Todos los estados</option>
        <option v-for="e in estadosUnicos" :key="e">{{ e }}</option>
      </select>
      <select v-model="filtroEstatus" class="fi">
        <option value="">Todos los estatus</option>
        <option value="autorizado">Autorizado</option>
        <option value="pendiente">Pendiente</option>
        <option value="inactivo">Inactivo</option>
      </select>
    </div>

    <div v-if="loading" class="loading-center"><span class="spinner"></span></div>

    <div v-else class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th><th>Nombre</th><th>Tipo</th><th>Municipio</th><th>Estado</th>
            <th>Estatus</th><th>PWA</th><th>Coordenadas</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in filtered" :key="c.id">
            <td>{{ c.id }}</td>
            <td class="td-name">{{ c.nombre_central }}</td>
            <td>{{ c.tipo || '—' }}</td>
            <td>{{ c.municipio }}</td>
            <td>{{ c.estado }}</td>
            <td>
              <span class="badge" :class="c.estatus === 'autorizado' ? 'badge--success' : c.estatus === 'inactivo' ? 'badge--danger' : 'badge--warning'">
                {{ c.estatus }}
              </span>
            </td>
            <td>
              <button class="btn-toggle" :class="{ active: c.visible_pwa }"
                @click="togglePWA(c)">{{ c.visible_pwa ? 'Sí' : 'No' }}</button>
            </td>
            <td class="td-coords">{{ c.latitud ? c.latitud.toFixed(4) + ', ' + c.longitud?.toFixed(4) : '—' }}</td>
            <td>
              <div class="action-btns">
                <button v-if="c.estatus !== 'autorizado'" class="btn-action btn-ok" @click="setEstatus(c, 'autorizado')"><Check :size="14" /></button>
                <button v-if="c.estatus !== 'inactivo'" class="btn-action btn-no" @click="setEstatus(c, 'inactivo')"><X :size="14" /></button>
              </div>
            </td>
          </tr>
          <tr v-if="!filtered.length"><td colspan="9" class="empty-state">Sin centrales</td></tr>
        </tbody>
      </table>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { authService } from '@/services/auth.service'
import AdminLayout from '@/components/AdminLayout.vue'
import type { Central } from '@/types'
import { Building2, Check, X } from 'lucide-vue-next'

const loading = ref(false)
const centrales = ref<Central[]>([])
const busqueda = ref('')
const filtroEstado = ref('')
const filtroEstatus = ref('')

const estadosUnicos = computed(() => {
  const s = new Set(centrales.value.map(c => c.estado).filter(Boolean))
  return [...s].sort()
})

const filtered = computed(() => {
  let list = centrales.value
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase()
    list = list.filter(c => c.nombre_central.toLowerCase().includes(q) || c.municipio?.toLowerCase().includes(q))
  }
  if (filtroEstado.value) list = list.filter(c => c.estado === filtroEstado.value)
  if (filtroEstatus.value) list = list.filter(c => c.estatus === filtroEstatus.value)
  return list
})

async function load() {
  loading.value = true
  try { centrales.value = await authService.getCentrales() }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function togglePWA(c: Central) {
  try {
    const updated = await authService.updateCentral(c.id, { visible_pwa: !c.visible_pwa })
    Object.assign(c, updated)
  } catch (e) { console.error(e) }
}

async function setEstatus(c: Central, estatus: string) {
  try {
    const updated = await authService.updateCentral(c.id, { estatus })
    Object.assign(c, updated)
  } catch (e) { console.error(e) }
}

onMounted(load)
</script>

<style scoped>
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px;
  padding: 1rem 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2);
}
.top-bar__title { font-size: 1.2rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__count { font-size: 0.85rem; color: rgba(255,255,255,0.8); background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 8px; }
.filters-bar {
  display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;
  background: #fff; padding: 0.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.fi { padding: 6px 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 0.82rem; background: #fff; }
.fi-wide { flex: 1; min-width: 200px; }
.loading-center { display: flex; justify-content: center; padding: 3rem; }
.empty-state { text-align: center; padding: 2rem; color: #bbb; }
.td-name { font-weight: 600; max-width: 200px; }
.td-coords { font-size: 0.75rem; color: #888; font-family: monospace; }
.btn-toggle {
  padding: 3px 10px; border: 1px solid #e0e0e0; border-radius: 6px;
  font-size: 0.75rem; background: #fafafa; cursor: pointer; font-weight: 600;
}
.btn-toggle.active { background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7; }
.action-btns { display: flex; gap: 4px; }
.btn-action {
  width: 26px; height: 26px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.btn-ok { background: #e8f5e9; color: #2e7d32; }
.btn-ok:hover { background: #c8e6c9; }
.btn-no { background: #ffebee; color: #c62828; }
.btn-no:hover { background: #ffcdd2; }
</style>
