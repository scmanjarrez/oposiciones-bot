import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const ALL_STATUSES = ['VIGENTE', 'DESFASADA', 'DEROGADA', 'ERRÓNEA']
const STORAGE_KEY = 'opos-settings'

export const useSettingsStore = defineStore('settings', () => {
  const saved = (() => {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') } catch { return null }
  })()

  const allowedStatuses = ref(saved?.allowedStatuses ?? ['VIGENTE'])
  const blindMode = ref(saved?.blindMode ?? true)

  watch([allowedStatuses, blindMode], () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      allowedStatuses: allowedStatuses.value,
      blindMode: blindMode.value,
    }))
  }, { deep: true })

  function toggleStatus(status) {
    const idx = allowedStatuses.value.indexOf(status)
    if (idx === -1) {
      allowedStatuses.value = [...allowedStatuses.value, status]
    } else if (allowedStatuses.value.length > 1) {
      // always keep at least one active
      allowedStatuses.value = allowedStatuses.value.filter(s => s !== status)
    }
  }

  function toggleBlind() {
    blindMode.value = !blindMode.value
  }

  function isAllowed(status) {
    return allowedStatuses.value.includes(status)
  }

  return { allowedStatuses, toggleStatus, isAllowed, blindMode, toggleBlind }
})
