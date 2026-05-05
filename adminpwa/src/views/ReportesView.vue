<template>
  <AdminLayout>
    <div class="top-bar">
      <h1 class="top-bar__title"><ClipboardList :size="22" /> Reportes Jitomate</h1>
    </div>

    <!-- Filtros -->
    <div class="filters-bar">
      <input type="date" v-model="filtros.fecha_desde" class="fi" placeholder="Desde" />
      <input type="date" v-model="filtros.fecha_hasta" class="fi" placeholder="Hasta" />
      <select v-model="filtros.corte" class="fi">
        <option value="">Corte</option>
        <option value="matutino">Matutino</option>
        <option value="mediodia">Mediodía</option>
      </select>
      <select v-model="filtros.estado" class="fi">
        <option value="">Estado</option>
        <option v-for="e in estados" :key="e">{{ e }}</option>
      </select>
      <input type="text" v-model="filtros.capturista" class="fi" placeholder="Capturista..." />
      <button class="btn btn--primary btn--sm" @click="load">Buscar</button>
    </div>

    <!-- Tabla -->
    <div class="table-container">
      <div v-if="loading" class="loading-center"><span class="spinner"></span></div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Fecha</th><th>Corte</th><th>Central</th><th>Estado</th>
            <th>1ra</th><th>2da</th><th>3ra</th>
            <th>Capturista</th><th>Tardía</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reportes" :key="r.id">
            <td>{{ r.fecha }}</td>
            <td><span class="badge" :class="r.corte === 'matutino' ? 'badge--success' : 'badge--primary'">{{ r.corte }}</span></td>
            <td>{{ r.nombre_central }}</td>
            <td>{{ r.estado }}</td>
            <td>{{ r.sin_dato_primera ? '—' : r.precio_primera != null ? '$' + r.precio_primera.toFixed(2) : '—' }}</td>
            <td>{{ r.sin_dato_segunda ? '—' : r.precio_segunda != null ? '$' + r.precio_segunda.toFixed(2) : '—' }}</td>
            <td>{{ r.sin_dato_tercera ? '—' : r.precio_tercera != null ? '$' + r.precio_tercera.toFixed(2) : '—' }}</td>
            <td>{{ r.capturista_nombre }}</td>
            <td><span v-if="r.captura_tardia" class="badge badge--warning">Tardía</span></td>
          </tr>
          <tr v-if="!reportes.length"><td colspan="9" class="empty-state">Sin reportes</td></tr>
        </tbody>
      </table>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { authService } from '@/services/auth.service'
import AdminLayout from '@/components/AdminLayout.vue'
import type { ReporteJitomate } from '@/types'
import { ClipboardList } from 'lucide-vue-next'

const loading = ref(false)
const reportes = ref<ReporteJitomate[]>([])
const filtros = reactive({ fecha_desde: '', fecha_hasta: '', corte: '', estado: '', capturista: '' })

const estados = computed(() => {
  const s = new Set(reportes.value.map(r => r.estado).filter(Boolean))
  return [...s].sort()
})

async function load() {
  loading.value = true
  try {
    const p: Record<string, string> = {}
    Object.entries(filtros).forEach(([k, v]) => { if (v) p[k] = v })
    reportes.value = await authService.getReportes(p)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.top-bar {
  background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px;
  padding: 1rem 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2);
}
.top-bar__title { font-size: 1.2rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.filters-bar {
  display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;
  background: #fff; padding: 0.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.fi {
  padding: 6px 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 0.82rem;
  background: #fff; min-width: 110px;
}
.loading-center { display: flex; justify-content: center; padding: 3rem; }
.empty-state { text-align: center; padding: 2rem; color: #bbb; }
</style>
