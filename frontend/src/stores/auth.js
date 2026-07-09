import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const apiKey = ref(localStorage.getItem('api_key') || 'demo-test-key-12345')

  const isAuthenticated = computed(() => !!token.value)

  function initializeAuth() {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
    }
  }

  async function login(username, password) {
    try {
      const response = await authAPI.login(username, password)
      const data = response.data

      token.value = data.access_token
      refreshToken.value = data.refresh_token

      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      const userResponse = await authAPI.getCurrentUser()
      user.value = userResponse.data
      localStorage.setItem('user', JSON.stringify(userResponse.data))

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  function logout() {
    token.value = null
    refreshToken.value = null
    user.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function refresh() {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      const response = await authAPI.refreshToken(refreshToken.value)
      const data = response.data

      token.value = data.access_token
      refreshToken.value = data.refresh_token

      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      return { success: true }
    } catch (error) {
      logout()
      return { success: false }
    }
  }

  return {
    token,
    refreshToken,
    user,
    apiKey,
    isAuthenticated,
    initializeAuth,
    login,
    logout,
    refresh
  }
})
