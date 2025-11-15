<template>
  <div class="analytics-tab container py-4">

    <h4 class="fw-semibold text-primary mb-4">Analytics</h4>

    <!-- Loader -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else>

      <!-- For Admin -->
      <template v-if="role === Role.ADMIN">
        <div class="row g-4">

          <div class="col-lg-6">
            <ChartCard title="Appointments Trend">
              <div class="chart-container"><canvas ref="appointmentsTrend"></canvas></div>
            </ChartCard>
          </div>

          <div class="col-lg-6">
            <ChartCard title="Specialization Demand">
              <div class="chart-container"><canvas ref="specializationDemand"></canvas></div>
            </ChartCard>
          </div>

          <div class="col-lg-6">
            <ChartCard title="Visit Type Distribution">
              <div class="chart-container"><canvas ref="visitTypeDist"></canvas></div>
            </ChartCard>
          </div>

          <div class="col-lg-6">
            <ChartCard title="Patient Retention Trend (Last 6 Months)">
              <div class="chart-container"><canvas ref="retentionTrend"></canvas></div>
            </ChartCard>
          </div>

        </div>
      </template>

      <!-- For Doctor -->
      <template v-else-if="role === Role.DOCTOR">
        <div class="row g-4">

          <div class="col-lg-6">
            <ChartCard title="Your Appointments This Month">
              <div class="chart-container"><canvas ref="doctorMonthly"></canvas></div>
            </ChartCard>
          </div>

          <div class="col-lg-6">
            <ChartCard title="Follow-Up Rate">
              <div class="chart-container"><canvas ref="followupRate"></canvas></div>
            </ChartCard>
          </div>

        </div>
      </template>


      <!-- For Patient -->
      <template v-else-if="role === Role.PATIENT">
        <div class="row g-4">

          <div class="col-lg-6">
            <ChartCard title="Visit Frequency Trend (Last 6 Months)">
              <div class="chart-container"><canvas ref="patientFrequency"></canvas></div>
            </ChartCard>
          </div>

          <div class="col-lg-6">
            <ChartCard title="Most Visited Departments">
              <div class="chart-container"><canvas ref="patientDepartments"></canvas></div>
            </ChartCard>
          </div>

        </div>
      </template>

      <div v-else class="text-muted">No analytics available for this role.</div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue"
import { Chart } from "chart.js/auto"
import ChartCard from '../ChartCard.vue'
import { Role } from "../../utils"
import api from '../../api'

// Admin Refs
const appointmentsTrend = ref(null)
const specializationDemand = ref(null)
const visitTypeDist = ref(null)
const retentionTrend = ref(null)

// Doctor Refs
const doctorMonthly = ref(null)
const followupRate = ref(null)

// Patient Refs
const patientFrequency = ref(null)
const patientDepartments = ref(null)

const loading = ref(true)
const storedUser = JSON.parse(localStorage.getItem("user"))
const role = storedUser?.role || ""

const charts = []
function destroyCharts() {
  charts.forEach(c => c.destroy())
  charts.length = 0
}

function renderLineChart(canvas, chartData) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [{
        label: chartData.label,
        data: chartData.values,
        borderWidth: 2,
        tension: 0.3
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  })
}

function renderBarChart(canvas, chartData) {
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: chartData.labels,
      datasets: [{ label: chartData.label, data: chartData.values }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  })
}

function renderPieChart(canvas, chartData) {
  return new Chart(canvas, {
    type: "pie",
    data: { labels: chartData.labels, datasets: [{ data: chartData.values }] },
    options: { responsive: true, maintainAspectRatio: false }
  })
}

function renderDoughnutChart(canvas, chartData) {
  return new Chart(canvas, {
    type: "doughnut",
    data: { labels: chartData.labels, datasets: [{ data: chartData.values }] },
    options: { responsive: true, maintainAspectRatio: false }
  })
}

onMounted(async () => {
  try {
    const res = await api.get("/analytics/charts")
    const data = res.data

    loading.value = false
    await nextTick()
    destroyCharts()

    if (role === Role.ADMIN) {
      charts.push(renderLineChart(appointmentsTrend.value, data.appointments_trend))
      charts.push(renderBarChart(specializationDemand.value, data.specialization_demand))
      charts.push(renderPieChart(visitTypeDist.value, data.visit_types))
      charts.push(renderLineChart(retentionTrend.value, data.retention_trend))
    }

    if (role === Role.DOCTOR) {
      charts.push(renderLineChart(doctorMonthly.value, data.doctor_monthly))
      charts.push(renderDoughnutChart(followupRate.value, data.followup_rate))
    }

    if (role === Role.PATIENT) {
      charts.push(renderLineChart(patientFrequency.value, data.patient_frequency))
      charts.push(renderBarChart(patientDepartments.value, data.patient_departments))
    }

  } catch (err) {
    console.error("Analytics load error:", err)
  }
})
</script>

<style>
.chart-container {
  height: 300px;
}
</style>
