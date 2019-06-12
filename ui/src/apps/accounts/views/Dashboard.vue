<template>
  <div class="dashboard-view">
    <el-row class="count-warpper" :gutter="28">

      <el-col :span="6">
        <router-link :to="`${has('GET,/devices') ? '/devices/devices' : '/' }`">
          <el-card class="box-card">
            <el-row class="count-card">
              <el-col :span="12">
                <i class="iconfont icon-devices-dashboard"></i>
              </el-col>
              <el-col class="count-desc" :span="12">
                <li>{{ $t('dashboard.devicesCount') }}</li>
                <li class="count-text">
                  <span id="device-count-text2"></span>
                </li>
              </el-col>
            </el-row>
          </el-card>
        </router-link>
      </el-col>

      <el-col :span="6">
        <router-link :to="`${has('GET,/devices') ? '/devices/gateways' : '/' }`">
          <el-card class="box-card">
            <el-row class="count-card">
              <el-col :span="12">
                <i class="iconfont icon-gateways"></i>
              </el-col>
              <el-col class="count-desc" :span="12">
                <li>{{ $t('dashboard.gatewaysCount') }}</li>
                <li>
                  <span class="count-text" id="gateway-count-text2"></span>
                </li>
              </el-col>
            </el-row>
          </el-card>
        </router-link>
      </el-col>

      <el-col :span="6">
        <router-link :to="`${has('GET,/products') ? '/products' : '/'}`" tag="div">
          <el-card class="box-card">
            <el-row class="count-card">
              <el-col :span="12">
                <i class="iconfont icon-products"></i>
              </el-col>
              <el-col class="count-desc" :span="12">
                <li>{{ $t('dashboard.productsCount') }}</li>
                <li class="count-text">
                  <span id="product-count-text2"></span>
                </li>
              </el-col>
            </el-row>
          </el-card>
        </router-link>
      </el-col>

      <el-col :span="6">
        <router-link :to="`${has('GET,/groups') ? '/devices/groups' : '/' }`">
          <el-card class="box-card">
            <el-row class="count-card">
              <el-col :span="12">
                <i class="iconfont icon-groups"></i>
              </el-col>
              <el-col class="count-desc" :span="12">
                <li>{{ $t('dashboard.groupsCount') }}</li>
                <li class="count-text">
                  <span id="group-count-text2"></span>
                </li>
              </el-col>
            </el-row>
          </el-card>
        </router-link>
      </el-col>

    </el-row>

    <el-row class="metrics-charts" :gutter="28">
      <!-- Current devices online status -->
      <el-col class="online-situation" :span="12">
        <el-card class="box-card">
          <template slot="header">
            <div class="header--title">{{ $t('dashboard.online') }}</div>
            <!-- Total number of devices -->
            <div class="total-count">
              <span>{{ $t('dashboard.devicesNum') }}</span>
              <span class="count-text">{{ currentCount.status.total }}</span>
            </div>
          </template>
          <el-row style="margin-top: 0;" type="flex" align="middle">
            <el-col :span="12" :lg="14">
              <pie-doughnut-chart
                chartId="device-online-situation"
                :chartName="$t('dashboard.online')"
                :colors="[colorGreen, colorPink, colorPurple]"
                :chartData="onlineSituationData">
              </pie-doughnut-chart>
            </el-col>
            <el-col class="describe" :span="12" :lg="10">
              <li>
                <span></span>
                {{ $t('dashboard.onlineNum') }}：{{ currentCount.status.online }}
              </li>
              <li>
                <span></span>
                {{ $t('dashboard.offlineNum') }}：{{ currentCount.status.offline }}
              </li>
              <li>
                <span></span>
                {{ $t('dashboard.sleepNum') }}：{{ currentCount.status.sleep }}
              </li>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- Last 24 hours connection -->
      <el-col class="breakdown-situation" :span="12">
        <el-card class="box-card">
          <template slot="header">
            <div class="header--title">{{ $t('dashboard.connectState') }}</div>
            <div class="total-count">
              <span>{{ $t('dashboard.connectTotal') }}</span>
              <span class="count-text">{{ currentCount.connect.total }}</span>
            </div>
          </template>
          <el-row style="margin-top: 0;" type="flex" align="middle">
            <el-col :span="12" :lg="14">
              <pie-doughnut-chart
                chartId="device-breakdown-situation"
                :chartName="$t('dashboard.connectState')"
                :colors="[colorPink, colorGreen]"
                :chartData="breakdownSituationData">
              </pie-doughnut-chart>
            </el-col>
            <el-col class="describe" :span="12" :lg="10">
              <li>
                <span></span>
                {{ $t('dashboard.connectFailure') }}：{{ currentCount.connect.failed }}
              </li>
              <li>
                <span></span>
                {{ $t('dashboard.connectSuccess') }}：{{ currentCount.connect.success }}
              </li>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- Total number of devices -->
    <el-row class="metrics-charts">
      <el-card class="box-card">
        <template slot="header">
          <span>{{ $t('dashboard.devicesNum') }}</span>
          <el-radio-group v-model="totalTimeUnit" size="mini" change="loadData">
            <el-radio-button v-for="(unit, index) in timeUnits" :key="index" :label="unit.value">
              {{ unit.label }}
            </el-radio-button>
          </el-radio-group>
        </template>
        <line-chart
          ref="deviceLineChart"
          chartId="total-count-chart"
          :yTitle="[$t('dashboard.devicesNum')]"
          :chartColor="[colorGreen]"
          :smooth="0.8"
          :showSymbol="false"
          :leftbar="leftbar"
          :chartData="totalCountChartData"
          :axisColor="axisColor">
        </line-chart>
      </el-card>
    </el-row>

    <!-- Message count -->
    <el-row class="metrics-charts line-chart">
      <el-card class="box-card">
        <template slot="header">
          <div class="header--title">{{ $t('dashboard.message') }}</div>
          <el-radio-group v-model="eventMessageCountTimeUnit" size="mini" change="loadData">
            <el-radio-button v-for="(unit, index) in timeUnits" :key="index" :label="unit.value">
              {{ unit.label }}
            </el-radio-button>
          </el-radio-group>
        </template>
        <line-chart
          ref="messageLineChart"
          chartId="event-message-count-chart"
          :yTitle="[
            $t('dashboard.login'),
            $t('dashboard.publish'),
            $t('dashboard.receive'),
            $t('dashboard.subscribe'),
            $t('dashboard.unsubscribe'),
          ]"
          :chartColor="[colorGreen, colorPink, '#8199F3', colorPurple, '#EFC044']"
          :smooth="0.6"
          :showSymbol="false"
          :delayTime="1000"
          :leftbar="leftbar"
          :chartData="eventMessageCountChartData"
          :axisColor="axisColor">
        </line-chart>
        <div class="describe event-message-count">
          <li class="login">
            <span></span>
            {{ $t('dashboard.login') }}
          </li>
          <li class="publish">
            <span></span>
            {{ $t('dashboard.publish') }}
          </li>
          <li class="receive">
            <span></span>
            {{ $t('dashboard.receive') }}
          </li>
          <li class="subscribe">
            <span></span>
            {{ $t('dashboard.subscribe') }}
          </li>
          <li class="unsubscribe">
            <span></span>
            {{ $t('dashboard.unsubscribe') }}
          </li>
        </div>
      </el-card>
    </el-row>

    <!-- Traffic Statistics -->
    <el-row class="metrics-charts line-chart">
      <el-card class="box-card">
        <template slot="header">
          <div class="header--title">{{ $t('dashboard.traffic') }}（KB）</div>
          <el-radio-group v-model="dataTrafficTimeUnit" size="mini" change="loadData">
            <el-radio-button v-for="(unit, index) in timeUnits" :key="index" :label="unit.value">
              {{ unit.label }}
            </el-radio-button>
          </el-radio-group>
        </template>
        <line-chart
          ref="flowLineChart"
          chartId="data-traffic-chart"
          :yTitle="[
            $t('dashboard.login'),
            $t('dashboard.publish'),
            $t('dashboard.receive'),
            $t('dashboard.subscribe'),
            $t('dashboard.unsubscribe'),
          ]"
          :chartColor="[colorGreen, colorPink, '#8199F3', colorPurple, '#EFC044']"
          :smooth="true"
          :showSymbol="false"
          :delayTime="1000"
          :leftbar="leftbar"
          :chartData="dataTrafficChartData"
          :axisColor="axisColor">
        </line-chart>
        <div class="describe event-data-traffic">
          <li class="login">
            <span></span>
            {{ $t('dashboard.login') }}
          </li>
          <li class="publish">
            <span></span>
            {{ $t('dashboard.publish') }}
          </li>
          <li class="receive">
            <span></span>
            {{ $t('dashboard.receive') }}
          </li>
          <li class="subscribe">
            <span></span>
            {{ $t('dashboard.subscribe') }}
          </li>
          <li class="unsubscribe">
            <span></span>
            {{ $t('dashboard.unsubscribe') }}
          </li>
        </div>
      </el-card>
    </el-row>

    <!-- <el-row>
      <el-card class="box-card">
        <div slot="header">
          <span>设备在线情况</span>
          <el-radio-group v-model="onlineTimeUnit" size="mini" change="loadData">
            <el-radio-button v-for="(unit, index) in timeUnits" :key="index" :label="unit.value">
              {{ unit.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
        <line-chart
          chartId="online-situation-chart"
          :yTitle="['在线设备数', '离线设备数', '休眠设备数']"
          :chartColor="['#23c88e', '#ff7956', '#ffc74a']"
          :smooth="true"
          :leftbar="leftbar"
          :chartData="onlineSituationChartData">
        </line-chart>
      </el-card>
    </el-row> -->

    <!-- TODO: Next version available -->
    <!-- <el-row>
      <el-card class="box-card">
        <div slot="header">
          <span>设备故障情况</span>
          <el-radio-group v-model="breakdownTimeUnit" size="mini" change="loadData">
            <el-radio-button v-for="(unit, index) in timeUnits" :key="index" :label="unit.value">
              {{ unit.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
        <line-chart
          chartId="breakdown-situation-chart"
          :yTitle="['故障设备数', '正常设备数']"
          :chartColor="['#ec5f26', '#5fa1f4']"
          :smooth="true"
          :leftbar="leftbar"
          :chartData="breakdownSituationChartData">
        </line-chart>
      </el-card>
    </el-row> -->
  </div>
</template>


<script>
import CountUp from 'countup.js'
import PieDoughnutChart from '@/components/charts/PieDoughnut'
import LineChart from '@/components/charts/Line'
import { httpGet } from '@/utils/api'

export default {
  name: 'dashboard-view',

  components: {
    PieDoughnutChart,
    LineChart,
  },

  data() {
    return {
      // Current quantity
      currentCount: {
        devices: 0,
        products: 0,
        groups: 0,
        tenants: 0,
        users: 0,
        gateways: 0,
        status: {
          online: 0,
          offline: 0,
          leep: 0,
        },
        connect: {
          failure: 0,
          success: 0,
          total: 0,
        },
      },
      // Current devices online status
      onlineSituationData: [
        { value: 0, name: this.$t('dashboard.onlineNum') },
        { value: 0, name: this.$t('dashboard.offlineNum') },
        { value: 0, name: this.$t('dashboard.sleepNum') },
      ],
      // Last 24 hours connection
      breakdownSituationData: [
        { value: 0, name: this.$t('dashboard.connectFailure') },
        { value: 0, name: this.$t('dashboard.connectSuccess') },
      ],
      // time unit
      timeUnits: [
        { label: this.$t('dashboard.hour'), value: 'hour' },
        { label: this.$t('dashboard.day'), value: 'day' },
        { label: this.$t('dashboard.month'), value: 'month' },
      ],
      // Total number of devices
      totalTimeUnit: 'hour',
      totalCountChartData: [
        {
          xData: [],
          yData: [],
        },
      ],
      // Message count
      eventMessageCountTimeUnit: 'hour',
      eventMessageCountChartData: [
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
      ],
      // Traffic statistics
      dataTrafficTimeUnit: 'hour',
      dataTrafficChartData: [
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
      ],
      // Device online situation
      // onlineTimeUnit: 'hour',
      // onlineSituationChartData: [
      //   {
      //     xData: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
      //     yData: [220, 182, 191, 234, 290, 330, 310],
      //   },
      //   {
      //     xData: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
      //     yData: [20, 82, 91, 34, 90, 30, 10],
      //   },
      //   {
      //     xData: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
      //     yData: [0, 2, 1, 4, 10, 0, 10],
      //   },
      // ],
      // Equipment failure
      // breakdownTimeUnit: 'hour',
      // breakdownSituationChartData: [
      //   {
      //     xData: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
      //     yData: [0, 2, 1, 4, 10, 0, 10],
      //   },
      //   {
      //     xData: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
      //     yData: [220, 182, 191, 234, 290, 330, 310],
      //   },
      // ],
      colorGreen: '',
      colorPink: '',
      colorPurple: '',
      axisColor: {},
    }
  },

  computed: {
    leftbar() {
      return this.$store.state.accounts.leftbar.width
    },
    // Get the theme
    currentTheme() {
      return this.$store.state.accounts.currentTheme || 'light'
    },
  },

  watch: {
    totalTimeUnit: 'loadDeviceCount',
    eventMessageCountTimeUnit: 'loadMessageCount',
    dataTrafficTimeUnit: 'loadDataTraffic',
    currentTheme: 'resetCharts',
  },

  methods: {
    // Get the public color value
    getThemeColor() {
      const root = getComputedStyle(document.body)
      this.colorGreen = root.getPropertyValue('--color-main-green').trim()
      this.colorPink = root.getPropertyValue('--color-main-pink').trim()
      this.colorPurple = root.getPropertyValue('--color-main-purple').trim()
      this.axisColor = {
        colorAxisLine: root.getPropertyValue('--color-echarts-line-axis_line').trim(),
        colorAxisLabel: root.getPropertyValue('--color-echarts-line-axis_label').trim(),
        colorSplitLine: root.getPropertyValue('--color-echarts-line-split_line').trim(),
      }
    },
    // Redraw the table after switching topics
    resetCharts() {
      this.getThemeColor()
      setTimeout(() => {
        this.$refs.deviceLineChart.reDrawEchart()
        this.$refs.messageLineChart.reDrawEchart()
        this.$refs.flowLineChart.reDrawEchart()
      }, 500)
    },

    loadCurrentCount() {
      httpGet('/overview/current_count').then((res) => {
        const cc = res.data.current_count
        Object.assign(this.currentCount, cc)
        this.onlineSituationData = [
          { value: cc.status.online, name: this.$t('dashboard.onlineNum') },
          { value: cc.status.offline, name: this.$t('dashboard.offlineNum') },
          { value: cc.status.sleep, name: this.$t('dashboard.sleepNum') },
        ]
        this.breakdownSituationData = [
          { value: cc.connect.failure, name: this.$t('dashboard.connectFailure') },
          { value: cc.connect.success, name: this.$t('dashboard.connectSuccess') },
        ]
        this.countUps()
      })
    },

    loadDeviceCount() {
      httpGet(`/overview/devices_count?time_unit=${this.totalTimeUnit}`)
        .then((res) => {
          this.totalCountChartData[0].xData = res.data.time
          this.totalCountChartData[0].yData = res.data.value
        })
    },

    loadMessageCount() {
      const lineNum = ['login', 'publish', 'receive', 'subscribe', 'unsubscribe']
      httpGet(`/overview/messages_count?time_unit=${this.eventMessageCountTimeUnit}`)
        .then((res) => {
          lineNum.forEach((item, index) => {
            this.eventMessageCountChartData[index].xData = res.data[item].time
            this.eventMessageCountChartData[index].yData = res.data[item].value
          })
        })
    },

    loadDataTraffic() {
      const lineNum = ['login', 'publish', 'receive', 'subscribe', 'unsubscribe']
      httpGet(`/overview/messages_flow?time_unit=${this.dataTrafficTimeUnit}`)
        .then((res) => {
          lineNum.forEach((item, index) => {
            this.dataTrafficChartData[index].xData = res.data[item].time
            this.dataTrafficChartData[index].yData = res.data[item].value
          })
        })
    },

    loadData() {
      this.loadCurrentCount()
      this.loadDeviceCount()
      this.loadMessageCount()
      this.loadDataTraffic()
    },

    upup(domId, count) {
      const countEle = document.getElementById(domId)
      const options = {
        useEasing: true,
        useGrouping: true,
        separator: ',',
        decimal: '.',
      }
      const countup = new CountUp(countEle, 0, count, 0, 1.5, options)
      if (!countup.error) {
        countup.start()
      }
    },

    countUps() {
      const cc = this.currentCount
      const domIds = [
        'device-count-text',
        'product-count-text',
        'group-count-text',
        'gateway-count-text',
      ]
      const counts = [cc.devices, cc.products, cc.groups, cc.gateways]
      for (let i = 0; i < domIds.length; i += 1) {
        this.upup(`${domIds[i]}1`, counts[i])
        this.upup(`${domIds[i]}2`, counts[i])
      }
    },
  },

  created() {
    this.getThemeColor()
    this.loadData()
  },
}
</script>


<style lang="scss">
.dashboard-view {
  .box-card {
    border-radius: 6px;
    box-shadow: 0 2px 12px 1px var(--color-shadow);
    border: none;
    background-color: var(--color-bg-card);
  }
  .count-warpper {
    cursor: pointer;
    .box-card {
      .el-card__body {
        padding: 20px 28px;
      }
    }
  }
  .count-card {
    margin-top: 0 !important;
    text-align: center;
    height: 60px !important;
    .iconfont {
      display: inline-block;
      float: left;
      width: 60px;
      height: 60px;
      line-height: 60px;
      font-size: 28px;
      font-weight: 600;
      color: var(--color-main-green);
      background-color: var(--color-bg-icon);
      border-radius: 50%;
    }
    .count-desc {
      text-align: right;
      color: var(--color-text-default);
      font-size: 16px;
      .count-text {
        font-size: 24px;
        color: var(--color-text-lighter);
      }
      li {
        line-height: 30px;
      }
    }
  }

  .el-row {
    margin-top: 28px;
    &.metrics-charts {
      .el-card__header {
        border-bottom: none;
        font-size: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--color-text-lighter);
        .total-count {
          font-size: 14px;
          color: var(--color-text-default);
          display: flex;
          align-items: center;
          .count-text {
            font-size: 20px;
            color: var(--color-text-lighter);
            font-weight: 400;
            margin-left: 12px;
          }
        }
      }
    }
  }

  .online-situation {
    .describe {
      li:nth-child(1) > span {
        background-color: var(--color-main-green);
      }
      li:nth-child(2) > span {
        background-color: var(--color-main-pink);
      }
      li:nth-child(3) > span {
        background-color: var(--color-main-purple);
      }
    }
  }
  .breakdown-situation {
    .describe {
      li:nth-child(1) > span {
        background-color: var(--color-main-pink);
      }
      li:nth-child(2) > span {
        background-color: var(--color-main-green);
      }
    }
  }

  .describe {
    padding: 20px 0 20px 20px;
    li {
      font-size: 14px;
      color: var(--color-text-light);
      line-height: 30px;
    }
    li > span {
      display: inline-block;
      line-height: 35px;
      width: 12px;
      height: 12px;
      background-color: red;
      border-radius: 12px;
      margin-right: 5px;
    }
  }

  .line-chart {
    .describe {
      text-align: center;
      padding: 12px 0 0 0;
      li {
        display: inline-block;
        margin: 0 20px;
      }
      /* '#23c88e', '#e86aa6', '#8199F3', '#a57ebc', '#EFC044' */
      &.event-message-count, &.event-data-traffic {
        li {
          &.login > span {
            background-color: var(--color-main-green);
          }
          &.publish > span {
            background-color: var(--color-main-pink);
          }
          &.receive > span {
            background-color: #8199F3;
          }
          &.subscribe > span {
            background-color: var(--color-main-purple);
          }
          &.unsubscribe > span {
            background-color: #EFC044;
          }
        }
      }
    }
  }

  .el-radio-group {
    float: right;
    .el-radio-button__inner {
      padding: 4px 10px;
      background-color: var(--color-bg-card);
      border-color: var(--color-line-bg);
      color: var(--color-text-light);
    }
    .el-radio-button__orig-radio:checked + .el-radio-button__inner {
      background-color: var(--color-main-green);
      border-color: var(--color-main-green);
      color: #fff;
    }
  }

  #device-online-situation,
  #device-breakdown-situation {
    width: 100%;
    height: 185px;
  }
  #total-count-chart,
  #event-message-count-chart,
  #data-traffic-chart,
  #online-situation-chart,
  #breakdown-situation-chart {
    width: 100%;
    height: 200px;
  }
}
</style>
