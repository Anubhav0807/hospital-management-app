<template>
  <div class="card shadow-sm border-0 h-100 rounded-4">
    <div class="card-body">
      <div v-if="title" class="d-flex align-items-center gap-2 mb-2">
        <i class="bi bi-clipboard-pulse text-success fs-5"></i>
        <span class="fw-semibold">{{ title }}</span>
      </div>

      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <h6 class="fw-semibold mb-1">{{ treat.doctor.name }}</h6>
          <small class="text-muted">{{ treat.doctor.department.name }}</small>
        </div>
        <span class="badge bg-secondary">{{ titleCase(treat.status) }}</span>
      </div>

      <p class="text-muted mb-1">
        <i class="bi bi-calendar-event me-1"></i>
        {{ formatDateTime(treat.date) }}
      </p>
      <p class="text-muted mb-2">
        <i class="bi bi-file-medical me-1"></i>
        Diagnosis: {{ treat.diagnosis || 'N/A' }}
      </p>
      <p class="text-muted">
        <i class="bi bi-capsule me-1"></i>
        Prescription: {{ treat.prescription || 'N/A' }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { formatDateTime, titleCase } from '../../../../utils';

defineProps({
  treat: Object,
  title: String
})
</script>
