<template>
  <AdminLayout>
    <div class="cap-page">
      <div class="top-bar">
        <div class="top-bar__pattern"></div>
        <div class="top-bar__text">
          <h1 class="top-bar__title"><Users :size="22" /> Capturistas</h1>
          <span class="top-bar__subtitle">Usuarios registrados en la aplicación móvil</span>
        </div>
        <span class="top-bar__count">{{ filtered.length }} de {{ usuarios.length }}</span>
      </div>

      <div class="filters-bar">
        <input type="text" v-model="busqueda" class="fi fi-wide" placeholder="Buscar por nombre o email..." />
      </div>

      <div v-if="loading" class="loading-center"><span class="spinner"></span></div>

      <div v-else class="scroll-table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Nombre</th><th>Email</th><th>CURP</th><th>Tipo</th>
              <th>Estado / Municipio</th><th>Registro</th><th v-if="auth.hasPermiso('capturistas:acciones')" class="th-actions">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filtered" :key="u.id">
              <td class="td-name">{{ u.name }}</td>
              <td>{{ u.email }}</td>
              <td class="td-mono">{{ u.curp || '—' }}</td>
              <td><span class="badge badge--primary">{{ u.tipo_capturista || 'CAPTURISTA' }}</span></td>
              <td>{{ u.estado || '—' }} / {{ getMuniName(u.municipio) }}</td>
              <td>{{ formatDate(u.created_at) }}</td>
              <td v-if="auth.hasPermiso('capturistas:acciones')">
                <div class="actions-cell">
                  <button class="act-btn act-btn--view" title="Ver detalle" @click="openView(u)"><Eye :size="15" /></button>
                  <button class="act-btn act-btn--edit" title="Editar" @click="openEdit(u)"><Pencil :size="15" /></button>
                  <button class="act-btn act-btn--del" title="Eliminar" @click="openDelete(u)"><Trash2 :size="15" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!filtered.length"><td :colspan="auth.hasPermiso('capturistas:acciones') ? 7 : 6" class="empty-state">Sin capturistas</td></tr>
          </tbody>
        </table>
      </div>

      <!-- MODAL: VER DETALLE -->
      <Teleport to="body">
        <div v-if="viewUser" class="overlay" @click.self="viewUser = null">
          <div class="modal modal--view">
            <div class="modal__header">
              <h2>Detalle del capturista</h2>
              <button class="modal__close" @click="viewUser = null"><X :size="18" /></button>
            </div>
            <div class="modal__body">
              <div class="detail-grid">
                <div class="detail-item"><span class="detail-label">Nombre</span><span class="detail-value">{{ viewUser.name }}</span></div>
                <div class="detail-item"><span class="detail-label">Email</span><span class="detail-value">{{ viewUser.email }}</span></div>
                <div class="detail-item"><span class="detail-label">CURP</span><span class="detail-value mono">{{ viewUser.curp || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Tipo</span><span class="detail-value">{{ viewUser.tipo_capturista || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Estado</span><span class="detail-value">{{ viewUser.estado || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Municipio</span><span class="detail-value">{{ getMuniName(viewUser.municipio) }}</span></div>
                <div class="detail-item"><span class="detail-label">Localidad</span><span class="detail-value">{{ viewUser.localidad || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Telefono</span><span class="detail-value">{{ viewUser.telefono || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">CAC</span><span class="detail-value">{{ viewUser.cac_nombre || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Territorio</span><span class="detail-value">{{ viewUser.territorio || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Ruta</span><span class="detail-value">{{ viewUser.ruta || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Correo inst.</span><span class="detail-value">{{ viewUser.correo_institucional || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Rol interno</span><span class="detail-value">{{ viewUser.rol_interno || '—' }}</span></div>
                <div class="detail-item"><span class="detail-label">Registro</span><span class="detail-value">{{ formatDate(viewUser.created_at) }}</span></div>
              </div>
            </div>
            <div class="modal__footer">
              <button class="mbtn mbtn--secondary" @click="viewUser = null">Cerrar</button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- MODAL: EDITAR -->
      <Teleport to="body">
        <div v-if="editUser" class="overlay" @click.self="editUser = null">
          <div class="modal modal--edit">
            <div class="modal__header">
              <h2>Editar capturista</h2>
              <button class="modal__close" @click="editUser = null"><X :size="18" /></button>
            </div>
            <div class="modal__body">
              <div class="form-grid">
                <div class="fg"><label class="fl">Nombre</label><input v-model="editForm.name" class="finput" /></div>
                <div class="fg"><label class="fl">Email</label><input v-model="editForm.email" class="finput" type="email" /></div>
                <div class="fg"><label class="fl">CURP</label><input v-model="editForm.curp" class="finput" /></div>
                <div class="fg">
                  <label class="fl">Tipo capturista</label>
                  <select v-model="editForm.tipo_capturista" class="finput">
                    <option value="">— Seleccionar —</option>
                    <option value="CAPTURISTA">Capturista</option>
                    <option value="SUPERVISOR">Supervisor</option>
                    <option value="COORDINADOR">Coordinador</option>
                  </select>
                </div>
                <div class="fg">
                  <label class="fl">Estado</label>
                  <select v-model="editForm.estado" class="finput" @change="onEstadoChange">
                    <option value="">— Seleccionar estado —</option>
                    <option v-for="e in estados" :key="e.cve_ent" :value="e.nom_ent">{{ e.nom_ent }}</option>
                  </select>
                </div>
                <div class="fg">
                  <label class="fl">Municipio</label>
                  <select v-model="editForm.municipio" class="finput" :disabled="!municipios.length">
                    <option :value="0">— Seleccionar municipio —</option>
                    <option v-for="m in municipios" :key="m.clave_mun" :value="m.clave_mun">{{ m.nomgeo }}</option>
                  </select>
                </div>
                <div class="fg"><label class="fl">Telefono</label><input v-model="editForm.telefono" class="finput" /></div>
                <div class="fg"><label class="fl">Localidad</label><input v-model="editForm.localidad" class="finput" /></div>
                <div class="fg"><label class="fl">CAC nombre</label><input v-model="editForm.cac_nombre" class="finput" /></div>
                <div class="fg"><label class="fl">Territorio</label><input v-model="editForm.territorio" class="finput" /></div>
                <div class="fg"><label class="fl">Ruta</label><input v-model="editForm.ruta" class="finput" /></div>
                <div class="fg"><label class="fl">Correo inst.</label><input v-model="editForm.correo_institucional" class="finput" /></div>
                <div class="fg"><label class="fl">Rol interno</label><input v-model="editForm.rol_interno" class="finput" /></div>
              </div>
            </div>
            <div class="modal__footer">
              <button class="mbtn mbtn--secondary" @click="editUser = null">Cancelar</button>
              <button class="mbtn mbtn--primary" :disabled="saving" @click="saveEdit">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- MODAL: ELIMINAR -->
      <Teleport to="body">
        <div v-if="deleteTarget" class="overlay" @click.self="deleteTarget = null">
          <div class="modal modal--delete">
            <div class="modal__header modal__header--danger">
              <h2>Eliminar capturista</h2>
              <button class="modal__close" @click="deleteTarget = null"><X :size="18" /></button>
            </div>
            <div class="modal__body modal__body--center">
              <div class="del-icon"><Trash2 :size="32" /></div>
              <p class="del-text">Se eliminara permanentemente a:</p>
              <p class="del-name">{{ deleteTarget.name }}</p>
              <p class="del-email">{{ deleteTarget.email }}</p>
              <p class="del-warn">Esta accion no se puede deshacer.</p>
            </div>
            <div class="modal__footer">
              <button class="mbtn mbtn--secondary" @click="deleteTarget = null">Cancelar</button>
              <button class="mbtn mbtn--danger" :disabled="deleting" @click="confirmDelete">{{ deleting ? 'Eliminando...' : 'Eliminar' }}</button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- TOAST -->
      <Teleport to="body">
        <div v-if="toast" :class="['toast-msg', 'toast-msg--' + toast.type]">{{ toast.text }}</div>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/components/AdminLayout.vue'
import type { PWAUser } from '@/types'
import { Users, Eye, Pencil, Trash2, X } from 'lucide-vue-next'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const usuarios = ref<PWAUser[]>([])
const busqueda = ref('')

const viewUser = ref<PWAUser | null>(null)
const editUser = ref<PWAUser | null>(null)
const deleteTarget = ref<PWAUser | null>(null)
const toast = ref<{ text: string; type: string } | null>(null)

const editForm = reactive({
  name: '', email: '', curp: '', tipo_capturista: '', estado: '',
  municipio: 0 as number, telefono: '', localidad: '', cac_nombre: '', territorio: '',
  ruta: '', correo_institucional: '', rol_interno: ''
})

const estados = ref<{ cve_ent: string; nom_ent: string }[]>([])
const municipios = ref<{ clave_mun: number; nomgeo: string; cve_ent: string; territorio: string | null }[]>([])
const allMunicipiosCache = ref<Map<number, string>>(new Map())

const filtered = computed(() => {
  if (!busqueda.value) return usuarios.value
  const q = busqueda.value.toLowerCase()
  return usuarios.value.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q))
})

function formatDate(iso?: string) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

function showToast(text: string, type = 'success') {
  toast.value = { text, type }
  setTimeout(() => { toast.value = null }, 3000)
}

function openView(u: PWAUser) { viewUser.value = u }

function getMuniName(id: number | null | undefined): string {
  if (!id) return '—'
  return allMunicipiosCache.value.get(id) || String(id)
}

async function loadEstados() {
  try { estados.value = await authService.getEstados() } catch (e) { console.error(e) }
}

async function loadMunicipios(estadoName: string) {
  municipios.value = []
  if (!estadoName) return
  const est = estados.value.find(e => e.nom_ent === estadoName)
  if (!est) return
  try {
    const data = await authService.getMunicipios(est.cve_ent)
    municipios.value = data
    for (const m of data) { allMunicipiosCache.value.set(m.clave_mun, m.nomgeo) }
  } catch (e) { console.error(e) }
}

function onEstadoChange() {
  editForm.municipio = 0
  loadMunicipios(editForm.estado)
}

async function openEdit(u: PWAUser) {
  editUser.value = u
  editForm.name = u.name || ''
  editForm.email = u.email || ''
  editForm.curp = u.curp || ''
  editForm.tipo_capturista = u.tipo_capturista || ''
  editForm.estado = u.estado || ''
  editForm.municipio = u.municipio || 0
  editForm.telefono = u.telefono || ''
  editForm.localidad = u.localidad || ''
  editForm.cac_nombre = u.cac_nombre || ''
  editForm.territorio = u.territorio || ''
  editForm.ruta = u.ruta || ''
  editForm.correo_institucional = u.correo_institucional || ''
  editForm.rol_interno = u.rol_interno || ''
  if (u.estado) await loadMunicipios(u.estado)
}

async function saveEdit() {
  if (!editUser.value) return
  saving.value = true
  try {
    const data: Record<string, any> = {}
    for (const [k, v] of Object.entries(editForm)) {
      if (k === 'municipio') { if (v) data[k] = v }
      else if (v) data[k] = v
    }
    await authService.updateUsuarioPWA(editUser.value.id, data)
    editUser.value = null
    showToast('Capturista actualizado')
    await load()
  } catch (e) { showToast('Error al actualizar', 'error') }
  finally { saving.value = false }
}

function openDelete(u: PWAUser) { deleteTarget.value = u }

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await authService.deleteUsuarioPWA(deleteTarget.value.id)
    deleteTarget.value = null
    showToast('Capturista eliminado')
    await load()
  } catch (e) { showToast('Error al eliminar', 'error') }
  finally { deleting.value = false }
}

async function loadMuniNamesForUsers(users: PWAUser[]) {
  const usedEstados = new Set(users.map(u => u.estado).filter(Boolean) as string[])
  const promises = []
  for (const estName of usedEstados) {
    const est = estados.value.find(e => e.nom_ent === estName)
    if (!est) continue
    promises.push(
      authService.getMunicipios(est.cve_ent).then(munis => {
        for (const m of munis) allMunicipiosCache.value.set(m.clave_mun, m.nomgeo)
      }).catch(() => {})
    )
  }
  await Promise.all(promises)
}

async function load() {
  loading.value = true
  try {
    await loadEstados()
    const users = await authService.getUsuariosPWA()
    await loadMuniNamesForUsers(users)
    usuarios.value = users
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
/* Page layout: fill height, no outer scroll */
.cap-page {
  display: flex; flex-direction: column; height: calc(100vh - 48px); overflow: hidden;
}
.top-bar {
  display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
  background: linear-gradient(135deg, #B71C1C, #D32F2F); border-radius: 14px;
  padding: 0.85rem 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 4px 16px rgba(183,28,28,0.2);
  position: relative; overflow: hidden;
}
.top-bar__pattern {
  position: absolute; inset: 0; pointer-events: none; border-radius: 14px; overflow: hidden;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cellipse cx='16' cy='20' rx='9' ry='8' fill='none' stroke='%23600000' stroke-width='1.2' opacity='0.55'/%3E%3Cline x1='16' y1='12' x2='16' y2='8' stroke='%23600000' stroke-width='1.1' stroke-linecap='round' opacity='0.55'/%3E%3Cpath d='M16,11 C13,9 10,9.5 9.5,11.5' fill='none' stroke='%23600000' stroke-width='1' stroke-linecap='round' opacity='0.55'/%3E%3Cpath d='M16,11 C19,9 22,9.5 22.5,11.5' fill='none' stroke='%23600000' stroke-width='1' stroke-linecap='round' opacity='0.55'/%3E%3Cpath d='M16,10.5 C15.5,7.5 15,5.5 16,4.5 C17,5.5 16.5,7.5 16,10.5' fill='none' stroke='%23600000' stroke-width='1' stroke-linecap='round' opacity='0.55'/%3E%3C/svg%3E");
  background-size: 32px 32px;
  background-repeat: repeat;
}
.top-bar__text { display: flex; flex-direction: column; gap: 2px; position: relative; z-index: 1; }
.top-bar__title { font-size: 1.15rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__subtitle { font-size: 0.75rem; color: rgba(255,255,255,0.75); font-weight: 400; padding-left: 2px; }
.top-bar__count { font-size: 0.8rem; color: rgba(255,255,255,0.9); background: rgba(255,255,255,0.18); padding: 3px 10px; border-radius: 8px; position: relative; z-index: 1; }
.filters-bar {
  display: flex; gap: 0.5rem; flex-shrink: 0; margin-bottom: 0.75rem;
  background: #fff; padding: 0.6rem 0.75rem; border-radius: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.fi { padding: 6px 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 0.82rem; outline: none; transition: border-color .15s; }
.fi:focus { border-color: #D32F2F; }
.fi-wide { flex: 1; }
.loading-center { display: flex; justify-content: center; padding: 3rem; }

/* Scrollable table container */
.scroll-table-wrap {
  flex: 1; overflow-y: auto; overflow-x: auto;
  background: #fff; border-radius: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.table thead { position: sticky; top: 0; z-index: 2; }
.table th {
  padding: 0.7rem 0.85rem; text-align: left; font-weight: 600; font-size: 0.78rem;
  color: #666; background: #fafafa; border-bottom: 1px solid #eee; white-space: nowrap;
}
.table td { padding: 0.65rem 0.85rem; border-bottom: 1px solid #f5f5f5; color: #444; white-space: nowrap; }
.table tbody tr:hover { background: #fef8f8; }
.th-actions { text-align: center; width: 120px; }
.empty-state { text-align: center; padding: 2rem; color: #bbb; }
.td-name { font-weight: 600; color: #222; }
.td-mono { font-family: monospace; font-size: 0.78rem; }

/* Action buttons */
.actions-cell { display: flex; align-items: center; justify-content: center; gap: 6px; }
.act-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border: none; border-radius: 10px;
  cursor: pointer; transition: all .15s;
}
.act-btn--view { background: #E3F2FD; color: #1565C0; }
.act-btn--view:hover { background: #BBDEFB; }
.act-btn--edit { background: #FFF8E1; color: #F57F17; }
.act-btn--edit:hover { background: #FFF3C4; }
.act-btn--del { background: #FFEBEE; color: #C62828; }
.act-btn--del:hover { background: #FFCDD2; }

/* ── Overlay & Modal (Apple 2026 style) ── */
.overlay {
  position: fixed; inset: 0; z-index: 9000;
  background: rgba(0,0,0,0.35); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
  animation: fadeIn .2s ease;
}
.modal {
  background: #fff; border-radius: 20px; width: 100%; max-height: 90vh;
  display: flex; flex-direction: column;
  box-shadow: 0 24px 80px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.08);
  animation: modalIn .25s ease;
}
.modal--view { max-width: 520px; }
.modal--edit { max-width: 560px; }
.modal--delete { max-width: 400px; }

.modal__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.1rem 1.5rem; border-bottom: 1px solid #f0f0f0; flex-shrink: 0;
}
.modal__header h2 { font-size: 1.05rem; font-weight: 700; color: #222; margin: 0; }
.modal__header--danger h2 { color: #C62828; }
.modal__close {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border: none; border-radius: 50%;
  background: #f5f5f5; color: #888; cursor: pointer; transition: all .15s;
}
.modal__close:hover { background: #eee; color: #333; }

.modal__body { padding: 1.25rem 1.5rem; overflow-y: auto; flex: 1; }
.modal__body--center { text-align: center; }

.modal__footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 0.6rem;
  padding: 1rem 1.5rem; border-top: 1px solid #f0f0f0; flex-shrink: 0;
}

/* Detail grid */
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }
.detail-item { display: flex; flex-direction: column; }
.detail-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.4px; color: #aaa; font-weight: 600; margin-bottom: 2px; }
.detail-value { font-size: 0.88rem; color: #333; font-weight: 500; }
.detail-value.mono { font-family: monospace; font-size: 0.82rem; }

/* Form grid */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.fg { display: flex; flex-direction: column; }
.fl { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.3px; color: #999; font-weight: 600; margin-bottom: 3px; }
.finput {
  padding: 8px 12px; border: 1.5px solid #e8e8e8; border-radius: 10px;
  font-size: 0.88rem; color: #333; background: #fafafa; outline: none; transition: all .15s;
}
.finput:focus { border-color: #D32F2F; background: #fff; box-shadow: 0 0 0 3px rgba(211,47,47,0.08); }
select.finput { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; padding-right: 28px; }
select.finput:disabled { opacity: 0.45; cursor: not-allowed; }

/* Modal buttons */
.mbtn {
  padding: 8px 20px; border: none; border-radius: 12px; font-size: 0.88rem;
  font-weight: 600; cursor: pointer; transition: all .15s;
}
.mbtn:disabled { opacity: 0.5; cursor: not-allowed; }
.mbtn--primary { background: #D32F2F; color: #fff; }
.mbtn--primary:hover:not(:disabled) { background: #B71C1C; }
.mbtn--secondary { background: #f0f0f0; color: #555; }
.mbtn--secondary:hover { background: #e4e4e4; }
.mbtn--danger { background: #C62828; color: #fff; }
.mbtn--danger:hover:not(:disabled) { background: #B71C1C; }

/* Delete modal content */
.del-icon { color: #C62828; margin-bottom: 0.75rem; }
.del-text { font-size: 0.9rem; color: #666; margin: 0 0 0.35rem; }
.del-name { font-size: 1.05rem; font-weight: 700; color: #222; margin: 0; }
.del-email { font-size: 0.85rem; color: #888; margin: 0 0 0.75rem; }
.del-warn { font-size: 0.78rem; color: #C62828; font-weight: 600; margin: 0; padding: 6px 12px; background: #FFEBEE; border-radius: 8px; display: inline-block; }

/* Toast */
.toast-msg {
  position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  padding: 10px 24px; border-radius: 14px; font-size: 0.88rem; font-weight: 600;
  z-index: 10000; animation: slideUp .3s ease; box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.toast-msg--success { background: #2e7d32; color: #fff; }
.toast-msg--error { background: #C62828; color: #fff; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes modalIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(16px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .cap-page { height: calc(100vh - 56px); }
  .detail-grid, .form-grid { grid-template-columns: 1fr; }
  .modal { border-radius: 16px; margin: 0.5rem; }
  .table th, .table td { padding: 0.5rem 0.6rem; font-size: 0.78rem; }
  .act-btn { width: 28px; height: 28px; border-radius: 8px; }
}
</style>
