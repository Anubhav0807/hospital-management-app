<template>
  <div class="modal fade" tabindex="-1" aria-hidden="true" ref="cancelModalRef">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 rounded-4 shadow">

        <!-- Header -->
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title fw-semibold">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Cancel Appointment
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="hide"></button>
        </div>

        <!-- Body -->
        <div class="modal-body text-center py-4" v-if="localAppt">
          <p class="mb-3">
            Are you sure you want to cancel your appointment with
            <strong>{{ localAppt.doctor.name }}</strong>?
          </p>
          <small class="text-muted d-block">This action cannot be undone.</small>
        </div>

        <!-- Footer -->
        <div class="modal-footer justify-content-center border-0 pb-4">
          <button class="btn btn-secondary px-4" @click="hide">No, Keep it</button>
          <button class="btn btn-danger px-4" @click="confirmCancel">Yes, Cancel</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import { useToast } from '../../../../composables/useToast'
import api from '../../../../api'

const emit = defineEmits(['cancelled'])
const toast = useToast()

const localAppt = ref(null)

const cancelModalRef = ref(null)
let cancelModal = null

onMounted(() => {
  cancelModal = new Modal(cancelModalRef.value)
})

function show(appt) {
  localAppt.value = appt
  cancelModal.show()
}

function hide() {
  cancelModal.hide()
}

async function confirmCancel() {
  if (!localAppt.value) return
  
  try {
    await api.patch(`/patient/appointment/${localAppt.value.id}`)
    hide()
    emit('cancelled')
  } catch (err) {
    toast.error('Unable to cancel the appointment.')
  }
}

defineExpose({ show, hide })
</script>

<style scoped>
.modal-content {
  border-radius: 1rem;
}
</style>
