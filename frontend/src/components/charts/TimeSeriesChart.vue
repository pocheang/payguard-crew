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
  GridComponent,
  ToolboxComponent,
  DataZoomComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  ToolboxComponent,
  DataZoomComponent,
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
      text: '交易量时间序列分析',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['总交易量', '成功交易', '失败交易', '成功率'],
      top: 30
    },
    toolbox: {
      feature: {
        saveAsImage: { title: '保存为图片' },
        dataZoom: { title: { zoom: '区域缩放', back: '还原' } },
        restore: { title: '还原' }
      }
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
      data: props.data.map(item => item.time)
    },
    yAxis: [
      {
        type: 'value',
        name: '交易量',
        position: 'left'
      },
      {
        type: 'value',
        name: '成功率(%)',
        position: 'right',
        max: 100
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '总交易量',
        type: 'line',
        data: props.data.map(item => item.total),
        smooth: true,
        itemStyle: {
          color: '#3b82f6'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
            ]
          }
        }
      },
      {
        name: '成功交易',
        type: 'line',
        data: props.data.map(item => item.success),
        smooth: true,
        itemStyle: {
          color: '#22c55e'
        }
      },
      {
        name: '失败交易',
        type: 'line',
        data: props.data.map(item => item.failed),
        smooth: true,
        itemStyle: {
          color: '#ef4444'
        }
      },
      {
        name: '成功率',
        type: 'line',
        yAxisIndex: 1,
        data: props.data.map(item => item.successRate),
        smooth: true,
        itemStyle: {
          color: '#f59e0b'
        },
        lineStyle: {
          width: 3,
          type: 'dashed'
        },
        symbol: 'diamond',
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
