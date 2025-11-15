<template>
  <router-view />

  <!-- GLOBAL TOAST STACK -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div
      v-for="t in toasts"
      :key="t.id"
      class="toast text-white border-0 mb-2 show"
      :class="`bg-${t.type}`"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">
          {{ t.message }}
        </div>
        <button
          type="button"
          class="btn-close btn-close-white me-2 m-auto"
          aria-label="Close"
          @click="remove(t.id)"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useToast } from './composables/useToast'

const { toasts, remove } = useToast()
</script>
