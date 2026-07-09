<template>
  <div v-if="totalPages > 1" class="pagination">
    <button
      @click="goToPage(currentPage - 1)"
      :disabled="currentPage === 1"
      class="pagination-btn"
    >
      ‹ 上一页
    </button>

    <div class="pagination-numbers">
      <button
        v-for="page in visiblePages"
        :key="page"
        @click="goToPage(page)"
        :class="['pagination-number', { active: page === currentPage }]"
      >
        {{ page }}
      </button>
    </div>

    <button
      @click="goToPage(currentPage + 1)"
      :disabled="currentPage === totalPages"
      class="pagination-btn"
    >
      下一页 ›
    </button>

    <div class="pagination-info">
      共 {{ total }} 条，第 {{ currentPage }}/{{ totalPages }} 页
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  total: {
    type: Number,
    required: true
  },
  maxVisible: {
    type: Number,
    default: 7
  }
})

const emit = defineEmits(['page-change'])

const totalPages = computed(() => {
  return Math.ceil(props.total / props.pageSize)
})

const visiblePages = computed(() => {
  const pages = []
  const half = Math.floor(props.maxVisible / 2)

  let start = Math.max(1, props.currentPage - half)
  let end = Math.min(totalPages.value, start + props.maxVisible - 1)

  if (end - start + 1 < props.maxVisible) {
    start = Math.max(1, end - props.maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
    emit('page-change', page)
  }
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0;
  flex-wrap: wrap;
}

.pagination-btn,
.pagination-number {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled),
.pagination-number:hover:not(.active) {
  background: #f9fafb;
  border-color: #8b5cf6;
  color: #8b5cf6;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-numbers {
  display: flex;
  gap: 0.25rem;
}

.pagination-number.active {
  background: #8b5cf6;
  border-color: #8b5cf6;
  color: white;
}

.pagination-info {
  margin-left: auto;
  font-size: 0.875rem;
  color: #6b7280;
}

@media (max-width: 640px) {
  .pagination {
    justify-content: center;
  }

  .pagination-info {
    margin-left: 0;
    width: 100%;
    text-align: center;
  }
}
</style>
