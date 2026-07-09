import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useReviewStore = defineStore('review', () => {
  const pendingReviews = ref([])
  const statistics = ref(null)
  const loading = ref(false)

  function setPendingReviews(reviews) {
    pendingReviews.value = reviews
  }

  function setStatistics(stats) {
    statistics.value = stats
  }

  function updateReviewStatus(transactionId, newStatus) {
    const review = pendingReviews.value.find(r => r.transaction_id === transactionId)
    if (review) {
      review.status = newStatus
    }
  }

  return {
    pendingReviews,
    statistics,
    loading,
    setPendingReviews,
    setStatistics,
    updateReviewStatus
  }
})
