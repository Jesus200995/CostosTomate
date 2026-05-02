import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Toast } from '@/types'

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const toasts = ref<Toast[]>([])
  const modalActive = ref(false)
  let toastId = 0

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function closeSidebar() {
    sidebarOpen.value = false
  }

  function showToast(message: string, type: Toast['type'] = 'info', duration = 3000) {
    const id = ++toastId
    toasts.value.push({ id, message, type, duration })
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
  }

  function removeToast(id: number) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  function openModal() {
    modalActive.value = true
  }

  function closeModal() {
    modalActive.value = false
  }

  return {
    sidebarOpen, toasts, modalActive,
    toggleSidebar, closeSidebar,
    showToast, removeToast,
    openModal, closeModal
  }
})
