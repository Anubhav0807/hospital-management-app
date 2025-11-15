<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Appointments</h4>

      <!-- Refresh button -->
      <button class="btn btn-outline-primary btn-sm" @click="fetchAppointments">
        <i class="bi bi-arrow-clockwise me-1"></i> Refresh
      </button>
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
                'bg-success': appt.status === ApptStatus.COMPLETED,
                'bg-danger': appt.status === ApptStatus.CANCELLED,
                'bg-primary': appt.status === ApptStatus.BOOKED
              }">
                {{ titleCase(appt.status) }}
              </span>
            </td>
            <td class="text-center">
              <button v-if="appt.status === ApptStatus.BOOKED" class="btn btn-sm btn-outline-success me-2"
                @click="markCompleted(appt)">
                <i class="bi bi-check-circle"></i>
              </button>
              <button v-if="appt.status === ApptStatus.BOOKED" class="btn btn-sm btn-outline-danger"
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
import { useToast } from '../../../composables/useToast'
import { ApptStatus, titleCase } from '../../../utils'
import api from '../../../api'

const toast = useToast();

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

async function fetchAppointments() {
  try {
    const response = await api.get('/admin/appointments')
    appointments.value = response.data.appointments
  } catch (err) {
    toast.error('Failed to fetch the appointments.')
  }
}

async function markCompleted(appt) {
  try {
    await api.put(`/admin/appointment/${appt.id}`, { status: ApptStatus.COMPLETED })
    appt.status = ApptStatus.COMPLETED
  } catch (err) {
    toast.error(`Unable to mark the appointment as ${ApptStatus.COMPLETED}.`)
  }
}

async function cancelAppointment(appt) {
  try {
    await api.put(`/admin/appointment/${appt.id}`, { status: ApptStatus.CANCELLED })
    appt.status = ApptStatus.CANCELLED
  } catch (err) {
    toast.error(`Unable to mark the appointment as ${ApptStatus.COMPLETED}.`)
  }
}

onMounted(fetchAppointments)
</script>

<style scoped>
.table td,
.table th {
  vertical-align: middle;
}
</style>
