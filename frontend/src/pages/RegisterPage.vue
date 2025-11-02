<template>
  <div class="wrapper d-flex justify-content-center align-items-center min-vh-100">
    <div class="card bg-white p-5 shadow-sm m-5">
      <h2 class="text-center mb-4 fw-semibold text-primary">Create Patient Account</h2>

      <form @submit.prevent="handleRegister" novalidate>
        <!-- Name -->
        <div class="floating-group mb-3">
          <input
            type="text"
            id="name"
            v-model="name"
            class="form-control floating-input"
            placeholder=" "
            required
          />
          <label for="name" class="floating-label">Full Name</label>
        </div>

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

        <!-- Contact Number -->
        <div class="floating-group mb-3">
          <input
            type="tel"
            id="contact"
            v-model="contact_number"
            class="form-control floating-input"
            placeholder=" "
            required
          />
          <label for="contact" class="floating-label">Contact Number</label>
        </div>

        <!-- Age -->
        <div class="floating-group mb-3">
          <input
            type="number"
            id="age"
            v-model="age"
            class="form-control floating-input"
            placeholder=" "
            min="0"
            required
          />
          <label for="age" class="floating-label">Age</label>
        </div>

        <!-- Gender -->
        <div class="mb-3">
          <label class="form-label fw-semibold small text-secondary">Gender</label>
          <div class="d-flex gap-3">
            <div class="form-check">
              <input
                class="form-check-input"
                type="radio"
                id="male"
                value="MALE"
                v-model="gender"
                required
              />
              <label class="form-check-label" for="male">Male</label>
            </div>
            <div class="form-check">
              <input
                class="form-check-input"
                type="radio"
                id="female"
                value="FEMALE"
                v-model="gender"
              />
              <label class="form-check-label" for="female">Female</label>
            </div>
            <div class="form-check">
              <input
                class="form-check-input"
                type="radio"
                id="other"
                value="OTHER"
                v-model="gender"
              />
              <label class="form-check-label" for="other">Other</label>
            </div>
          </div>
        </div>

        <!-- Address -->
        <div class="floating-group mb-3">
          <textarea
            id="address"
            v-model="address"
            class="form-control floating-input"
            placeholder=" "
            rows="2"
            required
          ></textarea>
          <label for="address" class="floating-label">Address</label>
        </div>

        <!-- Medical History -->
        <div class="floating-group mb-3">
          <textarea
            id="medical_history"
            v-model="medical_history"
            class="form-control floating-input"
            placeholder=" "
            rows="3"
          ></textarea>
          <label for="medical_history" class="floating-label">Medical History</label>
        </div>

        <!-- Error -->
        <div v-if="errorMessage" class="alert alert-danger py-2 small mb-3">
          {{ errorMessage }}
        </div>

        <!-- Submit -->
        <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? "Registering..." : "Register" }}
        </button>

        <!-- Back to login -->
        <p class="text-center mt-4 mb-0 small text-muted">
          Already have an account?
          <a href="#" class="text-primary fw-semibold" @click.prevent="handleLogin">
            Login here
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

const name = ref("");
const email = ref("");
const password = ref("");
const contact_number = ref("");
const age = ref("");
const gender = ref("");
const address = ref("");
const medical_history = ref("");
const loading = ref(false);
const errorMessage = ref("");
const router = useRouter();

const handleRegister = async () => {
  errorMessage.value = "";
  loading.value = true;

  try {
    const payload = {
      name: name.value,
      email: email.value,
      password: password.value,
      contact_number: contact_number.value,
      age: age.value,
      gender: gender.value,
      address: address.value,
      medical_history: medical_history.value || null,
    };

    const response = await api.post("/auth/register", payload, {
      headers: { "Content-Type": "application/json" },
    });

    console.log(response.data.message);
    localStorage.setItem('token', response.data.access_token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    router.push('/dashboard')
  } catch (error) {
    console.error("Registration failed:", error);
    errorMessage.value =
      error.response?.data?.message || "Registration failed. Please try again.";
  } finally {
    loading.value = false;
  }
};

const handleLogin = () => {
  router.push("/login");
};
</script>
