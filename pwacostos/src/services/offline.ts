import { ref } from 'vue'
import api from './api'

// ─── Estado de conexión reactivo (singleton) ────────────────────

const isOnline = ref(navigator.onLine)

let _onlineTimer: ReturnType<typeof setTimeout> | null = null
function _handleOnline() {
  isOnline.value = true
  // Delay breve para evitar disparos múltiples por red inestable
  if (_onlineTimer) clearTimeout(_onlineTimer)
  _onlineTimer = setTimeout(() => { syncAll() }, 2000)
}
function _handleOffline() { isOnline.value = false }

// Register listeners immediately at module load
window.addEventListener('online', _handleOnline)
window.addEventListener('offline', _handleOffline)

export function useOnlineStatus() {
  return { isOnline }
}

// ─── IndexedDB helpers ──────────────────────────────────────────

const DB_NAME = 'costos_offline'
const DB_VERSION = 1

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains('catalogos'))
        db.createObjectStore('catalogos')          // key-value store
      if (!db.objectStoreNames.contains('pendingQueue'))
        db.createObjectStore('pendingQueue', { keyPath: 'id', autoIncrement: true })
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

// ─── Catálogos cache ────────────────────────────────────────────

export async function setCatalogo(key: string, data: any): Promise<void> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('catalogos', 'readwrite')
    tx.objectStore('catalogos').put(data, key)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

export async function getCatalogo<T = any>(key: string): Promise<T | null> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('catalogos', 'readonly')
    const req = tx.objectStore('catalogos').get(key)
    req.onsuccess = () => resolve(req.result ?? null)
    req.onerror = () => reject(req.error)
  })
}

// ─── Cola de operaciones pendientes ─────────────────────────────

interface PendingItem {
  id?: number
  type: 'precio' | 'propuesta'
  payload: any
  createdAt: string
}

export async function addPending(type: PendingItem['type'], payload: any): Promise<void> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('pendingQueue', 'readwrite')
    tx.objectStore('pendingQueue').add({
      type,
      payload,
      createdAt: new Date().toISOString()
    })
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

export async function getPendingCount(): Promise<number> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('pendingQueue', 'readonly')
    const req = tx.objectStore('pendingQueue').count()
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function getAllPending(): Promise<PendingItem[]> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('pendingQueue', 'readonly')
    const req = tx.objectStore('pendingQueue').getAll()
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function removePending(id: number): Promise<void> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('pendingQueue', 'readwrite')
    tx.objectStore('pendingQueue').delete(id)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

// ─── Sincronización ─────────────────────────────────────────────

const pendingCount = ref(0)
const pendingItems = ref<Array<{ id: number; type: string; payload: any; createdAt: string }>>([])
let _syncing = false

export function usePendingCount() {
  refreshPendingCount()
  return { pendingCount, pendingItems }
}

export async function refreshPendingCount() {
  try {
    const items = await getAllPending()
    pendingCount.value = items.length
    pendingItems.value = items.map(i => ({ id: i.id!, type: i.type, payload: i.payload, createdAt: i.createdAt }))
  } catch { /* ignore */ }
}

export async function syncAll(): Promise<{ synced: number; failed: number }> {
  if (_syncing || !navigator.onLine) return { synced: 0, failed: 0 }
  _syncing = true

  let synced = 0
  let failed = 0

  try {
    const items = await getAllPending()
    for (const item of items) {
      if (!navigator.onLine) break          // red se fue, dejar de intentar
      try {
        if (item.type === 'precio') {
          await api.post('/mercados/precio', item.payload)
        } else if (item.type === 'propuesta') {
          await api.post('/mercados/proponer', item.payload)
        }
        await removePending(item.id!)
        synced++
      } catch (err: any) {
        // Si el server respondió 2xx o 409 (duplicado), el registro ya existe → eliminar de la cola
        const status = err?.response?.status
        if (status && status >= 200 && status < 300) {
          await removePending(item.id!)
          synced++
        } else {
          failed++
        }
      }
    }
  } catch { /* db error */ }

  _syncing = false
  await refreshPendingCount()
  return { synced, failed }
}

// Intento de sincronización periódica cada 30s si hay pendientes
setInterval(async () => {
  if (navigator.onLine && (await getPendingCount()) > 0) {
    syncAll()
  }
}, 30000)
