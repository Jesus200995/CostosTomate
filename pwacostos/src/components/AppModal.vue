<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <div class="modal-header">
            <div class="modal-header__title">
              <slot name="header">Modal</slot>
            </div>
            <button class="modal-close" @click="$emit('close')" aria-label="Cerrar">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <slot name="body"></slot>
          </div>
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'

defineProps<{ show: boolean }>()
defineEmits<{ close: [] }>()
</script>
