import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuditStore = defineStore('audit', () => {
  const recentAudits = ref([])
  const statistics = ref(null)
  const loading = ref(false)

  function addAudit(audit) {
    recentAudits.value.unshift(audit)
    if (recentAudits.value.length > 50) {
      recentAudits.value = recentAudits.value.slice(0, 50)
    }
  }

  function setStatistics(stats) {
    statistics.value = stats
  }

  function clearRecentAudits() {
    recentAudits.value = []
  }

  return {
    recentAudits,
    statistics,
    loading,
    addAudit,
    setStatistics,
    clearRecentAudits
  }
})
