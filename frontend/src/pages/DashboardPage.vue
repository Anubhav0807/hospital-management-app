<template>
  <Dashboard v-if="user" :title="titleCase(user.role)" :tabs="tabs[user.role]" :user="user" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { titleCase } from '../utils'

import Dashboard from '../components/dashboard/Dashboard.vue'

const user = ref(null)

const tabs = {
  admin: [
    { label: 'Home', component: 'HomeTab', name: 'home', icon: 'bi bi-house' },
    { label: 'Doctors', component: 'DoctorsTab', name: 'doctors', icon: 'bi bi-person-badge' },
    { label: 'Patients', component: 'PatientsTab', name: 'patients', icon: 'bi bi-people' },
    { label: 'Appointments', component: 'AppointmentsTab', name: 'appointments', icon: 'bi bi-calendar-check' }
  ],
  doctor: [
    { label: 'Home', component: 'HomeTab', name: 'home', icon: 'bi bi-house-door' },
    { label: 'Appointments', component: 'AppointmentsTab', name: 'appointments', icon: 'bi bi-calendar2-check' },
    { label: 'Patients', component: 'PatientsTab', name: 'patients', icon: 'bi bi-people' },
    { label: 'Availability', component: 'AvailabilityTab', name: 'availability', icon: 'bi bi-clock' }
  ],
  patient: [
    { label: 'Home', component: 'HomeTab', name: 'home', icon: 'bi bi-house-door' },
    { label: 'Appointments', component: 'AppointmentsTab', name: 'appointments', icon: 'bi bi-calendar2-check' },
    { label: 'Doctors', component: 'DoctorsTab', name: 'doctors', icon: 'bi bi-person-badge' },
    { label: 'New Booking', component: 'BookingTab', name: 'new-booking', icon: 'bi bi-calendar-plus', hidden: true }
  ]
}

onMounted(() => {
  const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
  user.value = storedUser
})
</script>
