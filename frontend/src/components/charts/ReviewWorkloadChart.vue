<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { init, use } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
  LineChart,
  CanvasRenderer
])

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  height: {
    type: String,
    default: '350px'
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = init(chartRef.value)

  const option = {
    title: {
      text: '审核员工作量统计',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(item => {
          result += item.marker + ' ' + item.seriesName + ': ' + item.value
          if (item.seriesName === '批准率') {
            result += '%'
          }
          result += '<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['总审核数', '已批准', '已拒绝', '批准率'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.data.map(item => item.reviewer),
      axisLabel: {
        interval: 0,
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '审核数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '批准率(%)',
        position: 'right',
        max: 100
      }
    ],
    series: [
      {
        name: '总审核数',
        type: 'bar',
        data: props.data.map(item => item.total_reviews),
        itemStyle: {
          color: '#3b82f6'
        }
      },
      {
        name: '已批准',
        type: 'bar',
        data: props.data.map(item => item.approved),
        itemStyle: {
          color: '#22c55e'
        }
      },
      {
        name: '已拒绝',
        type: 'bar',
        data: props.data.map(item => item.rejected),
        itemStyle: {
          color: '#ef4444'
        }
      },
      {
        name: '批准率',
        type: 'line',
        yAxisIndex: 1,
        data: props.data.map(item => item.approval_rate),
        itemStyle: {
          color: '#f59e0b'
        },
        lineStyle: {
          width: 2
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }

  chartInstance.setOption(option)
}

const resize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chartInstance?.dispose()
})

watch(() => props.data, () => {
  initChart()
}, { deep: true })
</script>
