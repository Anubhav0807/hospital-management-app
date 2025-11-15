<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold">
        <span v-if="user">{{ titleCase(user.role) }}</span>
        Profile
      </h2>
      <div>
        <button class="btn btn-secondary me-2" @click="router.back">
          <i class="bi bi-arrow-left"></i> Back
        </button>
        <button class="btn btn-primary" @click="updateProfile">
          <i class="bi bi-save"></i> Update Profile
        </button>
      </div>
    </div>

    <div v-if="user">
      <!-- Common Info -->
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="user.email" type="email" class="form-control" disabled />
      </div>

      <div class="row">
        <div class="col-md-6 mb-3">
          <label class="form-label">Name</label>
          <input v-model="user.name" type="text" class="form-control" />
        </div>

        <div class="col-md-6 mb-3">
          <label class="form-label">Contact Number</label>
          <input v-model="user.contact_number" type="text" class="form-control" />
        </div>
      </div>

      <!-- Dynamic Component -->
      <component :is="currentProfileComponent" v-if="user.role !== 'admin'" :user="user" />
    </div>
  </div>
</template>

<script setup>
import { shallowRef, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../composables/useToast'
import { titleCase } from '../utils'
import api from '../api'

import DoctorProfile from '../components/profiles/DoctorProfile.vue'
import PatientProfile from '../components/profiles/PatientProfile.vue'

const router = useRouter()
const toast = useToast();
const user = ref(null)
const currentProfileComponent = shallowRef(null)

async function loadProfile() {
  try {
    const res = await api.get('/auth/profile')
    user.value = res.data

    switch (user.value.role.toLowerCase()) {
      case 'doctor':
        currentProfileComponent.value = DoctorProfile
        break
      case 'patient':
        currentProfileComponent.value = PatientProfile
        break
    }
  } catch (err) {
    toast.error('Unable to load the profile.')
  }
}

async function updateProfile() {
  try {
    await api.put('/auth/profile', user.value)
    toast.success('Profile updated successfully!')
  } catch (err) {
    toast.error('Unable to update the profile.')
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.container {
  max-width: 700px;
}
</style>
