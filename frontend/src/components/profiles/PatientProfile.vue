<template>
  <div class="row">
    <div class="col-md-6 mb-3">
      <label class="form-label">Age</label>
      <input v-model="user.patient_profile.age" type="number" class="form-control" />
    </div>

    <div class="col-md-6 mb-3">
      <label class="form-label">Gender</label>
      <select v-model="user.patient_profile.gender" class="form-select">
        <option value="male">Male</option>
        <option value="female">Female</option>
        <option value="other">Other</option>
      </select>
    </div>
  </div>

  <div class="mb-3">
    <label class="form-label">Address</label>
    <textarea v-model="user.patient_profile.address" class="form-control" rows="2"></textarea>
  </div>

  <div class="mb-3">
    <label class="form-label">Medical History</label>
    <textarea v-model="user.patient_profile.medical_history" class="form-control" rows="3"></textarea>
  </div>
</template>

<script setup>
defineProps({
  user: { type: Object, required: true },
})
</script>
