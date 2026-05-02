<template>
  <router-view v-slot="{ Component, route }">
    <Transition :name="route.meta.guest ? 'page-auth' : 'page'" mode="out-in">
      <component :is="Component" :key="route.path" />
    </Transition>
  </router-view>

  <!-- PWA update toast -->
  <Transition name="pwa-toast">
    <div v-if="showUpdateToast" class="pwa-update-toast">
      <span>🔄 App actualizada. Aplicando cambios…</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRegisterSW } from 'virtual:pwa-register/vue'

const showUpdateToast = ref(false)

const { needRefresh, updateServiceWorker } = useRegisterSW({
  immediate: true,
  onRegisteredSW(_url: string, registration: ServiceWorkerRegistration | undefined) {
    if (registration) {
      setInterval(() => { registration.update() }, 60 * 1000)
    }
  }
})

watch(needRefresh, (val) => {
  if (val) {
    showUpdateToast.value = true
    updateServiceWorker(true)
    setTimeout(() => { showUpdateToast.value = false }, 4000)
  }
})
</script>

<style scoped>
.pwa-update-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #1e293b, #334155);
  color: #f8fafc;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  z-index: 10000;
  white-space: nowrap;
}
.pwa-toast-enter-active,
.pwa-toast-leave-active {
  transition: all 0.4s ease;
}
.pwa-toast-enter-from,
.pwa-toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
