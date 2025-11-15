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
                {{ formatDateTime(appt.datetime) }} ·
                {{ appt.reason || "General Checkup" }}
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
                @click="openTreatmentModal(appt)">
                <span class="d-inline-flex align-items-center">
                  <i class="bi bi-check-circle me-1"></i>
                  <span>Complete</span>
                </span>
              </button>
              <button class="btn btn-outline-danger btn-sm" :disabled="appt.status === Status.CANCELLED"
                @click="cancelAppointment(appt)">
                <span class="d-inline-flex align-items-center">
                  <i class="bi bi-x-circle me-1"></i>
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

    <!-- Treatment Modal -->
    <div class="modal fade" id="treatmentModal" tabindex="-1" aria-labelledby="treatmentModalLabel" aria-hidden="true"
      ref="modalRef">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title" id="treatmentModalLabel">
              Complete Appointment
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="saveTreatment">

              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label">Visit Type</label>
                  <select v-model="form.visit_type" class="form-select" required>
                    <option disabled value="">Select type</option>
                    <option :value="VisitType.OFFLINE">In Person</option>
                    <option :value="VisitType.ONLINE">Online</option>
                  </select>
                </div>

                <div class="col-md-8 mb-3">
                  <label class="form-label">Diagnosis</label>
                  <input v-model="form.diagnosis" type="text" class="form-control" placeholder="Enter diagnosis"
                    required />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Tests Done</label>
                <input v-model="form.test_done" type="text" class="form-control"
                  placeholder="Enter tests done (if any)" />
              </div>

              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea v-model="form.prescription" class="form-control" rows="2"
                  placeholder="Prescribed medications"></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label">Additional Notes</label>
                <textarea v-model="form.notes" class="form-control" rows="2" placeholder="Any extra notes"></textarea>
              </div>
            </form>
          </div>


          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button type="button" class="btn btn-primary" :disabled="loading" @click="saveTreatment">
              <span v-if="loading" class="spinner-border spinner-border-sm"></span>
              <span v-else>Save & Complete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import { useToast } from '../../../composables/useToast'
import { Status, VisitType, formatDateTime, titleCase } from '../../../utils'
import api from '../../../api'

const toast = useToast()

const appointments = ref([])
const activeFilter = ref(Status.BOOKED)
const filterOptions = [...Object.values(Status), 'all']

const selectedAppointment = ref(null)
const loading = ref(false)
const modalRef = ref(null)
let modalInstance = null

const form = ref({
  visit_type: '',
  diagnosis: '',
  test_done: '',
  prescription: '',
  notes: ''
})

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
    toast.error('Failed to fetch the appointments.')
  }
}

async function cancelAppointment(appt) {
  try {
    await api.patch(`/doctor/appointment/${appt.id}`)
    appt.status = Status.CANCELLED
  } catch (err) {
    toast.error('Unable to cancel the appointment.')
  }
}

function openTreatmentModal(appt) {
  selectedAppointment.value = appt
  form.value = {
    visit_type: '',
    diagnosis: '',
    test_done: '',
    prescription: '',
    notes: ''
  }
  if (!modalInstance)
    modalInstance = new Modal(modalRef.value)
  modalInstance.show()
}

async function saveTreatment() {
  if (!selectedAppointment.value) return
  loading.value = true
  try {
    await api.post('/doctor/treatment', {
      appointment_id: selectedAppointment.value.id,
      ...form.value
    })
    // update status locally
    selectedAppointment.value.status = Status.COMPLETED
    modalInstance.hide()
  } catch (err) {
    toast.error('Unable to save the treatment.')
  } finally {
    loading.value = false
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
</style>
