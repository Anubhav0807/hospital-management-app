<template>
  <div class="modal fade" tabindex="-1" aria-hidden="true" ref="paymentModalRef">
    <div class="modal-dialog modal-dialog-centered payment-modal">
      <div class="modal-content rounded-4 border-0 shadow">

        <div class="modal-header border-0">
          <h5 class="modal-title fw-bold">Payment</h5>
          <button type="button" class="btn-close" @click="hide"></button>
        </div>

        <div class="modal-body px-4 pb-4">

          <div class="row g-4 align-items-stretch">

            <!-- Treatment Summary -->
            <div class="col-12 col-md-6 d-flex">
              <div class="info-box p-3 rounded-3 border bg-light w-100 h-100" v-if="selectedTreat">
                <div class="mb-2">
                  <div class="fw-semibold text-primary mb-1">
                    {{ selectedTreat.doctor.name }}
                  </div>
                  <div class="text-muted small">
                    {{ selectedTreat.doctor.department.name }}
                  </div>
                </div>

                <div class="small mb-2">
                  <i class="bi bi-calendar-event me-1"></i>
                  {{ formatDateTime(selectedTreat.date) }}
                </div>

                <div class="small mb-2">
                  <i class="bi bi-file-medical me-1"></i>
                  {{ selectedTreat.diagnosis }}
                </div>

                <div class="amount-box mt-5 p-3 rounded-3 text-center">
                  <div class="fw-semibold">Amount</div>
                  <div class="fs-4 fw-bold text-success">₹{{ selectedTreat.fee }}</div>
                </div>
              </div>
            </div>

            <!-- QR or Pay Button -->
            <div class="col-12 col-md-6 d-flex">
              <div class="qr-section d-flex flex-column justify-content-center align-items-center w-100 h-100">

                <!-- Desktop QR -->
                <div v-if="!isMobile && !showSuccess" class="p-3 border rounded-3 shadow-sm text-center">
                  <div ref="qrContainer" class="qr-box mb-2"></div>
                  <small v-if="polling" class="text-muted">Scan the QR Code</small>
                </div>

                <!-- Mobile Button -->
                <div v-else-if="isMobile && !showSuccess" class="w-100 text-center">
                  <button class="btn btn-primary w-100 py-2" @click="completeMobilePayment">
                    Pay with UPI
                  </button>
                </div>

                <!-- Success -->
                <div v-if="showSuccess" class="text-center py-4 success-wrapper">
                  <div class="success-circle">
                    <i class="bi bi-check2"></i>
                  </div>
                  <p class="fw-semibold mt-3 fs-5">Payment Successful!</p>
                </div>

              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Modal } from 'bootstrap'
import QRCode from 'qrcode'
import api from '../../../../api'
import { PaymentStatus, formatDateTime } from '../../../../utils'
import { useToast } from '../../../../composables/useToast'

const emit = defineEmits(['paid'])

const toast = useToast()

// Bootstrap modal instance
const paymentModalRef = ref(null)
let modal = null

const selectedTreat = ref(null)
const showSuccess = ref(false)

const qrContainer = ref(null)
const isMobile = ref(window.innerWidth < 768)

const polling = ref(false)
let pollInterval = null

function show(treat) {
  selectedTreat.value = treat
  showSuccess.value = false

  modal.show()

  if (!isMobile.value) {
    generateQRCode()
    startPolling()
  }
}

function hide() {
  stopPolling()
  modal.hide()
}

function generateQRCode() {
  if (!qrContainer.value || !selectedTreat.value) return

  const baseUrl = api.defaults.baseURL
  const token = selectedTreat.value.payment_token

  const url = `${baseUrl}/patient/payment/confirm/${token}`
  console.log('Payment URL: ', url)

  qrContainer.value.innerHTML = ''
  QRCode.toCanvas(url, { width: 220 }, (err, canvas) => {
    if (!err) qrContainer.value.appendChild(canvas)
  })
}

// On Desktop: Polling
function startPolling() {
  polling.value = true
  pollInterval = setInterval(checkStatus, 3000)
}

function stopPolling() {
  polling.value = false
  if (pollInterval) clearInterval(pollInterval)
}

async function checkStatus() {
  if (!selectedTreat.value) return

  try {
    const res = await api.get(`/patient/payment/status/${selectedTreat.value.treat_id}`)
    if (res.data.status === PaymentStatus.PAID) {
      stopPolling()
      triggerSuccess()
    }
  } catch (err) {
    console.error(err)
  }
}

// On Mobile: Instant Dummy Payment
async function completeMobilePayment() {
  try {
    await api.get(`/patient/payment/confirm/${selectedTreat.value.payment_token}`)
    triggerSuccess()
  } catch (err) {
    toast.error('Payment failed.')
  }
}

function triggerSuccess() {
  showSuccess.value = true
  emit('paid', selectedTreat.value)
  setTimeout(() => {
    hide()
  }, 1500)
}

function handleResize() {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  modal = new Modal(paymentModalRef.value)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

defineExpose({ show, hide })
</script>

<style scoped>
.payment-modal {
  max-width: 680px;
  width: 100%;
  margin: 1.5rem auto;
}

.info-box,
.qr-section {
  min-height: 292px;
}

.qr-box canvas {
  width: 180px !important;
  height: auto !important;
  max-width: 100%;
}

.amount-box {
  background: #f2fff4;
  border: 1px solid #d3f5da;
}

.success-wrapper {
  animation: fadeIn 0.5s ease-out;
}

.success-circle {
  width: 100px;
  height: 100px;
  background: #e7f9ed;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto;
  animation: pop 0.4s ease-out;
}

.success-circle i {
  font-size: 3rem;
  color: #28a745;
  animation: fadeInTick 0.4s ease-out 0.2s forwards;
  opacity: 0;
}

@keyframes pop {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes fadeInTick {
  0% { opacity: 0; transform: scale(0.7); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .payment-modal {
    max-width: 90% !important;
    margin: 1rem auto;
  }

  .info-box,
  .qr-section {
    min-height: unset;
  }

  .qr-box canvas {
    width: 150px !important;
  }
}
</style>
