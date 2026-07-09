<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">待审核交易</h1>
        <p class="text-gray-600 mt-1">管理和处理需要人工审核的交易</p>
      </div>
      <button @click="loadReviews" class="btn-primary" :disabled="loading">
        {{ loading ? '加载中...' : '刷新' }}
      </button>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">优先级</label>
          <select v-model="filters.priority" @change="loadReviews" class="input-field">
            <option value="">全部</option>
            <option value="urgent">紧急</option>
            <option value="high">高</option>
            <option value="normal">正常</option>
            <option value="low">低</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">分配给</label>
          <select v-model="filters.assigned_to" @change="loadReviews" class="input-field">
            <option value="">全部</option>
            <option value="me">我的任务</option>
            <option value="unassigned">未分配</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">显示数量</label>
          <select v-model.number="filters.limit" @change="loadReviews" class="input-field">
            <option :value="50">50</option>
            <option :value="100">100</option>
            <option :value="200">200</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn-secondary w-full">
            重置筛选
          </button>
        </div>
      </div>
    </div>

    <!-- Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">待处理</p>
            <p class="text-2xl font-bold text-blue-600">{{ stats.pending || 0 }}</p>
          </div>
          <span class="text-3xl">⏳</span>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">审核中</p>
            <p class="text-2xl font-bold text-yellow-600">{{ stats.in_review || 0 }}</p>
          </div>
          <span class="text-3xl">👁️</span>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">已批准</p>
            <p class="text-2xl font-bold text-green-600">{{ stats.approved || 0 }}</p>
          </div>
          <span class="text-3xl">✅</span>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">已拒绝</p>
            <p class="text-2xl font-bold text-red-600">{{ stats.rejected || 0 }}</p>
          </div>
          <span class="text-3xl">❌</span>
        </div>
      </div>
    </div>

    <!-- Review List -->
    <div class="card">
      <h3 class="text-lg font-bold text-gray-800 mb-4">
        待审核列表 ({{ reviews.length }})
      </h3>

      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p class="text-gray-600">加载中...</p>
      </div>

      <div v-else-if="reviews.length === 0" class="text-center py-12">
        <span class="text-6xl mb-4 block">✅</span>
        <p class="text-gray-600">没有待审核的交易</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="review in reviews"
          :key="review.transaction_id"
          class="border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:shadow-md transition-all cursor-pointer"
          @click="viewDetail(review.transaction_id)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <h4 class="font-bold text-gray-800">{{ review.transaction_id }}</h4>
                <span :class="getPriorityBadgeClass(review.priority)">
                  {{ getPriorityLabel(review.priority) }}
                </span>
                <span :class="getStatusBadgeClass(review.status)">
                  {{ getStatusLabel(review.status) }}
                </span>
              </div>
              <div class="text-sm text-gray-600 space-y-1">
                <p>创建时间: {{ formatDate(review.created_at) }}</p>
                <p v-if="review.assigned_to">分配给: {{ review.assigned_to }}</p>
                <p v-else class="text-yellow-600">未分配审核人</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click.stop="assignToMe(review.transaction_id)"
                class="px-3 py-1 bg-primary-100 text-primary-700 rounded text-sm font-medium hover:bg-primary-200 transition"
              >
                分配给我
              </button>
              <button
                @click.stop="viewDetail(review.transaction_id)"
                class="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm font-medium hover:bg-gray-200 transition"
              >
                查看详情 →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { reviewAPI } from '../services/api'
import { useReviewStore } from '../stores/review'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const reviewStore = useReviewStore()
const authStore = useAuthStore()

const loading = ref(false)
const reviews = ref([])
const stats = ref({})

const filters = ref({
  priority: '',
  assigned_to: '',
  limit: 100
})

async function loadReviews() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.assigned_to === 'me') {
      params.assigned_to = authStore.user?.username || 'me'
    }
    params.limit = filters.value.limit

    const response = await reviewAPI.getPendingReviews(params)
    reviews.value = response.data.data || []
    reviewStore.setPendingReviews(reviews.value)

    await loadStatistics()
  } catch (error) {
    console.error('Failed to load reviews:', error)
  } finally {
    loading.value = false
  }
}

async function loadStatistics() {
  try {
    const response = await reviewAPI.getStatistics()
    stats.value = response.data.data?.status_distribution || {}
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

async function assignToMe(transactionId) {
  try {
    await reviewAPI.assignReviewer(transactionId, {
      assigned_to: authStore.user?.username || 'me',
      assigner: authStore.user?.username || 'system'
    })
    alert('分配成功')
    loadReviews()
  } catch (error) {
    alert('分配失败: ' + (error.response?.data?.detail || error.message))
  }
}

function viewDetail(transactionId) {
  router.push(`/review/${transactionId}`)
}

function resetFilters() {
  filters.value = {
    priority: '',
    assigned_to: '',
    limit: 100
  }
  loadReviews()
}

function getPriorityLabel(priority) {
  const labels = {
    urgent: '紧急',
    high: '高',
    normal: '正常',
    low: '低'
  }
  return labels[priority] || priority
}

function getPriorityBadgeClass(priority) {
  const classes = {
    urgent: 'badge bg-red-100 text-red-700',
    high: 'badge bg-orange-100 text-orange-700',
    normal: 'badge bg-blue-100 text-blue-700',
    low: 'badge bg-gray-100 text-gray-700'
  }
  return classes[priority] || 'badge'
}

function getStatusLabel(status) {
  const labels = {
    pending: '待处理',
    in_review: '审核中',
    approved: '已批准',
    rejected: '已拒绝',
    escalated: '已上报',
    archived: '已归档'
  }
  return labels[status] || status
}

function getStatusBadgeClass(status) {
  const classes = {
    pending: 'badge bg-yellow-100 text-yellow-700',
    in_review: 'badge bg-blue-100 text-blue-700',
    approved: 'badge bg-green-100 text-green-700',
    rejected: 'badge bg-red-100 text-red-700',
    escalated: 'badge bg-purple-100 text-purple-700',
    archived: 'badge bg-gray-100 text-gray-700'
  }
  return classes[status] || 'badge'
}

function formatDate(timestamp) {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString('zh-CN')
}

onMounted(() => {
  loadReviews()
})
</script>
