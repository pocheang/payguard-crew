import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

// 获取API基础URL
const getBaseURL = () => {
  // 开发和生产环境都使用相对路径，由 Vite 代理处理
  // 这样避免了 CORS 问题和环境变量配置问题
  return '/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    if (authStore.apiKey) {
      config.headers['X-API-Key'] = authStore.apiKey
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken })
}

export const auditAPI = {
  auditTransaction: (data) => api.post('/audit/transaction', data),
  getReport: (transactionId) => api.get(`/audit/report/${transactionId}`),
  getLogs: (transactionId) => api.get(`/audit/logs/${transactionId}`)
}

export const batchAPI = {
  batchAudit: (transactions, maxConcurrent = 10) =>
    api.post('/audit/batch', { transactions, max_concurrent: maxConcurrent }),
  listReports: (params) => api.get('/audit/list', { params }),
  getStatistics: (startDate, endDate) =>
    api.get('/audit/statistics', { params: { start_date: startDate, end_date: endDate } }),
  exportCSV: (transactionIds) =>
    api.get('/audit/export/csv', {
      params: { transaction_ids: transactionIds },
      responseType: 'blob'
    }),
  exportExcel: (transactionIds) =>
    api.get('/audit/export/excel', {
      params: { transaction_ids: transactionIds },
      responseType: 'blob'
    })
}

export const reviewAPI = {
  createReview: (data) => api.post('/review/create', data),
  updateStatus: (transactionId, data) => api.post(`/review/${transactionId}/status`, data),
  assignReviewer: (transactionId, data) => api.post(`/review/${transactionId}/assign`, data),
  addComment: (transactionId, data) => api.post(`/review/${transactionId}/comment`, data),
  getReviewDetail: (transactionId) => api.get(`/review/${transactionId}`),
  getPendingReviews: (params) => api.get('/review/list/pending', { params }),
  getStatistics: () => api.get('/review/statistics')
}

export const healthAPI = {
  check: () => api.get('/health/health')
}

export default api
