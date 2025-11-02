<template>
  <div>
    <div class="text-center mt-5">Welcome, {{ role }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const role = ref(null)

onMounted(() => {
  const user = JSON.parse(localStorage.getItem("user") || "{}")
  role.value = user.role
})
</script>
