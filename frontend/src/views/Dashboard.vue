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
              {{ stats.high_risk_percentage || 0 }}%
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
              {{ stats.medium_risk_percentage || 0 }}%
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
              {{ stats.low_risk_percentage || 0 }}%
            </p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">✅</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Risk Distribution Chart -->
      <div class="card">
        <h3 class="text-lg font-bold text-gray-800 mb-4">风险等级分布</h3>
        <div class="h-64">
          <Bar v-if="chartDataReady" :data="riskChartData" :options="chartOptions" />
          <div v-else class="h-full flex items-center justify-center text-gray-400">
            暂无数据
          </div>
        </div>
      </div>

      <!-- Decision Distribution Chart -->
      <div class="card">
        <h3 class="text-lg font-bold text-gray-800 mb-4">决策分布</h3>
        <div class="h-64">
          <Doughnut v-if="chartDataReady" :data="decisionChartData" :options="doughnutOptions" />
          <div v-else class="h-full flex items-center justify-center text-gray-400">
            暂无数据
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
      <h3 class="text-lg font-bold text-gray-800 mb-4">最近审计记录</h3>
      <div v-if="recentAudits.length > 0" class="space-y-2">
        <div
          v-for="audit in recentAudits.slice(0, 10)"
          :key="audit.transaction_id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div>
            <p class="font-medium text-gray-800">{{ audit.transaction_id }}</p>
            <p class="text-sm text-gray-500">
              {{ formatDate(audit.timestamp) }}
            </p>
          </div>
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-600">
              {{ audit.amount }} {{ audit.currency }}
            </span>
            <span :class="getRiskBadgeClass(audit.risk_level)">
              {{ audit.risk_level?.toUpperCase() }}
            </span>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-400">
        暂无审计记录
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { batchAPI } from '../services/api'
import { useAuditStore } from '../stores/audit'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

const auditStore = useAuditStore()
const loading = ref(false)
const stats = ref({})

const recentAudits = computed(() => auditStore.recentAudits)
const chartDataReady = computed(() => stats.value.risk_distribution && Object.keys(stats.value.risk_distribution).length > 0)

const riskChartData = computed(() => ({
  labels: ['低风险', '中风险', '高风险'],
  datasets: [
    {
      label: '交易数量',
      data: [
        stats.value.risk_distribution?.low || 0,
        stats.value.risk_distribution?.medium || 0,
        stats.value.risk_distribution?.high || 0
      ],
      backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
    }
  ]
}))

const decisionChartData = computed(() => ({
  labels: ['批准', '待审核', '拒绝'],
  datasets: [
    {
      data: [
        stats.value.decision_distribution?.approve || 0,
        stats.value.decision_distribution?.review || 0,
        stats.value.decision_distribution?.reject || 0
      ],
      backgroundColor: ['#10b981', '#3b82f6', '#ef4444']
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}

async function loadStatistics() {
  loading.value = true
  try {
    const response = await batchAPI.getStatistics()
    stats.value = response.data.data || response.data
    auditStore.setStatistics(stats.value)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
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
})
</script>
