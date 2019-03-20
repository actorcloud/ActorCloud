<template>
  <div :id="chartId">
  </div>
</template>


<script>
import echarts from 'echarts/lib/echarts'
import 'echarts/lib/chart/pie'
import 'echarts/lib/component/grid'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'

import { hex2rgba } from '@/utils/chartUtils'
import resize from './mixins/resize'

export default {
  name: 'pie-doughnut-chart',

  mixins: [resize],

  props: {
    // DOM container id
    chartId: {
      type: String,
      required: true,
    },
    // The left menu is wide and narrow
    leftbar: {
      type: String,
      default: 'wide',
    },
    // Whether to display title
    showTitle: {
      type: Boolean,
      default: false,
    },
    // Chart title
    chartTitle: {
      type: String,
      default: '',
    },
    // Chart name
    chartName: {
      type: String,
      required: true,
    },
    // Chart colors
    colors: {
      type: Array,
      default: () => {
        return ['#23c88e', '#A57EBC', '#F38ABC']
      },
    },
    // chart data
    chartData: {
      type: Array,
      default: () => {
        return []
      },
    },
  },

  data() {
    return {
      chart: undefined,
    }
  },

  watch: {
    chartData: {
      deep: true,
      handler: 'drawChart',
    },
  },

  methods: {
    drawChart() {
      this.chart = echarts.init(document.getElementById(this.chartId))
      const chartData = this.getStyleData()
      const option = {
        color: this.colors,
        title: {
          show: this.showTitle,
          text: this.chartTitle,
          x: 'center',
          y: 'center',
          textStyle: {
            fontWeight: 'normal',
            color: this.colors[0],
            fontSize: '30',
          },
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)',
          confine: true,
        },
        series: [
          {
            name: this.chartName,
            type: 'pie',
            radius: ['80%', '85%'],
            avoidLabelOverlap: false,
            hoverOffset: 6,
            label: {
              normal: {
                show: false,
                position: 'center',
              },
              emphasis: {
                show: false,
              },
            },
            labelLine: {
              normal: {
                show: false,
              },
            },
            data: chartData,
          },
        ],
      }
      this.chart.setOption(option)
    },

    getStyleData() {
      const { valueSum, count } = this.getDataSize()
      const pieSize = valueSum * 0.01
      const chartData = []

      this.chartData.forEach((data, i) => {
        const color = this.colors[i]
        const shadowColor = hex2rgba(color, 0.4)
        data.itemStyle = {
          normal: {
            borderWidth: 5,
            borderRadius: 5,
            shadowOffsetX: 2,
            shadowOffsetY: 12,
            shadowBlur: 12,
            shadowColor,
            color,
          },
        }
        chartData.push(data)
        if (count > 1 && data.value > 0) {
          chartData.push({
            value: pieSize,
            name: '',
            itemStyle: {
              normal: {
                label: {
                  show: false,
                },
                labelLine: {
                  show: false,
                },
                color: 'rgba(0, 0, 0, 0)',
                borderColor: 'rgba(0, 0, 0, 0)',
                borderWidth: 0,
              },
            },
          })
        }
      })
      return chartData
    },

    getDataSize() {
      let valueSum = 0
      let count = 0
      this.chartData.forEach(({ value }) => {
        valueSum += value
        if (value > 0) {
          count += 1
        }
      })
      return { valueSum, count }
    },
  },

  mounted() {
    this.drawChart()
  },
}
</script>
