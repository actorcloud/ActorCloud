<template>
  <div :id="chartId">
  </div>
</template>


<script>
import echarts from 'echarts/lib/echarts'
import 'echarts/lib/chart/line'
import 'echarts/lib/component/grid'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'
import 'echarts/lib/component/markLine'
import 'echarts/lib/component/markPoint'

import { hex2rgba } from '@/utils/chartUtils'
import resize from './mixins/resize'

export default {
  name: 'line-chart',

  mixins: [resize],

  props: {
    // DOM container id
    chartId: {
      type: String,
      required: true,
    },
    // The menu on the left is wide and narrow
    leftbar: {
      type: String,
      default: 'wide',
    },
    // Whether it is a smooth graph
    smooth: {
      type: [Boolean, Number],
      default: false,
    },
    // Whether to display value points
    showSymbol: {
      type: Boolean,
      default: true,
    },
    // Whether it is a ladder diagram and ladder diagram type
    stepType: {
      type: String,
      default: '',
    },
    // Y-coordinate title
    yTitle: {
      type: Array,
      default: () => {
        return ['']
      },
    },
    // Chart line color
    chartColor: {
      type: Array,
      default: () => {
        return ['#23c88e']
      },
    },
    axisColor: {
      type: Object,
      default: () => ({}),
    },
    // Chart data
    chartData: {
      type: Array,
      default: () => {
        return [
          {
            xData: [],
            yData: [],
          },
        ]
      },
    },
  },

  data() {
    return {
      seriesConfig: [],
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
    setSeriesConfig() {
      this.seriesConfig = []
      for (let i = 0; i < this.yTitle.length; i += 1) {
        const shadowColor = hex2rgba(this.chartColor[i], 0.4)
        this.seriesConfig.push({
          name: this.yTitle[i],
          type: 'line',
          symbolSize: 5,
          showSymbol: this.showSymbol,
          data: this.chartData[i].yData,
          smooth: this.smooth,
          step: this.stepType,
          lineStyle: {
            normal: {
              shadowColor,
              width: 2,
              shadowBlur: 8,
              shadowOffsetY: 10,
            },
          },
          markLine: {
            data: this.markLineData,
          },
        })
      }
    },
    drawChart() {
      this.setSeriesConfig()
      this.chart = echarts.init(document.getElementById(this.chartId))
      const option = {
        color: this.chartColor,
        tooltip: {
          trigger: 'axis',
          confine: true,
        },
        grid: {
          left: '2%',
          right: '2%',
          top: '3%',
          bottom: '3%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.chartData[0].xData,
          axisLine: {
            lineStyle: {
              color: this.axisColor.colorAxisLine,
            },
          },
          axisLabel: {
            textStyle: {
              color: this.axisColor.colorAxisLabel,
            },
          },
        },
        yAxis: {
          type: 'value',
          minInterval: 1,
          axisLine: {
            lineStyle: {
              color: this.axisColor.colorAxisLine,
            },
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: this.axisColor.colorSplitLine,
            },
          },
          axisLabel: {
            textStyle: {
              color: this.axisColor.colorAxisLabel,
            },
          },
        },
        series: this.seriesConfig,
      }
      this.chart.setOption(option)
    },
    // Redraw the echarts charts
    reDrawEchart() {
      // Destroy
      this.chart.dispose()
      // Redraw the chart
      this.chart = undefined
      this.drawChart()
    },
  },

  mounted() {
    this.drawChart()
  },
}
</script>
