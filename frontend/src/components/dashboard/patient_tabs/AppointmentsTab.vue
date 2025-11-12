<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
      <div>
        <h4 class="fw-bold mb-0">My Appointments</h4>
        <p class="text-muted mb-0">Manage all your bookings in one place.</p>
      </div>
      <button class="btn btn-primary mt-3 mt-md-0" @click="navigateToBooking">
        <i class="bi bi-calendar-plus me-1"></i> Book New Appointment
      </button>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'upcoming' }" @click="activeTab = 'upcoming'">
          Upcoming
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'past' }" @click="activeTab = 'past'">
          Past
        </button>
      </li>
    </ul>

    <!-- Upcoming Appointments -->
    <div v-if="activeTab === 'upcoming'">
      <div v-if="upcoming.length" class="row g-3">
        <div v-for="appt in upcoming" :key="appt.id" class="col-md-6">
          <AppointmentCard :appt="appt" @cancel="openCancelModal" />
        </div>
      </div>

      <div v-else class="text-center py-5 text-muted">
        <i class="bi bi-calendar-x fs-1 mb-2"></i>
        <p>No upcoming appointments.</p>
      </div>
    </div>

    <!-- Past Appointments -->
    <div v-if="activeTab === 'past'">
      <div v-if="past.length" class="row g-3">
        <div v-for="treat in past" :key="treat.id" class="col-md-6">
          <TreatmentCard :treat="treat" />
        </div>
      </div>

      <div v-else class="text-center py-5 text-muted">
        <i class="bi bi-archive fs-1 mb-2"></i>
        <p>No past appointments found.</p>
      </div>
    </div>

    <CancelModal ref="cancelModalRef" :appt="selectedAppt" @cancelled="handleCancelled" />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../../api'

import AppointmentCard from './ui/AppointmentCard.vue'
import TreatmentCard from './ui/TreatmentCard.vue'
import CancelModal from './ui/CancelModal.vue'

const router = useRouter()
const activeTab = ref('upcoming')
const selectedAppt = ref(null)
const cancelModalRef = ref(null)
const upcoming = ref([])
const past = ref([])

async function loadAppointments() {
  try {
    const res = await api.get('/patient/appointments')
    upcoming.value = res.data.upcoming
    past.value = res.data.past
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

function navigateToBooking() {
  router.push({
    path: '/dashboard',
    query: { tab: 'new-booking' }
  })
}

function openCancelModal(appt) {
  selectedAppt.value = appt
  cancelModalRef.value.show()
}

async function handleCancelled() {
  await loadAppointments()
}

onMounted(loadAppointments)
</script>
