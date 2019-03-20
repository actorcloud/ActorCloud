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
import resize from './mixins/resize'

export default {
  name: 'pie-chart',
  mixins: [resize],

  props: {
    // The left menu is wide and narrow
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
    // Chart data
    chartData: {
      type: Array,
      default: () => [],
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
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)',
        },
        series: [
          {
            type: 'pie',
            radius: '70%',
            center: ['50%', '55%'],
            data: this.chartData,
            itemStyle: {
              emphasis: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
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
