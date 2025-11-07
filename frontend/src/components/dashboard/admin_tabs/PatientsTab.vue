<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Manage Patients</h4>
    </div>

    <!-- Search -->
    <div class="mb-3">
      <input
        v-model="searchQuery"
        type="text"
        class="form-control"
        placeholder="Search by name, ID, or contact..."
      />
    </div>

    <!-- Patients Table -->
    <div v-if="filteredPatients.length" class="table-responsive">
      <table class="table table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Age</th>
            <th>Gender</th>
            <th>Contact</th>
            <th>Address</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="patient in filteredPatients" :key="patient.id">
            <td>{{ patient.id }}</td>
            <td>{{ patient.name }}</td>
            <td>{{ patient.age }}</td>
            <td>{{ patient.gender }}</td>
            <td>{{ patient.contact }}</td>
            <td>{{ patient.address }}</td>
            <td>
              <span
                class="badge"
                :class="patient.blacklisted ? 'bg-danger' : 'bg-success'"
              >
                {{ patient.blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
            <td class="text-center">
              <button
                class="btn btn-sm btn-outline-warning me-2"
                @click="toggleBlacklist(patient)"
              >
                <i
                  :class="patient.blacklisted ? 'bi bi-person-check' : 'bi bi-person-fill-slash'"
                ></i>
              </button>
              <button
                class="btn btn-sm btn-outline-danger"
                @click="removePatient(patient.id)"
              >
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center text-muted mt-5">
      <i class="bi bi-person-slash fs-3"></i>
      <p class="mt-2">No patients found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../../api.js'

const patients = ref([])
const searchQuery = ref('')

const filteredPatients = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return patients.value.filter(
    p =>
      p.name.toLowerCase().includes(q) ||
      p.contact.toLowerCase().includes(q) ||
      p.id.toString().includes(q)
  )
})

// ✅ Fetch patients from API
async function fetchPatients() {
  try {
    const res = await api.get('/admin/patients')
    patients.value = res.data
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function removePatient(id) {
  if (!confirm('Are you sure you want to remove this patient?')) return
  try {
    await api.delete(`/admin/patient/${id}`)
    patients.value = patients.value.filter(p => p.id !== id)
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

async function toggleBlacklist(patient) {
  try {
    const res = await api.patch(
      `/admin/patient/${patient.id}/blacklist`,
      { blacklisted: !patient.blacklisted }
    )
    patient.blacklisted = res.data.blacklisted
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
  }
}

onMounted(fetchPatients)
</script>

<style scoped>
.table td,
.table th {
  vertical-align: middle;
}
</style>
