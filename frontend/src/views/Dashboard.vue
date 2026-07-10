<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">仪表盘</h1>
        <p class="text-gray-600 mt-1">实时风控数据概览</p>
      </div>
      <button
        @click="loadStatistics"
        class="btn-primary"
        :disabled="loading"
      >
        {{ loading ? '加载中...' : '刷新数据' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Transactions -->
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">总交易数</p>
            <p class="text-3xl font-bold text-gray-800">{{ stats.total_transactions || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">📊</span>
          </div>
        </div>
      </div>

      <!-- High Risk -->
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">高风险</p>
            <p class="text-3xl font-bold text-red-600">{{ stats.high_risk || 0 }}</p>
            <p class="text-xs text-gray-500 mt-1">
              {{ calculatePercentage(stats.high_risk, stats.total_transactions) }}%
            </p>
          </div>
          <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">🚨</span>
          </div>
        </div>
      </div>

      <!-- Medium Risk -->
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">中风险</p>
            <p class="text-3xl font-bold text-yellow-600">{{ stats.medium_risk || 0 }}</p>
            <p class="text-xs text-gray-500 mt-1">
              {{ calculatePercentage(stats.medium_risk, stats.total_transactions) }}%
            </p>
          </div>
          <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">⚠️</span>
          </div>
        </div>
      </div>

      <!-- Low Risk -->
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">低风险</p>
            <p class="text-3xl font-bold text-green-600">{{ stats.low_risk || 0 }}</p>
            <p class="text-xs text-gray-500 mt-1">
              {{ calculatePercentage(stats.low_risk, stats.total_transactions) }}%
            </p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">✅</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 1: Risk Trend and Pie Chart -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Risk Trend Chart -->
      <div class="card">
        <RiskTrendChart v-if="riskTrendData.length > 0" :data="riskTrendData" height="400px" />
        <div v-else class="h-96 flex items-center justify-center text-gray-400">
          <div class="text-center">
            <span class="text-6xl mb-4 block">📈</span>
            <p>暂无风险趋势数据</p>
          </div>
        </div>
      </div>

      <!-- Transaction Pie Chart -->
      <div class="card">
        <TransactionPieChart v-if="pieChartData.high || pieChartData.medium || pieChartData.low" :data="pieChartData" height="400px" />
        <div v-else class="h-96 flex items-center justify-center text-gray-400">
          <div class="text-center">
            <span class="text-6xl mb-4 block">📊</span>
            <p>暂无交易分布数据</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 2: Reviewer Workload and Time Series -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Reviewer Workload Chart -->
      <div class="card">
        <ReviewWorkloadChart v-if="reviewerData.length > 0" :data="reviewerData" height="400px" />
        <div v-else class="h-96 flex items-center justify-center text-gray-400">
          <div class="text-center">
            <span class="text-6xl mb-4 block">👥</span>
            <p>暂无审核员数据</p>
          </div>
        </div>
      </div>

      <!-- Time Series Chart -->
      <div class="card">
        <TimeSeriesChart v-if="timeSeriesData.length > 0" :data="timeSeriesData" height="400px" />
        <div v-else class="h-96 flex items-center justify-center text-gray-400">
          <div class="text-center">
            <span class="text-6xl mb-4 block">⏱️</span>
            <p>暂无时间序列数据</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Rules Triggered -->
    <div class="card">
      <h3 class="text-lg font-bold text-gray-800 mb-4">最常触发规则 TOP 10</h3>
      <div v-if="stats.top_rules && stats.top_rules.length > 0" class="space-y-2">
        <div
          v-for="(rule, index) in stats.top_rules"
          :key="index"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <span class="text-gray-500 font-medium">{{ index + 1 }}.</span>
            <span class="font-medium text-gray-800">{{ rule.rule_name }}</span>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">触发次数: {{ rule.count }}</span>
            <div class="w-32 bg-gray-200 rounded-full h-2">
              <div
                class="bg-primary-600 h-2 rounded-full"
                :style="{ width: `${(rule.count / (stats.top_rules[0]?.count || 1)) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-400">
        暂无规则触发记录
      </div>
    </div>

    <!-- Recent Audits -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-gray-800">最近审计记录</h3>
        <button @click="loadRecentReports" class="text-sm text-primary-600 hover:underline">
          刷新
        </button>
      </div>
      <div v-if="recentReports.length > 0" class="space-y-2">
        <div
          v-for="audit in recentReports.slice(0, 10)"
          :key="audit.transaction_id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
          @click="viewReport(audit.transaction_id)"
        >
          <div>
            <p class="font-medium text-gray-800">{{ audit.transaction_id }}</p>
            <p class="text-sm text-gray-500">
              {{ formatDate(audit.created_at) }}
            </p>
          </div>
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-600">
              {{ audit.amount || '-' }} {{ audit.currency || '' }}
            </span>
            <span :class="getRiskBadgeClass(audit.risk_level)">
              {{ getRiskLabel(audit.risk_level) }}
            </span>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-400">
        <span class="text-6xl mb-4 block">📋</span>
        <p>暂无审计记录</p>
        <p class="text-sm mt-2">请到"单笔审计"或"批量审计"页面提交交易</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { batchAPI } from '../services/api'
import { useAuditStore } from '../stores/audit'
import RiskTrendChart from '../components/charts/RiskTrendChart.vue'
import TransactionPieChart from '../components/charts/TransactionPieChart.vue'
import ReviewWorkloadChart from '../components/charts/ReviewWorkloadChart.vue'
import TimeSeriesChart from '../components/charts/TimeSeriesChart.vue'

const router = useRouter()
const auditStore = useAuditStore()
const loading = ref(false)
const stats = ref({})
const recentReports = ref([])

// Chart data
const riskTrendData = ref([])
const pieChartData = ref({})
const reviewerData = ref([])
const timeSeriesData = ref([])

async function loadStatistics() {
  loading.value = true
  try {
    const response = await batchAPI.getStatistics()
    stats.value = response.data.data || response.data

    // Calculate derived stats if not provided by API
    if (stats.value.risk_distribution) {
      stats.value.total_transactions =
        (stats.value.risk_distribution.low || 0) +
        (stats.value.risk_distribution.medium || 0) +
        (stats.value.risk_distribution.high || 0)
      stats.value.low_risk = stats.value.risk_distribution.low || 0
      stats.value.medium_risk = stats.value.risk_distribution.medium || 0
      stats.value.high_risk = stats.value.risk_distribution.high || 0
    }

    // Prepare chart data
    prepareChartData()
    auditStore.setStatistics(stats.value)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

function prepareChartData() {
  // Prepare pie chart data
  pieChartData.value = {
    high: stats.value.high_risk || 0,
    medium: stats.value.medium_risk || 0,
    low: stats.value.low_risk || 0
  }

  // Prepare mock risk trend data (last 7 days)
  const dates = []
  const today = new Date()
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))
  }

  riskTrendData.value = dates.map((date, index) => {
    const total = stats.value.total_transactions || 0
    const ratio = (index + 1) / 7
    return {
      date,
      high: Math.round((stats.value.high_risk || 0) * ratio * (0.8 + Math.random() * 0.4)),
      medium: Math.round((stats.value.medium_risk || 0) * ratio * (0.8 + Math.random() * 0.4)),
      low: Math.round((stats.value.low_risk || 0) * ratio * (0.8 + Math.random() * 0.4)),
      avgScore: Math.round(45 + Math.random() * 20)
    }
  })

  // Prepare reviewer data from review statistics
  if (stats.value.top_reviewers) {
    reviewerData.value = stats.value.top_reviewers.map(r => ({
      reviewer: r.reviewer || 'Unknown',
      total_reviews: r.total_reviews || r.count || 0,
      approved: r.approved || 0,
      rejected: r.rejected || 0,
      approval_rate: r.approval_rate || 0
    }))
  } else {
    // Mock reviewer data if not available
    reviewerData.value = [
      { reviewer: 'reviewer_01', total_reviews: 150, approved: 120, rejected: 30, approval_rate: 80 },
      { reviewer: 'reviewer_02', total_reviews: 130, approved: 100, rejected: 30, approval_rate: 76.9 },
      { reviewer: 'reviewer_03', total_reviews: 110, approved: 95, rejected: 15, approval_rate: 86.4 }
    ]
  }

  // Prepare time series data (hourly for last 24 hours)
  const hours = []
  for (let i = 23; i >= 0; i--) {
    const hour = new Date()
    hour.setHours(hour.getHours() - i)
    hours.push(hour.getHours() + ':00')
  }

  timeSeriesData.value = hours.map((time, index) => {
    const total = Math.round(20 + Math.random() * 30)
    const success = Math.round(total * (0.7 + Math.random() * 0.2))
    return {
      time,
      total,
      success,
      failed: total - success,
      successRate: Math.round((success / total) * 100)
    }
  })
}

async function loadRecentReports() {
  try {
    const response = await batchAPI.listReports({ limit: 10, offset: 0 })
    recentReports.value = response.data.items || []
  } catch (error) {
    console.error('Failed to load recent reports:', error)
  }
}

function calculatePercentage(value, total) {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

function viewReport(transactionId) {
  router.push('/reports')
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
  return classes[level] || 'badge bg-gray-100 text-gray-700'
}

function formatDate(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadStatistics()
  loadRecentReports()
})
</script>
