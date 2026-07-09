<template>
  <div v-if="show" :class="['loading-overlay', { 'loading-fullscreen': fullscreen }]">
    <div class="loading-spinner">
      <div class="spinner-ring"></div>
      <p v-if="text" class="loading-text">{{ text }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: ''
  },
  fullscreen: {
    type: Boolean,
    default: false
  },
  delay: {
    type: Number,
    default: 0
  }
})

const visible = ref(false)

watch(() => props.show, (newVal) => {
  if (newVal && props.delay > 0) {
    setTimeout(() => {
      visible.value = newVal
    }, props.delay)
  } else {
    visible.value = newVal
  }
})

onMounted(() => {
  visible.value = props.show
})
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 1000;
}

.loading-fullscreen {
  position: fixed;
  backdrop-filter: blur(4px);
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner-ring {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(139, 92, 246, 0.2);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}
</style>
