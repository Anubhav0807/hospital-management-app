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
              <button
                class="btn btn-outline-primary btn-sm"
                @click="toggleHistory(patient)"
              >
                <i
                  class="bi"
                  :class="expandedPatient === patient.id ? 'bi-chevron-up' : 'bi-chevron-down'"
                ></i>
              </button>
              <button
                class="btn btn-outline-secondary btn-sm"
                @click="openDetails(patient)"
              >
                <i class="bi bi-eye me-1"></i>
                Details
              </button>
            </div>
          </div>
        </div>

        <!-- Collapsible Medical History -->
        <transition name="fade">
          <div v-if="expandedPatient === patient.id" class="border-top p-3 bg-light">
            <div v-if="loadingHistory[patient.id]" class="text-center py-3">
              <div class="spinner-border text-primary" role="status"></div>
            </div>

            <div v-else-if="patientHistory[patient.id]?.length">
              <h6 class="fw-semibold text-secondary mb-3">
                <i class="bi bi-journal-medical me-2"></i>Medical History
              </h6>

              <div
                v-for="(record, idx) in patientHistory[patient.id]"
                :key="idx"
                class="card border-0 shadow-sm mb-2"
              >
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <strong>{{ formatDateTime(record.date) }}</strong>
                      <small class="text-muted d-block">
                        Appointment ID: {{ record.appointment_id }}
                      </small>
                    </div>
                    <span :class="statusBadge(record.status)">{{ titleCase(record.status) }}</span>
                  </div>

                  <div class="row g-2">
                    <div class="col-md-6">
                      <h6 class="fw-semibold text-secondary mb-1">Diagnosis</h6>
                      <p class="mb-0 small">{{ record.diagnosis || '—' }}</p>
                    </div>
                    <div class="col-md-6">
                      <h6 class="fw-semibold text-secondary mb-1">Prescription</h6>
                      <p class="mb-0 small">{{ record.prescription || '—' }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center text-muted py-3">
              <i class="bi bi-folder2-open fs-4 d-block mb-1"></i>
              No history found for this patient.
            </div>
          </div>
        </transition>
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
import api from '../../../api'

const patients = ref([])
const search = ref('')
const selectedPatient = ref(null)
const detailsModal = ref(null)
const expandedPatient = ref(null)
const patientHistory = ref({})
const loadingHistory = ref({})
let modalInstance = null

const filteredPatients = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return patients.value
  return patients.value.filter(p => p.name.toLowerCase().includes(query))
})

function statusBadge(status) {
  switch (status?.toLowerCase()) {
    case 'completed':
      return 'badge bg-success'
    case 'cancelled':
      return 'badge bg-danger'
    default:
      return 'badge bg-secondary'
  }
}

async function fetchPatients() {
  try {
    const res = await api.get('/doctor/patients')
    patients.value = res.data.patients
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function toggleHistory(patient) {
  if (expandedPatient.value === patient.id) {
    expandedPatient.value = null
    return
  }

  expandedPatient.value = patient.id

  // Only load history once
  if (patientHistory.value[patient.id]) return

  loadingHistory.value[patient.id] = true
  try {
    const res = await api.get(`/doctor/patient/${patient.id}/history`)
    patientHistory.value[patient.id] = res.data.history || []
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
    patientHistory.value[patient.id] = []
  } finally {
    loadingHistory.value[patient.id] = false
  }
}

// Modal
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

.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
