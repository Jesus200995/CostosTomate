<template>
  <AdminLayout>
    <div class="perm-page">
      <div class="top-bar">
        <h1 class="top-bar__title"><ShieldCheck :size="22" /> Permisos de Usuarios</h1>
        <span class="top-bar__count">{{ filtered.length }} de {{ usuarios.length }}</span>
      </div>

      <div class="filters-bar">
        <input type="text" v-model="busqueda" class="fi fi-wide" placeholder="Buscar por nombre o correo..." />
        <select v-model="filtroRol" class="fi">
          <option value="">Todos los roles</option>
          <option value="administrador">Administrador</option>
          <option value="usuario">Usuario</option>
        </select>
        <select v-model="filtroEstatus" class="fi">
          <option value="">Todos los estatus</option>
          <option value="activo">Activo</option>
          <option value="inactivo">Inactivo</option>
        </select>
      </div>

      <div v-if="loading" class="loading-center"><span class="spinner"></span></div>

      <div v-else class="scroll-table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Teléfono</th>
              <th>Rol</th>
              <th>Estatus</th>
              <th>Registro</th>
              <th class="th-actions">Permisos</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filtered" :key="u.id">
              <td class="td-name">{{ u.nombre }} {{ u.apellido_paterno }} {{ u.apellido_materno }}</td>
              <td>{{ u.correo }}</td>
              <td>{{ u.telefono }}</td>
              <td>
                <span class="badge" :class="u.rol === 'administrador' ? 'badge--admin' : 'badge--user'">
                  <ShieldCheck v-if="u.rol === 'administrador'" :size="11" />
                  <User v-else :size="11" />
                  {{ u.rol === 'administrador' ? 'Admin' : 'Usuario' }}
                </span>
              </td>
              <td>
                <span class="badge" :class="u.estatus === 'activo' ? 'badge--active' : 'badge--inactive'">
                  {{ u.estatus }}
                </span>
              </td>
              <td>{{ formatDate(u.created_at) }}</td>
              <td>
                <div class="actions-cell">
                  <button class="act-btn act-btn--info" title="Ver detalle" @click="openView(u)">
                    <Eye :size="14" />
                  </button>
                  <button
                    class="act-btn"
                    :class="u.rol === 'administrador' ? 'act-btn--demote' : 'act-btn--promote'"
                    :title="u.rol === 'administrador' ? 'Quitar admin' : 'Hacer admin'"
                    :disabled="u.id === auth.user?.id"
                    @click="openRolModal(u)"
                  >
                    <ShieldCheck v-if="u.rol !== 'administrador'" :size="14" />
                    <ShieldOff v-else :size="14" />
                  </button>
                  <button
                    class="act-btn"
                    :class="u.estatus === 'activo' ? 'act-btn--deactivate' : 'act-btn--activate'"
                    :title="u.estatus === 'activo' ? 'Desactivar' : 'Activar'"
                    :disabled="u.id === auth.user?.id"
                    @click="toggleEstatus(u)"
                  >
                    <UserCheck v-if="u.estatus !== 'activo'" :size="14" />
                    <UserX v-else :size="14" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7" class="empty-state">Sin usuarios registrados</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- MODAL: VER DETALLE -->
      <Teleport to="body">
        <div v-if="viewUser" class="overlay" @click.self="viewUser = null">
          <div class="modal modal--view">
            <div class="modal__header">
              <h2>Detalle del usuario</h2>
              <button class="modal__close" @click="viewUser = null"><X :size="18" /></button>
            </div>
            <div class="modal__body">
              <div class="user-card">
                <div class="user-card__avatar">
                  {{ initials(viewUser) }}
                </div>
                <div class="user-card__name">{{ viewUser.nombre }} {{ viewUser.apellido_paterno }} {{ viewUser.apellido_materno }}</div>
                <div class="user-card__badges">
                  <span class="badge" :class="viewUser.rol === 'administrador' ? 'badge--admin' : 'badge--user'">
                    {{ viewUser.rol }}
                  </span>
                  <span class="badge" :class="viewUser.estatus === 'activo' ? 'badge--active' : 'badge--inactive'">
                    {{ viewUser.estatus }}
                  </span>
                </div>
              </div>
              <div class="detail-grid">
                <div class="detail-item"><span class="detail-label">Correo</span><span class="detail-value">{{ viewUser.correo }}</span></div>
                <div class="detail-item"><span class="detail-label">Teléfono</span><span class="detail-value">{{ viewUser.telefono }}</span></div>
                <div class="detail-item"><span class="detail-label">CURP</span><span class="detail-value mono">{{ viewUser.curp }}</span></div>
                <div class="detail-item"><span class="detail-label">Registro</span><span class="detail-value">{{ formatDate(viewUser.created_at) }}</span></div>
              </div>
            </div>
            <div class="modal__footer">
              <button class="mbtn mbtn--secondary" @click="viewUser = null">Cerrar</button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- MODAL: CAMBIO DE ROL -->
      <Teleport to="body">
        <div v-if="rolTarget" class="overlay" @click.self="rolTarget = null">
          <div class="modal modal--confirm">
            <div class="modal__header" :class="rolTarget.rol === 'administrador' ? 'modal__header--warning' : 'modal__header--promote'">
              <h2>{{ rolTarget.rol === 'administrador' ? 'Quitar permisos de Admin' : 'Otorgar permisos de Admin' }}</h2>
              <button class="modal__close" @click="rolTarget = null"><X :size="18" /></button>
            </div>
            <div class="modal__body modal__body--center">
              <div class="confirm-icon" :class="rolTarget.rol === 'administrador' ? 'confirm-icon--warning' : 'confirm-icon--promote'">
                <ShieldOff v-if="rolTarget.rol === 'administrador'" :size="32" />
                <ShieldCheck v-else :size="32" />
              </div>
              <p class="confirm-text">
                {{ rolTarget.rol === 'administrador'
                  ? '¿Quitar permisos de administrador a:'
                  : '¿Otorgar permisos de administrador a:' }}
              </p>
              <p class="confirm-name">{{ rolTarget.nombre }} {{ rolTarget.apellido_paterno }}</p>
              <p class="confirm-warn" v-if="rolTarget.rol === 'administrador'">
                Este usuario perderá acceso al panel de administración.
              </p>
              <p class="confirm-warn confirm-warn--green" v-else>
                Este usuario tendrá acceso completo al panel de administración.
              </p>
            </div>
            <div class="modal__footer">
              <button class="mbtn mbtn--secondary" @click="rolTarget = null">Cancelar</button>
              <button
                class="mbtn"
                :class="rolTarget.rol === 'administrador' ? 'mbtn--warning' : 'mbtn--promote'"
                :disabled="saving"
                @click="confirmRol"
              >{{ saving ? 'Guardando...' : (rolTarget.rol === 'administrador' ? 'Quitar Admin' : 'Hacer Admin') }}</button>
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
import { ref, computed, onMounted } from 'vue'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/components/AdminLayout.vue'
import type { AdminUser } from '@/types'
import { ShieldCheck, ShieldOff, Eye, User, UserCheck, UserX, X } from 'lucide-vue-next'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const usuarios = ref<AdminUser[]>([])
const busqueda = ref('')
const filtroRol = ref('')
const filtroEstatus = ref('')

const viewUser = ref<AdminUser | null>(null)
const rolTarget = ref<AdminUser | null>(null)
const toast = ref<{ text: string; type: string } | null>(null)

const filtered = computed(() => {
  return usuarios.value.filter(u => {
    const q = busqueda.value.toLowerCase()
    const matchQ = !q || u.nombre.toLowerCase().includes(q) || u.correo.toLowerCase().includes(q)
    const matchRol = !filtroRol.value || u.rol === filtroRol.value
    const matchEst = !filtroEstatus.value || u.estatus === filtroEstatus.value
    return matchQ && matchRol && matchEst
  })
})

function formatDate(iso?: string) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

function initials(u: AdminUser) {
  return ((u.nombre?.[0] || '') + (u.apellido_paterno?.[0] || '')).toUpperCase()
}

function showToast(text: string, type = 'success') {
  toast.value = { text, type }
  setTimeout(() => { toast.value = null }, 3000)
}

function openView(u: AdminUser) { viewUser.value = u }
function openRolModal(u: AdminUser) { rolTarget.value = u }

async function toggleEstatus(u: AdminUser) {
  const nuevo = u.estatus === 'activo' ? 'inactivo' : 'activo'
  try {
    const updated = await authService.updateEstatus(u.id, nuevo)
    Object.assign(u, updated)
    showToast(`Usuario ${nuevo === 'activo' ? 'activado' : 'desactivado'}`)
  } catch (e) { showToast('Error al cambiar estatus', 'error') }
}

async function confirmRol() {
  if (!rolTarget.value) return
  saving.value = true
  const nuevoRol = rolTarget.value.rol === 'administrador' ? 'usuario' : 'administrador'
  try {
    const updated = await authService.updateRol(rolTarget.value.id, nuevoRol)
    const idx = usuarios.value.findIndex(u => u.id === rolTarget.value!.id)
    if (idx !== -1) Object.assign(usuarios.value[idx], updated)
    rolTarget.value = null
    showToast(`Rol actualizado a ${nuevoRol}`)
  } catch (e) { showToast('Error al cambiar rol', 'error') }
  finally { saving.value = false }
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
.perm-page {
  display: flex; flex-direction: column; height: calc(100vh - 48px); overflow: hidden;
}
.top-bar {
  display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
  background: linear-gradient(135deg, #1a237e, #283593); border-radius: 14px;
  padding: 0.85rem 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 4px 16px rgba(26,35,126,0.2);
}
.top-bar__title { font-size: 1.15rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__count { font-size: 0.8rem; color: rgba(255,255,255,0.8); background: rgba(255,255,255,0.15); padding: 3px 10px; border-radius: 8px; }

.filters-bar {
  display: flex; gap: 0.5rem; flex-shrink: 0; margin-bottom: 0.75rem;
  background: #fff; padding: 0.6rem 0.75rem; border-radius: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.fi { padding: 6px 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 0.82rem; outline: none; transition: border-color .15s; }
.fi:focus { border-color: #3949ab; }
.fi-wide { flex: 1; }
.loading-center { display: flex; justify-content: center; padding: 3rem; }

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
.table tbody tr:hover { background: #f8f9ff; }
.th-actions { text-align: center; width: 120px; }
.empty-state { text-align: center; padding: 2rem; color: #bbb; }
.td-name { font-weight: 600; color: #222; }

/* Badges */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.72rem; font-weight: 700; padding: 3px 9px; border-radius: 20px;
  text-transform: capitalize; letter-spacing: 0.2px;
}
.badge--admin { background: #e8eaf6; color: #283593; }
.badge--user { background: #f5f5f5; color: #616161; }
.badge--active { background: #e8f5e9; color: #2e7d32; }
.badge--inactive { background: #ffebee; color: #c62828; }

/* Action buttons */
.actions-cell { display: flex; align-items: center; justify-content: center; gap: 6px; }
.act-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border: none; border-radius: 10px;
  cursor: pointer; transition: all .15s;
}
.act-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.act-btn--info { background: #e3f2fd; color: #1565C0; }
.act-btn--info:hover { background: #BBDEFB; }
.act-btn--promote { background: #e8eaf6; color: #283593; }
.act-btn--promote:not(:disabled):hover { background: #c5cae9; }
.act-btn--demote { background: #fff3e0; color: #E65100; }
.act-btn--demote:not(:disabled):hover { background: #ffe0b2; }
.act-btn--activate { background: #e8f5e9; color: #2e7d32; }
.act-btn--activate:not(:disabled):hover { background: #c8e6c9; }
.act-btn--deactivate { background: #ffebee; color: #c62828; }
.act-btn--deactivate:not(:disabled):hover { background: #ffcdd2; }

/* Overlay & Modal */
.overlay {
  position: fixed; inset: 0; z-index: 9000;
  background: rgba(0,0,0,0.35); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
  animation: fadeIn .2s ease;
}
.modal {
  background: #fff; border-radius: 20px; width: 100%; max-height: 90vh;
  display: flex; flex-direction: column;
  box-shadow: 0 24px 80px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.08);
  animation: modalIn .25s ease;
}
.modal--view { max-width: 480px; }
.modal--confirm { max-width: 400px; }

.modal__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.1rem 1.5rem; border-bottom: 1px solid #f0f0f0; flex-shrink: 0;
}
.modal__header h2 { font-size: 1.05rem; font-weight: 700; color: #222; margin: 0; }
.modal__header--warning h2 { color: #E65100; }
.modal__header--promote h2 { color: #283593; }
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

/* User card in view modal */
.user-card { text-align: center; margin-bottom: 1.25rem; }
.user-card__avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: linear-gradient(135deg, #1a237e, #3949ab);
  color: #fff; font-weight: 700; font-size: 1.25rem;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 0.75rem;
}
.user-card__name { font-size: 1.1rem; font-weight: 700; color: #222; margin-bottom: 0.5rem; }
.user-card__badges { display: flex; gap: 6px; justify-content: center; }

/* Detail grid */
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }
.detail-item { display: flex; flex-direction: column; }
.detail-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.4px; color: #aaa; font-weight: 600; margin-bottom: 2px; }
.detail-value { font-size: 0.88rem; color: #333; font-weight: 500; }
.detail-value.mono { font-family: monospace; font-size: 0.82rem; }

/* Confirm modal */
.confirm-icon { margin-bottom: 0.75rem; }
.confirm-icon--warning { color: #E65100; }
.confirm-icon--promote { color: #283593; }
.confirm-text { font-size: 0.9rem; color: #666; margin: 0 0 0.35rem; }
.confirm-name { font-size: 1.05rem; font-weight: 700; color: #222; margin: 0 0 0.75rem; }
.confirm-warn {
  font-size: 0.78rem; font-weight: 600; margin: 0; padding: 6px 12px;
  background: #FFF3E0; color: #E65100; border-radius: 8px; display: inline-block;
}
.confirm-warn--green { background: #e8f5e9; color: #2e7d32; }

/* Buttons */
.mbtn {
  padding: 8px 20px; border: none; border-radius: 12px; font-size: 0.88rem;
  font-weight: 600; cursor: pointer; transition: all .15s;
}
.mbtn:disabled { opacity: 0.5; cursor: not-allowed; }
.mbtn--secondary { background: #f0f0f0; color: #555; }
.mbtn--secondary:hover { background: #e4e4e4; }
.mbtn--warning { background: #E65100; color: #fff; }
.mbtn--warning:hover:not(:disabled) { background: #BF360C; }
.mbtn--promote { background: #283593; color: #fff; }
.mbtn--promote:hover:not(:disabled) { background: #1a237e; }

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
  .perm-page { height: calc(100vh - 56px); }
  .filters-bar { flex-wrap: wrap; }
  .detail-grid { grid-template-columns: 1fr; }
  .modal { border-radius: 16px; }
}
</style>
