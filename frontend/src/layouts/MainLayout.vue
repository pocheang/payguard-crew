<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Top Navigation -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-6 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-2xl">🛡️</span>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-800">PayGuard</h1>
              <p class="text-xs text-gray-500">风控审计系统</p>
            </div>
          </div>

          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <!-- Health Status -->
            <div class="flex items-center space-x-2">
              <span :class="[
                'w-2 h-2 rounded-full',
                apiStatus === 'online' ? 'bg-green-500' : 'bg-red-500'
              ]"></span>
              <span class="text-sm text-gray-600">{{ apiStatus === 'online' ? '在线' : '离线' }}</span>
            </div>

            <!-- User Info -->
            <div class="flex items-center space-x-3">
              <div class="text-right">
                <p class="text-sm font-medium text-gray-800">{{ user?.username || 'User' }}</p>
                <p class="text-xs text-gray-500">{{ user?.roles?.join(', ') || 'Viewer' }}</p>
              </div>
              <button
                @click="handleLogout"
                class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="flex">
      <!-- Sidebar -->
      <aside class="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-73px)] sticky top-[73px]">
        <nav class="p-4 space-y-1">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
            active-class="bg-primary-50 text-primary-700 hover:bg-primary-100"
          >
            <span class="text-xl">{{ item.icon }}</span>
            <span class="font-medium">{{ item.label }}</span>
          </router-link>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { healthAPI } from '../services/api'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const apiStatus = ref('online')

const menuItems = [
  { path: '/dashboard', icon: '📊', label: '仪表盘' },
  { path: '/audit/single', icon: '🔍', label: '单笔审计' },
  { path: '/audit/batch', icon: '📦', label: '批量审计' },
  { path: '/review/pending', icon: '✋', label: '待审核' },
  { path: '/reports', icon: '📄', label: '报告查询' }
]

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

async function checkAPIHealth() {
  try {
    await healthAPI.check()
    apiStatus.value = 'online'
  } catch (error) {
    apiStatus.value = 'offline'
  }
}

onMounted(() => {
  checkAPIHealth()
  setInterval(checkAPIHealth, 30000)
})
</script>
