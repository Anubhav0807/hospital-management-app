<template>
  <div class="patients-tab container py-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-semibold text-primary mb-0">
        <i class="bi bi-people me-2"></i> My Patients
      </h4>
      <button class="btn btn-outline-primary btn-sm" @click="fetchPatients">
        <i class="bi bi-arrow-clockwise me-1"></i> Refresh
      </button>
    </div>

    <!-- Search Bar -->
    <div class="input-group mb-4">
      <span class="input-group-text bg-white">
        <i class="bi bi-search"></i>
      </span>
      <input
        v-model="search"
        type="text"
        class="form-control"
        placeholder="Search patients by name..."
      />
    </div>

    <!-- Patient List -->
    <div v-if="filteredPatients.length">
      <div
        v-for="patient in filteredPatients"
        :key="patient.id"
        class="card shadow-sm border-0 mb-3"
      >
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="fw-semibold mb-1">{{ patient.name }}</h6>
              <small class="text-muted">
                Age {{ patient.age }} · {{ titleCase(patient.gender) }}<br />
                <i class="bi bi-telephone me-1"></i>{{ patient.phone }}
              </small>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex gap-2">
              <!-- NEW: Navigate to History -->
              <button
                class="btn btn-outline-info btn-sm"
                title="Medical History"
                @click="openHistory(patient.id)"
              >
                <i class="bi bi-clock-history"></i>
              </button>

              <!-- Details Button -->
              <button
                class="btn btn-outline-secondary btn-sm"
                @click="openDetails(patient)"
              >
                <i class="bi bi-eye"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center text-muted py-4">
      <i class="bi bi-person-x fs-3 d-block mb-2"></i>
      No patients assigned yet.
    </div>

    <!-- Details Modal -->
    <div class="modal fade" tabindex="-1" ref="detailsModal" id="detailsModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-person-lines-fill me-2"></i> Patient Details
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedPatient">
            <p><strong>Name:</strong> {{ selectedPatient.name }}</p>
            <p><strong>Age:</strong> {{ selectedPatient.age }}</p>
            <p><strong>Gender:</strong> {{ titleCase(selectedPatient.gender) }}</p>
            <p><strong>Phone:</strong> {{ selectedPatient.phone }}</p>
            <p><strong>Email:</strong> {{ selectedPatient.email }}</p>
            <p><strong>Last Visit:</strong> {{ formatDateTime(selectedPatient.last_visit) || 'N/A' }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { formatDateTime, titleCase } from '../../../utils'
import { Modal } from 'bootstrap'
import { useRouter } from 'vue-router'
import api from '../../../api'

const router = useRouter()

const patients = ref([])
const search = ref('')
const selectedPatient = ref(null)
const detailsModal = ref(null)
let modalInstance = null

// Computed list after search filter
const filteredPatients = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return patients.value
  return patients.value.filter(p => p.name.toLowerCase().includes(q))
})

// Fetch doctor's patients
async function fetchPatients() {
  try {
    const res = await api.get('/doctor/patients')
    patients.value = res.data.patients
  } catch (err) {
    console.error('API Error:', err.response?.data?.error || err.message)
  }
}

// Navigate to full medical history
function openHistory(patientId) {
  router.push({
    path: '/dashboard',
    query: {
      tab: 'history',
      patient_id: patientId
    }
  })
}

// Modal for patient details
function openDetails(patient) {
  selectedPatient.value = patient
  nextTick(() => {
    if (!modalInstance) {
      modalInstance = new Modal(detailsModal.value)
    }
    modalInstance.show()
  })
}

onMounted(fetchPatients)
</script>

<style scoped>
.patients-tab {
  min-height: calc(100vh - 100px);
}

.card {
  border-radius: 0.75rem;
}

.modal-content {
  border-radius: 0.75rem;
}
</style>
