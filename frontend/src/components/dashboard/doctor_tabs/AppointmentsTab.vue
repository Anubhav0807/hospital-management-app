<template>
  <div class="appointments-tab container py-4">
    <!-- Title -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-semibold text-primary mb-0">
        <i class="bi bi-calendar2-check me-2"></i> Appointments
      </h4>
      <button class="btn btn-outline-primary btn-sm" @click="fetchAppointments">
        <i class="bi bi-arrow-clockwise me-1"></i> Refresh
      </button>
    </div>

    <!-- Filters -->
    <div class="d-flex flex-wrap gap-2 mb-3">
      <button v-for="opt in filterOptions" :key="opt" @click="activeFilter = opt" class="btn btn-sm"
        :class="activeFilter === opt ? 'btn-primary' : 'btn-outline-secondary'">
        {{ titleCase(opt) }}
      </button>
    </div>

    <!-- Appointment List -->
    <div v-if="filteredAppointments.length">
      <div v-for="appt in filteredAppointments" :key="appt.id" class="card shadow-sm border-0 mb-3">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="fw-semibold mb-1">{{ appt.patient_name }}</h6>
              <small class="text-muted">
                {{ formatDate(appt.datetime) }} · {{ appt.reason || 'General Checkup' }}
              </small>
              <div class="mt-2">
                <span :class="statusBadge(appt.status)">
                  {{ titleCase(appt.status) }}
                </span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex gap-1">
              <button class="btn btn-outline-success btn-sm" :disabled="appt.status === Status.COMPLETED"
                @click="markStatus(appt, Status.COMPLETED)">
                <span class="d-inline-flex align-items-center">
                  <i class="bi bi-check-circle me-1"></i>
                  <span>Complete</span>
                </span>
              </button>
              <button class="btn btn-outline-danger btn-sm" :disabled="appt.status === Status.CANCELLED"
                @click="markStatus(appt, Status.CANCELLED)">
                <span class="d-inline-flex align-items-center">
                  <i class="bi bi-check-circle me-1"></i>
                  <span>Cancel</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center text-muted py-4">
      <i class="bi bi-calendar-x fs-3 d-block mb-2"></i>
      No appointments found for this period.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Status, formatDate, titleCase } from '../../../utils'
import api from '../../../api'

const appointments = ref([])
const activeFilter = ref(Status.BOOKED)

const filterOptions = [...Object.values(Status), 'all']

const filteredAppointments = computed(() => {
  if (activeFilter.value === 'all') return appointments.value
  return appointments.value.filter(a => a.status === activeFilter.value)
})

function statusBadge(status) {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'badge bg-success'
    case 'cancelled':
      return 'badge bg-danger'
    default:
      return 'badge bg-secondary'
  }
}

async function fetchAppointments() {
  try {
    const res = await api.get('/doctor/appointments')
    appointments.value = res.data.appointments
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function markStatus(appt, newStatus) {
  try {
    console.log(newStatus)
    await api.patch(`/doctor/appointments/${appt.id}`, { status: newStatus })
    appt.status = newStatus
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

onMounted(fetchAppointments)
</script>

<style scoped>
.appointments-tab {
  min-height: calc(100vh - 100px);
}

.card {
  border-radius: 0.75rem;
}

.badge {
  font-size: 0.85rem;
  padding: 0.4em 0.6em;
}

.modal-content {
  border-radius: 0.75rem;
}

textarea {
  resize: none;
}
</style>
