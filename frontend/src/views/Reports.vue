<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-800">审计报告查询</h1>
      <p class="text-gray-600 mt-1">查询历史审计记录并导出报告</p>
    </div>

    <!-- Search and Filters -->
    <div class="card">
      <h3 class="text-lg font-bold text-gray-800 mb-4">查询条件</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">风险等级</label>
          <select v-model="filters.risk_level" class="input-field">
            <option value="">全部</option>
            <option value="low">低风险</option>
            <option value="medium">中风险</option>
            <option value="high">高风险</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">决策结果</label>
          <select v-model="filters.decision" class="input-field">
            <option value="">全部</option>
            <option value="approve">批准</option>
            <option value="review">待审核</option>
            <option value="reject">拒绝</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">每页显示</label>
          <select v-model.number="filters.limit" class="input-field">
            <option :value="50">50</option>
            <option :value="100">100</option>
            <option :value="200">200</option>
          </select>
        </div>
      </div>
      <div class="flex space-x-2 mt-4">
        <button @click="searchReports" class="btn-primary">
          🔍 查询
        </button>
        <button @click="resetFilters" class="btn-secondary">
          重置
        </button>
      </div>
    </div>

    <!-- Export Actions -->
    <div class="card">
      <h3 class="text-lg font-bold text-gray-800 mb-4">批量导出</h3>
      <div class="flex items-center space-x-4">
        <p class="text-sm text-gray-600">
          已选择 {{ selectedIds.length }} 条记录
        </p>
        <button
          @click="selectAll"
          class="text-sm text-primary-600 hover:underline"
          :disabled="reports.length === 0"
        >
          全选
        </button>
        <button
          @click="clearSelection"
          class="text-sm text-gray-600 hover:underline"
          :disabled="selectedIds.length === 0"
        >
          清空
        </button>
        <div class="flex-1"></div>
        <button
          @click="exportCSV"
          class="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition"
          :disabled="selectedIds.length === 0 || exporting"
        >
          {{ exporting ? '导出中...' : '📥 导出CSV' }}
        </button>
        <button
          @click="exportExcel"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          :disabled="selectedIds.length === 0 || exporting"
        >
          {{ exporting ? '导出中...' : '📊 导出Excel' }}
        </button>
      </div>
    </div>

    <!-- Reports Table -->
    <div class="card">
      <h3 class="text-lg font-bold text-gray-800 mb-4">
        审计记录 ({{ pagination.total || 0 }})
      </h3>

      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p class="text-gray-600">加载中...</p>
      </div>

      <div v-else-if="reports.length === 0" class="text-center py-12">
        <span class="text-6xl mb-4 block">📋</span>
        <p class="text-gray-600">暂无审计记录</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  @change="toggleSelectAll"
                  :checked="selectedIds.length === reports.length && reports.length > 0"
                  class="w-4 h-4 text-primary-600 border-gray-300 rounded"
                />
              </th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">交易ID</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">用户ID</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">金额</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">风险等级</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">风险分数</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">决策</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">创建时间</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr
              v-for="report in reports"
              :key="report.transaction_id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-4 py-3">
                <input
                  type="checkbox"
                  :value="report.transaction_id"
                  v-model="selectedIds"
                  class="w-4 h-4 text-primary-600 border-gray-300 rounded"
                />
              </td>
              <td class="px-4 py-3">
                <span class="font-medium text-gray-800">{{ report.transaction_id }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600">
                {{ report.user_id || '-' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-600">
                {{ report.amount || '-' }} {{ report.currency || '' }}
              </td>
              <td class="px-4 py-3">
                <span :class="getRiskBadgeClass(report.risk_level)">
                  {{ getRiskLabel(report.risk_level) }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm font-medium text-gray-800">
                {{ report.risk_score || '-' }}
              </td>
              <td class="px-4 py-3">
                <span :class="getDecisionBadgeClass(report.decision)">
                  {{ getDecisionLabel(report.decision) }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600">
                {{ formatDate(report.created_at) }}
              </td>
              <td class="px-4 py-3">
                <button
                  @click="viewDetail(report.transaction_id)"
                  class="text-primary-600 hover:text-primary-800 text-sm font-medium"
                >
                  查看
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total > 0" class="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-600">
          显示 {{ pagination.offset + 1 }} - {{ Math.min(pagination.offset + pagination.limit, pagination.total) }} / 共 {{ pagination.total }} 条
        </div>
        <div class="flex space-x-2">
          <button
            @click="previousPage"
            :disabled="pagination.offset === 0"
            class="px-3 py-1 border border-gray-300 rounded text-sm font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <button
            @click="nextPage"
            :disabled="pagination.offset + pagination.limit >= pagination.total"
            class="px-3 py-1 border border-gray-300 rounded text-sm font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { batchAPI } from '../services/api'

const loading = ref(false)
const exporting = ref(false)
const reports = ref([])
const selectedIds = ref([])

const filters = ref({
  risk_level: '',
  decision: '',
  limit: 100
})

const pagination = ref({
  total: 0,
  offset: 0,
  limit: 100
})

async function searchReports() {
  loading.value = true
  try {
    const params = {
      limit: filters.value.limit,
      offset: pagination.value.offset
    }
    if (filters.value.risk_level) params.risk_level = filters.value.risk_level
    if (filters.value.decision) params.decision = filters.value.decision

    const response = await batchAPI.listReports(params)
    reports.value = response.data.items || []
    pagination.value.total = response.data.total || 0
    pagination.value.limit = response.data.limit || filters.value.limit
    pagination.value.offset = response.data.offset || 0
  } catch (error) {
    console.error('Failed to load reports:', error)
    alert('查询失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.value = {
    risk_level: '',
    decision: '',
    limit: 100
  }
  pagination.value.offset = 0
  selectedIds.value = []
  searchReports()
}

function selectAll() {
  selectedIds.value = reports.value.map(r => r.transaction_id)
}

function clearSelection() {
  selectedIds.value = []
}

function toggleSelectAll(event) {
  if (event.target.checked) {
    selectAll()
  } else {
    clearSelection()
  }
}

async function exportCSV() {
  if (selectedIds.value.length === 0) return
  exporting.value = true
  try {
    const response = await batchAPI.exportCSV(selectedIds.value)
    downloadFile(response.data, 'audit_reports.csv', 'text/csv')
  } catch (error) {
    alert('导出失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    exporting.value = false
  }
}

async function exportExcel() {
  if (selectedIds.value.length === 0) return
  exporting.value = true
  try {
    const response = await batchAPI.exportExcel(selectedIds.value)
    downloadFile(response.data, 'audit_reports.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  } catch (error) {
    alert('导出失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    exporting.value = false
  }
}

function downloadFile(data, filename, type) {
  const blob = new Blob([data], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function viewDetail(transactionId) {
  alert(`查看详情: ${transactionId}\n\n此功能需要实现详情页面`)
}

function previousPage() {
  if (pagination.value.offset > 0) {
    pagination.value.offset = Math.max(0, pagination.value.offset - pagination.value.limit)
    searchReports()
  }
}

function nextPage() {
  if (pagination.value.offset + pagination.value.limit < pagination.value.total) {
    pagination.value.offset += pagination.value.limit
    searchReports()
  }
}

function getRiskLabel(level) {
  const labels = { low: '低风险', medium: '中风险', high: '高风险' }
  return labels[level] || level
}

function getRiskBadgeClass(level) {
  const classes = {
    low: 'badge-success',
    medium: 'badge-warning',
    high: 'badge-danger'
  }
  return classes[level] || 'badge'
}

function getDecisionLabel(decision) {
  const labels = { approve: '批准', review: '待审核', reject: '拒绝' }
  return labels[decision] || decision
}

function getDecisionBadgeClass(decision) {
  const classes = {
    approve: 'badge-success',
    review: 'badge-warning',
    reject: 'badge-danger'
  }
  return classes[decision] || 'badge'
}

function formatDate(timestamp) {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN')
}

onMounted(() => {
  searchReports()
})
</script>
