<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
      <div>
        <h4 class="fw-bold mb-0">Book Appointment</h4>
        <p class="text-muted mb-0">Schedule a visit with your preferred doctor.</p>
      </div>
      <button class="btn btn-outline-secondary mt-3 mt-md-0" @click="router.back">
        <i class="bi bi-arrow-left me-1"></i> Back
      </button>
    </div>

    <!-- Step 1: Department Selection -->
    <div v-if="!doctorId && !doctors.length" class="card shadow-sm border-0 mb-4">
      <div class="card-header bg-light fw-semibold">Choose Department</div>
      <div class="card-body">
        <p class="text-muted small mb-3">Select the department to see available doctors.</p>

        <select v-model="selectedDepartment" @change="loadDoctors" class="form-select mb-3">
          <option value="" disabled>Select Department</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">
            {{ dept.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Step 2: Doctor Selection -->
    <div v-else-if="!doctorId && doctors.length" class="card shadow-sm border-0 mb-4">
      <div class="card-header bg-light fw-semibold">Choose Doctor</div>
      <div class="card-body">
        <div class="row g-3">
          <div v-for="doc in doctors" :key="doc.id" class="col-md-4 col-sm-6">
            <div class="border rounded p-3 h-100 text-center cursor-pointer"
              :class="{ 'border-primary': selectedDoctor?.id === doc.id }" @click="selectDoctor(doc)">
              <h6 class="fw-semibold mb-1">{{ doc.name }}</h6>
              <p class="text-muted small mb-0">{{ doc.department.name }}</p>
              <p class="text-muted small mb-0">
                <i class="bi bi-briefcase me-1"></i>
                {{ doc.experience_years || 0 }} years experience
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Doctor Info -->
    <div v-if="doctorId" class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center flex-wrap">
          <div>
            <h5 class="fw-semibold mb-1">{{ doctorName }}</h5>
            <p class="text-muted mb-0">{{ department }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 4: Availability -->
    <div v-if="availability.length" id="availability" class="availability-section my-4">
      <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
        <h5 class="fw-bold mb-0">Doctor's Availability (Next 7 Days)</h5>
      </div>

      <div class="availability-grid">
        <div v-for="slot in availability" :key="slot.date" class="availability-slot" :class="{
          unavailable: !slot.available,
          selected: selectedDate === slot.date
        }" @click="slot.available && selectDate(slot)">
          <div class="date">{{ formatDate(slot.date) }}</div>

          <div v-if="slot.available && slot.start_time && slot.end_time" class="time">
            <i class="bi bi-clock me-1"></i>
            {{ formatTimeTo12Hour(slot.start_time) }} - {{ formatTimeTo12Hour(slot.end_time) }}
          </div>

          <span class="status" :class="slot.available ? 'available' : 'unavailable'">
            {{ slot.available ? 'Available' : 'Unavailable' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Step 5: Select Time -->
    <div v-if="selectedDate" id="select-time" class="time-slot-section my-5">
      <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
        <h5 class="fw-bold mb-1">
          <i class="bi bi-clock-history me-2 text-primary"></i>
          Select Time Slot
        </h5>
        <span class="text-muted small">For {{ formatDate(selectedDate) }}</span>
      </div>

      <div class="time-slot-container">
        <div v-for="slotObj in timeSlots" :key="slotObj.time" class="time-slot"
          :class="{ selected: selectedTime === slotObj.time, disabled: slotObj.disabled }"
          @click="!slotObj.disabled && (selectedTime = slotObj.time)">
          <span>{{ formatTimeTo12Hour(slotObj.time) }}</span>
        </div>
      </div>

      <div class="text-center mt-4">
        <button class="btn btn-primary btn-lg rounded-pill px-5 py-2 shadow-sm" :disabled="!selectedTime"
          @click="confirmBooking">
          <i class="bi bi-check2-circle me-2"></i>
          Confirm Booking
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { formatDate } from '../../../utils'
import api from '../../../api'

const router = useRouter()
const route = useRoute()

const doctorId = ref(route.query.doctor_id)
const doctorName = ref(route.query.doctor_name)
const department = ref(route.query.department)
const reschedule = ref(route.query.reschedule)
const apptId = ref(route.query.appt_id)

const selectedDepartment = ref('')
const selectedDoctor = ref(null)
const selectedDate = ref(null)
const selectedTime = ref(null)

const departments = ref([])
const doctors = ref([])
const availability = ref([])
const timeSlots = ref([])
const bookedByDate = ref({})

function formatTimeTo12Hour(time) {
  if (!time) return ''
  const [hour, minute] = time.split(':').map(Number)
  const period = hour >= 12 ? 'PM' : 'AM'
  const adjustedHour = hour % 12 || 12
  return `${adjustedHour}:${minute.toString().padStart(2, '0')} ${period}`
}

function minutesOfDay(h, m) {
  return h * 60 + m
}

async function fetchBookedSlotsForRange(doctorId, startDateStr, endDateStr) {
  try {
    const res = await api.get(`/patient/doctor-bookings/${doctorId}?start_date=${startDateStr}&end_date=${endDateStr}`)
    return res.data.booked_datetimes || []
  } catch (err) {
    console.error('API Error:', err.response?.data || err.message)
    return []
  }
}

async function loadDepartments() {
  try {
    const res = await api.get('/patient/doctor-departments')
    departments.value = res.data.departments
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function loadDoctors() {
  if (!selectedDepartment.value) return
  try {
    const res = await api.get(`/patient/doctors?department_id=${selectedDepartment.value}`)
    doctors.value = res.data.doctors
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

function selectDoctor(doc) {
  doctorId.value = doc.id
  doctorName.value = doc.name
  department.value = doc.department.name
  selectedDoctor.value = doc
  loadAvailability()
}

async function loadAvailability() {
  if (!doctorId.value) return
  try {
    const res = await api.get(`/patient/doctor-availability/${doctorId.value}?days=7`)
    availability.value = res.data.availability

    if (availability.value.length) {
      const dates = availability.value.map(s => s.date).sort()
      const startDateStr = dates[0]
      const endDateStr = dates[dates.length - 1]

      const bookedDatetimes = await fetchBookedSlotsForRange(doctorId.value, startDateStr, endDateStr)

      const map = {}
      for (const dtStr of bookedDatetimes) {
        const d = new Date(dtStr)
        const dateKey = d.toISOString().slice(0, 10)
        const startMin = minutesOfDay(d.getHours(), d.getMinutes())
        const endMin = startMin + 30
        if (!map[dateKey]) map[dateKey] = []
        map[dateKey].push([startMin, endMin])
      }
      bookedByDate.value = map
    }

    setTimeout(() => {
      document.getElementById('availability').scrollIntoView()
    }, 100)
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

function generateTimeSlots(start, end, dateStr) {
  const slots = []
  const [startH, startM] = start.split(':').map(Number)
  const [endH, endM] = end.split(':').map(Number)
  const current = new Date(dateStr)
  current.setHours(startH, startM, 0, 0)
  const endTime = new Date(dateStr)
  endTime.setHours(endH, endM, 0, 0)

  const booked = bookedByDate.value[dateStr] || []

  while (current < endTime) {
    const hh = String(current.getHours()).padStart(2, '0')
    const mm = String(current.getMinutes()).padStart(2, '0')
    const tStart = minutesOfDay(current.getHours(), current.getMinutes())
    const tEnd = tStart + 30
    let disabled = false

    for (const [bStart, bEnd] of booked) {
      if (tStart < bEnd && tEnd > bStart) {
        disabled = true
        break
      }
    }

    slots.push({ time: `${hh}:${mm}`, disabled })
    current.setMinutes(current.getMinutes() + 30)
  }

  return slots
}

function selectDate(slot) {
  selectedDate.value = slot.date
  selectedTime.value = null

  if (slot.available && slot.start_time && slot.end_time) {
    timeSlots.value = generateTimeSlots(slot.start_time, slot.end_time, slot.date)
  } else {
    timeSlots.value = []
  }

  setTimeout(() => {
    document.getElementById('select-time').scrollIntoView()
  }, 100)
}

async function confirmBooking() {
  if (!selectedDate.value || !selectedTime.value) {
    alert('Please select a date and time.')
    return
  }

  const datetime = `${selectedDate.value}T${selectedTime.value}`

  try {
    if (reschedule.value) {
      await api.put(`/patient/appointment/${apptId.value}`, { datetime })
      alert('Appointment rescheduled successfully!')
    } else {
      await api.post('/patient/appointments', { doctor_id: doctorId.value, datetime })
      alert('Appointment booked successfully!')
    }
    router.push({ path: '/dashboard', query: { tab: 'appointments' } })
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
    alert(err.response.data?.error || 'Failed to book appointment.')
  }
}

onMounted(() => {
  if (!doctorId.value) loadDepartments()
  else loadAvailability()
})
</script>

<style scoped>
.card {
  border-radius: 1rem;
}

.border-primary {
  border: 2px solid #0d6efd !important;
}

.btn {
  border-radius: 0.75rem;
}

.cursor-pointer {
  cursor: pointer;
}

.availability-section {
  width: 100%;
}

.availability-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1rem;
}

.availability-slot {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 16px;
  padding: 1.2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.availability-slot:hover {
  transform: translateY(-3px);
  border-color: #0d6efd;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.15);
}

.availability-slot.selected {
  border-color: #0d6efd;
  background-color: #f0f6ff;
}

.availability-slot.unavailable {
  background-color: #f8f9fa;
  color: #999;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.85;
}

.availability-slot .date {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.4rem;
}

.availability-slot .time {
  color: #555;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.status {
  display: inline-block;
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  border-radius: 50px;
  font-weight: 500;
}

.status.available {
  background-color: #d1f7d1;
  color: #0a662a;
}

.status.unavailable {
  background-color: #e9ecef;
  color: #6c757d;
}

.time-slot-section {
  width: 100%;
  background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 100%);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 14px rgba(13, 110, 253, 0.08);
}

.time-slot-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.time-slot {
  background: #fff;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  text-align: center;
  font-weight: 500;
  color: #0d6efd;
  border: 2px solid #e0e7ff;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.time-slot:hover {
  background: #f0f6ff;
  border-color: #0d6efd;
  transform: translateY(-3px);
  box-shadow: 0 4px 10px rgba(13, 110, 253, 0.15);
}

.time-slot.selected {
  background: #0d6efd;
  color: white;
  border-color: #0d6efd;
  transform: scale(1.05);
  box-shadow: 0 6px 14px rgba(13, 110, 253, 0.3);
}

.time-slot.disabled {
  opacity: 0.45;
  cursor: not-allowed;
  pointer-events: none;
  background: #f8f9fa;
  color: #8a8a8a;
  border-color: #e9ecef;
  transform: none;
  box-shadow: none;
}

.time-slot:active {
  transform: scale(0.97);
}

.btn[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
