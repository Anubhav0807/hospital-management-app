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
            @input="onFilterChange"
          />
        </div>
      </div>

      <div class="col-md-3">
        <label class="form-label small">Start Date</label>
        <input type="date" v-model="startDate" class="form-control" @change="onFilterChange" />
      </div>

      <div class="col-md-3">
        <label class="form-label small">End Date</label>
        <input type="date" v-model="endDate" class="form-control" @change="onFilterChange" />
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
          <!-- Loading Spinner -->
          <tr v-if="loading">
            <td colspan="7" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </td>
          </tr>

          <!-- Records -->
          <tr v-for="(t, index) in treatments" :key="t.id" v-else>
            <td>{{ index + 1 + (currentPage - 1) * perPage }}</td>
            <td>{{ formatDate(t.date) }}</td>
            <td>{{ titleCase(t.visit_type) }}</td>
            <td>{{ t.diagnosis }}</td>
            <td>{{ t.test_done || '-' }}</td>
            <td>{{ t.prescription || '-' }}</td>
            <td>{{ t.notes || '-' }}</td>
          </tr>

          <!-- No Data -->
          <tr v-if="!loading && treatments.length === 0">
            <td colspan="7" class="text-center py-3 text-muted">No records found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <nav class="mt-3 d-flex justify-content-center" v-if="totalPages > 1">
      <ul class="pagination">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" @click="goToPage(currentPage - 1)">
            Previous
          </button>
        </li>

        <li
          class="page-item"
          v-for="page in totalPages"
          :key="page"
          :class="{ active: currentPage === page }"
        >
          <button class="page-link" @click="goToPage(page)">
            {{ page }}
          </button>
        </li>

        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button class="page-link" @click="goToPage(currentPage + 1)">
            Next
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '../../composables/useToast'
import { titleCase, formatDate } from '../../utils'
import api from '../../api'

const toast = useToast()
const route = useRoute()
const router = useRouter()

const patient_id = ref(route.query.patient_id)

const treatments = ref([])
const totalRecords = ref(0)

const searchQuery = ref('')
const startDate = ref('')
const endDate = ref('')

const currentPage = ref(1)
const perPage = ref(10)

const loading = ref(false)

async function fetchTreatments(page = 1) {
  loading.value = true
  try {
    const res = await api.get('/history/treatments', {
      params: {
        patient_id: patient_id.value,
        page,
        per_page: perPage.value,
        search: searchQuery.value,
        start_date: startDate.value,
        end_date: endDate.value
      }
    })

    treatments.value = res.data.treatments
    totalRecords.value = res.data.total
  } catch (err) {
    toast.error('Failed to load history.')
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchTreatments(page)
}

function onFilterChange() {
  currentPage.value = 1
  fetchTreatments(1)
}

const totalPages = computed(() =>
  Math.ceil(totalRecords.value / perPage.value)
)

async function exportCSV() {
  try {
    const res = await api.post('/history/export', {
      patient_id: patient_id.value
    })

    toast.success(res.data.message)
  } catch (err) {
    toast.error('Failed to export.')
  }
}

onMounted(() => fetchTreatments(1))
</script>

<style scoped>
.table {
  font-size: 0.9rem;
}

.pagination .page-link {
  cursor: pointer;
}
</style>
