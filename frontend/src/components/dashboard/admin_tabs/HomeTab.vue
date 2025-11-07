<template>
  <div class="container">
    <h3 class="mb-4 text-center">Dashboard Overview</h3>

    <div class="row g-4 justify-content-center">
      <!-- Doctors -->
      <div class="col-md-4">
        <div class="card text-center shadow-sm border-0">
          <div class="card-body">
            <i class="bi bi-person-badge fs-1 text-primary mb-2"></i>
            <h5 class="card-title">Doctors</h5>
            <p class="card-text fs-4 fw-bold">{{ counts.doctors }}</p>
          </div>
        </div>
      </div>

      <!-- Patients -->
      <div class="col-md-4">
        <div class="card text-center shadow-sm border-0">
          <div class="card-body">
            <i class="bi bi-people fs-1 text-success mb-2"></i>
            <h5 class="card-title">Patients</h5>
            <p class="card-text fs-4 fw-bold">{{ counts.patients }}</p>
          </div>
        </div>
      </div>

      <!-- Appointments -->
      <div class="col-md-4">
        <div class="card text-center shadow-sm border-0">
          <div class="card-body">
            <i class="bi bi-calendar-check fs-1 text-warning mb-2"></i>
            <h5 class="card-title">Appointments</h5>
            <p class="card-text fs-4 fw-bold">{{ counts.appointments }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../../api'

const router = useRouter();

const counts = ref({
  doctors: 0,
  patients: 0,
  appointments: 0
})

onMounted(async () => {
  try {
    const response = await api.get('/admin/summary')
    counts.value = response.data
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
})
</script>

<style scoped>
.card {
  border-radius: 1rem;
  transition: transform 0.2s ease-in-out;
}
.card:hover {
  transform: translateY(-5px);
}
h3 {
  font-weight: 600;
}
</style>
