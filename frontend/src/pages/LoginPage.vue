<template>
  <div class="wrapper d-flex justify-content-center align-items-center min-vh-100">
    <div class="card bg-white p-5 shadow-sm">
      <h2 class="text-center mb-4 fw-semibold text-primary">Welcome Back</h2>

      <form @submit.prevent="handleLogin" novalidate>
        <!-- Email -->
        <div class="floating-group mb-3">
          <input
            type="email"
            id="email"
            v-model="email"
            class="form-control floating-input"
            placeholder=" "
            required
          />
          <label for="email" class="floating-label">Email address</label>
        </div>

        <!-- Password -->
        <div class="floating-group mb-3">
          <input
            type="password"
            id="password"
            v-model="password"
            class="form-control floating-input"
            placeholder=" "
            required
          />
          <label for="password" class="floating-label">Password</label>
        </div>

        <!-- Forgot Password -->
        <div class="text-end mb-3">
          <a href="#" class="small text-decoration-none text-primary" @click.prevent="handleForgotPassword">
            Forgot password?
          </a>
        </div>

        <!-- Error message -->
        <div v-if="errorMessage" class="alert alert-danger py-2 small mb-3">
          {{ errorMessage }}
        </div>

        <!-- Submit -->
        <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? "Logging in..." : "Login" }}
        </button>

        <!-- Register -->
        <p class="text-center mt-4 mb-0 small text-muted">
          Don't have an account?
          <a href="#" class="text-primary fw-semibold" @click.prevent="handleRegister">
            Register here
          </a>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from '../api'

const router = useRouter();

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("");

const handleLogin = async () => {
  errorMessage.value = "";
  loading.value = true;

  try {
    const response = await api.post("/auth/login", {
      email: email.value,
      password: password.value,
    });
    localStorage.setItem("token", response.data.access_token)
    localStorage.setItem("user", JSON.stringify(response.data.user))
    router.push("/dashboard");
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message || "Invalid email or password.";
  } finally {
    loading.value = false;
  }
};

const handleForgotPassword = () => {
  router.push("/reset-password");
};

const handleRegister = () => {
  router.push("/register");
};
</script>
