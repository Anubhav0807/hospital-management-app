<template>
  <div class="card shadow-sm border-0 h-100 rounded-4">
    <div class="card-body">
      <!-- Title -->
      <div v-if="title" class="d-flex align-items-center gap-2 mb-2">
        <i class="bi bi-clipboard-pulse text-success fs-5"></i>
        <span class="fw-semibold">{{ title }}</span>
      </div>

      <!-- Doctor -->
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <h6 class="fw-semibold mb-1">{{ treat.doctor.name }}</h6>
          <small class="text-muted">{{ treat.doctor.department.name }}</small>
        </div>
        <span class="badge bg-secondary">{{ titleCase(treat.status) }}</span>
      </div>

      <!-- Date -->
      <p class="text-muted mb-1">
        <i class="bi bi-calendar-event me-1"></i>
        {{ formatDateTime(treat.date) }}
      </p>

      <!-- Diagnosis -->
      <p class="text-muted mb-1">
        <i class="bi bi-file-medical me-1"></i>
        Diagnosis: {{ treat.diagnosis || 'N/A' }}
      </p>

      <!-- Prescription -->
      <p class="text-muted mb-2">
        <i class="bi bi-capsule me-1"></i>
        Prescription: {{ treat.prescription || 'N/A' }}
      </p>

      <!-- Payment Section (only when appointment/treatment is completed) -->
      <div v-if="treat.status === ApptStatus.COMPLETED" class="mt-3 pt-2 border-top">

        <!-- PAID -->
        <div v-if="treat.payment_status === PaymentStatus.PAID" class="d-flex align-items-center gap-2">
          <span class="badge bg-success">Payment Completed</span>
          <span class="fw-semibold">₹{{ treat.fee }}</span>
        </div>

        <!-- Payment Pending -->
        <div v-else-if="treat.payment_status === PaymentStatus.PENDING" class="d-flex align-items-center justify-content-between">
          <span class="badge bg-warning text-dark">Payment Pending</span>
          <button class="btn btn-primary btn-sm" @click="$emit('pay', treat)">
            Pay Now
          </button>
        </div>

        <!-- Payment Failed -->
        <div v-else-if="treat.payment_status === PaymentStatus.FAILED" class="d-flex align-items-center justify-content-between">
          <span class="badge bg-danger">Payment Failed</span>
          <button class="btn btn-primary btn-sm" @click="$emit('pay', treat)">
            Retry
          </button>
        </div>

        <!-- Payment Refunded -->
        <div v-else-if="treat.payment_status === PaymentStatus.REFUNDED">
          <span class="badge bg-info text-dark">Payment Refunded</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ApptStatus, PaymentStatus, formatDateTime, titleCase } from '../../../../utils';

defineProps({
  treat: Object,
  title: String
})
</script>
