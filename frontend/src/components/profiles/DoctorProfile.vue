<template>
  <div v-if="user.doctor_profile" class="mb-3">
    <label class="form-label">Department</label>
    <input v-model="user.doctor_profile.department_name" type="text" class="form-control" readonly />
  </div>

  <div v-if="user.doctor_profile" class="mb-3">
    <label class="form-label">Experience (years)</label>
    <input v-model="user.doctor_profile.experience_years" type="number" class="form-control" />
  </div>
</template>

<script setup>
defineProps({
  user: { type: Object, required: true },
})
</script>
