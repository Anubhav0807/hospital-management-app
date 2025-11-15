<template>
  <div class="card shadow-sm border-0 mb-4 rounded-3">
    <div class="card-header bg-white fw-semibold">{{ title }}</div>
    <div class="card-body">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String
})
</script>
