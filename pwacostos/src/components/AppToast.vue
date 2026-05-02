<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite">
      <TransitionGroup name="toast">
        <div
          v-for="toast in ui.toasts"
          :key="toast.id"
          class="toast"
          :class="'toast--' + toast.type"
          @click="ui.removeToast(toast.id)"
        >
          <component :is="iconMap[toast.type]" :size="18" />
          <span>{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import { CheckCircle2, XCircle, AlertTriangle, Info } from 'lucide-vue-next'
import type { Component } from 'vue'

const ui = useUiStore()

const iconMap: Record<string, Component> = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertTriangle,
  info: Info
}
</script>
