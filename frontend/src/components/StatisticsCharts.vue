<template>
  <div class="statistics-charts">
    <!-- 风险趋势图 -->
    <Card title="风险趋势分析" class="mb-4">
      <Chart :option="riskTrendOption" height="300px" />
    </Card>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <!-- 风险等级分布 -->
      <Card title="风险等级分布">
        <Chart :option="riskDistributionOption" height="280px" />
      </Card>

      <!-- 审核状态分布 -->
      <Card title="审核状态分布">
        <Chart :option="reviewStatusOption" height="280px" />
      </Card>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 审核人工作量 -->
      <Card title="审核人工作量">
        <Chart :option="workloadOption" height="280px" />
      </Card>

      <!-- 交易量趋势 -->
      <Card title="交易量趋势">
        <Chart :option="transactionTrendOption" height="280px" />
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Chart from '../components/Chart.vue'
import Card from '../components/Card.vue'
import { auditService } from '../services/audit'

const stats = ref(null)
const loading = ref(false)

// 风险趋势图配置
const riskTrendOption = computed(() => ({
  title: {
    text: '近7天风险趋势',
    left: 'center',
    textStyle: { fontSize: 14 }
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['低风险', '中风险', '高风险'],
    bottom: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: getLast7Days(),
    boundaryGap: false
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '低风险',
      type: 'line',
      smooth: true,
      data: [120, 132, 101, 134, 90, 230, 210],
      itemStyle: { color: '#10b981' }
    },
    {
      name: '中风险',
      type: 'line',
      smooth: true,
      data: [220, 182, 191, 234, 290, 330, 310],
      itemStyle: { color: '#f59e0b' }
    },
    {
      name: '高风险',
      type: 'line',
      smooth: true,
      data: [150, 232, 201, 154, 190, 330, 410],
      itemStyle: { color: '#ef4444' }
    }
  ]
}))

// 风险等级分布饼图
const riskDistributionOption = computed(() => ({
  title: {
    text: '风险等级占比',
    left: 'center',
    textStyle: { fontSize: 14 }
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center'
  },
  series: [
    {
      name: '风险等级',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 1048, name: '低风险', itemStyle: { color: '#10b981' } },
        { value: 735, name: '中风险', itemStyle: { color: '#f59e0b' } },
        { value: 580, name: '高风险', itemStyle: { color: '#ef4444' } }
      ]
    }
  ]
}))

// 审核状态分布柱状图
const reviewStatusOption = computed(() => ({
  title: {
    text: '审核状态统计',
    left: 'center',
    textStyle: { fontSize: 14 }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['待审核', '审核中', '已通过', '已拒绝', '已升级']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '数量',
      type: 'bar',
      data: [
        { value: 320, itemStyle: { color: '#3b82f6' } },
        { value: 150, itemStyle: { color: '#f59e0b' } },
        { value: 890, itemStyle: { color: '#10b981' } },
        { value: 120, itemStyle: { color: '#ef4444' } },
        { value: 45, itemStyle: { color: '#8b5cf6' } }
      ],
      barWidth: '50%'
    }
  ]
}))

// 审核人工作量
const workloadOption = computed(() => ({
  title: {
    text: '审核人工作量',
    left: 'center',
    textStyle: { fontSize: 14 }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['待审核', '审核中'],
    bottom: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['张三', '李四', '王五', '赵六']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '待审核',
      type: 'bar',
      stack: 'total',
      data: [5, 3, 7, 2],
      itemStyle: { color: '#3b82f6' }
    },
    {
      name: '审核中',
      type: 'bar',
      stack: 'total',
      data: [3, 2, 4, 1],
      itemStyle: { color: '#f59e0b' }
    }
  ]
}))

// 交易量趋势
const transactionTrendOption = computed(() => ({
  title: {
    text: '交易量趋势',
    left: 'center',
    textStyle: { fontSize: 14 }
  },
  tooltip: {
    trigger: 'axis'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: getLast7Days(),
    boundaryGap: false
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '交易量',
      type: 'line',
      smooth: true,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(59, 130, 246, 0.5)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.1)' }
          ]
        }
      },
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      itemStyle: { color: '#3b82f6' }
    }
  ]
}))

// 获取最近7天日期
function getLast7Days() {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    days.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }
  return days
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 这里应该调用实际的API
    // const response = await auditService.getStatistics()
    // stats.value = response.data
    console.log('Loading statistics data...')
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.statistics-charts {
  padding: 1rem;
}
</style>
