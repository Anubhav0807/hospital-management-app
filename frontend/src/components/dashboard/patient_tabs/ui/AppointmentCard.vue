<template>
  <div class="card shadow-sm border-0 h-100 rounded-4">
    <div class="card-body">
      <div v-if="title" class="d-flex align-items-center gap-2 mb-2">
        <i class="bi bi-clock-history text-danger fs-5"></i>
        <span class="fw-semibold">{{ title }}</span>
      </div>

      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <h6 class="fw-semibold mb-1">{{ appt.doctor.name }}</h6>
          <small class="text-muted">{{ appt.doctor.department.name }}</small>
        </div>
        <span class="badge bg-info text-dark">{{ titleCase(appt.status) }}</span>
      </div>

      <p class="text-muted mb-1">
        <i class="bi bi-clock me-1"></i>
        {{ formatDateTime(appt.date) }}
      </p>
      <p class="text-muted mb-2">
        <i class="bi bi-building me-1"></i>
        {{ appt.doctor.department.description }}
      </p>

      <div class="d-flex gap-2 mt-2">
        <button class="btn btn-outline-primary btn-sm" @click="handleReschedule"
          :disabled="appt.status !== ApptStatus.BOOKED">
          <i class="bi bi-arrow-repeat me-1"></i> Reschedule
        </button>
        <button class="btn btn-outline-danger btn-sm" @click="emit('cancel', appt)"
          :disabled="appt.status !== ApptStatus.BOOKED">
          <i class="bi bi-x-circle me-1"></i> Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ApptStatus, formatDateTime, titleCase } from '../../../../utils'

const router = useRouter()
const props = defineProps({ appt: Object, title: String })
const emit = defineEmits(['cancel'])

function handleReschedule() {
  router.push({
    path: '/dashboard',
    query: {
      tab: 'new-booking',
      doctor_id: props.appt.doctor.id,
      doctor_name: props.appt.doctor.name,
      department: props.appt.doctor.department.name,
      appt_id: props.appt.id,
      reschedule: true
    },
  })
}
</script>
