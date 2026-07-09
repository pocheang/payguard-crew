<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center space-x-4">
      <button @click="goBack" class="text-gray-600 hover:text-gray-800">
        ← 返回
      </button>
      <div>
        <h1 class="text-2xl font-bold text-gray-800">审核详情</h1>
        <p class="text-gray-600 mt-1">{{ transactionId }}</p>
      </div>
    </div>

    <div v-if="loading" class="card">
      <div class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p class="text-gray-600">加载中...</p>
      </div>
    </div>

    <div v-else-if="review" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column - Review Info and Actions -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Review Status -->
        <div class="card">
          <h3 class="text-lg font-bold text-gray-800 mb-4">审核状态</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600 mb-1">当前状态</p>
              <span :class="getStatusBadgeClass(review.record.status)">
                {{ getStatusLabel(review.record.status) }}
              </span>
            </div>
            <div>
              <p class="text-sm text-gray-600 mb-1">优先级</p>
              <span :class="getPriorityBadgeClass(review.record.priority)">
                {{ getPriorityLabel(review.record.priority) }}
              </span>
            </div>
            <div>
              <p class="text-sm text-gray-600 mb-1">创建时间</p>
              <p class="text-sm font-medium">{{ formatDate(review.record.created_at) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 mb-1">分配给</p>
              <p class="text-sm font-medium">{{ review.record.assigned_to || '未分配' }}</p>
            </div>
          </div>
        </div>

        <!-- Transaction Details -->
        <div class="card">
          <h3 class="text-lg font-bold text-gray-800 mb-4">交易信息</h3>
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-600">交易ID</p>
                <p class="font-medium">{{ review.record.transaction_id }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">金额</p>
                <p class="font-medium">示例金额</p>
              </div>
            </div>
            <p class="text-xs text-gray-500">* 完整交易数据需要集成交易系统</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div v-if="review.record.status === 'pending' || review.record.status === 'in_review'" class="card">
          <h3 class="text-lg font-bold text-gray-800 mb-4">审核操作</h3>

          <!-- Comment Input -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">审核意见</label>
            <textarea
              v-model="comment"
              class="input-field"
              rows="3"
              placeholder="输入审核意见..."
            ></textarea>
          </div>

          <!-- Action Buttons -->
          <div class="grid grid-cols-3 gap-3">
            <button
              @click="updateStatus('approved')"
              class="px-4 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition"
              :disabled="actionLoading"
            >
              ✅ 批准
            </button>
            <button
              @click="updateStatus('rejected')"
              class="px-4 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition"
              :disabled="actionLoading"
            >
              ❌ 拒绝
            </button>
            <button
              @click="updateStatus('escalated')"
              class="px-4 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition"
              :disabled="actionLoading"
            >
              ⬆️ 上报
            </button>
          </div>

          <!-- Quick Start Review -->
          <button
            v-if="review.record.status === 'pending'"
            @click="updateStatus('in_review')"
            class="w-full mt-3 btn-primary"
            :disabled="actionLoading"
          >
            开始审核
          </button>
        </div>

        <!-- Comments History -->
        <div class="card">
          <h3 class="text-lg font-bold text-gray-800 mb-4">
            评论记录 ({{ review.comments?.length || 0 }})
          </h3>

          <div v-if="review.comments && review.comments.length > 0" class="space-y-3">
            <div
              v-for="(comment, index) in review.comments"
              :key="index"
              class="p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-800">{{ comment.user_id }}</span>
                <span class="text-xs text-gray-500">{{ formatDate(comment.created_at) }}</span>
              </div>
              <p class="text-sm text-gray-700">{{ comment.comment }}</p>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-400">
            暂无评论
          </div>

          <!-- Add Comment -->
          <div class="mt-4 pt-4 border-t border-gray-200">
            <div class="flex space-x-2">
              <input
                v-model="newComment"
                type="text"
                class="input-field flex-1"
                placeholder="添加评论..."
                @keyup.enter="addComment"
              />
              <button @click="addComment" class="btn-primary">
                发送
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Quick Info -->
      <div class="lg:col-span-1">
        <!-- Timeline -->
        <div class="card">
          <h3 class="text-lg font-bold text-gray-800 mb-4">审核时间线</h3>
          <div class="space-y-4">
            <div class="flex items-start space-x-3">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-sm">📝</span>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-800">创建审核</p>
                <p class="text-xs text-gray-500">{{ formatDate(review.record.created_at) }}</p>
              </div>
            </div>

            <div v-if="review.record.updated_at" class="flex items-start space-x-3">
              <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-sm">🔄</span>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-800">最后更新</p>
                <p class="text-xs text-gray-500">{{ formatDate(review.record.updated_at) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card mt-6">
          <h3 class="text-lg font-bold text-gray-800 mb-4">快速操作</h3>
          <div class="space-y-2">
            <button
              @click="reassign"
              class="w-full btn-secondary text-left"
            >
              🔄 重新分配
            </button>
            <button
              @click="viewAuditReport"
              class="w-full btn-secondary text-left"
            >
              📊 查看审计报告
            </button>
            <button
              @click="exportRecord"
              class="w-full btn-secondary text-left"
            >
              📥 导出记录
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card">
      <div class="text-center py-12">
        <span class="text-6xl mb-4 block">❌</span>
        <p class="text-gray-600">审核记录不存在</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { reviewAPI } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const transactionId = route.params.transactionId
const loading = ref(false)
const actionLoading = ref(false)
const review = ref(null)
const comment = ref('')
const newComment = ref('')

async function loadReview() {
  loading.value = true
  try {
    const response = await reviewAPI.getReviewDetail(transactionId)
    review.value = response.data.data
  } catch (error) {
    console.error('Failed to load review:', error)
  } finally {
    loading.value = false
  }
}

async function updateStatus(newStatus) {
  if (!comment.value && (newStatus === 'approved' || newStatus === 'rejected')) {
    alert('请输入审核意见')
    return
  }

  actionLoading.value = true
  try {
    await reviewAPI.updateStatus(transactionId, {
      status: newStatus,
      reviewer: authStore.user?.username || 'reviewer',
      comment: comment.value
    })
    alert('状态更新成功')
    comment.value = ''
    loadReview()
  } catch (error) {
    alert('更新失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    actionLoading.value = false
  }
}

async function addComment() {
  if (!newComment.value.trim()) return

  try {
    await reviewAPI.addComment(transactionId, {
      user_id: authStore.user?.username || 'user',
      comment: newComment.value
    })
    newComment.value = ''
    loadReview()
  } catch (error) {
    alert('添加评论失败: ' + (error.response?.data?.detail || error.message))
  }
}

function reassign() {
  const assignee = prompt('输入审核人用户名:')
  if (assignee) {
    reviewAPI.assignReviewer(transactionId, {
      assigned_to: assignee,
      assigner: authStore.user?.username || 'system'
    }).then(() => {
      alert('重新分配成功')
      loadReview()
    }).catch(error => {
      alert('分配失败: ' + (error.response?.data?.detail || error.message))
    })
  }
}

function viewAuditReport() {
  alert('审计报告查看功能开发中')
}

function exportRecord() {
  alert('导出功能开发中')
}

function goBack() {
  router.push('/review/pending')
}

function getPriorityLabel(priority) {
  const labels = { urgent: '紧急', high: '高', normal: '正常', low: '低' }
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
  loadReview()
})
</script>
