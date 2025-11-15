<template>
  <div class="history-tab container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-semibold text-primary mb-0">
        <i class="bi bi-clock-history me-2"></i> Patient History
      </h4>

      <div>
        <button
          v-if="patient_id"
          class="btn btn-outline-primary btn-sm me-2"
          @click="router.back"
        >
          <i class="bi bi-arrow-left me-1"></i> Back
        </button>

        <button
          class="btn btn-outline-success btn-sm"
          @click="exportCSV"
        >
          <i class="bi bi-download me-1"></i> Export CSV
        </button>
      </div>
    </div>

    <!-- Filter Row -->
    <div class="row mb-3 g-2 align-items-end">
      <div class="col-md-6">
        <label class="form-label small">Search</label>
        <div class="input-group">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input
            v-model="searchQuery"
            type="text"
            class="form-control"
            placeholder="Search diagnosis, notes, prescription, tests..."
          />
        </div>
      </div>

      <div class="col-md-3">
        <label class="form-label small">Start Date</label>
        <input type="date" v-model="startDate" class="form-control" />
      </div>

      <div class="col-md-3">
        <label class="form-label small">End Date</label>
        <input type="date" v-model="endDate" class="form-control" />
      </div>
    </div>

    <div class="table-responsive shadow-sm rounded">
      <table class="table table-striped align-middle">
        <thead class="table-primary">
          <tr>
            <th>#</th>
            <th>Date</th>
            <th>Visit Type</th>
            <th>Diagnosis</th>
            <th>Tests Done</th>
            <th>Prescription</th>
            <th>Notes</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(t, index) in paginated" :key="t.id">
            <td>{{ index + 1 + (currentPage - 1) * perPage }}</td>
            <td>{{ formatDate(t.date) }}</td>
            <td>{{ titleCase(t.visit_type) }}</td>
            <td>{{ t.diagnosis }}</td>
            <td>{{ t.test_done || '-' }}</td>
            <td>{{ t.prescription || '-' }}</td>
            <td>{{ t.notes || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <nav class="mt-3 d-flex justify-content-center">
      <ul class="pagination">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" @click="prevPage">Previous</button>
        </li>

        <li
          class="page-item"
          v-for="page in totalPages"
          :key="page"
          :class="{ active: currentPage === page }"
        >
          <button class="page-link" @click="currentPage = page">
            {{ page }}
          </button>
        </li>

        <li
          class="page-item"
          :class="{ disabled: currentPage === totalPages }"
        >
          <button class="page-link" @click="nextPage">Next</button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { titleCase, formatDate } from '../../utils'
import api from '../../api'

const route = useRoute()
const router = useRouter()

const patient_id = ref(route.query.patient_id)

const treatments = ref([])
const searchQuery = ref('')
const startDate = ref('')
const endDate = ref('')

const currentPage = ref(1)
const perPage = ref(10)

async function fetchTreatments() {
  try {
    const res = await api.get('/history/treatments', {
      params: { patient_id: patient_id.value }
    })
    treatments.value = res.data.treatments
  } catch (err) {
    console.error('API Error:', err.response?.data || err.message)
  }
}

const filtered = computed(() => {
  let list = treatments.value

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(t =>
      [t.diagnosis, t.prescription, t.notes, t.test_done]
        .filter(Boolean)
        .some(field => field.toLowerCase().includes(q))
    )
  }

  if (startDate.value) {
    const start = new Date(startDate.value)
    list = list.filter(t => new Date(t.date) >= start)
  }

  if (endDate.value) {
    const end = new Date(endDate.value)
    end.setHours(23, 59, 59)
    list = list.filter(t => new Date(t.date) <= end)
  }

  return list
})

const totalPages = computed(() =>
  Math.ceil(filtered.value.length / perPage.value)
)

const paginated = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filtered.value.slice(start, start + perPage.value)
})

function prevPage() {
  if (currentPage.value > 1) currentPage.value--
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++
}

async function exportCSV() {
  try {
    const res = await api.post('/history/export', {
      patient_id: patient_id.value
    })

    alert('Export Started')
  } catch (err) {
    console.error('API Error:', err.response?.data || err.message)
  }
}

onMounted(fetchTreatments)
</script>

<style scoped>
.table {
  font-size: 0.9rem;
}

.pagination .page-link {
  cursor: pointer;
}
</style>
