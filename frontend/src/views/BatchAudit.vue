<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-800">批量交易审计</h1>
      <p class="text-gray-600 mt-1">上传或输入多笔交易进行批量风险评估</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column - Input -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Input Method Selection -->
        <div class="card">
          <div class="flex items-center space-x-4 mb-4">
            <button
              @click="inputMethod = 'manual'"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-colors',
                inputMethod === 'manual'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              手动输入
            </button>
            <button
              @click="inputMethod = 'json'"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-colors',
                inputMethod === 'json'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              JSON导入
            </button>
          </div>

          <!-- Manual Input -->
          <div v-if="inputMethod === 'manual'" class="space-y-4">
            <p class="text-sm text-gray-600">
              当前已添加 {{ transactions.length }} 笔交易（最多100笔）
            </p>

            <form @submit.prevent="addTransaction" class="space-y-4 p-4 bg-gray-50 rounded-lg">
              <div class="grid grid-cols-2 gap-4">
                <input
                  v-model="newTx.transaction_id"
                  type="text"
                  class="input-field"
                  placeholder="交易ID *"
                  required
                />
                <input
                  v-model.number="newTx.amount"
                  type="number"
                  class="input-field"
                  placeholder="金额 *"
                  required
                />
                <input
                  v-model="newTx.user_id"
                  type="text"
                  class="input-field"
                  placeholder="用户ID *"
                  required
                />
                <input
                  v-model="newTx.merchant_id"
                  type="text"
                  class="input-field"
                  placeholder="商户ID *"
                  required
                />
              </div>
              <button type="submit" class="btn-primary" :disabled="transactions.length >= 100">
                ➕ 添加到列表
              </button>
            </form>

            <!-- Quick Add Samples -->
            <div class="flex space-x-2">
              <button @click="addSampleTransactions(5)" class="btn-secondary text-sm">
                添加 5 笔样例
              </button>
              <button @click="addSampleTransactions(20)" class="btn-secondary text-sm">
                添加 20 笔样例
              </button>
              <button @click="clearTransactions" class="text-red-600 text-sm hover:underline">
                清空列表
              </button>
            </div>
          </div>

          <!-- JSON Input -->
          <div v-else class="space-y-4">
            <p class="text-sm text-gray-600">粘贴JSON格式的交易数组</p>
            <textarea
              v-model="jsonInput"
              class="input-field font-mono text-sm"
              rows="10"
              placeholder='[{"transaction_id": "TX001", "amount": 1000, "user_id": "USER001", ...}]'
            ></textarea>
            <button @click="parseJSON" class="btn-primary">
              解析JSON
            </button>
          </div>
        </div>

        <!-- Transaction List -->
        <div v-if="transactions.length > 0" class="card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-800">
              交易列表 ({{ transactions.length }})
            </h3>
            <button @click="clearTransactions" class="text-sm text-red-600 hover:underline">
              清空
            </button>
          </div>

          <div class="space-y-2 max-h-96 overflow-y-auto">
            <div
              v-for="(tx, index) in transactions"
              :key="index"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div>
                <p class="font-medium text-gray-800">{{ tx.transaction_id }}</p>
                <p class="text-sm text-gray-600">
                  {{ tx.amount }} {{ tx.currency || 'USD' }} • {{ tx.user_id }}
                </p>
              </div>
              <button
                @click="removeTransaction(index)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                删除
              </button>
            </div>
          </div>

          <!-- Batch Settings -->
          <div class="mt-4 pt-4 border-t border-gray-200">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              最大并发数 (1-50)
            </label>
            <input
              v-model.number="maxConcurrent"
              type="number"
              min="1"
              max="50"
              class="input-field w-32"
            />
          </div>

          <!-- Submit Button -->
          <div class="mt-4">
            <button
              @click="submitBatch"
              class="w-full btn-primary py-3"
              :disabled="loading || transactions.length === 0"
            >
              {{ loading ? '审计中...' : `🚀 批量审计 (${transactions.length} 笔)` }}
            </button>
          </div>
        </div>
      </div>

      <!-- Right Column - Results -->
      <div class="lg:col-span-1">
        <!-- Loading State -->
        <div v-if="loading" class="card">
          <div class="flex flex-col items-center justify-center py-12">
            <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mb-4"></div>
            <p class="text-gray-600 font-medium">批量审计中...</p>
            <p class="text-sm text-gray-500 mt-2">已处理: {{ processedCount }} / {{ transactions.length }}</p>
            <div class="w-full bg-gray-200 rounded-full h-2 mt-4">
              <div
                class="bg-primary-600 h-2 rounded-full transition-all"
                :style="{ width: `${(processedCount / transactions.length) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Results Summary -->
        <div v-else-if="batchResult" class="card">
          <h3 class="text-lg font-bold text-gray-800 mb-4">审计结果</h3>

          <!-- Summary Stats -->
          <div class="space-y-3 mb-6">
            <div class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <span class="text-sm font-medium text-blue-800">总数</span>
              <span class="text-xl font-bold text-blue-600">{{ batchResult.total }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span class="text-sm font-medium text-green-800">成功</span>
              <span class="text-xl font-bold text-green-600">{{ batchResult.success }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <span class="text-sm font-medium text-red-800">失败</span>
              <span class="text-xl font-bold text-red-600">{{ batchResult.failed }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span class="text-sm font-medium text-gray-800">耗时</span>
              <span class="text-xl font-bold text-gray-600">{{ batchResult.duration_seconds }}s</span>
            </div>
          </div>

          <!-- Risk Distribution -->
          <div class="mb-6">
            <p class="text-sm font-medium text-gray-700 mb-2">风险分布</p>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">低风险</span>
                <span class="badge-success">{{ riskDistribution.low }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">中风险</span>
                <span class="badge-warning">{{ riskDistribution.medium }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">高风险</span>
                <span class="badge-danger">{{ riskDistribution.high }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="space-y-2">
            <button @click="viewDetailedResults" class="w-full btn-primary">
              查看详细结果
            </button>
            <button @click="exportResults" class="w-full btn-secondary">
              导出报告
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="card">
          <div class="text-center py-12">
            <span class="text-6xl mb-4 block">📦</span>
            <p class="text-gray-600">添加交易后</p>
            <p class="text-gray-600">开始批量审计</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Results Modal -->
    <div v-if="showDetails" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-800">详细审计结果</h3>
          <button @click="showDetails = false" class="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          <div class="space-y-3">
            <div
              v-for="(result, index) in batchResult.results"
              :key="index"
              class="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium text-gray-800">{{ result.transaction_id }}</span>
                <span :class="getRiskBadgeClass(result.risk_level)">
                  {{ result.risk_level?.toUpperCase() }}
                </span>
              </div>
              <div class="text-sm text-gray-600 space-y-1">
                <p>风险分数: {{ result.risk_score }}</p>
                <p>决策: {{ getDecisionLabel(result.decision) }}</p>
                <p v-if="result.triggered_rules?.length">
                  触发规则: {{ result.triggered_rules.length }} 条
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { batchAPI } from '../services/api'

const inputMethod = ref('manual')
const transactions = ref([])
const jsonInput = ref('')
const maxConcurrent = ref(10)
const loading = ref(false)
const processedCount = ref(0)
const batchResult = ref(null)
const showDetails = ref(false)

const newTx = ref({
  transaction_id: '',
  amount: 1000,
  user_id: '',
  merchant_id: '',
  currency: 'USD',
  account_age_days: 365,
  transaction_frequency_1h: 1,
  ip_location_status: 'normal',
  device_status: 'normal',
  kyc_status: 'verified',
  merchant_risk_level: 'low',
  is_blacklisted: false,
  timestamp: new Date().toISOString()
})

const riskDistribution = computed(() => {
  if (!batchResult.value?.results) return { low: 0, medium: 0, high: 0 }
  return batchResult.value.results.reduce((acc, r) => {
    acc[r.risk_level] = (acc[r.risk_level] || 0) + 1
    return acc
  }, { low: 0, medium: 0, high: 0 })
})

function addTransaction() {
  if (transactions.value.length >= 100) {
    alert('最多添加100笔交易')
    return
  }
  transactions.value.push({ ...newTx.value, timestamp: new Date().toISOString() })
  newTx.value.transaction_id = ''
  newTx.value.user_id = ''
  newTx.value.merchant_id = ''
}

function removeTransaction(index) {
  transactions.value.splice(index, 1)
}

function clearTransactions() {
  transactions.value = []
  batchResult.value = null
}

function addSampleTransactions(count) {
  const riskLevels = ['low', 'medium', 'high']
  for (let i = 0; i < count && transactions.value.length < 100; i++) {
    const risk = riskLevels[Math.floor(Math.random() * 3)]
    transactions.value.push({
      transaction_id: `TX_${Date.now()}_${i}`,
      user_id: `USER_${Math.floor(Math.random() * 100)}`,
      merchant_id: `MERCHANT_${Math.floor(Math.random() * 50)}`,
      amount: risk === 'high' ? 10000 + Math.random() * 20000 : 100 + Math.random() * 5000,
      currency: 'USD',
      account_age_days: risk === 'high' ? 10 : 365,
      transaction_frequency_1h: risk === 'high' ? 10 : 2,
      ip_location_status: risk === 'high' ? 'abnormal' : 'normal',
      device_status: risk === 'medium' || risk === 'high' ? 'abnormal' : 'normal',
      kyc_status: risk === 'high' ? 'unverified' : 'verified',
      merchant_risk_level: risk,
      is_blacklisted: false,
      timestamp: new Date().toISOString()
    })
  }
}

function parseJSON() {
  try {
    const parsed = JSON.parse(jsonInput.value)
    if (!Array.isArray(parsed)) {
      alert('JSON必须是数组格式')
      return
    }
    if (parsed.length > 100) {
      alert('最多100笔交易，已截取前100笔')
      transactions.value = parsed.slice(0, 100)
    } else {
      transactions.value = parsed
    }
    jsonInput.value = ''
    inputMethod.value = 'manual'
  } catch (error) {
    alert('JSON格式错误: ' + error.message)
  }
}

async function submitBatch() {
  loading.value = true
  processedCount.value = 0
  batchResult.value = null

  try {
    const response = await batchAPI.batchAudit(transactions.value, maxConcurrent.value)
    batchResult.value = response.data
  } catch (error) {
    alert('批量审计失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

function viewDetailedResults() {
  showDetails.value = true
}

function exportResults() {
  const csv = convertToCSV(batchResult.value.results)
  downloadFile(csv, 'batch_audit_results.csv', 'text/csv')
}

function convertToCSV(data) {
  const headers = ['交易ID', '风险等级', '风险分数', '决策', '触发规则数']
  const rows = data.map(r => [
    r.transaction_id,
    r.risk_level,
    r.risk_score,
    r.decision,
    r.triggered_rules?.length || 0
  ])
  return [headers, ...rows].map(row => row.join(',')).join('\n')
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function getRiskBadgeClass(level) {
  const classes = {
    low: 'badge-success',
    medium: 'badge-warning',
    high: 'badge-danger'
  }
  return classes[level] || 'badge bg-gray-100 text-gray-700'
}

function getDecisionLabel(decision) {
  const labels = { approve: '批准', review: '审核', reject: '拒绝' }
  return labels[decision] || decision
}
</script>
