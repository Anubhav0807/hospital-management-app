import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  function show(message, type = 'success') {
    const id = Date.now() + Math.random()

    toasts.value.push({
      id,
      message,
      type
    })

    // Auto-remove after 4 seconds
    setTimeout(() => remove(id), 4000)

    return id
  }

  function success(msg) {
    show(msg, 'success')
  }

  function error(msg) {
    show(msg, 'danger')
  }

  function warning(msg) {
    show(msg, 'warning')
  }

  function info(msg) {
    show(msg, 'info')
  }

  function remove(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return {
    toasts,
    show,
    success,
    error,
    warning,
    info,
    remove
  }
}
