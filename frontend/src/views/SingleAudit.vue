<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-800">单笔交易审计</h1>
      <p class="text-gray-600 mt-1">提交单笔交易进行风险评估</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column - Form -->
      <div class="lg:col-span-2">
        <div class="card">
          <h2 class="text-xl font-bold text-gray-800 mb-6">交易信息</h2>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <!-- Transaction ID -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">交易ID *</label>
              <input
                v-model="form.transaction_id"
                type="text"
                class="input-field"
                placeholder="TXN_20260709_001"
                required
              />
            </div>

            <!-- Amount and Currency -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">金额 *</label>
                <input
                  v-model.number="form.amount"
                  type="number"
                  step="0.01"
                  class="input-field"
                  placeholder="1000"
                  required
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">货币 *</label>
                <select v-model="form.currency" class="input-field">
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="CNY">CNY</option>
                  <option value="JPY">JPY</option>
                </select>
              </div>
            </div>

            <!-- User and Merchant -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">用户ID *</label>
                <input
                  v-model="form.user_id"
                  type="text"
                  class="input-field"
                  placeholder="USER_001"
                  required
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">商户ID *</label>
                <input
                  v-model="form.merchant_id"
                  type="text"
                  class="input-field"
                  placeholder="MERCHANT_001"
                  required
                />
              </div>
            </div>

            <!-- Risk Factors -->
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">账户年龄（天）</label>
                <input
                  v-model.number="form.account_age_days"
                  type="number"
                  class="input-field"
                  placeholder="365"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">1小时内交易次数</label>
                <input
                  v-model.number="form.transaction_frequency_1h"
                  type="number"
                  class="input-field"
                  placeholder="1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">KYC状态</label>
                <select v-model="form.kyc_status" class="input-field">
                  <option value="verified">已验证</option>
                  <option value="basic_verified">基础验证</option>
                  <option value="unverified">未验证</option>
                </select>
              </div>
            </div>

            <!-- Device and IP Status -->
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">IP位置状态</label>
                <select v-model="form.ip_location_status" class="input-field">
                  <option value="normal">正常</option>
                  <option value="abnormal">异常</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">设备状态</label>
                <select v-model="form.device_status" class="input-field">
                  <option value="normal">正常</option>
                  <option value="abnormal">异常</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">商户风险等级</label>
                <select v-model="form.merchant_risk_level" class="input-field">
                  <option value="low">低</option>
                  <option value="medium">中</option>
                  <option value="high">高</option>
                </select>
              </div>
            </div>

            <!-- Blacklist -->
            <div class="flex items-center">
              <input
                v-model="form.is_blacklisted"
                type="checkbox"
                id="blacklist"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label for="blacklist" class="ml-2 text-sm text-gray-700">用户在黑名单中</label>
            </div>

            <!-- Submit Button -->
            <div class="pt-4">
              <button
                type="submit"
                class="w-full btn-primary py-3"
                :disabled="loading"
              >
                {{ loading ? '审计中...' : '🔍 开始审计' }}
              </button>
            </div>
          </form>

          <!-- Quick Test Buttons -->
          <div class="mt-6 pt-6 border-t border-gray-200">
            <p class="text-sm font-medium text-gray-700 mb-3">快速测试场景：</p>
            <div class="flex flex-wrap gap-2">
              <button @click="fillLowRisk" class="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition">
                ✅ 低风险场景
              </button>
              <button @click="fillMediumRisk" class="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg text-sm font-medium hover:bg-yellow-200 transition">
                ⚠️ 中风险场景
              </button>
              <button @click="fillHighRisk" class="px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition">
                🚨 高风险场景
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Result -->
      <div class="lg:col-span-1">
        <!-- Loading State -->
        <div v-if="loading" class="card">
          <div class="flex flex-col items-center justify-center py-12">
            <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mb-4"></div>
            <p class="text-gray-600">正在分析交易...</p>
            <p class="text-sm text-gray-500 mt-2">这可能需要几秒钟</p>
          </div>
        </div>

        <!-- Result Card -->
        <div v-else-if="result" class="card">
          <h3 class="text-lg font-bold text-gray-800 mb-4">审计结果</h3>

          <!-- Risk Level -->
          <div class="text-center mb-6">
            <div class="text-6xl mb-2">{{ getRiskEmoji(result.risk_level) }}</div>
            <h4 class="text-2xl font-bold mb-2" :class="getRiskColorClass(result.risk_level)">
              {{ getRiskLabel(result.risk_level) }}
            </h4>
            <p class="text-gray-600">风险分数: {{ result.risk_score }}</p>
          </div>

          <!-- Decision -->
          <div class="mb-4 p-3 rounded-lg" :class="getDecisionBgClass(result.decision)">
            <p class="text-sm font-medium text-center">
              决策: <span class="font-bold">{{ getDecisionLabel(result.decision) }}</span>
            </p>
          </div>

          <!-- Triggered Rules -->
          <div v-if="result.triggered_rules && result.triggered_rules.length > 0" class="mb-4">
            <p class="text-sm font-medium text-gray-700 mb-2">触发规则:</p>
            <div class="space-y-2 max-h-48 overflow-y-auto">
              <div
                v-for="(rule, index) in result.triggered_rules"
                :key="index"
                class="p-2 bg-gray-50 rounded text-sm"
              >
                <p class="font-medium text-gray-800">{{ rule.rule_name }}</p>
                <p v-if="rule.description" class="text-xs text-gray-600 mt-1">{{ rule.description }}</p>
              </div>
            </div>
          </div>

          <!-- Suggestion -->
          <div v-if="result.suggestion" class="p-3 bg-blue-50 rounded-lg">
            <p class="text-sm font-medium text-blue-800 mb-1">建议:</p>
            <p class="text-xs text-blue-600">{{ result.suggestion }}</p>
          </div>

          <!-- Actions -->
          <div class="mt-4 pt-4 border-t border-gray-200 space-y-2">
            <button
              v-if="result.decision === 'review'"
              @click="createReview"
              class="w-full btn-primary"
            >
              创建人工审核
            </button>
            <button @click="viewDetails" class="w-full btn-secondary">
              查看详细报告
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="card">
          <div class="text-center py-12">
            <span class="text-6xl mb-4 block">🔍</span>
            <p class="text-gray-600">填写交易信息后</p>
            <p class="text-gray-600">开始风险评估</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auditAPI, reviewAPI } from '../services/api'
import { useAuditStore } from '../stores/audit'

const router = useRouter()
const auditStore = useAuditStore()

const loading = ref(false)
const result = ref(null)

const form = ref({
  transaction_id: '',
  user_id: '',
  merchant_id: '',
  amount: 1000,
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

async function handleSubmit() {
  loading.value = true
  result.value = null

  try {
    const response = await auditAPI.auditTransaction(form.value)
    result.value = response.data

    auditStore.addAudit({
      ...form.value,
      risk_level: result.value.risk_level,
      risk_score: result.value.risk_score,
      decision: result.value.decision
    })
  } catch (error) {
    alert('审计失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

async function createReview() {
  try {
    await reviewAPI.createReview({
      transaction_id: form.value.transaction_id,
      priority: result.value.risk_level === 'high' ? 'urgent' : 'normal'
    })
    alert('审核记录已创建')
    router.push('/review/pending')
  } catch (error) {
    alert('创建审核失败: ' + (error.response?.data?.detail || error.message))
  }
}

function viewDetails() {
  // Mock detailed view
  alert('详细报告功能开发中')
}

function fillLowRisk() {
  form.value = {
    transaction_id: 'TXN_LOW_' + Date.now(),
    user_id: 'USER_ALICE',
    merchant_id: 'MERCHANT_AMAZON',
    amount: 500,
    currency: 'USD',
    account_age_days: 730,
    transaction_frequency_1h: 1,
    ip_location_status: 'normal',
    device_status: 'normal',
    kyc_status: 'verified',
    merchant_risk_level: 'low',
    is_blacklisted: false,
    timestamp: new Date().toISOString()
  }
}

function fillMediumRisk() {
  form.value = {
    transaction_id: 'TXN_MED_' + Date.now(),
    user_id: 'USER_BOB',
    merchant_id: 'MERCHANT_UNKNOWN',
    amount: 5000,
    currency: 'USD',
    account_age_days: 30,
    transaction_frequency_1h: 5,
    ip_location_status: 'abnormal',
    device_status: 'normal',
    kyc_status: 'basic_verified',
    merchant_risk_level: 'medium',
    is_blacklisted: false,
    timestamp: new Date().toISOString()
  }
}

function fillHighRisk() {
  form.value = {
    transaction_id: 'TXN_HIGH_' + Date.now(),
    user_id: 'USER_CHARLIE',
    merchant_id: 'MERCHANT_SUSPICIOUS',
    amount: 25000,
    currency: 'USD',
    account_age_days: 3,
    transaction_frequency_1h: 15,
    ip_location_status: 'abnormal',
    device_status: 'abnormal',
    kyc_status: 'unverified',
    merchant_risk_level: 'high',
    is_blacklisted: false,
    timestamp: new Date().toISOString()
  }
}

function getRiskEmoji(level) {
  const emojis = { low: '✅', medium: '⚠️', high: '🚨' }
  return emojis[level] || '⚪'
}

function getRiskLabel(level) {
  const labels = { low: '低风险', medium: '中风险', high: '高风险' }
  return labels[level] || '未知'
}

function getRiskColorClass(level) {
  const classes = { low: 'text-green-600', medium: 'text-yellow-600', high: 'text-red-600' }
  return classes[level] || 'text-gray-600'
}

function getDecisionLabel(decision) {
  const labels = { approve: '批准通过', review: '人工审核', reject: '拒绝交易' }
  return labels[decision] || decision
}

function getDecisionBgClass(decision) {
  const classes = {
    approve: 'bg-green-100 text-green-800',
    review: 'bg-yellow-100 text-yellow-800',
    reject: 'bg-red-100 text-red-800'
  }
  return classes[decision] || 'bg-gray-100 text-gray-800'
}
</script>
