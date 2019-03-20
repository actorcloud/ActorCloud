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
  name: 'pattern-status',

  mixins: [resize],

  props: {
    redraw: {
      type: Boolean,
      default: true,
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
      type: Object,
      required: true,
      default: () => {
        return {
          yDisplay: {
            pattern: [],
            value: [],
          },
        }
      },
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

  /* eslint-disable */
    data() {
      return {
        chart: undefined,
        colors: [
          '#fb7293', '#e7bcf4', '#ffdb5b', '#ff9f7e', '#8277ea',
          '#9fe6b8', '#38a2db', '#fb7293'
        ],
        yAxisMax: Math.max(
          ...this.yDisplay.value) + (this.yDisplay.value[1] - this.yDisplay.value[0]) / 2,
        yAxisMin: Math.min(
          ...this.yDisplay.value) - (this.yDisplay.value[1] - this.yDisplay.value[0]) / 2,
        seriesConfig: [],
      }
    },

    watch: {
      // Redraw: 'drawPatternStatusChart',
      chartData: {
        deep: true,
        handler: 'drawPatternStatusChart',
      },
    },

    methods: {
      setSeries() {
        this.seriesConfig = [
          {
            type: 'scatter',
            smooth: false,
            xAxisIndex: 1,
            yAxisIndex: 0,
          },
          {
            name: this.chartTitle,
            type: 'line',
            symbol: 'none',
            step: 'start',
            z: 100,
            itemStyle: {
              normal: {
                color: '#2fc285',
              },
            },
            lineStyle: {
              normal: {
                width: 3,
              },
            },
            label: {
              normal: {
                show: false,
              },
            },
            data: this.chartData.yData,
          }
        ]
        for (let i = 0; i < this.yDisplay.pattern.length; i++) {
          const patternData = this.yDisplay.value[i] +
            (this.yDisplay.value[1] - this.yDisplay.value[0]) / 2
          this.seriesConfig.push({
            type: 'line',
            name: this.yDisplay.pattern[i],
            symbol: 'none',
            z: this.yDisplay.pattern.length - i + 1,
            lineStyle: {
              normal: {
                width: 0,
                opacity: 0,
              },
            },
            areaStyle: {
              normal: {
                color: this.colors[i % 8],
              },
            },
            data: [...Array(this.chartData.xData.length)].map(() => patternData),
          })
        }
      },
      drawPatternStatusChart() {
        if (this.chart) {
          this.setSeries()
        }
        this.chart = echarts.init(document.getElementById(this.chartId))
        const option = {
          textStyle: {
            color: '#a8a8a8',
            fontSize: 12,
          },
          title: {
            text: this.chartTitle,
            x: '50%',
            y: '0%',
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
            top: '10%',
            bottom: '10%',
            borderWidth: 0,
          },
          xAxis: [{
            type: 'category',
            boundaryGap: 0,
            data: this.chartData.xData,
            splitLine: {
              show: false,
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
            min: this.yAxisMin,
            max: this.yAxisMax,
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
            data: this.yDisplay.pattern,
          }],
          series: this.seriesConfig,
        }
        this.chart.setOption(option)
      },
    },

    created() {
      this.setSeries()
    },

    mounted() {
      this.drawPatternStatusChart()
    },
  }
</script>
