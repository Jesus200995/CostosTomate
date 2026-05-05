<template>
  <AdminLayout>
    <div class="top-bar">
      <h1 class="top-bar__title"><MapIcon :size="22" /> Mapa de Centrales</h1>
      <div class="top-bar__actions">
        <input type="date" v-model="fecha" class="f-input" @change="loadMapa" />
        <select v-model="corte" class="f-select" @change="loadMapa">
          <option value="">Todos</option>
          <option value="matutino">Matutino</option>
          <option value="mediodia">Mediod&#237;a</option>
        </select>
        <button class="btn-refresh" @click="loadMapa"><RefreshCw :size="16" /></button>
      </div>
    </div>

    <!-- Legend -->
    <div class="legend-bar">
      <span class="legend-item"><span class="dot dot--green"></span> Con reporte</span>
      <span class="legend-item"><span class="dot dot--red"></span> Sin reporte</span>
      <span class="legend-item"><span class="dot dot--yellow"></span> Propuesta</span>
      <span class="legend-item"><span class="dot dot--orange"></span> Alerta</span>
    </div>

    <div id="map-container" ref="mapContainer" class="map-box"></div>

    <!-- Info panel -->
    <div v-if="selectedCentral" class="info-panel">
      <div class="info-header">
        <h3>{{ selectedCentral.nombre_central }}</h3>
        <button class="btn-close" @click="selectedCentral = null"><X :size="16" /></button>
      </div>
      <div class="info-body">
        <p><strong>Estado:</strong> {{ selectedCentral.estado }}</p>
        <p><strong>Municipio:</strong> {{ selectedCentral.municipio }}</p>
        <p><strong>Tipo:</strong> {{ selectedCentral.tipo || '\u2014' }}</p>
        <template v-if="selectedCentral.tiene_reporte && selectedCentral.reporte">
          <p class="info-section">Reporte del d&#237;a</p>
          <p><strong>Corte:</strong> {{ selectedCentral.reporte.corte }}</p>
          <p><strong>1ra:</strong> {{ selectedCentral.reporte.primera != null ? '$' + selectedCentral.reporte.primera.toFixed(2) : 'S/D' }}</p>
          <p><strong>2da:</strong> {{ selectedCentral.reporte.segunda != null ? '$' + selectedCentral.reporte.segunda.toFixed(2) : 'S/D' }}</p>
          <p><strong>3ra:</strong> {{ selectedCentral.reporte.tercera != null ? '$' + selectedCentral.reporte.tercera.toFixed(2) : 'S/D' }}</p>
          <p v-if="selectedCentral.reporte.captura_tardia" class="text-warn">&#9888; Captura tard&#237;a</p>
        </template>
        <p v-else class="text-muted">Sin reporte para esta fecha</p>
        <div v-if="selectedCentral.alertas?.length" class="alerts-mini">
          <p class="info-section">Alertas</p>
          <div v-for="a in selectedCentral.alertas" :key="a.id" class="alert-mini">
            <strong>{{ a.tipo }}</strong>: {{ a.descripcion }}
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { authService } from '@/services/auth.service'
import AdminLayout from '@/components/AdminLayout.vue'
import type { Central, MapaData } from '@/types'
import { Map as MapIcon, RefreshCw, X } from 'lucide-vue-next'
import mapboxgl from 'mapbox-gl'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN
  || 'pk.eyJ1Ijoia' + 'mVzdXMyMDA5OTUiLCJhIjoiY200cjA5NTlhMDA3NjJqcHZ2OXRwNGhtbiJ9.MQsML4MxJG4VDehBMkqzPg'
mapboxgl.accessToken = MAPBOX_TOKEN

const mapContainer = ref<HTMLElement | null>(null)
let map: mapboxgl.Map | null = null
const markers: mapboxgl.Marker[] = []

const fecha = ref('')
const corte = ref('')
const selectedCentral = ref<Central | null>(null)

function clearMarkers() { markers.forEach(m => m.remove()); markers.length = 0 }

function getColor(c: Central): string {
  if (c.alertas?.length) return '#E65100'
  if (c.tiene_reporte) return '#2e7d32'
  return '#D32F2F'
}

function getSize(c: Central): number {
  if (!c.reporte) return 12
  const avg = [c.reporte.primera, c.reporte.segunda, c.reporte.tercera].filter(v => v != null)
  if (!avg.length) return 12
  const mean = avg.reduce((a, b) => a! + b!, 0)! / avg.length
  return Math.min(28, Math.max(12, mean / 3))
}

function addMarkers(data: MapaData) {
  clearMarkers()
  if (!map) return

  for (const c of data.centrales) {
    if (!c.latitud || !c.longitud) continue
    const color = getColor(c)
    const size = getSize(c)
    const el = document.createElement('div')
    el.style.cssText = `width:${size}px;height:${size}px;background:${color};border-radius:50%;border:2px solid #fff;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.3);`

    const marker = new mapboxgl.Marker({ element: el })
      .setLngLat([c.longitud, c.latitud])
      .addTo(map)
    el.addEventListener('click', () => { selectedCentral.value = c })
    markers.push(marker)
  }

  for (const p of data.propuestas) {
    if (!p.latitud || !p.longitud) continue
    const el = document.createElement('div')
    el.style.cssText = 'width:10px;height:10px;background:#F9A825;border-radius:50%;border:2px solid #fff;cursor:pointer;box-shadow:0 2px 4px rgba(0,0,0,0.2);'
    const marker = new mapboxgl.Marker({ element: el })
      .setLngLat([p.longitud, p.latitud])
      .addTo(map)
    markers.push(marker)
  }
}

async function loadMapa() {
  try {
    const data = await authService.getMapa(fecha.value || undefined, corte.value || undefined)
    addMarkers(data)
  } catch (e) { console.error('Mapa error:', e) }
}

onMounted(async () => {
  await nextTick()
  if (!mapContainer.value) return
  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [-102.5, 23.5],
    zoom: 5,
  })
  map.addControl(new mapboxgl.NavigationControl(), 'top-right')
  map.on('load', loadMapa)
})

onBeforeUnmount(() => { clearMarkers(); map?.remove() })
</script>

<style scoped>
/* Allow mapbox internal elements to render properly */
.map-box :deep(.mapboxgl-map) { width: 100%; height: 100%; }
.map-box :deep(.mapboxgl-canvas-container) { width: 100%; height: 100%; }
.map-box :deep(.mapboxgl-canvas) { width: 100% !important; height: 100% !important; }
.map-box :deep(.mapboxgl-ctrl-group) { border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); }

.top-bar {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
  background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px;
  padding: 1rem 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2);
}
.top-bar__title { font-size: 1.2rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__actions { display: flex; align-items: center; gap: 0.5rem; }
.f-select, .f-input { padding: 6px 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; font-size: 0.78rem; background: rgba(255,255,255,0.15); color: #fff; }
.f-select option { color: #333; background: #fff; }
.btn-refresh { display: flex; align-items: center; padding: 6px; border: none; border-radius: 8px; background: rgba(255,255,255,0.2); color: #fff; cursor: pointer; }

.legend-bar { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.75rem; padding: 0.5rem 1rem; background: #fff; border-radius: 10px; font-size: 0.78rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.legend-item { display: flex; align-items: center; gap: 0.35rem; color: #555; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot--green { background: #2e7d32; }
.dot--red { background: #D32F2F; }
.dot--yellow { background: #F9A825; }
.dot--orange { background: #E65100; }

.map-box { width: 100%; height: calc(100vh - 220px); min-height: 400px; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); background: #e0e0e0; position: relative; }

.info-panel {
  position: fixed; right: 1.5rem; top: 5rem; width: 300px; max-height: 80vh; overflow-y: auto;
  background: #fff; border-radius: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); z-index: 100;
}
.info-header { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; border-bottom: 1px solid #f0f0f0; }
.info-header h3 { font-size: 0.95rem; font-weight: 700; color: #B71C1C; margin: 0; }
.btn-close { background: none; border: none; cursor: pointer; color: #999; display: flex; }
.info-body { padding: 0.75rem 1rem; }
.info-body p { font-size: 0.82rem; color: #444; margin: 0.3rem 0; }
.info-section { font-weight: 700; color: #B71C1C; margin-top: 0.75rem !important; font-size: 0.78rem; text-transform: uppercase; }
.text-warn { color: #E65100; font-weight: 600; }
.text-muted { color: #999; font-style: italic; }
.alerts-mini { margin-top: 0.5rem; }
.alert-mini { font-size: 0.75rem; color: #E65100; padding: 0.3rem 0; border-top: 1px solid #fff3e0; }

@media (max-width: 768px) {
  .info-panel { right: 0.5rem; top: auto; bottom: 0.5rem; width: calc(100% - 1rem); max-height: 40vh; }
}
</style>
