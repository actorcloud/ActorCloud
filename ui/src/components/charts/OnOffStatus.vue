<template>
  <div :id="chartId">
  </div>
</template>


<script>
import echarts from 'echarts/lib/echarts'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/scatter'
import 'echarts/lib/component/grid'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'
import resize from './mixins/resize'

export default {
  name: 'on-off-status',

  mixins: [resize],

  props: {
    redraw: {
      type: Boolean,
      default: true,
    },
    delayTime: {
      type: Number,
      default: 0,
    },
    chartId: {
      type: String,
      required: true,
    },
    chartTitle: {
      type: String,
      required: true,
    },
    yDisplay: {
      type: Array,
      required: true,
    },
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
      handler: 'drawOnOffStatusChart',
    },
  },

  methods: {
    drawOnOffStatusChart() {
      this.chart = echarts.init(document.getElementById(this.chartId))
      const option = {
        textStyle: {
          color: '#a8a8a8',
          fontSize: 12,
        },
        title: {
          text: this.chartTitle,
          x: '50%',
          y: '4%',
          textAlign: 'center',
          textStyle: {
            color: '#a8a8a8',
            fontSize: 12,
          },
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}',
        },
        grid: {
          left: '4%',
          right: '4%',
          bottom: '5%',
          containLabel: true,
        },
        xAxis: [{
          type: 'category',
          data: this.chartData.xData,
          splitLine: {
            show: false,
          },
          axisLine: {
            lineStyle: {
              color: '#a8a8a8',
            },
          },
        }, {
          type: 'value',
          gridIndex: 0,
          axisLabel: {
            show: false,
          },
          splitLine: {
            show: false,
          },
          axisTick: {
            show: false,
          },
        }],
        yAxis: [{
          interval: 15,
          show: false,
          min: -0.5,
          max: 1.5,
          position: 'right',
          splitLine: {
            show: false,
          },
          axisLabel: {
            show: true,
          },
        }, {
          type: 'category',
          position: 'left',
          axisLabel: {
            show: true,
          },
          splitLine: {
            show: false,
          },
          axisLine: {
            lineStyle: {
              color: '#a8a8a8',
            },
          },
          data: this.yDisplay,
        }],
        series: [{
          type: 'scatter',
          smooth: false,
          xAxisIndex: 1,
          yAxisIndex: 0,
        }, {
          type: 'line',
          name: this.yDisplay[0],
          symbol: 'none',
          z: 2,
          lineStyle: {
            normal: {
              width: 0,
              opacity: 0,
            },
          },
          areaStyle: {
            normal: {
              color: 'red',
            },
          },
          data: [...Array(this.chartData.xData.length)].map(() => 0.5),
        }, {
          type: 'line',
          name: this.yDisplay[1],
          symbol: 'none',
          z: 0,
          lineStyle: {
            normal: {
              width: 0,
              opacity: 0,
            },
          },
          areaStyle: {
            normal: {
              color: 'green',
            },
          },
          data: [...Array(this.chartData.xData.length)].map(() => 1.5),
        }, {
          name: this.chartTitle,
          type: 'line',
          symbol: 'none',
          step: 'start',
          zleve: 4,
          itemStyle: {
            normal: {
              color: '#000',
            },
          },
          lineStyle: {
            normal: {
              width: 3,
            },
          },
          label: {
            normal: {
              show: true,
            },
          },
          data: this.chartData.yData,
        }],
      }
      this.chart.setOption(option)
    },
    // Delay
    delayDo() {
      setTimeout(this.drawOnOffStatusChart, this.delayTime)
    },
  },

  mounted() {
    this.delayDo()
  },
}
</script>
