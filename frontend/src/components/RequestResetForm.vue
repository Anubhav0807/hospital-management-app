<template>
  <div>
    <p class="text-muted small text-center mb-4">
      Enter your registered email address and we'll send you a link to reset your password.
    </p>

    <form @submit.prevent="handleResetPassword" novalidate>
      <!-- Email -->
      <div class="floating-group mb-4">
        <input type="email" id="email" v-model="email" class="form-control floating-input" placeholder=" " required />
        <label for="email" class="floating-label">Email address</label>
      </div>

      <!-- Message -->
      <div v-if="message" class="alert py-2 small mb-3" :class="messageClass">
        {{ message }}
      </div>

      <!-- Submit -->
      <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
        {{ loading ? "Sending..." : "Send Reset Link" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from '../api'

const email = ref("");
const loading = ref(false);
const message = ref("");
const messageClass = ref("");

const handleResetPassword = async () => {
  message.value = "";
  messageClass.value = "";
  loading.value = true;

  try {
    const response = await api.post("/auth/reset-password", {
      email: email.value,
    });

    message.value = response.data?.message || "Reset link sent to your email.";
    messageClass.value = "alert-success";
  } catch (error) {
    console.error("Error:", error);
    message.value = error.response?.data?.message || "Failed to send reset link.";
    messageClass.value = "alert-danger";
  } finally {
    loading.value = false;
  }
};
</script>
