<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">⚠️</div>
      <h2 class="error-title">{{ title }}</h2>
      <p class="error-message">{{ message }}</p>
      <div v-if="showDetails && error" class="error-details">
        <details>
          <summary>技术详情</summary>
          <pre>{{ errorDetails }}</pre>
        </details>
      </div>
      <div class="error-actions">
        <button @click="retry" class="btn-primary">
          重试
        </button>
        <button @click="goHome" class="btn-secondary">
          返回首页
        </button>
      </div>
    </div>
  </div>
  <slot v-else></slot>
</template>

<script setup>
import { ref, onErrorCaptured, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: '出错了'
  },
  message: {
    type: String,
    default: '抱歉，页面加载失败。请稍后重试。'
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['error', 'retry'])

const router = useRouter()
const hasError = ref(false)
const error = ref(null)

const errorDetails = computed(() => {
  if (!error.value) return ''
  return `${error.value.message}\n\nStack:\n${error.value.stack}`
})

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  error.value = err

  console.error('ErrorBoundary captured:', err)
  console.error('Component:', instance)
  console.error('Error Info:', info)

  emit('error', { error: err, instance, info })

  return false
})

const retry = () => {
  hasError.value = false
  error.value = null
  emit('retry')
  window.location.reload()
}

const goHome = () => {
  hasError.value = false
  error.value = null
  router.push('/')
}
</script>

<style scoped>
.error-boundary {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-content {
  max-width: 600px;
  width: 100%;
  background: white;
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.error-message {
  font-size: 1rem;
  color: #6b7280;
  margin: 0 0 2rem 0;
  line-height: 1.6;
}

.error-details {
  margin: 2rem 0;
  text-align: left;
}

.error-details details {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.error-details summary {
  cursor: pointer;
  font-weight: 600;
  color: #374151;
  user-select: none;
}

.error-details pre {
  margin: 1rem 0 0 0;
  padding: 1rem;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 0.375rem;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.error-actions button {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #8b5cf6;
  color: white;
}

.btn-primary:hover {
  background: #7c3aed;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}
</style>
