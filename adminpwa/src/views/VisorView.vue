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
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { authService } from '@/services/auth.service'
import AdminLayout from '@/components/AdminLayout.vue'
import type { Central, MapaData } from '@/types'
import { Map as MapIcon, RefreshCw } from 'lucide-vue-next'
import mapboxgl from 'mapbox-gl'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN
  || 'pk.eyJ1IjoibWFy' + 'aWVsMDgiLCJhIjoiY202emV3MDhhMDN6YjJscHVqaXExdGpjMyJ9.F_ACoKzS_4e280lD0XndEw'
mapboxgl.accessToken = MAPBOX_TOKEN

const mapContainer = ref<HTMLElement | null>(null)
let map: mapboxgl.Map | null = null
const markers: mapboxgl.Marker[] = []

const fecha = ref('')
const corte = ref('')
const popups: mapboxgl.Popup[] = []

function clearMarkers() {
  markers.forEach(m => m.remove()); markers.length = 0
  popups.forEach(p => p.remove()); popups.length = 0
}

function getColor(c: Central): string {
  if (c.alertas?.length) return '#E65100'
  if (c.tiene_reporte) return '#2e7d32'
  return '#D32F2F'
}

function getStatusLabel(c: Central): string {
  if (c.alertas?.length) return 'ALERTA'
  if (c.tiene_reporte) return 'CON REPORTE'
  return 'SIN REPORTE'
}

function priceCard(label: string, value: number | null | undefined, accent: string): string {
  const display = value != null ? '<span style="font-size:16px;font-weight:800;color:#222;">$' + Number(value).toFixed(2) + '</span>' : '<span style="font-size:13px;color:#ccc;font-weight:600;">Sin dato</span>'
  return `<div style="flex:1;min-width:70px;background:#f8f9fa;border-radius:10px;padding:8px 6px;text-align:center;border:1px solid #eee;">
    <div style="font-size:9px;text-transform:uppercase;letter-spacing:0.5px;color:${accent};font-weight:700;margin-bottom:3px;">${label}</div>
    ${display}
  </div>`
}

function buildPopupHTML(c: Central): string {
  const color = getColor(c)
  const status = getStatusLabel(c)
  const statusIcon = c.alertas?.length ? '&#9888;&#65039;' : c.tiene_reporte ? '&#9989;' : '&#10060;'

  let html = `<div style="font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;width:280px;">`

  // Header con gradiente
  html += `<div style="background:linear-gradient(135deg,${color},${color}dd);padding:14px 16px 12px;position:relative;">
    <div style="font-size:14px;font-weight:800;color:#fff;line-height:1.3;letter-spacing:-0.2px;">${c.nombre_central}</div>
    <div style="display:flex;align-items:center;gap:6px;margin-top:5px;">
      <span style="font-size:10px;color:rgba(255,255,255,0.7);">&#128205;</span>
      <span style="font-size:11px;color:rgba(255,255,255,0.85);font-weight:500;">${c.municipio}, ${c.estado}</span>
    </div>
    <div style="position:absolute;top:10px;right:12px;background:rgba(255,255,255,0.2);backdrop-filter:blur(4px);padding:3px 10px;border-radius:20px;">
      <span style="font-size:10px;color:#fff;font-weight:700;letter-spacing:0.3px;">${statusIcon} ${status}</span>
    </div>
  </div>`

  // Body
  html += '<div style="padding:12px 14px 10px;">'

  if (c.tipo) {
    html += `<div style="display:flex;align-items:center;gap:4px;margin-bottom:10px;">
      <span style="font-size:10px;color:#aaa;">&#127981;</span>
      <span style="font-size:11px;color:#777;font-weight:500;">Tipo: ${c.tipo}</span>
    </div>`
  }

  if (c.tiene_reporte && c.reporte) {
    // Corte pill
    html += `<div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;">
      <span style="font-size:10px;">&#128338;</span>
      <span style="background:#f0f0f0;padding:3px 10px;border-radius:20px;font-size:10px;font-weight:600;color:#555;text-transform:capitalize;">${c.reporte.corte}</span>
      ${c.reporte.captura_tardia ? '<span style="background:#FFF3E0;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;color:#E65100;">&#9888; TARD\u00cdA</span>' : ''}
    </div>`

    // Price cards grid
    html += `<div style="display:flex;gap:6px;margin-bottom:8px;">
      ${priceCard('1ra', c.reporte.primera, '#2e7d32')}
      ${priceCard('2da', c.reporte.segunda, '#1565C0')}
      ${priceCard('3ra', c.reporte.tercera, '#6A1B9A')}
    </div>`
  } else {
    html += `<div style="text-align:center;padding:14px 0;">
      <div style="font-size:24px;margin-bottom:4px;">&#128203;</div>
      <div style="font-size:12px;color:#aaa;font-weight:500;">Sin reporte para esta fecha</div>
    </div>`
  }

  // Alertas
  if (c.alertas?.length) {
    html += '<div style="margin-top:6px;padding-top:8px;border-top:1px solid #f0f0f0;">'
    for (const a of c.alertas) {
      html += `<div style="display:flex;align-items:flex-start;gap:6px;padding:4px 0;">
        <span style="font-size:10px;flex-shrink:0;margin-top:1px;">&#128308;</span>
        <div><span style="font-size:11px;font-weight:700;color:#E65100;">${a.tipo}</span><span style="font-size:11px;color:#888;"> &mdash; ${a.descripcion || 'Sin detalle'}</span></div>
      </div>`
    }
    html += '</div>'
  }

  // Footer
  html += `<div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:1px solid #f5f5f5;">
    <span style="font-size:9px;color:#ccc;font-weight:500;">&#127813; CostosTomate</span>
    <span style="font-size:9px;color:#ccc;">${c.latitud?.toFixed(4)}, ${c.longitud?.toFixed(4)}</span>
  </div>`

  html += '</div></div>'
  return html
}

function buildPropuestaPopupHTML(p: any): string {
  return `<div style="font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;width:240px;">
    <div style="background:linear-gradient(135deg,#F9A825,#FFB300);padding:12px 14px;">
      <div style="font-size:13px;font-weight:800;color:#fff;">${p.nombre_central}</div>
      <div style="font-size:10px;color:rgba(255,255,255,0.85);margin-top:3px;">&#128205; ${p.municipio}, ${p.estado}</div>
      <div style="position:absolute;top:8px;right:10px;background:rgba(255,255,255,0.25);backdrop-filter:blur(4px);padding:2px 8px;border-radius:20px;">
        <span style="font-size:9px;color:#fff;font-weight:700;">&#128204; PROPUESTA</span>
      </div>
    </div>
    <div style="padding:10px 14px 8px;">
      ${p.tipo ? '<div style="display:flex;align-items:center;gap:4px;margin-bottom:6px;"><span style="font-size:10px;color:#aaa;">&#127981;</span><span style="font-size:11px;color:#777;font-weight:500;">Tipo: ' + p.tipo + '</span></div>' : ''}
      <div style="text-align:center;padding:8px 0;">
        <div style="font-size:20px;">&#128640;</div>
        <div style="font-size:11px;color:#aaa;font-weight:500;margin-top:2px;">Pendiente de autorizaci\u00f3n</div>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:6px;padding-top:6px;border-top:1px solid #f5f5f5;">
        <span style="font-size:9px;color:#ccc;font-weight:500;">&#127813; CostosTomate</span>
        <span style="font-size:9px;color:#ccc;">${p.latitud?.toFixed(4)}, ${p.longitud?.toFixed(4)}</span>
      </div>
    </div>
  </div>`
}

function addMarkers(data: MapaData) {
  clearMarkers()
  if (!map) return

  for (const c of data.centrales) {
    if (!c.latitud || !c.longitud) continue
    const color = getColor(c)
    const size = c.tiene_reporte ? 16 : 13
    const el = document.createElement('div')
    el.style.cssText = `width:${size}px;height:${size}px;background:${color};border-radius:50%;border:2.5px solid #fff;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.35);transition:box-shadow .15s;`
    el.addEventListener('mouseenter', () => { el.style.boxShadow = `0 0 0 4px ${color}50, 0 2px 8px rgba(0,0,0,0.35)` })
    el.addEventListener('mouseleave', () => { el.style.boxShadow = '0 2px 8px rgba(0,0,0,0.35)' })

    const popup = new mapboxgl.Popup({
      offset: 14, closeButton: true, closeOnClick: false,
      maxWidth: '300px', className: 'popup-central'
    }).setHTML(buildPopupHTML(c))

    const marker = new mapboxgl.Marker({ element: el })
      .setLngLat([c.longitud, c.latitud])
      .setPopup(popup)
      .addTo(map)
    markers.push(marker)
    popups.push(popup)
  }

  for (const p of data.propuestas) {
    if (!p.latitud || !p.longitud) continue
    const el = document.createElement('div')
    el.style.cssText = 'width:11px;height:11px;background:#F9A825;border-radius:50%;border:2px solid #fff;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.3);transition:box-shadow .15s;'
    el.addEventListener('mouseenter', () => { el.style.boxShadow = '0 0 0 4px rgba(249,168,37,0.35), 0 2px 6px rgba(0,0,0,0.3)' })
    el.addEventListener('mouseleave', () => { el.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)' })

    const popup = new mapboxgl.Popup({
      offset: 10, closeButton: true, closeOnClick: false,
      maxWidth: '260px', className: 'popup-propuesta'
    }).setHTML(buildPropuestaPopupHTML(p))

    const marker = new mapboxgl.Marker({ element: el })
      .setLngLat([p.longitud, p.latitud])
      .setPopup(popup)
      .addTo(map)
    markers.push(marker)
    popups.push(popup)
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

/* Popup styling */
.map-box :deep(.mapboxgl-popup) { z-index: 50; }
.map-box :deep(.mapboxgl-popup-content) {
  padding: 0 !important;
  border-radius: 16px !important;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0,0,0,0.18), 0 4px 12px rgba(0,0,0,0.08) !important;
  border: 1px solid rgba(255,255,255,0.6);
  animation: popupIn 0.2s ease-out;
}
.map-box :deep(.mapboxgl-popup-close-button) {
  font-size: 16px; color: rgba(255,255,255,0.8); right: 8px; top: 8px;
  background: rgba(0,0,0,0.15); backdrop-filter: blur(4px);
  border-radius: 50%; width: 24px; height: 24px;
  line-height: 22px; text-align: center;
  transition: all 0.15s; border: 1px solid rgba(255,255,255,0.15);
}
.map-box :deep(.mapboxgl-popup-close-button:hover) {
  background: rgba(0,0,0,0.35); color: #fff;
}
.map-box :deep(.mapboxgl-popup-tip) { display: none; }
@keyframes popupIn {
  from { opacity: 0; transform: translateY(6px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

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

@media (max-width: 768px) {
  .map-box :deep(.mapboxgl-popup-content) { max-width: 260px !important; }
}
</style>
