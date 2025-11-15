<template>
  <div class="doctor-home-tab container py-4">
    <h3 class="mb-4 text-center">Dashboard Overview</h3>

    <!-- Quick Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-4" v-for="card in stats" :key="card.label">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center">
            <i :class="card.icon + ' text-primary fs-3 me-3'"></i>
            <div>
              <h6 class="text-muted mb-1">{{ card.label }}</h6>
              <h5 class="fw-semibold mb-0">{{ card.value }}</h5>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Appointments -->
    <div class="d-flex justify-content-center">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-white border-bottom-0 d-flex justify-content-between align-items-center">
          <h5 class="mb-0">
            <i class="bi bi-calendar2-check me-2"></i> Upcoming Appointments (Next {{ days }} Days)
          </h5>
        </div>
        <div class="card-body">
          <div v-if="appointments.length" class="list-group list-group-flush">
            <div v-for="appt in appointments" :key="appt.id"
              class="list-group-item d-flex justify-content-between align-items-start">
              <div>
                <h6 class="fw-semibold mb-1">{{ appt.patient_name }}</h6>
                <small class="text-muted">
                  {{ formatDateTime(appt.datetime) }} · {{ appt.reason || 'General Checkup' }}
                </small>
              </div>
              <span :class="statusBadge(appt.status)">
                {{ titleCase(appt.status) }}
              </span>
            </div>
          </div>
          <div v-else class="text-center text-muted py-3">
            <i class="bi bi-calendar-x fs-3 d-block mb-2"></i>
            No upcoming appointments this week.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '../../../composables/useToast';
import { formatDateTime, titleCase } from '../../../utils';
import api from '../../../api'

const toast = useToast()

const appointments = ref([])
const days = ref(7);
const stats = ref([
  { label: 'Today\'s Appointments', value: 0, icon: 'bi bi-clock' },
  { label: 'Patients Assigned', value: 0, icon: 'bi bi-people' },
  { label: 'Completed This Week', value: 0, icon: 'bi bi-check-circle' }
])

function statusBadge(status) {
  switch (status) {
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
    const res = await api.get(`/doctor/appointments?days=${days.value}`)
    appointments.value = res.data.appointments

    stats.value[0].value = res.data.today_count
    stats.value[1].value = res.data.patient_count
    stats.value[2].value = res.data.completed_count
  } catch (err) {
    toast.error('Failed to fetch the appointments.')
  }
}

onMounted(fetchAppointments)
</script>

<style scoped>
.doctor-home-tab {
  min-height: calc(100vh - 100px);
}

.card {
  border-radius: 0.75rem;
}

.badge {
  font-size: 0.85rem;
  padding: 0.4em 0.6em;
}
</style>
