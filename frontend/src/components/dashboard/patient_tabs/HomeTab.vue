<template>
  <div class="container py-4">
    <!-- Greeting -->
    <div class="mb-4">
      <h4 class="fw-bold">Welcome, {{ user.name }} 👋</h4>
      <p class="text-muted mb-0">
        Here's a quick look at your health and appointments.
      </p>
    </div>

    <!-- Quick Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-4" v-for="(item, i) in statCards" :key="i">
        <div class="card shadow-sm border-0 h-100 rounded-4">
          <div class="card-body text-center">
            <i :class="item.icon + ' fs-3 ' + item.color + ' mb-2'"></i>
            <h6 class="fw-semibold mb-1">{{ item.title }}</h6>
            <p class="fs-5 fw-bold mb-0">{{ item.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Next Appointment + Recent Diagnosis -->
    <div class="d-flex justify-content-around align-items-center flex-wrap gap-3">
      <AppointmentCard v-if="nextAppointment" :appt="nextAppointment" title="Next Appointment"
        @cancel="openCancelModal" />
      <div v-else class="card-body text-muted d-flex align-items-center justify-content-center py-5">
        No upcoming appointments found.
      </div>

      <TreatmentCard v-if="recentTreatment" :treat="recentTreatment" title="Recent Diagnosis" />
      <div v-else class="card-body text-muted d-flex align-items-center justify-content-center py-5">
        No diagnosis available yet.
      </div>
    </div>

    <CancelModal ref="cancelModalRef" :appt="selectedAppt" @cancelled="handleCancelled" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useToast } from '../../../composables/useToast'
import api from '../../../api'

import AppointmentCard from './ui/AppointmentCard.vue'
import TreatmentCard from './ui/TreatmentCard.vue'
import CancelModal from './ui/CancelModal.vue'

const toast = useToast()

const user = ref({ name: 'Patient' })
const stats = ref({ upcoming: 0, visited: 0, prescriptions: 0 })
const nextAppointment = ref(null)
const recentTreatment = ref(null)
const selectedAppt = ref(null)
const cancelModalRef = ref(null)

const statCards = computed(() => [
  { title: 'Upcoming Appointments', value: stats.value.upcoming, icon: 'bi bi-calendar-check', color: 'text-primary' },
  { title: 'Doctors Visited', value: stats.value.visited, icon: 'bi bi-person-video3', color: 'text-success' },
  { title: 'Prescriptions', value: stats.value.prescriptions, icon: 'bi bi-file-medical', color: 'text-danger' },
])

async function loadSummary() {
  try {
    const res = await api.get('/patient/summary')
    user.value = res.data.user
    stats.value = res.data.stats
    nextAppointment.value = res.data.next_appointment
    recentTreatment.value = res.data.recent_diagnosis
  } catch (err) {
    toast.error('Failed to load the summary.')
  }
}

function openCancelModal(appt) {
  selectedAppt.value = appt
  cancelModalRef.value.show()
}

async function handleCancelled() {
  await loadSummary()
}

onMounted(loadSummary)
</script>

<style scoped>
.card {
  border-radius: 1rem;
}
</style>
