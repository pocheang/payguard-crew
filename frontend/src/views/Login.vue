<template>
  <div class="min-h-screen flex items-center justify-center gradient-primary px-4 py-12 relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 1s"></div>
    </div>

    <div class="max-w-md w-full relative z-10 animate-fade-in">
      <!-- Logo and Title -->
      <div class="text-center mb-8 animate-slide-down">
        <div class="inline-flex items-center justify-center w-20 h-20 bg-white rounded-2xl shadow-strong mb-4 hover:scale-110 transition-transform duration-300">
          <span class="text-5xl">🛡️</span>
        </div>
        <h1 class="text-4xl font-bold text-white mb-2 tracking-tight">PayGuard</h1>
        <p class="text-primary-100 text-lg">Enterprise Payment Risk Control</p>
      </div>

      <!-- Login Card -->
      <div class="card animate-slide-up shadow-strong">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">登录</h2>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              <span class="flex items-center gap-2">
                <span>👤</span>
                <span>用户名</span>
              </span>
            </label>
            <Input
              v-model="form.username"
              type="text"
              placeholder="admin 或 demo"
              :disabled="loading"
              prefixIcon="👤"
              size="lg"
            />
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              <span class="flex items-center gap-2">
                <span>🔒</span>
                <span>密码</span>
              </span>
            </label>
            <Input
              v-model="form.password"
              type="password"
              placeholder="输入密码"
              :disabled="loading"
              prefixIcon="🔒"
              size="lg"
            />
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-4 bg-danger-50 border border-danger-200 rounded-lg animate-slide-down">
            <div class="flex items-start gap-3">
              <span class="text-xl">❌</span>
              <p class="text-sm text-danger-700 flex-1">{{ errorMessage }}</p>
            </div>
          </div>

          <!-- Login Button -->
          <Button
            type="submit"
            variant="primary"
            size="lg"
            :loading="loading"
            :disabled="loading"
            full-width
            icon="🔐"
          >
            {{ loading ? '登录中...' : '登录' }}
          </Button>
        </form>

        <!-- Demo Credentials -->
        <div class="mt-6 pt-6 border-t border-gray-200">
          <p class="text-sm text-gray-600 mb-3 font-medium flex items-center gap-2">
            <span>💡</span>
            <span>测试账号：</span>
          </p>
          <div class="space-y-2 text-sm">
            <button
              @click="fillAdmin"
              class="w-full flex items-center justify-between p-3 bg-gradient-to-r from-primary-50 to-purple-50 hover:from-primary-100 hover:to-purple-100 rounded-lg transition-all duration-200 border border-primary-100 hover:border-primary-300 group"
            >
              <span class="flex items-center gap-2 text-gray-700 font-medium">
                <span class="text-lg">👑</span>
                <span>管理员</span>
              </span>
              <code class="text-primary-600 font-mono text-xs bg-white px-2 py-1 rounded group-hover:bg-primary-50 transition-colors">admin / admin123</code>
            </button>
            <button
              @click="fillDemo"
              class="w-full flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-lg transition-all duration-200 border border-blue-100 hover:border-blue-300 group"
            >
              <span class="flex items-center gap-2 text-gray-700 font-medium">
                <span class="text-lg">📊</span>
                <span>分析师</span>
              </span>
              <code class="text-blue-600 font-mono text-xs bg-white px-2 py-1 rounded group-hover:bg-blue-50 transition-colors">demo / demo123</code>
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center mt-6 animate-fade-in" style="animation-delay: 0.3s">
        <p class="text-white/80 text-sm backdrop-blur-sm bg-white/10 inline-block px-4 py-2 rounded-full">
          © 2026 PayGuard. All rights reserved.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Button from '../components/Button.vue'
import Input from '../components/Input.vue'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''

  try {
    const result = await authStore.login(form.value.username, form.value.password)

    if (result.success) {
      router.push('/dashboard')
    } else {
      errorMessage.value = result.error || '登录失败，请检查用户名和密码'
    }
  } catch (error) {
    errorMessage.value = '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function fillAdmin() {
  form.value.username = 'admin'
  form.value.password = 'admin123'
}

function fillDemo() {
  form.value.username = 'demo'
  form.value.password = 'demo123'
}
</script>
