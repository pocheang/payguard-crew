// 应用配置
export const config = {
  // API配置
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  apiTimeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  requestTimeout: parseInt(import.meta.env.VITE_REQUEST_TIMEOUT) || 60000,

  // 应用信息
  appName: import.meta.env.VITE_APP_NAME || 'PayGuard',
  appVersion: import.meta.env.VITE_APP_VERSION || '0.2.0',

  // 功能开关
  enableMock: import.meta.env.VITE_ENABLE_MOCK === 'true',
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',

  // Token配置
  tokenKey: 'payguard_token',
  refreshTokenKey: 'payguard_refresh_token',
  userKey: 'payguard_user',

  // 分页配置
  defaultPageSize: 10,
  pageSizeOptions: [10, 20, 50, 100],

  // 风险等级配置
  riskLevels: {
    low: { label: '低风险', color: 'success', value: 'low' },
    medium: { label: '中风险', color: 'warning', value: 'medium' },
    high: { label: '高风险', color: 'danger', value: 'high' }
  },

  // 决策类型配置
  decisions: {
    approve: { label: '通过', color: 'success', value: 'approve' },
    reject: { label: '拒绝', color: 'danger', value: 'reject' },
    manual_review: { label: '人工审核', color: 'warning', value: 'manual_review' }
  },

  // 审核状态配置
  reviewStatus: {
    pending: { label: '待审核', color: 'warning', value: 'pending' },
    approved: { label: '已批准', color: 'success', value: 'approved' },
    rejected: { label: '已拒绝', color: 'danger', value: 'rejected' },
    escalated: { label: '已升级', color: 'info', value: 'escalated' }
  }
}

export default config
