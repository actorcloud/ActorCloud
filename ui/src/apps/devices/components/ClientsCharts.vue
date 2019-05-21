<template>
  <div class="clients-charts-view">
    <el-row class="custom-header">
      <el-col :span="12">
        <el-button
          icon="el-icon-setting"
          class="custom-header__btn shadow-btn"
          size="small"
          round
          :disabled="noData"
          @click="openCustomChart">
          {{ $t('charts.customChart') }}
        </el-button>
      </el-col>
      <el-col :span="12">
        <el-radio-group class="time-unit__radio" v-model="timeUnit" size="small" @change="loadChartData">
          <el-radio-button v-for="(unit, index) in timeUnits" :key="index" :label="unit.value">
            {{ unit.label }}
          </el-radio-button>
        </el-radio-group>
      </el-col>
    </el-row>

    <div v-if="!noData" class="chart-main" v-loading="chartLoading" :element-loading-text="$t('oper.isLoading')">
      <div v-for="(item, index) in chartsData" :key="index">
        <el-card
          v-if="displayDataPoints.includes(item.dataPointID)"
          class="chart-main__card">
          <div slot="header">
            <span>{{ item.chartName }}</span>
          </div>
          <div class="grid-content">
            <!-- Line chart data points -->
            <line-chart
              :chartId="`device-data-chart-${index}`"
              :yTitle="item.chartName"
              :chartData="item.chartData">
            </line-chart>
          </div>
        </el-card>
      </div>
    </div>

    <div v-if="noData" class="no-data">
      <el-row><img src="../assets/images/noData.png" /></el-row>
      <el-row style="color: var(--color-text-lighter); font-size: 30px; margin-top: 20px; margin-bottom: 40px;">
        {{ $t('oper.noData') }}
      </el-row>
    </div>

    <!-- Custom charts dialog -->
    <emq-dialog :title="$t('charts.customChart')" :visible.sync="dialogVisible" @confirm="handleCustomChart">
      <el-popover
        ref="addDevicePopover"
        placement="top-start"
        trigger="hover"
        :content="$t('charts.showDataPoints')">
      </el-popover>
      <i
        class="el-icon-question tips-icon"
        :style="{ left: lang === 'en' ? '135px' : '115px' }"
        v-popover:addDevicePopover>
      </i>
      <el-checkbox-group v-model="dataPoints">
        <el-checkbox
          v-for="(item, index) in chartsData"
          class="data-point__tag"
          :key="index"
          :label="item.dataPointID">
          {{ item.chartName }}
        </el-checkbox>
      </el-checkbox-group>
    </emq-dialog>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import LineChart from '@/components/charts/SingleLine'
import EmqDialog from '@/components/EmqDialog'

export default {
  name: 'clients-charts-view',

  components: {
    LineChart,
    EmqDialog,
  },

  props: {
    url: {
      type: String,
      requried: true,
    },
  },

  data() {
    return {
      timer: 0,
      dialogVisible: false,
      chartLoading: false,
      noData: false,
      // CheckBox binding value
      dataPoints: [],
      // Final displayed data points chart
      displayDataPoints: [],
      timeUnit: '5m',
      chartsData: [],
      timeUnits: [
        { label: '5m', value: '5m' },
        { label: '1h', value: '1h' },
        { label: '6h', value: '6h' },
        { label: '1d', value: '1d' },
        { label: '1w', value: '1w' },
      ],
    }
  },

  computed: {
    lang() {
      return this.$store.state.accounts.lang
    },
  },

  methods: {
    loadChartData() {
      this.noData = false
      this.chartLoading = true
      this.chartsData = []
      httpGet(`${this.url}?timeUnit=${this.timeUnit}`).then((res) => {
        if (res.data.length === 0) {
          this.noData = true
          this.chartLoading = false
          return
        }
        res.data.forEach((item) => {
          this.displayDataPoints.push(item.dataPointID)
          this.chartsData.push({
            chartName: item.chartName,
            dataPointID: item.dataPointID,
            chartData: {
              xData: item.chartData.time,
              yData: item.chartData.value,
            },
          })
        })
        if (this.dataPoints.length > 0) {
          this.displayDataPoints = this.dataPoints.slice()
        }
        this.chartLoading = false
      })
    },

    openCustomChart() {
      this.dataPoints = this.displayDataPoints.slice()
      this.dialogVisible = true
    },

    handleCustomChart() {
      this.displayDataPoints = this.dataPoints.slice()
      this.dialogVisible = false
    },
  },

  created() {
    this.loadChartData()
  },
}
</script>

<style lang="scss">
.clients-charts-view {

  .el-card {
    .el-card__body {
      padding: 20px;
    }
  }

  .chart-main {
    margin-top: 25px;

    .el-card.chart-main__card {
      .el-card__header {
        font-size: 16px;
      }

      .el-card-body {
        padding: 20px;
      }

      .grid-content {
        > div {
          height: 300px;
        }
      }
      color: #929394;
    }
  }

  .emq-dialog {
    .tips-icon {
      position: absolute;
      top: 20px;
      right: 20px;
      width: 10px;
      cursor: pointer;
    }

    .data-point__tag {
      background-color: var(--color-bg-tag);
      padding: 5px 10px;
      border-radius: 14px;
      color: var(--color-text-lighter);
    }
    .el-checkbox__inner {
      border-radius: 50%;
    }
    .el-checkbox__input.is-checked + .el-checkbox__label {
      color: var(--color-text-lighter);
    }
    .el-checkbox__input.is-checked .el-checkbox__inner {
      border-radius: 50%;
    }
  }
}
</style>
