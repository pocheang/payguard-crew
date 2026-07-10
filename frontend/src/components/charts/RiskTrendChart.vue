<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { init, use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
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
    default: '400px'
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = init(chartRef.value)

  const option = {
    title: {
      text: '风险趋势分析',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['高风险', '中风险', '低风险', '平均风险分'],
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
      boundaryGap: false,
      data: props.data.map(item => item.date)
    },
    yAxis: [
      {
        type: 'value',
        name: '交易数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '风险分',
        position: 'right',
        max: 100
      }
    ],
    series: [
      {
        name: '高风险',
        type: 'line',
        stack: 'Total',
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(239, 68, 68, 0.4)' },
              { offset: 1, color: 'rgba(239, 68, 68, 0.1)' }
            ]
          }
        },
        emphasis: {
          focus: 'series'
        },
        data: props.data.map(item => item.high),
        itemStyle: {
          color: '#ef4444'
        }
      },
      {
        name: '中风险',
        type: 'line',
        stack: 'Total',
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(251, 146, 60, 0.4)' },
              { offset: 1, color: 'rgba(251, 146, 60, 0.1)' }
            ]
          }
        },
        emphasis: {
          focus: 'series'
        },
        data: props.data.map(item => item.medium),
        itemStyle: {
          color: '#fb923c'
        }
      },
      {
        name: '低风险',
        type: 'line',
        stack: 'Total',
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(34, 197, 94, 0.4)' },
              { offset: 1, color: 'rgba(34, 197, 94, 0.1)' }
            ]
          }
        },
        emphasis: {
          focus: 'series'
        },
        data: props.data.map(item => item.low),
        itemStyle: {
          color: '#22c55e'
        }
      },
      {
        name: '平均风险分',
        type: 'line',
        yAxisIndex: 1,
        data: props.data.map(item => item.avgScore),
        itemStyle: {
          color: '#3b82f6'
        },
        lineStyle: {
          width: 3
        },
        symbol: 'circle',
        symbolSize: 6
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
