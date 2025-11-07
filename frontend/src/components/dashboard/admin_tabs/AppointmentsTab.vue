<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Appointments</h4>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-3">
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

    <!-- Appointment List -->
    <div v-if="filteredAppointments.length" class="table-responsive">
      <table class="table table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Doctor</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appt in filteredAppointments" :key="appt.id">
            <td>{{ appt.id }}</td>
            <td>{{ appt.patient }}</td>
            <td>{{ appt.doctor }}</td>
            <td>{{ appt.date }}</td>
            <td>{{ appt.time }}</td>
            <td>
              <span class="badge" :class="{
                'bg-success': appt.status === Status.COMPLETED,
                'bg-danger': appt.status === Status.CANCELLED,
                'bg-primary': appt.status === Status.BOOKED
              }">
                {{ appt.status }}
              </span>
            </td>
            <td class="text-center">
              <button v-if="appt.status === Status.BOOKED" class="btn btn-sm btn-outline-success me-2"
                @click="markCompleted(appt)">
                <i class="bi bi-check-circle"></i>
              </button>
              <button v-if="appt.status === Status.BOOKED" class="btn btn-sm btn-outline-danger"
                @click="cancelAppointment(appt)">
                <i class="bi bi-x-circle"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center text-muted mt-5">
      <i class="bi bi-calendar-x fs-3"></i>
      <p class="mt-2">No {{ activeTab }} appointments found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../../api'

const Status = {
  BOOKED: "booked",
  COMPLETED: "completed",
  CANCELLED: "cancelled"
}

const activeTab = ref('upcoming')
const appointments = ref([])

const filteredAppointments = computed(() => {
  const now = Date.now();
  if (activeTab.value === 'upcoming') {
    return appointments.value.filter(appt => appt.timestamp >= now)
  } else {
    return appointments.value.filter(appt => appt.timestamp < now)
  }
})

async function markCompleted(appt) {
  try {
    await api.put(`/appointment/${appt.id}`, { status: Status.COMPLETED })
    appt.status = Status.COMPLETED
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function cancelAppointment(appt) {
  try {
    await api.put(`/appointment/${appt.id}`, { status: Status.CANCELLED })
    appt.status = Status.CANCELLED
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

onMounted(async () => {
  try {
    const response = await api.get('/appointments')
    appointments.value = response.data.appointments
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
})
</script>

<style scoped>
.table td,
.table th {
  vertical-align: middle;
}
</style>
