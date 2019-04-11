<template>
  <div class="overview-view emq-crud">
    <div class="crud-header default-header">
      <el-row type="flex" justify="space-between" align="middle">
        <el-col :span="16">
          <tabs-card-head :tabs="$store.state.base.tabs.operate_reporting">
          </tabs-card-head>
        </el-col>
      </el-row>
    </div>

    <!-- Pie-doughnut -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <pie-doughnut-chart
            chartId="person-tenant-chart"
            :chartName="$t('operations.personalTenantCount')"
            :showTitle="true"
            :chartTitle="onlinePersonalTenant[0].value.toString()"
            :colors="['#23c88e', '#dedede']"
            :leftbar="leftbar"
            :chartData="onlinePersonalTenant">
          </pie-doughnut-chart>
          <div class="total-count">{{ $t('operations.personalTenantCount') }}:
            <span>
              {{ countData.personalTenant }}
            </span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <pie-doughnut-chart
            chartId="company-tenant-chart"
            :chartName="$t('operations.companyTenantCount')"
            :showTitle="true"
            :chartTitle="onlineCompanyTenant[0].value.toString()"
            :colors="['#23c88e', '#dedede']"
            :leftbar="leftbar"
            :chartData="onlineCompanyTenant">
          </pie-doughnut-chart>
          <div class="total-count">{{ $t('operations.companyTenantCount') }}:
            <span>
              {{ countData.companyTenant }}
            </span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <pie-doughnut-chart
            chartId="company-account-chart"
            :chartName="$t('operations.companyUserCount')"
            :showTitle="true"
            :chartTitle="onlineCompanyUser[0].value.toString()"
            :colors="['#23c88e', '#dedede']"
            :leftbar="leftbar"
            :chartData="onlineCompanyUser">
          </pie-doughnut-chart>
          <div class="total-count">{{ $t('operations.companyUserCount') }}
            <span>
              {{ countData.companyUserCount }}
            </span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <pie-doughnut-chart
            chartId="device-account-chart"
            :chartName="$t('operations.deviceCount')"
            :showTitle="true"
            :chartTitle="onlineDevice[0].value.toString()"
            :colors="['#23c88e', '#dedede']"
            :leftbar="leftbar"
            :chartData="onlineDevice">
          </pie-doughnut-chart>
          <div class="total-count">{{ $t('operations.deviceCount') }}
            <span>
              {{ countData.deviceCount }}
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Line -->
    <el-row>
      <el-card>
        <div slot="header">
          <span>{{ $t('operations.accountCount') }}</span>
        </div>
        <line-chart
          ref="accountLine"
          chartId="account-count-chart"
          :yTitle="[$t('operations.accountTotal'), $t('operations.accountNew')]"
          :chartColor="['#23c88e', '#2f76fb']"
          :smooth="true"
          :leftbar="leftbar"
          :chartData="accountCountChartData"
          :axisColor="axisColor">
        </line-chart>
        <div class="line-desc">
          <span style="background-color: #23c88e;"></span> {{ $t('operations.accountTotal') }} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
          <span style="background-color: #2f76fb;"></span> {{ $t('operations.accountNew') }}
        </div>
      </el-card>
    </el-row>

    <el-row>
      <el-card>
        <div slot="header">
          <span>{{ $t('operations.deviceCount') }}</span>
        </div>
        <line-chart
          ref="deviceLine"
          chartId="device-count-chart"
          :yTitle="[$t('operations.deviceTotal'), $t('operations.deviceNew')]"
          :chartColor="['#978bf6', '#2f76fb']"
          :smooth="true"
          :leftbar="leftbar"
          :chartData="deviceCountChartData"
          :axisColor="axisColor">
        </line-chart>
        <div class="line-desc">
          <span style="background-color: #978bf6;"></span> {{ $t('operations.deviceTotal') }} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
          <span style="background-color: #2f76fb;"></span> {{ $t('operations.deviceNew') }}
        </div>
      </el-card>
    </el-row>

    <el-row>
      <el-card>
        <div slot="header">
          <span>{{ $t('operations.messageCount') }}</span>
        </div>
        <line-chart
          ref="messageLine"
          chartId="message-count-chart"
          :yTitle="[$t('operations.messageCount')]"
          :chartColor="['#efc23d']"
          :smooth="true"
          :leftbar="leftbar"
          :chartData="messageCountChartData"
          :axisColor="axisColor">
        </line-chart>
        <div class="line-desc">
          <span style="background-color: #efc23d;"></span> {{ $t('operations.messageCount') }}
        </div>
      </el-card>
    </el-row>

    <el-row>
      <el-card>
        <div slot="header">
          <span>{{ $t('operations.apiCalls') }}</span>
        </div>
        <line-chart
          ref="apiLine"
          chartId="api-count-chart"
          :yTitle="[$t('operations.apiCalls')]"
          :chartColor="['#55acf6']"
          :smooth="true"
          :leftbar="leftbar"
          :chartData="apiCountChartData"
          :axisColor="axisColor">
        </line-chart>
        <div class="line-desc">
          <span style="background-color: #55acf6;"></span> {{ $t('operations.apiCalls') }}
        </div>
      </el-card>
    </el-row>
  </div>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import PieDoughnutChart from '@/components/charts/PieDoughnut'
import LineChart from '@/components/charts/Line'
import { httpGet } from '@/utils/api'

export default {
  name: 'overview-view',

  components: {
    TabsCardHead,
    PieDoughnutChart,
    LineChart,
  },

  data() {
    return {
      poll: '',
      tableActions: ['view'],
      countData: {
        personalTenant: 0,
        companyTenant: 0,
        companyUserCount: 0,
        deviceCount: 0,
      },
      onlinePersonalTenant: [
        { value: 0, name: this.$t('operations.onlineTenant') },
        { value: 0, name: this.$t('operations.offlineTenant') },
      ],
      onlineCompanyTenant: [
        { value: 0, name: this.$t('operations.onlineTenant') },
        { value: 0, name: this.$t('operations.offlineTenant') },
      ],
      onlineCompanyUser: [
        { value: 0, name: this.$t('operations.onlineAccount') },
        { value: 0, name: this.$t('operations.offlineAccount') },
      ],
      onlineDevice: [
        { value: 0, name: this.$t('operations.onlineDevice') },
        { value: 0, name: this.$t('operations.offlineDevice') },
      ],
      accountCountChartData: [
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
      ],
      deviceCountChartData: [
        {
          xData: [],
          yData: [],
        },
        {
          xData: [],
          yData: [],
        },
      ],
      messageCountChartData: [
        {
          xData: [],
          yData: [],
        },
      ],
      apiCountChartData: [
        {
          xData: [],
          yData: [],
        },
      ],
      axisColor: {},
    }
  },

  computed: {
    leftbar() {
      return this.$store.state.base.leftbar.width
    },
    currentTheme() {
      return this.$store.state.base.currentTheme || 'light'
    },
  },

  watch: {
    currentTheme: 'resetCharts',
  },

  methods: {
    // Get public colors
    getThemeColor() {
      const root = getComputedStyle(document.body)
      this.axisColor = {
        colorAxisLine: root.getPropertyValue('--color-echarts-line-axis_line').trim(),
        colorAxisLabel: root.getPropertyValue('--color-echarts-line-axis_label').trim(),
        colorSplitLine: root.getPropertyValue('--color-echarts-line-split_line').trim(),
      }
    },
    // Theme swtiching re-drawing
    resetCharts() {
      this.getThemeColor()
      setTimeout(() => {
        this.$refs.accountLine.reDrawEchart()
        this.$refs.deviceLine.reDrawEchart()
        this.$refs.messageLine.reDrawEchart()
        this.$refs.apiLine.reDrawEchart()
      }, 500)
    },

    /* eslint-disable */
    loadData() {
      httpGet('/operate_overview?operateType=count').then((res) => {
        const d = res.data
        this.countData = d
        this.onlinePersonalTenant[0].value = d.onlinePersonalTenant
        this.onlinePersonalTenant[1].value = d.personalTenant - d.onlinePersonalTenant

        this.onlineCompanyTenant[0].value = d.onlineCompanyTenant
        this.onlineCompanyTenant[1].value = d.companyTenant - d.onlineCompanyTenant

        this.onlineCompanyUser[0].value = d.onlineCompanyUser
        this.onlineCompanyUser[1].value = d.companyUserCount - d.onlineCompanyUser

        this.onlineDevice[0].value = d.onlineDevice
        this.onlineDevice[1].value = d.deviceCount - d.onlineDevice
      })
      httpGet('/operate_overview?operateType=chart').then((res) => {
        const d = res.data
        this.accountCountChartData[0].xData = d.userCount.time
        this.accountCountChartData[0].yData = d.userCount.value.defaultValue
        this.accountCountChartData[1].xData = d.userCount.time
        this.accountCountChartData[1].yData = d.userCount.value.increaseValue

        this.deviceCountChartData[0].xData = d.deviceCount.time
        this.deviceCountChartData[0].yData = d.deviceCount.value.defaultValue
        this.deviceCountChartData[1].xData = d.deviceCount.time
        this.deviceCountChartData[1].yData = d.deviceCount.value.increaseValue

        this.messageCountChartData[0].xData = d.messageCount.time
        this.messageCountChartData[0].yData = d.messageCount.value

        this.apiCountChartData[0].xData = d.apiCount.time
        this.apiCountChartData[0].yData = d.apiCount.value
      })
    },
  },

  created() {
    this.getThemeColor()
    this.loadData()
    this.poll = setInterval(() => {
      this.loadData()
    }, 5000)
  },
  beforeDestroy() {
    clearInterval(this.poll)
  },
}
</script>


<style lang="scss">
.overview-view {
  .emq-crud {
    .el-card,
    .footer {
      display: none;
    }
  }
  .emq-crud .crud-header {
    margin-bottom: 0px;
  }
  .el-card {
    margin-top: 20px;
    .el-card__header {
      color: var(--color-text-lighter);
    }
  }
  #person-tenant-chart,
  #company-tenant-chart,
  #company-account-chart,
  #device-account-chart {
    width: 100%;
    height: 175px;
  }
  #account-count-chart,
  #device-count-chart,
  #message-count-chart,
  #api-count-chart {
    width: 100%;
    height: 200px;
  }
  .line-desc {
    padding-top: 10px;
    text-align: center;
    color: var(--color-text-light);    span {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
  }
  .total-count {
    font-size: 14px;
    color: var(--color-text-lighter);
    display: flex;
    justify-content: center;
    span {
      color: var(--color-text-light);
    }
  }
}
</style>
