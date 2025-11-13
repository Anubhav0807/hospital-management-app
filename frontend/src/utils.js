export const Status = {
  BOOKED: "booked",
  COMPLETED: "completed",
  CANCELLED: "cancelled"
}

export const VisitType = {
  ONLINE: "online",
  OFFLINE: "offline"
}

export function formatDate(dt) {
  return new Date(dt).toLocaleString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short'
  })
}

export function formatDateTime(dt) {
  return new Date(dt).toLocaleString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
  .replace('am', 'AM')
  .replace('pm', 'PM')
}

export function titleCase(word) {
  if (!word) return ''
  return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
}
