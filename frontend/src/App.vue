<template>
  <ErrorBoundary>
    <router-view />
  </ErrorBoundary>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import ErrorBoundary from './components/ErrorBoundary.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initializeAuth()
})
</script>
