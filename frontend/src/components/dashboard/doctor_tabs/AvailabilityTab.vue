<template>
  <div class="availability-tab container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-semibold text-primary mb-0 d-flex align-items-center">
        <i class="bi bi-clock-history me-2"></i> Weekly Availability
      </h3>
      <button class="btn btn-outline-primary btn-sm" @click="fetchAvailability">
        <i class="bi bi-arrow-clockwise me-1"></i> Refresh
      </button>
    </div>

    <!-- Week Timeline -->
    <div class="week-timeline mb-4 shadow-sm p-3 bg-white rounded-3">
      <div v-for="(day, index) in availability" :key="index" class="timeline-day" :class="{ available: day.available }">
        <span class="day-label">{{ day.weekday.slice(0, 3) }}</span>
        <span class="status-dot"></span>
      </div>
    </div>

    <!-- Info -->
    <div class="alert alert-info small py-2 px-3 mb-4">
      <i class="bi bi-info-circle me-2"></i>
      Toggle availability for each day and adjust start/end times as needed.
    </div>

    <!-- Grid -->
    <div class="availability-grid">
      <div v-for="(day, index) in availability" :key="index" class="availability-card shadow-sm"
        :class="{ available: day.available }">
        <div class="availability-header d-flex justify-content-between align-items-center">
          <h5 class="fw-semibold mb-0">{{ day.weekday }}</h5>
          <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" role="switch" v-model="day.available" />
          </div>
        </div>

        <p class="text-muted small mb-3">{{ formatDate(day.date) }}</p>

        <div v-if="day.available" class="time-row">
          <div class="time-box">
            <label class="small text-secondary fw-semibold mb-1">Start</label>
            <input type="time" class="form-control form-control-sm text-center" v-model="day.start_time" />
          </div>
          <div class="time-box">
            <label class="small text-secondary fw-semibold mb-1">End</label>
            <input type="time" class="form-control form-control-sm text-center" v-model="day.end_time" />
          </div>
        </div>

        <div v-else class="text-muted text-center small py-3">
          <i class="bi bi-moon me-1"></i> Not Available
        </div>
      </div>
    </div>

    <!-- Save Bar -->
    <div class="save-bar shadow-sm mt-4 p-3 d-flex justify-content-end bg-white rounded">
      <button class="btn btn-primary" @click="saveAvailability">
        <i class="bi bi-save me-2"></i> Save Changes
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { formatDate } from '../../../utils'
import api from '../../../api'

const availability = ref([])

async function fetchAvailability() {
  try {
    const res = await api.get('/doctor/availability')
    availability.value = res.data.availability.map(d => ({
      ...d,
      weekday: new Date(d.date).toLocaleDateString('en-IN', { weekday: 'long' })
    }))
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
    availability.value = generateNext7Days()
  }
}

async function saveAvailability() {
  try {
    await api.put('/doctor/availability', { availability: availability.value })
    alert('Availability updated successfully!')
  } catch (err) {
    console.error('API Error:', err.response.data?.error || err.message)
    alert('Failed to update availability. Please try again.')
  }
}

onMounted(fetchAvailability)
</script>

<style scoped>
.availability-tab {
  min-height: calc(100vh - 100px);
}

/* Week Timeline */
.week-timeline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  background: #f8f9fa;
}

.timeline-day {
  flex: 1;
  text-align: center;
  padding: 0.5rem 0.25rem;
  border-radius: 0.5rem;
  transition: all 0.25s ease;
  position: relative;
  background: #fff;
  border: 1px solid #e3e6ea;
}

.timeline-day.available {
  background: #e7f1ff;
  border-color: #0d6efd;
}

.timeline-day .day-label {
  display: block;
  font-weight: 600;
  font-size: 0.9rem;
  color: #333;
}

.timeline-day .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-top: 4px;
  background-color: #aaa;
}

.timeline-day.available .status-dot {
  background-color: #0d6efd;
}

/* Grid layout (slightly narrower) */
.availability-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1rem;
}

/* Day card */
.availability-card {
  background: #fff;
  border-radius: 1rem;
  border: 1px solid #e3e6ea;
  padding: 1rem;
  transition: all 0.2s ease-in-out;
}

.availability-card.available {
  border-color: #0d6efd;
  box-shadow: 0 0 10px rgba(13, 110, 253, 0.15);
}

/* Header */
.availability-header h5 {
  font-size: 1rem;
}

/* Time section */
.time-row {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.time-box {
  flex: 1;
  min-width: 100px;
}

input[type='time'] {
  width: 100%;
  font-size: 0.85rem;
}

/* Save Bar */
.save-bar {
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.alert {
  border-radius: 0.75rem;
}

/* Responsive tweaks */
@media (max-width: 400px) {
  .time-box {
    flex: 1 1 100%;
  }
}
</style>
