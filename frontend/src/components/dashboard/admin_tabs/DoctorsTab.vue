<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Manage Doctors</h4>
      <button class="btn btn-primary" @click="openModal">
        <i class="bi bi-plus-lg me-1"></i> Add Doctor
      </button>
    </div>

    <!-- Search -->
    <div class="mb-3">
      <input
        v-model="searchQuery"
        type="text"
        class="form-control"
        placeholder="Search by name or department..."
      />
    </div>

    <!-- Doctors Table -->
    <div v-if="filteredDoctors.length" class="table-responsive">
      <table class="table table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th>Name</th>
            <th>Department</th>
            <th>Experience (yrs)</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doctor in filteredDoctors" :key="doctor.id">
            <td>{{ doctor.name }}</td>
            <td>{{ doctor.department.name }}</td>
            <td>{{ doctor.experience }}</td>
            <td>{{ doctor.contact }}</td>
            <td>
              <span class="badge" :class="doctor.blacklisted ? 'bg-danger' : 'bg-success'">
                {{ doctor.blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
            <td class="text-center">
              <button
                class="btn btn-sm btn-outline-warning me-2"
                title="Toggle Blacklist"
                @click="toggleBlacklist(doctor)"
              >
                <i :class="doctor.blacklisted ? 'bi bi-person-check' : 'bi bi-person-fill-slash'"></i>
              </button>
              <button
                class="btn btn-sm btn-outline-primary me-2"
                @click="editDoctor(doctor)"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteDoctor(doctor.id)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center text-muted mt-5">
      <i class="bi bi-person-slash fs-3"></i>
      <p class="mt-2">No doctors found.</p>
    </div>

    <!-- Add/Edit Doctor Modal -->
    <div
      class="modal fade"
      id="doctorModal"
      tabindex="-1"
      aria-labelledby="doctorModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="doctorModalLabel">
              {{ isEditing ? "Update Doctor" : "Add Doctor" }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="saveDoctor">
              <div class="mb-3" v-if="!isEditing">
                <label class="form-label">Email</label>
                <input v-model="form.email" type="email" class="form-control" required />
              </div>

              <div class="mb-3">
                <label class="form-label">Name</label>
                <input v-model="form.name" type="text" class="form-control" required />
              </div>

              <div class="d-flex flex-column flex-md-row justify-content-between">
                <div class="mb-3">
                  <label class="form-label">Contact Number</label>
                  <input v-model="form.contact" type="text" class="form-control" required />
                </div>

                <div class="mb-3">
                  <label class="form-label">Experience (in years)</label>
                  <input
                    v-model="form.experience_years"
                    type="number"
                    min="0"
                    class="form-control"
                    required
                  />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Department</label>
                <select v-model="form.department_id" class="form-select" required>
                  <option disabled value="">Select department</option>
                  <option v-for="d in departments" :key="d.id" :value="d.id">
                    {{ d.name }}
                  </option>
                </select>
              </div>

              <div class="d-flex justify-content-end">
                <button type="submit" class="btn btn-success">
                  {{ isEditing ? "Update" : "Add" }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import api from '../../../api.js'

const doctors = ref([])
const departments = ref([])
const searchQuery = ref('')
const isEditing = ref(false)
const editingId = ref(null)

const form = ref({
  email: '',
  name: '',
  contact: '',
  department_id: '',
  experience_years: ''
})

// Fetch Data
async function fetchDoctors() {
  try {
    const res = await api.get('/admin/doctors')
    doctors.value = res.data.doctors
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function fetchDepartments() {
  try {
    const res = await api.get('/admin/departments')
    departments.value = res.data.departments
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

// CRUD Actions
async function saveDoctor() {
  try {
    if (isEditing.value) {
      await api.put(`/admin/doctor/${editingId.value}`, form.value)
    } else {
      await api.post('/admin/doctor', form.value)
    }
    await fetchDoctors()
    resetForm()
    closeModal()
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function deleteDoctor(id) {
  if (confirm('Are you sure you want to delete this doctor?')) {
    try {
      await api.delete(`/admin/doctor/${id}`)
      doctors.value = doctors.value.filter(d => d.id !== id)
    } catch (err) {
      console.error('API Error:', err.response.data?.error || err.message)
    }
  }
}

async function toggleBlacklist(doctor) {
  try {
    await api.patch(`/admin/doctor/${doctor.id}/blacklist`, {
      blacklisted: !doctor.blacklisted
    })
    doctor.blacklisted = !doctor.blacklisted
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

// Modal Logic
function openModal() {
  resetForm()
  const modalEl = document.getElementById('doctorModal')
  const modal = Modal.getOrCreateInstance(modalEl)
  modal.show()
}

function editDoctor(doctor) {
  isEditing.value = true
  editingId.value = doctor.id
  form.value = {
    name: doctor.name,
    contact: doctor.contact,
    department_id: doctor.department.id,
    experience_years: doctor.experience,
    email: doctor.email
  }
  const modalEl = document.getElementById('doctorModal')
  const modal = Modal.getOrCreateInstance(modalEl)
  modal.show()
}

function closeModal() {
  const modalEl = document.getElementById('doctorModal')
  const modal = Modal.getOrCreateInstance(modalEl)
  modal.hide()
}

// Utility
function resetForm() {
  form.value = {
    email: '',
    name: '',
    contact: '',
    department_id: '',
    experience_years: ''
  }
}

// Search
const filteredDoctors = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return doctors.value.filter(
    d =>
      d.name.toLowerCase().includes(q) ||
      (d.department.name.toLowerCase().includes(q))
  )
})

// Lifecycle
onMounted(() => {
  fetchDoctors()
  fetchDepartments()
  
  // Bootstrap's built-in event for when the modal is FULLY HIDDEN
  const modalEl = document.getElementById('doctorModal')
  modalEl.addEventListener('hidden.bs.modal', () => {
    isEditing.value = false
    editingId.value = null
  })
})
</script>

<style scoped>
.table td,
.table th {
  vertical-align: middle;
}
</style>
