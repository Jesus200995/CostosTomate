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

function fmt(v: number | null | undefined): string {
  return v != null ? '$' + Number(v).toFixed(2) : '<span style="color:#999">S/D</span>'
}

function buildPopupHTML(c: Central): string {
  const color = getColor(c)
  const status = getStatusLabel(c)
  let html = `
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;min-width:220px;max-width:280px;">
      <div style="background:${color};color:#fff;padding:10px 14px;border-radius:12px 12px 0 0;margin:-10px -10px 0;">
        <div style="font-size:13px;font-weight:700;line-height:1.3;">&#127813; ${c.nombre_central}</div>
        <div style="font-size:10px;opacity:0.85;margin-top:2px;">${c.estado} &middot; ${c.municipio}</div>
      </div>
      <div style="padding:10px 4px 4px;">
        <div style="display:inline-block;background:${color}20;color:${color};font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;margin-bottom:8px;">${status}</div>`

  if (c.tipo) {
    html += `<div style="font-size:11px;color:#888;margin-bottom:6px;">Tipo: ${c.tipo}</div>`
  }

  if (c.tiene_reporte && c.reporte) {
    html += `
      <div style="font-size:11px;font-weight:700;color:#B71C1C;text-transform:uppercase;margin:8px 0 4px;border-top:1px solid #f0f0f0;padding-top:6px;">Reporte &mdash; ${c.reporte.corte}</div>
      <table style="width:100%;font-size:12px;border-collapse:collapse;">
        <tr style="background:#fafafa;"><td style="padding:4px 6px;font-weight:600;color:#555;">1ra calidad</td><td style="padding:4px 6px;text-align:right;font-weight:700;color:#333;">${fmt(c.reporte.primera)}</td></tr>
        <tr><td style="padding:4px 6px;font-weight:600;color:#555;">2da calidad</td><td style="padding:4px 6px;text-align:right;font-weight:700;color:#333;">${fmt(c.reporte.segunda)}</td></tr>
        <tr style="background:#fafafa;"><td style="padding:4px 6px;font-weight:600;color:#555;">3ra calidad</td><td style="padding:4px 6px;text-align:right;font-weight:700;color:#333;">${fmt(c.reporte.tercera)}</td></tr>
      </table>`
    if (c.reporte.captura_tardia) {
      html += `<div style="font-size:11px;color:#E65100;font-weight:600;margin-top:6px;">&#9888; Captura tard\u00eda</div>`
    }
  } else {
    html += `<div style="font-size:12px;color:#999;font-style:italic;margin-top:6px;">Sin reporte para esta fecha</div>`
  }

  if (c.alertas?.length) {
    html += `<div style="font-size:11px;font-weight:700;color:#E65100;text-transform:uppercase;margin:8px 0 4px;border-top:1px solid #f0f0f0;padding-top:6px;">Alertas (${c.alertas.length})</div>`
    for (const a of c.alertas) {
      html += `<div style="font-size:11px;color:#E65100;padding:2px 0;">&bull; <strong>${a.tipo}</strong>: ${a.descripcion || ''}</div>`
    }
  }

  html += `
        <div style="font-size:10px;color:#bbb;margin-top:8px;text-align:right;">${c.latitud?.toFixed(4)}, ${c.longitud?.toFixed(4)}</div>
      </div>
    </div>`
  return html
}

function buildPropuestaPopupHTML(p: any): string {
  return `
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;min-width:180px;">
      <div style="background:#F9A825;color:#fff;padding:8px 12px;border-radius:12px 12px 0 0;margin:-10px -10px 0;">
        <div style="font-size:12px;font-weight:700;">&#128204; ${p.nombre_central}</div>
        <div style="font-size:10px;opacity:0.9;">${p.estado} &middot; ${p.municipio}</div>
      </div>
      <div style="padding:8px 4px 4px;">
        <div style="display:inline-block;background:#FFF8E1;color:#F57F17;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;">PROPUESTA</div>
        ${p.tipo ? '<div style="font-size:11px;color:#888;margin-top:4px;">Tipo: ' + p.tipo + '</div>' : ''}
        <div style="font-size:10px;color:#bbb;margin-top:6px;text-align:right;">${p.latitud?.toFixed(4)}, ${p.longitud?.toFixed(4)}</div>
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
    el.style.cssText = `width:${size}px;height:${size}px;background:${color};border-radius:50%;border:2.5px solid #fff;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.35);transition:transform .15s;`
    el.addEventListener('mouseenter', () => { el.style.transform = 'scale(1.4)' })
    el.addEventListener('mouseleave', () => { el.style.transform = 'scale(1)' })

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
    el.style.cssText = 'width:11px;height:11px;background:#F9A825;border-radius:50%;border:2px solid #fff;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.3);transition:transform .15s;'
    el.addEventListener('mouseenter', () => { el.style.transform = 'scale(1.4)' })
    el.addEventListener('mouseleave', () => { el.style.transform = 'scale(1)' })

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
.map-box :deep(.mapboxgl-popup-content) {
  padding: 0 !important; border-radius: 14px !important; overflow: hidden;
  box-shadow: 0 8px 30px rgba(0,0,0,0.2) !important;
}
.map-box :deep(.mapboxgl-popup-close-button) {
  font-size: 18px; color: #fff; right: 6px; top: 6px; background: rgba(0,0,0,0.2);
  border-radius: 50%; width: 22px; height: 22px; line-height: 20px; text-align: center;
}
.map-box :deep(.mapboxgl-popup-close-button:hover) { background: rgba(0,0,0,0.4); }
.map-box :deep(.mapboxgl-popup-tip) { border-top-color: transparent; }

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
