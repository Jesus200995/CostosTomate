<template>
  <AdminLayout>
    <div class="top-bar">
      <div class="top-bar__pattern"></div>
      <div class="top-bar__text">
        <h1 class="top-bar__title"><MapIcon :size="22" /> Mapa</h1>
        <span class="top-bar__subtitle">Ubicación y estado de centrales de abasto</span>
      </div>
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
let activePopup: mapboxgl.Popup | null = null

function clearMarkers() {
  markers.forEach(m => m.remove()); markers.length = 0
  if (activePopup) { activePopup.remove(); activePopup = null }
}

function closeActivePopup() {
  if (activePopup) { activePopup.remove(); activePopup = null }
}

// SVG icon helpers (14x14)
const ICO = {
  pin: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
  check: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  x: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  alert: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  clock: '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  building: '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M8 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M16 14h.01"/></svg>',
  file: '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>',
  send: '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>',
}

function getColor(c: Central): string {
  if (c.alertas?.length) return '#E65100'
  if (c.tiene_reporte) return '#2e7d32'
  return '#D32F2F'
}

function getStatusBadge(c: Central): { icon: string; label: string } {
  if (c.alertas?.length) return { icon: ICO.alert, label: 'Alerta' }
  if (c.tiene_reporte) return { icon: ICO.check, label: 'Con reporte' }
  return { icon: ICO.x, label: 'Sin reporte' }
}

function priceCard(label: string, value: number | null | undefined, accent: string): string {
  const val = value != null
    ? `<div style="font-size:15px;font-weight:800;color:#222;margin-top:2px;">$${Number(value).toFixed(2)}</div>`
    : `<div style="font-size:11px;color:#bbb;font-weight:500;margin-top:4px;">Sin dato</div>`
  return `<div style="flex:1;background:#f8f9fa;border-radius:8px;padding:7px 4px;text-align:center;">
    <div style="font-size:9px;text-transform:uppercase;letter-spacing:0.5px;color:${accent};font-weight:700;">${label}</div>
    ${val}
  </div>`
}

function buildPopupHTML(c: Central): string {
  const color = getColor(c)
  const badge = getStatusBadge(c)
  const F = 'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;'

  let html = `<div style="${F}width:272px;">`

  // Header - nombre on its own line, status BELOW on second row, no overlap
  html += `<div style="background:linear-gradient(135deg,${color},${color}cc);padding:14px 16px 10px;">
    <div style="font-size:13px;font-weight:700;color:#fff;line-height:1.35;padding-right:4px;">${c.nombre_central}</div>
    <div style="display:flex;align-items:center;justify-content:space-between;margin-top:6px;">
      <div style="display:flex;align-items:center;gap:4px;color:rgba(255,255,255,0.8);">${ICO.pin}<span style="font-size:10px;font-weight:500;">${c.municipio}, ${c.estado}</span></div>
      <div style="display:flex;align-items:center;gap:3px;background:rgba(255,255,255,0.18);padding:2px 8px;border-radius:10px;color:#fff;">${badge.icon}<span style="font-size:9px;font-weight:600;">${badge.label}</span></div>
    </div>
  </div>`

  // Body
  html += '<div style="padding:10px 14px 8px;">'

  if (c.tipo) {
    html += `<div style="display:flex;align-items:center;gap:5px;margin-bottom:8px;color:#888;">${ICO.building}<span style="font-size:11px;font-weight:500;">${c.tipo}</span></div>`
  }

  if (c.tiene_reporte && c.reporte) {
    html += `<div style="display:flex;align-items:center;gap:5px;margin-bottom:8px;">
      <span style="color:#888;">${ICO.clock}</span>
      <span style="background:#f0f0f0;padding:2px 9px;border-radius:10px;font-size:10px;font-weight:600;color:#555;text-transform:capitalize;">${c.reporte.corte}</span>
      ${c.reporte.captura_tardia ? '<span style="background:#FFF3E0;padding:2px 8px;border-radius:10px;font-size:9px;font-weight:700;color:#E65100;">Tard\u00eda</span>' : ''}
    </div>`

    html += `<div style="display:flex;gap:5px;margin-bottom:6px;">
      ${priceCard('1ra', c.reporte.primera, '#2e7d32')}
      ${priceCard('2da', c.reporte.segunda, '#1565C0')}
      ${priceCard('3ra', c.reporte.tercera, '#6A1B9A')}
    </div>`
  } else {
    html += `<div style="text-align:center;padding:10px 0;color:#bbb;">
      <div style="margin:0 auto 4px;width:fit-content;">${ICO.file}</div>
      <div style="font-size:11px;font-weight:500;">Sin reporte para esta fecha</div>
    </div>`
  }

  if (c.alertas?.length) {
    html += '<div style="padding-top:6px;border-top:1px solid #f0f0f0;">'
    for (const a of c.alertas) {
      html += `<div style="display:flex;align-items:center;gap:5px;padding:3px 0;">
        <span style="color:#E65100;flex-shrink:0;">${ICO.alert}</span>
        <span style="font-size:10px;"><b style="color:#E65100;">${a.tipo}</b> <span style="color:#999;">${a.descripcion || ''}</span></span>
      </div>`
    }
    html += '</div>'
  }

  html += `<div style="display:flex;justify-content:flex-end;margin-top:6px;padding-top:5px;border-top:1px solid #f5f5f5;">
    <span style="font-size:9px;color:#ccc;">${c.latitud?.toFixed(4)}, ${c.longitud?.toFixed(4)}</span>
  </div>`

  html += '</div></div>'
  return html
}

function buildPropuestaPopupHTML(p: any): string {
  const F = 'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;'
  return `<div style="${F}width:240px;">
    <div style="background:linear-gradient(135deg,#F9A825,#FFB300);padding:12px 14px 10px;">
      <div style="font-size:13px;font-weight:700;color:#fff;line-height:1.3;">${p.nombre_central}</div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:5px;">
        <div style="display:flex;align-items:center;gap:4px;color:rgba(255,255,255,0.8);">${ICO.pin}<span style="font-size:10px;">${p.municipio}, ${p.estado}</span></div>
        <div style="display:flex;align-items:center;gap:3px;background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:10px;color:#fff;">${ICO.send}<span style="font-size:9px;font-weight:600;">Propuesta</span></div>
      </div>
    </div>
    <div style="padding:10px 14px 8px;">
      ${p.tipo ? '<div style="display:flex;align-items:center;gap:5px;margin-bottom:6px;color:#888;">' + ICO.building + '<span style="font-size:11px;">' + p.tipo + '</span></div>' : ''}
      <div style="text-align:center;padding:6px 0;color:#bbb;">
        <div style="font-size:11px;font-weight:500;">Pendiente de autorizaci\u00f3n</div>
      </div>
      <div style="display:flex;justify-content:flex-end;padding-top:5px;border-top:1px solid #f5f5f5;">
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
      offset: 16, closeButton: true, closeOnClick: true,
      maxWidth: '300px'
    }).setHTML(buildPopupHTML(c))

    el.addEventListener('click', () => { closeActivePopup(); popup.addTo(map!); activePopup = popup })

    const marker = new mapboxgl.Marker({ element: el })
      .setLngLat([c.longitud, c.latitud])
      .setPopup(popup)
      .addTo(map)
    markers.push(marker)
  }

  for (const p of data.propuestas) {
    if (!p.latitud || !p.longitud) continue
    const el = document.createElement('div')
    el.style.cssText = 'width:11px;height:11px;background:#F9A825;border-radius:50%;border:2px solid #fff;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.3);transition:box-shadow .15s;'
    el.addEventListener('mouseenter', () => { el.style.boxShadow = '0 0 0 4px rgba(249,168,37,0.35), 0 2px 6px rgba(0,0,0,0.3)' })
    el.addEventListener('mouseleave', () => { el.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)' })

    const popup = new mapboxgl.Popup({
      offset: 14, closeButton: true, closeOnClick: true,
      maxWidth: '260px'
    }).setHTML(buildPropuestaPopupHTML(p))

    el.addEventListener('click', () => { closeActivePopup(); popup.addTo(map!); activePopup = popup })

    const marker = new mapboxgl.Marker({ element: el })
      .setLngLat([p.longitud, p.latitud])
      .setPopup(popup)
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
.map-box :deep(.mapboxgl-popup-tip) {
  border-width: 10px; margin-top: -1px;
}
@keyframes popupIn {
  from { opacity: 0; transform: translateY(6px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.top-bar {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
  background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px;
  padding: 1rem 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2);
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
.top-bar__actions { display: flex; align-items: center; gap: 0.5rem; position: relative; z-index: 1; }
.btn-refresh { position: relative; z-index: 1; }
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
