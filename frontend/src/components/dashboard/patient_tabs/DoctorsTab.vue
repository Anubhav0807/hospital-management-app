<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
      <div>
        <h4 class="fw-bold mb-0">Find a Doctor</h4>
        <p class="text-muted mb-0">Search and book appointments easily.</p>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="row g-3 mb-4">
      <div class="col-md-6">
        <input v-model="searchQuery" type="text" class="form-control" placeholder="Search by doctor name" />
      </div>
      <div class="col-md-6">
        <select v-model="selectedDepartment" class="form-select">
          <option value="">All Departments</option>
          <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
        </select>
      </div>
    </div>

    <!-- Doctor Cards -->
    <div class="row g-4">
      <div v-for="doc in filteredDoctors" :key="doc.id" class="col-md-4 col-sm-6">
        <div class="card shadow-sm border-0 h-100 hover-card">
          <div class="card-body d-flex flex-column justify-content-between">
            <div>
              <!-- Doctor Info -->
              <div class="d-flex align-items-center mb-3">
                <div>
                  <h6 class="fw-semibold mb-0">{{ doc.name }}</h6>
                  <small class="text-muted">{{ doc.department.name }}</small>
                </div>
              </div>

              <p class="text-muted small mb-2">
                <i class="bi bi-building me-1"></i>
                {{ doc.department.description || 'General Department' }}
              </p>

              <!-- Availability Summary -->
              <div class="availability mt-3">
                <p class="fw-semibold small mb-2">
                  <i class="bi bi-calendar-week me-1"></i> Next 7 Days:
                </p>

                <div class="availability-strip">
                  <div
                    v-for="slot in doc.availability"
                    :key="slot.date"
                    class="day-slot"
                    :class="[
                      slot.available ? 'available' : 'unavailable',
                      isCompact ? 'compact' : null
                    ]"
                    :title="formatFullDate(slot.date)"
                  >
                    <div class="day fw-semibold">{{ formatDay(slot.date) }}</div>
                    <div class="date small">{{ formatDayNum(slot.date) }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Book Button -->
            <div class="mt-3">
              <button class="btn btn-primary w-100" @click="bookAppointment(doc)">
                <i class="bi bi-calendar-plus me-1"></i> Book Appointment
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- No results -->
      <div v-if="filteredDoctors.length === 0" class="text-center py-5 text-muted">
        <i class="bi bi-search fs-1 mb-2"></i>
        <p>No doctors found matching your search.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../../../composables/useToast'
import api from '../../../api'

const router = useRouter()
const toast = useToast()

const doctors = ref([])
const departments = ref([])
const searchQuery = ref('')
const selectedDepartment = ref('')

// Reactive flag to track viewport width
const isCompact = ref(window.innerWidth < 992)

function handleResize() {
  isCompact.value = window.innerWidth < 992
}

// Formatting function — uses locale API
function formatDay(dateStr) {
  const date = new Date(dateStr)
  const options = isCompact.value
    ? { weekday: 'narrow' }  // → 'M'
    : { weekday: 'short' }   // → 'Mon'
  return date.toLocaleDateString('en-IN', options)
}

function formatDayNum(dateStr) {
  return new Date(dateStr).getDate()
}

function formatFullDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

// Filtered list
const filteredDoctors = computed(() =>
  doctors.value.filter((doc) => {
    const matchesName = doc.name
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())
    const matchesDept =
      !selectedDepartment.value ||
      doc.department.name === selectedDepartment.value
    return matchesName && matchesDept
  })
)

// Load doctors
async function loadDoctors() {
  try {
    const res = await api.get('/patient/doctors')
    doctors.value = res.data.doctors
    departments.value = [...new Set(res.data.doctors.map((d) => d.department.name))]
  } catch (err) {
    toast.error('Failed to load the doctors.')
  }
}

// Navigate to booking
function bookAppointment(doc) {
  router.push({
    path: '/dashboard',
    query: {
      tab: 'new-booking',
      doctor_id: doc.id,
      doctor_name: doc.name,
      department: doc.department.name,
    },
  })
}

onMounted(() => {
  loadDoctors()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.card {
  border-radius: 1rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.hover-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* --- Clean & balanced availability strip --- */
.availability-strip {
  display: flex;
  justify-content: space-between;
  gap: 6px;
  overflow-x: auto;
  overflow-y: visible;
  padding: 2px 0;
}

.day-slot {
  flex: 1;
  min-width: 0;
  background: #f8f9fa;
  border-radius: 0.75rem;
  padding: 8px 0;
  text-align: center;
  transition: all 0.25s ease;
  border: 1px solid transparent;
  cursor: default;
}

.day-slot.compact {
  padding: 0px;
}

.day-slot.available {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
  border-color: rgba(25, 135, 84, 0.25);
}

.day-slot.unavailable {
  background-color: rgba(108, 117, 125, 0.05);
  color: #6c757d;
  border-color: rgba(108, 117, 125, 0.15);
}

.day-slot:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

/* Day and date */
.day {
  font-size: 0.8rem;
  font-weight: 600;
}

.date {
  font-size: 0.75rem;
}

/* Prevent squish on small screens: switch to single-letter weekday */
@media (max-width: 600px) {
  .day {
    font-size: 0.85rem;
    font-weight: 600;
  }

  .date {
    font-size: 0.7rem;
  }

  .availability-strip {
    gap: 4px;
  }
}
</style>
