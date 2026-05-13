<template>
  <AdminLayout>
    <div class="perm-page">
      <div class="top-bar">
        <div class="top-bar__left">
          <ShieldCheck :size="22" />
          <span>Permisos de Usuarios</span>
        </div>
        <button class="btn-add" @click="openCreate">
          <UserPlus :size="16" /><span>Añadir usuario</span>
        </button>
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
              <th class="th-actions">Acciones</th>
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
                  <button class="act-btn act-btn--edit" title="Editar usuario" @click="openEdit(u)">
                    <Pencil :size="14" />
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

      <!-- MODAL: CREAR USUARIO -->
      <Teleport to="body">
        <div v-if="showCreate" class="overlay" @click.self="showCreate = false">
          <div class="modal modal--lg">
            <div class="modal__header mh--blue">
              <div class="mh__title"><UserPlus :size="18" /> Nuevo Usuario</div>
              <button class="modal__close mclose--light" @click="showCreate = false"><X :size="18" /></button>
            </div>
            <div class="modal__body">
              <div class="form-grid">
                <div class="fg"><label class="fl">Nombre *</label><input v-model="createForm.nombre" class="finput" placeholder="Nombre" /></div>
                <div class="fg"><label class="fl">Apellido Paterno *</label><input v-model="createForm.apellido_paterno" class="finput" placeholder="Apellido Paterno" /></div>
                <div class="fg"><label class="fl">Apellido Materno *</label><input v-model="createForm.apellido_materno" class="finput" placeholder="Apellido Materno" /></div>
                <div class="fg"><label class="fl">CURP *</label><input v-model="createForm.curp" class="finput" placeholder="18 caracteres" maxlength="18" style="text-transform:uppercase" /></div>
                <div class="fg"><label class="fl">Correo *</label><input v-model="createForm.correo" class="finput" type="email" placeholder="correo@ejemplo.com" /></div>
                <div class="fg"><label class="fl">Teléfono *</label><input v-model="createForm.telefono" class="finput" placeholder="10 dígitos" maxlength="10" /></div>
                <div class="fg"><label class="fl">Contraseña *</label><input v-model="createForm.password" class="finput" type="password" placeholder="Mínimo 6 caracteres" /></div>
                <div class="fg"><label class="fl">Rol</label>
                  <select v-model="createForm.rol" class="finput">
                    <option value="usuario">Usuario</option>
                    <option value="administrador">Administrador</option>
                  </select>
                </div>
              </div>
              <div v-if="createForm.rol === 'usuario'" class="permisos-section">
                <div class="permisos-sec-title">
                  <KeyRound :size="16" />
                  <span>Acceso a vistas</span>
                  <span class="permisos-hint">Activa las secciones a las que tendrá acceso</span>
                </div>
                <div class="permisos-list">
                  <div v-for="v in VISTAS" :key="v.key" class="permiso-row" :class="{ 'permiso-row--on': createForm.permisos.includes(v.key) }">
                    <div class="permiso-row__icon"><component :is="v.icon" :size="18" /></div>
                    <div class="permiso-row__info">
                      <span class="permiso-row__label">{{ v.label }}</span>
                      <span class="permiso-row__desc">{{ v.desc }}</span>
                    </div>
                    <label class="sw">
                      <input type="checkbox" :value="v.key" v-model="createForm.permisos" class="sw__input" />
                      <span class="sw__track"><span class="sw__thumb"></span></span>
                    </label>
                  </div>
                </div>
              </div>
              <div v-else class="admin-note">
                <ShieldCheck :size="18" /><span>Acceso completo a todas las vistas como Administrador.</span>
              </div>
            </div>
            <div class="modal__footer">
              <button class="mbtn mbtn--ghost" @click="showCreate = false">Cancelar</button>
              <button class="mbtn mbtn--blue" :disabled="saving" @click="confirmCreate">
                <UserPlus :size="15" /> {{ saving ? 'Creando...' : 'Crear usuario' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- MODAL: EDITAR USUARIO -->
      <Teleport to="body">
        <div v-if="editTarget" class="overlay" @click.self="closeEdit">
          <div class="modal modal--lg">
            <div class="modal__header mh--indigo">
              <div class="mh__title"><Pencil :size="18" /> Editar Usuario</div>
              <button class="modal__close mclose--light" @click="closeEdit"><X :size="18" /></button>
            </div>
            <div class="modal__body">
              <div class="user-mini-card">
                <div class="umc__avatar">{{ initials(editTarget) }}</div>
                <div>
                  <div class="umc__name">{{ editTarget.nombre }} {{ editTarget.apellido_paterno }}</div>
                  <div class="umc__email">{{ editTarget.correo }}</div>
                </div>
              </div>

              <div class="edit-tabs">
                <button class="etab" :class="{ 'etab--active': editTab === 'datos' }" @click="editTab = 'datos'">
                  <UserCog :size="14" /> Datos
                </button>
                <button class="etab" :class="{ 'etab--active': editTab === 'permisos' }" @click="editTab = 'permisos'">
                  <KeyRound :size="14" /> Permisos
                </button>
                <button class="etab" :class="{ 'etab--active': editTab === 'rol' }" @click="editTab = 'rol'">
                  <ShieldCheck :size="14" /> Rol / Estatus
                </button>
              </div>

              <!-- TAB: Datos -->
              <div v-if="editTab === 'datos'" class="form-grid" style="margin-top:1rem">
                <div class="fg"><label class="fl">Nombre</label><input v-model="editForm.nombre" class="finput" /></div>
                <div class="fg"><label class="fl">Apellido Paterno</label><input v-model="editForm.apellido_paterno" class="finput" /></div>
                <div class="fg"><label class="fl">Apellido Materno</label><input v-model="editForm.apellido_materno" class="finput" /></div>
                <div class="fg"><label class="fl">CURP</label><input v-model="editForm.curp" class="finput" style="text-transform:uppercase" /></div>
                <div class="fg"><label class="fl">Correo</label><input v-model="editForm.correo" class="finput" type="email" /></div>
                <div class="fg"><label class="fl">Teléfono</label><input v-model="editForm.telefono" class="finput" /></div>
              </div>

              <!-- TAB: Permisos -->
              <div v-if="editTab === 'permisos'" style="margin-top:1rem">
                <div v-if="editTarget.rol === 'administrador'" class="admin-note">
                  <ShieldCheck :size="18" /><span>Los administradores tienen acceso completo. Cambia el rol a Usuario para gestionar permisos individuales.</span>
                </div>
                <div v-else class="permisos-list">
                  <div v-for="v in VISTAS" :key="v.key" class="permiso-row" :class="{ 'permiso-row--on': editPermisos.includes(v.key) }">
                    <div class="permiso-row__icon"><component :is="v.icon" :size="18" /></div>
                    <div class="permiso-row__info">
                      <span class="permiso-row__label">{{ v.label }}</span>
                      <span class="permiso-row__desc">{{ v.desc }}</span>
                    </div>
                    <label class="sw">
                      <input type="checkbox" :value="v.key" v-model="editPermisos" class="sw__input" @change="onPermisosChange" />
                      <span class="sw__track"><span class="sw__thumb"></span></span>
                    </label>
                  </div>
                </div>
              </div>

              <!-- TAB: Rol / Estatus -->
              <div v-if="editTab === 'rol'" style="margin-top:1rem">
                <div class="rol-grid">
                  <div class="rol-card" :class="{ 'rol-card--active': editForm.rol === 'usuario' }" @click="editForm.rol = 'usuario'">
                    <User :size="24" />
                    <div class="rol-card__label">Usuario</div>
                    <div class="rol-card__desc">Acceso limitado según permisos</div>
                    <div class="rol-radio"><span v-if="editForm.rol === 'usuario'" class="rol-radio__dot"></span></div>
                  </div>
                  <div class="rol-card" :class="{ 'rol-card--active rol-card--admin': editForm.rol === 'administrador', 'rol-card--admin-passive': editForm.rol !== 'administrador' }" @click="editTarget.id !== auth.user?.id && (editForm.rol = 'administrador')">
                    <ShieldCheck :size="24" />
                    <div class="rol-card__label">Administrador</div>
                    <div class="rol-card__desc">Acceso completo al sistema</div>
                    <div class="rol-radio"><span v-if="editForm.rol === 'administrador'" class="rol-radio__dot rol-radio__dot--admin"></span></div>
                  </div>
                </div>
                <div class="estatus-row">
                  <div class="estatus-info">
                    <component :is="editForm.estatus === 'activo' ? CheckCircle : XCircle" :size="18" :class="editForm.estatus === 'activo' ? 'ico--green' : 'ico--red'" />
                    <div>
                      <span class="estatus-label">Estatus de la cuenta</span>
                      <span :class="editForm.estatus === 'activo' ? 'estatus-val--active' : 'estatus-val--inactive'">{{ editForm.estatus }}</span>
                    </div>
                  </div>
                  <label class="sw sw--lg" v-if="editTarget.id !== auth.user?.id">
                    <input type="checkbox" :checked="editForm.estatus === 'activo'" class="sw__input"
                      @change="editForm.estatus = editForm.estatus === 'activo' ? 'inactivo' : 'activo'" />
                    <span class="sw__track"><span class="sw__thumb"></span></span>
                  </label>
                  <span v-else class="self-note">No puedes modificar tu propia cuenta</span>
                </div>
              </div>
            </div>
            <div class="modal__footer">
              <button class="mbtn mbtn--ghost" @click="closeEdit">Cancelar</button>
              <button class="mbtn mbtn--indigo" :disabled="saving" @click="confirmEdit">
                <Save :size="15" /> {{ saving ? 'Guardando...' : 'Guardar cambios' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- TOAST -->
      <Teleport to="body">
        <div v-if="toast" :class="['toast-msg', 'toast-msg--' + toast.type]">
          <component :is="toast.type === 'success' ? CheckCircle : XCircle" :size="16" />
          {{ toast.text }}
        </div>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, markRaw } from 'vue'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/components/AdminLayout.vue'
import type { AdminUser } from '@/types'
import {
  ShieldCheck, User, UserCheck, UserX, X, UserPlus, Pencil,
  Map, ClipboardList, Bell,
  KeyRound, UserCog, Save, CheckCircle, XCircle
} from 'lucide-vue-next'

const VISTAS = [
  { key: 'visor',      label: 'Mapa / Visor',      desc: 'Ver mapa interactivo de centrales y precios',  icon: markRaw(Map) },
  { key: 'reportes',   label: 'Reportes',           desc: 'Consultar reportes de precios de jitomate',    icon: markRaw(ClipboardList) },
  { key: 'alertas',    label: 'Alertas',            desc: 'Ver y gestionar alertas activas del sistema',  icon: markRaw(Bell) },
]

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const usuarios = ref<AdminUser[]>([])
const busqueda = ref('')
const filtroRol = ref('')
const filtroEstatus = ref('')

const showCreate = ref(false)
const editTarget = ref<AdminUser | null>(null)
const editTab = ref<'datos' | 'permisos' | 'rol'>('datos')
const toast = ref<{ text: string; type: string } | null>(null)

const editPermisos = ref<string[]>([])
const editForm = ref({ nombre: '', apellido_paterno: '', apellido_materno: '', curp: '', correo: '', telefono: '', rol: 'usuario', estatus: 'activo' })
const createForm = ref({ nombre: '', apellido_paterno: '', apellido_materno: '', curp: '', correo: '', telefono: '', password: '', rol: 'usuario', permisos: [] as string[] })

const filtered = computed(() => usuarios.value.filter(u => {
  const q = busqueda.value.toLowerCase()
  return (!q || u.nombre.toLowerCase().includes(q) || u.correo.toLowerCase().includes(q))
    && (!filtroRol.value || u.rol === filtroRol.value)
    && (!filtroEstatus.value || u.estatus === filtroEstatus.value)
}))

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

function openCreate() {
  createForm.value = { nombre: '', apellido_paterno: '', apellido_materno: '', curp: '', correo: '', telefono: '', password: '', rol: 'usuario', permisos: [] }
  showCreate.value = true
}

function openEdit(u: AdminUser) {
  editTarget.value = u
  editTab.value = 'datos'
  editForm.value = { nombre: u.nombre, apellido_paterno: u.apellido_paterno, apellido_materno: u.apellido_materno, curp: u.curp, correo: u.correo, telefono: u.telefono, rol: u.rol, estatus: u.estatus }
  editPermisos.value = [...(u.permisos || [])]
}

function closeEdit() { editTarget.value = null }

async function onPermisosChange() {
  if (!editTarget.value) return
  try {
    const res = await authService.updatePermisos(editTarget.value.id, editPermisos.value)
    const idx = usuarios.value.findIndex(u => u.id === editTarget.value!.id)
    if (idx !== -1) usuarios.value[idx].permisos = res.permisos
    if (auth.user?.id === editTarget.value.id) {
      auth.user.permisos = res.permisos
    }
  } catch { showToast('Error al actualizar permiso', 'error') }
}

async function confirmCreate() {
  const f = createForm.value
  if (!f.nombre || !f.apellido_paterno || !f.apellido_materno || !f.curp || !f.correo || !f.telefono || !f.password) {
    showToast('Completa todos los campos obligatorios', 'error'); return
  }
  saving.value = true
  try {
    const payload: Record<string, any> = { ...f, curp: f.curp.toUpperCase() }
    const created = await authService.createUsuario(payload)
    if (f.rol === 'usuario' && f.permisos.length) {
      const res = await authService.updatePermisos(created.id, f.permisos)
      created.permisos = res.permisos
    }
    usuarios.value.unshift(created)
    showCreate.value = false
    showToast('Usuario creado correctamente')
  } catch (e: any) {
    showToast(e?.response?.data?.detail || 'Error al crear usuario', 'error')
  } finally { saving.value = false }
}

async function confirmEdit() {
  if (!editTarget.value) return
  saving.value = true
  try {
    const f = editForm.value
    const promises: Promise<any>[] = []

    promises.push(authService.updateUsuario(editTarget.value.id, {
      nombre: f.nombre, apellido_paterno: f.apellido_paterno,
      apellido_materno: f.apellido_materno, curp: f.curp.toUpperCase(),
      correo: f.correo, telefono: f.telefono,
    }))

    if (f.rol !== editTarget.value.rol && !(editTarget.value.id === auth.user?.id && f.rol === 'usuario')) {
      promises.push(authService.updateRol(editTarget.value.id, f.rol))
    }
    if (f.estatus !== editTarget.value.estatus && editTarget.value.id !== auth.user?.id) {
      promises.push(authService.updateEstatus(editTarget.value.id, f.estatus))
    }
    promises.push(authService.updatePermisos(editTarget.value.id, editPermisos.value))

    await Promise.all(promises)

    const idx = usuarios.value.findIndex(u => u.id === editTarget.value!.id)
    if (idx !== -1) {
      Object.assign(usuarios.value[idx], { ...f, permisos: editPermisos.value })
    }
    if (auth.user?.id === editTarget.value.id) {
      auth.user.permisos = editPermisos.value
    }
    closeEdit()
    showToast('Usuario actualizado correctamente')
  } catch (e: any) {
    showToast(e?.response?.data?.detail || 'Error al guardar', 'error')
  } finally { saving.value = false }
}

async function toggleEstatus(u: AdminUser) {
  const nuevo = u.estatus === 'activo' ? 'inactivo' : 'activo'
  try {
    const updated = await authService.updateEstatus(u.id, nuevo)
    Object.assign(u, updated)
    showToast(`Usuario ${nuevo === 'activo' ? 'activado' : 'desactivado'}`)
  } catch { showToast('Error al cambiar estatus', 'error') }
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
.perm-page { display: flex; flex-direction: column; height: calc(100vh - 48px); overflow: hidden; }

.top-bar {
  display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
  background: linear-gradient(135deg, #1a237e, #3949ab); border-radius: 14px;
  padding: 0.85rem 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 4px 20px rgba(26,35,126,0.25);
}
.top-bar__left { display: flex; align-items: center; gap: 0.5rem; font-size: 1.1rem; font-weight: 700; color: #fff; }
.btn-add {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(255,255,255,0.95); color: #1a237e;
  border: none; padding: 0.5rem 1.1rem; border-radius: 12px;
  font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: all .15s;
}
.btn-add:hover { background: #fff; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

.filters-bar {
  display: flex; gap: 0.5rem; flex-shrink: 0; margin-bottom: 0.75rem;
  background: #fff; padding: 0.6rem 0.75rem; border-radius: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.fi { padding: 6px 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 0.82rem; outline: none; transition: border-color .15s; }
.fi:focus { border-color: #3949ab; }
.fi-wide { flex: 1; }
.loading-center { display: flex; justify-content: center; padding: 3rem; }

.scroll-table-wrap { flex: 1; overflow-y: auto; overflow-x: auto; background: #fff; border-radius: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.table thead { position: sticky; top: 0; z-index: 2; }
.table th { padding: 0.7rem 0.85rem; text-align: left; font-weight: 600; font-size: 0.78rem; color: #666; background: #fafafa; border-bottom: 1px solid #eee; white-space: nowrap; }
.table td { padding: 0.65rem 0.85rem; border-bottom: 1px solid #f5f5f5; color: #444; white-space: nowrap; }
.table tbody tr:hover { background: #f8f9ff; }
.th-actions { text-align: center; width: 90px; }
.empty-state { text-align: center; padding: 2rem; color: #bbb; }
.td-name { font-weight: 600; color: #222; }

.badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.72rem; font-weight: 700; padding: 3px 9px; border-radius: 20px; text-transform: capitalize; }
.badge--admin { background: #e8eaf6; color: #283593; }
.badge--user { background: #f5f5f5; color: #616161; }
.badge--active { background: #e8f5e9; color: #2e7d32; }
.badge--inactive { background: #ffebee; color: #c62828; }

.actions-cell { display: flex; align-items: center; justify-content: center; gap: 6px; }
.act-btn { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; border-radius: 10px; cursor: pointer; transition: all .15s; }
.act-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.act-btn--edit { background: #e8eaf6; color: #283593; }
.act-btn--edit:hover { background: #c5cae9; }
.act-btn--activate { background: #e8f5e9; color: #2e7d32; }
.act-btn--activate:not(:disabled):hover { background: #c8e6c9; }
.act-btn--deactivate { background: #ffebee; color: #c62828; }
.act-btn--deactivate:not(:disabled):hover { background: #ffcdd2; }

/* ── Overlay & Modal ── */
.overlay {
  position: fixed; inset: 0; z-index: 9000; background: rgba(0,0,0,0.4); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; padding: 1rem; animation: fadeIn .2s ease;
}
.modal {
  background: #fff; border-radius: 20px; width: 100%; max-height: 92vh;
  display: flex; flex-direction: column;
  box-shadow: 0 24px 80px rgba(0,0,0,0.18); animation: modalIn .25s ease;
}
.modal--lg { max-width: 580px; }

.modal__header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.5rem; flex-shrink: 0; border-radius: 20px 20px 0 0; }
.mh--blue { background: linear-gradient(135deg, #1a237e, #3949ab); }
.mh--indigo { background: linear-gradient(135deg, #283593, #5c6bc0); }
.mh__title { display: flex; align-items: center; gap: 0.5rem; font-size: 1rem; font-weight: 700; color: #fff; }
.modal__close { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; border-radius: 50%; cursor: pointer; transition: all .15s; }
.mclose--light { background: rgba(255,255,255,0.2); color: #fff; }
.mclose--light:hover { background: rgba(255,255,255,0.35); }

.modal__body { padding: 1.25rem 1.5rem; overflow-y: auto; flex: 1; }
.modal__footer { display: flex; align-items: center; justify-content: flex-end; gap: 0.6rem; padding: 1rem 1.5rem; border-top: 1px solid #f0f0f0; flex-shrink: 0; }

/* ── Form ── */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1.25rem; }
.fg { display: flex; flex-direction: column; gap: 4px; }
.fl { font-size: 0.73rem; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 0.3px; }
.finput { padding: 8px 10px; border: 1.5px solid #e0e0e0; border-radius: 10px; font-size: 0.88rem; outline: none; transition: border-color .15s; background: #fafafa; }
.finput:focus { border-color: #3949ab; background: #fff; }

/* ── Permisos list ── */
.permisos-section { border-top: 1px solid #f0f0f0; padding-top: 1rem; }
.permisos-sec-title { display: flex; align-items: center; gap: 0.5rem; font-size: 0.88rem; font-weight: 700; color: #333; margin-bottom: 0.75rem; }
.permisos-hint { font-size: 0.73rem; font-weight: 400; color: #aaa; margin-left: auto; }
.permisos-list { display: flex; flex-direction: column; gap: 8px; }

.permiso-row {
  display: flex; align-items: center; gap: 0.9rem; padding: 0.75rem 1rem;
  border: 1.5px solid #eee; border-radius: 14px; transition: all .2s; background: #fafafa;
}
.permiso-row--on { border-color: #3949ab; background: #f3f4fd; }
.permiso-row__icon { width: 38px; height: 38px; border-radius: 10px; background: #e8eaf6; color: #3949ab; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.permiso-row--on .permiso-row__icon { background: #3949ab; color: #fff; }
.permiso-row__info { display: flex; flex-direction: column; flex: 1; }
.permiso-row__label { font-size: 0.9rem; font-weight: 600; color: #222; }
.permiso-row__desc { font-size: 0.75rem; color: #999; }

/* ── Switch ── */
.sw { position: relative; display: inline-flex; align-items: center; cursor: pointer; flex-shrink: 0; }
.sw__input { position: absolute; opacity: 0; width: 0; height: 0; }
.sw__track {
  width: 44px; height: 24px; background: #ddd; border-radius: 999px;
  transition: background .2s; display: flex; align-items: center; padding: 2px;
}
.sw__thumb {
  width: 20px; height: 20px; background: #fff; border-radius: 50%;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2); transition: transform .2s;
}
.sw__input:checked ~ .sw__track { background: #3949ab; }
.sw__input:checked ~ .sw__track .sw__thumb { transform: translateX(20px); }
.sw--lg .sw__track { width: 52px; height: 28px; }
.sw--lg .sw__thumb { width: 24px; height: 24px; }
.sw--lg .sw__input:checked ~ .sw__track .sw__thumb { transform: translateX(24px); }

/* ── Admin note ── */
.admin-note { display: flex; align-items: center; gap: 0.6rem; background: #e8eaf6; color: #283593; border-radius: 12px; padding: 0.75rem 1rem; font-size: 0.85rem; font-weight: 600; margin-top: 1rem; }

/* ── User mini card ── */
.user-mini-card { display: flex; align-items: center; gap: 0.85rem; padding: 0.75rem 1rem; background: #f8f9ff; border-radius: 14px; margin-bottom: 1rem; border: 1px solid #e8eaf6; }
.umc__avatar { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #1a237e, #3949ab); color: #fff; font-weight: 700; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.umc__name { font-size: 0.95rem; font-weight: 700; color: #222; }
.umc__email { font-size: 0.78rem; color: #999; }

/* ── Edit tabs ── */
.edit-tabs { display: flex; gap: 6px; background: #f5f5f5; border-radius: 12px; padding: 4px; }
.etab { display: flex; align-items: center; gap: 5px; padding: 7px 14px; border: none; border-radius: 9px; background: transparent; color: #666; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all .15s; }
.etab--active { background: #fff; color: #283593; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }

/* ── Rol cards ── */
.rol-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 1rem; }
.rol-card {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 1.1rem; border: 2px solid #e0e0e0; border-radius: 16px;
  cursor: pointer; transition: all .2s; color: #888; text-align: center; background: #fafafa;
}
.rol-card--active { border-color: #3949ab; color: #283593; background: #f0f2ff; }
.rol-card--admin { border-color: #c62828; color: #b71c1c; background: #fff5f5; }
.rol-card--admin-passive { color: #888; }
.rol-card__label { font-size: 0.9rem; font-weight: 700; }
.rol-card__desc { font-size: 0.72rem; color: #aaa; }
.rol-radio { width: 16px; height: 16px; border: 2px solid currentColor; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-top: 4px; }
.rol-radio__dot { width: 8px; height: 8px; border-radius: 50%; background: #3949ab; }
.rol-radio__dot--admin { background: #c62828; }

/* ── Estatus row ── */
.estatus-row { display: flex; align-items: center; justify-content: space-between; padding: 1rem; background: #fafafa; border-radius: 14px; border: 1.5px solid #eee; }
.estatus-info { display: flex; align-items: center; gap: 0.75rem; }
.estatus-label { display: block; font-size: 0.78rem; font-weight: 600; color: #888; text-transform: uppercase; }
.estatus-val--active { display: block; font-size: 0.9rem; font-weight: 700; color: #2e7d32; }
.estatus-val--inactive { display: block; font-size: 0.9rem; font-weight: 700; color: #c62828; }
.ico--green { color: #2e7d32; }
.ico--red { color: #c62828; }
.self-note { font-size: 0.75rem; color: #bbb; font-style: italic; }

/* ── Buttons ── */
.mbtn { display: flex; align-items: center; gap: 6px; padding: 8px 20px; border: none; border-radius: 12px; font-size: 0.88rem; font-weight: 600; cursor: pointer; transition: all .15s; }
.mbtn:disabled { opacity: 0.5; cursor: not-allowed; }
.mbtn--ghost { background: #f0f0f0; color: #555; }
.mbtn--ghost:hover { background: #e4e4e4; }
.mbtn--blue { background: linear-gradient(135deg, #1a237e, #3949ab); color: #fff; }
.mbtn--blue:hover:not(:disabled) { background: linear-gradient(135deg, #0d1757, #283593); }
.mbtn--indigo { background: linear-gradient(135deg, #283593, #5c6bc0); color: #fff; }
.mbtn--indigo:hover:not(:disabled) { background: linear-gradient(135deg, #1a237e, #3949ab); }

/* ── Toast ── */
.toast-msg {
  position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  display: flex; align-items: center; gap: 8px;
  padding: 10px 20px; border-radius: 14px; font-size: 0.88rem; font-weight: 600;
  z-index: 10000; animation: slideUp .3s ease; box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.toast-msg--success { background: #2e7d32; color: #fff; }
.toast-msg--error { background: #C62828; color: #fff; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes modalIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(16px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .perm-page { height: auto; min-height: calc(100vh - 56px); overflow: visible; }
  .scroll-table-wrap { overflow-x: auto; }
  .form-grid { grid-template-columns: 1fr; }
  .rol-grid { grid-template-columns: 1fr; }
  .edit-tabs { flex-wrap: wrap; }
  .modal--lg { border-radius: 16px; }
}
</style>
