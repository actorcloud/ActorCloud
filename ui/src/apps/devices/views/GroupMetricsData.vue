<template>
  <div class="details-view group-metrics-data-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/devices/groups">分组</el-breadcrumb-item>
        <el-breadcrumb-item>聚合数据</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div class="detail-tabs">
      <group-detail-tabs></group-detail-tabs>
    </div>

    <div v-if="!noData">
      <div v-if="chartsMetricsData.length>0" class="time-chart-head">
        <el-row style="line-height: 32px;"></el-row>
        <el-radio-group class="time-unit__radio" v-model="timeUnit" size="small">
          <el-radio-button v-for="(unit, index) in timeUnits" :key="index" :label="unit.value">
            {{ unit.label }}
          </el-radio-button>
        </el-radio-group>
      </div>
      <div v-loading="chartLoading" element-loading-text="数据加载中...">
        <el-card
          v-for="(item, index) in chartsMetricsData"
          style="border-top: 2px solid #8fa4e8;"
          :key="index">
          <div slot="header" style="color: #747576; font-size: 16px;">
            <span>{{ item.displayName }}</span>
          </div>
          <el-row>
            <div class="grid-content">
              <!-- Line -->
              <line-chart
                v-if="item.chartType === 1"
                :redraw="leftWide"
                :chartId="`group-metrics-data-chart-${index}`"
                :yTitle="item.displayName"
                :leftbar="leftbar"
                :markLineData="markLine"
                :chartData="item.data">
              </line-chart>
                <!-- Bar -->
              <bar-chart
                v-if="item.chartType === 2"
                :redraw="leftWide"
                :chartId="`group-metrics-data-chart-${index}`"
                :yTitle="item.displayName"
                :leftbar="leftbar"
                :markLineData="markLine"
                :chartData="item.data">
              </bar-chart>
              <!-- Pie -->
              <pie-chart
                v-if="item.chartType === 3"
                :redraw="leftWide"
                :chartId="`group-metrics-data-chart-${index}`"
                :leftbar="leftbar"
                :chartData="item.data">
              </pie-chart>
            </div>
          </el-row>
        </el-card>
      </div>
    </div>

    <div v-if="noData" class="no-data">
      <el-row><img src="../assets/images/noData.png" /></el-row>
      <el-row style="color: var(--color-text-lighter); font-size: 30px; margin-top: 20px; margin-bottom: 40px;">
        该分组所属产品未定义聚合指标
      </el-row>
    </div>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import LineChart from '@/components/charts/SingleLine'
import BarChart from '@/components/charts/Bar'
import PieChart from '@/components/charts/Pie'
import GroupDetailTabs from '../components/GroupDetailTabs'

export default {
  name: 'group-metrics-data-view',

  components: {
    EmqDetailsPageHead,
    GroupDetailTabs,
    LineChart,
    BarChart,
    PieChart,
  },

  data() {
    return {
      chartLoading: false,
      leftWide: true,
      noData: false,
      timeUnits: [
        { label: '时', value: 'hour' },
        { label: '日', value: 'day' },
        { label: '月', value: 'month' },
      ],
      timeUnit: 'hour',
      markLine: [{ type: 'average', name: '平均值' }],
      chartsMetricsData: [],
    }
  },

  computed: {
    leftbar() {
      return this.$store.state.base.leftbar.width
    },
  },

  watch: {
    timeUnit: 'loadMetricsData',
  },

  methods: {
    loadMetricsData() {
      this.chartLoading = true
      this.chartsMetricsData = []
      httpGet(`/groups/${this.$route.params.id}/metrics_data?timeUnit=${this.timeUnit}`)
        .then((res) => {
          if (!res.data.length) {
            this.noData = true
          } else {
            res.data.forEach((item) => {
              this.chartsMetricsData.push({
                chartType: item.chartType,
                displayName: item.metricName,
                data: {
                  xData: item.metricData.time,
                  yData: item.metricData.value,
                },
              })
            })
          }
        })
      this.chartLoading = false
    },
  },

  created() {
    this.loadMetricsData()
  },
  mounted() {
    this.$store.watch((state) => {
      this.leftWide = state.base.leftbar.wide
    })
  },
}
</script>


<style lang="scss">
.group-metrics-data-view {
  .el-card {
    margin-top: 20px;
    margin-bottom: 0px;
  }
  .el-card__body {
    padding: 10px 15px !important;
  }
  .grid-content {
    > div {
      height: 300px;
    }
  }
  .no-data {
    text-align: center;
    margin-top: 40px;
    img {
      width: 30%;
      max-width: 440px;
      margin: 10px;
    }
  }
  .time-chart-head {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    margin-bottom: 10px;
  }
}
</style>
