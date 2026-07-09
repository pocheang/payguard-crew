<template>
  <transition name="toast">
    <div
      v-if="visible"
      :class="toastClasses"
      class="fixed z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-strong pointer-events-auto animate-slide-down"
      :style="positionStyle"
    >
      <!-- Icon -->
      <div class="flex-shrink-0">
        <span class="text-xl">{{ iconMap[type] }}</span>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <p v-if="title" class="font-semibold text-sm">{{ title }}</p>
        <p class="text-sm" :class="title ? 'mt-1' : ''">{{ message }}</p>
      </div>

      <!-- Close button -->
      <button
        v-if="closable"
        @click="close"
        class="flex-shrink-0 text-current opacity-70 hover:opacity-100 transition-opacity"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  title: String,
  message: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: 3000
  },
  position: {
    type: String,
    default: 'top-right',
    validator: (value) => ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center'].includes(value)
  },
  closable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)
let timer = null

const iconMap = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️'
}

const toastClasses = computed(() => {
  const typeClasses = {
    success: 'bg-success-50 text-success-900 border border-success-200',
    error: 'bg-danger-50 text-danger-900 border border-danger-200',
    warning: 'bg-warning-50 text-warning-900 border border-warning-200',
    info: 'bg-blue-50 text-blue-900 border border-blue-200'
  }

  return typeClasses[props.type]
})

const positionStyle = computed(() => {
  const positions = {
    'top-left': { top: '1rem', left: '1rem' },
    'top-right': { top: '1rem', right: '1rem' },
    'bottom-left': { bottom: '1rem', left: '1rem' },
    'bottom-right': { bottom: '1rem', right: '1rem' },
    'top-center': { top: '1rem', left: '50%', transform: 'translateX(-50%)' }
  }

  return positions[props.position]
})

const close = () => {
  visible.value = false
  emit('close')
}

const startTimer = () => {
  if (props.duration > 0) {
    timer = setTimeout(() => {
      close()
    }, props.duration)
  }
}

onMounted(() => {
  visible.value = true
  startTimer()
})

watch(() => props.duration, () => {
  if (timer) {
    clearTimeout(timer)
  }
  startTimer()
})
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
