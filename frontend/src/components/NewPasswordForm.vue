<template>
  <div>
    <form @submit.prevent="handleSetPassword" novalidate>
      <!-- New Password -->
      <div class="floating-group mb-4">
        <input
          type="password"
          id="password"
          v-model="password"
          class="form-control floating-input"
          placeholder=" "
          required
        />
        <label for="password" class="floating-label">New Password</label>
      </div>

      <!-- Confirm Password -->
      <div class="floating-group mb-4">
        <input
          type="password"
          id="confirmPassword"
          v-model="confirmPassword"
          class="form-control floating-input"
          placeholder=" "
          required
        />
        <label for="confirmPassword" class="floating-label">Confirm Password</label>
      </div>

      <!-- Message -->
      <div v-if="message" class="alert py-2 small mb-3" :class="alertClass">
        {{ message }}
      </div>

      <!-- Submit -->
      <button type="submit" class="btn btn-success w-100 py-2" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
        {{ loading ? 'Updating...' : 'Update Password' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()

const password = ref('')
const confirmPassword = ref('')
const message = ref('')
const alertClass = ref('')
const loading = ref(false)

const token = route.query.token

const handleSetPassword = async () => {
  if (password.value !== confirmPassword.value) {
    message.value = 'Passwords do not match.'
    alertClass.value = 'alert-danger'
    return
  }

  loading.value = true
  message.value = ''

  try {
    const res = await api.post('/auth/update-password', {
      token,
      new_password: password.value
    })

    message.value = res.data.message || 'Password updated successfully.'
    alertClass.value = 'alert-success'

    setTimeout(() => router.push('/login'), 2000)
  } catch (err) {
    message.value = err.response?.data?.error || 'Failed to update password.'
    alertClass.value = 'alert-danger'
  } finally {
    loading.value = false
  }
}
</script>
