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
import resize from './mixins/resize'

export default {
  name: 'single-line-chart',
  mixins: [resize],

  props: {
    // The left menu is wide and narrow
    leftbar: {
      type: String,
      default: 'wide',
    },
    // Delay execution time per second
    delayTime: {
      type: Number,
      default: 0,
    },
    // DOM container id
    chartId: {
      type: String,
      required: true,
    },
    // Chart title
    chartTitle: {
      type: String,
      default: '',
    },
    // Whether it is a smooth graph
    smooth: {
      type: Boolean,
      default: false,
    },
    // Whether it is a ladder diagram and ladder diagram type
    stepType: {
      type: String,
      default: '',
    },
    // Chart line color
    chartColor: {
      type: Array,
      default: () => {
        return ['#23c88e']
      },
    },
    // Chart left margin
    gridLeft: {
      type: String,
      default: '3%',
    },
    // Chart right margin
    gridRight: {
      type: String,
      default: '5%',
    },
    // Chart mark line, as to mark an average
    markLineData: {
      type: Array,
      default: () => {
        return []
      },
      // [{ type: 'average', name: '平均值' }],
    },
    // Chart data
    chartData: {
      type: Object,
      default: () => {
        return {
          chartData: {
            xData: [],
            yData: [],
          },
        }
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
      const option = {
        color: this.chartColor,
        title: {
          text: this.chartTitle,
          x: '50%',
          y: '0',
          textAlign: 'center',
          textStyle: {
            color: '#a8a8a8',
            fontSize: 12,
          },
        },
        tooltip: {
          trigger: 'axis',
        },
        grid: {
          left: this.gridLeft,
          right: this.gridRight,
          bottom: '5%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.chartData.xData,
          axisLine: {
            lineStyle: {
              color: '#a8a8a8',
            },
          },
        },
        yAxis: {
          type: 'value',
          minInterval: 1,
          axisLine: {
            lineStyle: {
              color: '#a8a8a8',
            },
          },
          splitLine: {
            show: false,
          },
        },
        series: [
          {
            name: this.chartTitle,
            type: 'line',
            symbolSize: 5,
            data: this.chartData.yData,
            smooth: this.smooth,
            step: this.stepType,
            itemStyle: {
              normal: {
                areaStyle: {
                  type: 'default',
                },
              },
            },
            markPoint: {
              data: [
                {
                  type: 'max',
                  name: '最大值',
                }, {
                  type: 'min',
                  name: '最小值',
                },
              ],
            },
            markLine: {
              data: this.markLineData,
            },
          },
        ],
      }
      this.chart.setOption(option)
    },
    // delay
    delayDo() {
      setTimeout(this.drawChart, this.delayTime)
    },
  },

  mounted() {
    this.delayDo()
  },
}
</script>
