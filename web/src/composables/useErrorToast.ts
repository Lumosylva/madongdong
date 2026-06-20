import { ref } from 'vue'

const message = ref('')
const visible = ref(false)
let hideTimer: ReturnType<typeof setTimeout> | null = null

export function useErrorToast() {
  const showError = (msg: string, duration = 3000) => {
    if (hideTimer) {
      clearTimeout(hideTimer)
      hideTimer = null
    }
    message.value = msg
    visible.value = true
    hideTimer = setTimeout(() => {
      visible.value = false
      hideTimer = null
    }, duration)
  }

  const hideError = () => {
    if (hideTimer) {
      clearTimeout(hideTimer)
      hideTimer = null
    }
    visible.value = false
  }

  return { message, visible, showError, hideError }
}
