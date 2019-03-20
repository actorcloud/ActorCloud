<template>
  <div :id="chartId">
  </div>
</template>


<script>
import echarts from 'echarts/lib/echarts'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/grid'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'
import resize from './mixins/resize'

export default {
  name: 'bar-chart',
  mixins: [resize],

  props: {
    // The menu on the left is wide and narrow
    leftbar: {
      type: String,
      default: 'wide',
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
    // chart fill color
    chartColor: {
      type: Array,
      default: () => {
        return ['#23c88e']
      },
    },
    // chart data
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
          y: '4%',
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
          left: '3%',
          right: '4%',
          bottom: '5%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
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
            type: 'bar',
            data: this.chartData.yData,
          },
        ],
      }
      this.chart.setOption(option)
    },
  },

  mounted() {
    this.drawChart()
  },
}
</script>
