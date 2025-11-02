<template>
  <div class="wrapper d-flex justify-content-center align-items-center min-vh-100">
    <div class="card bg-white p-5 shadow-sm">
      <h2 class="text-center mb-4 fw-semibold text-primary">Reset Password</h2>
      <component :is="currentComponent" />
      <!-- Back to login -->
      <p class="text-center mt-4 mb-0 small text-muted">
        Remembered your password?
        <router-link to="/login" class="text-primary fw-semibold">
          Go back to Login
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import RequestResetForm from '../components/RequestResetForm.vue'
import NewPasswordForm from '../components/NewPasswordForm.vue';

const route = useRoute()
const token = route.query.token || null

const currentComponent = computed(() =>
  token ? NewPasswordForm : RequestResetForm
)
</script>
