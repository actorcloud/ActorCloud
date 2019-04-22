<template>
  <div class="current-alert-details details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/current_alerts">{{ $t('alerts.currentAlerts') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <el-card :class="disabled ? 'is-details-form' : ''">
      <el-row :gutter="50">
        <el-form
          ref="record"
          label-position="left"
          label-width="110px"
          :disabled="disabled"
          :model="record">
          <el-col :span="12">
            <el-form-item prop="alertName" :label="$t('alerts.alertName')">
              <el-input v-model="record.alertName"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12" style="height: 41px;">
            <el-form-item prop="ruleName" :label="$t('alerts.rules')">
              <router-link
                v-if="record.ruleIntID"
                style="float: none;"
                :to="{ path: `/business_rules/${record.ruleIntID}`, query: { oper: 'view' } }">
                {{ record.ruleName }}
              </router-link>
              <router-link
                v-else-if="record.scopeIntID"
                style="float: none;"
                :to="{ path: `/scopes/scopes/${record.scopeIntID}`, query: { oper: 'view' } }">
                {{ record.ruleName }}
              </router-link>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="alertContent" :label="$t('alerts.alertContent')">
              <el-input v-model="record.alertContent"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="alertTimes" :label="$t('alerts.alertTimes')">
              <el-input v-model="record.alertTimes"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12" class="alert-severity-label">
            <el-form-item prop="alertSeverityLabelLabel" :label="$t('alerts.alertSeverity')">
              <template>
                <el-tag
                  :type="record.alertSeverity === 1
                    ? 'danger'
                    : record.alertSeverity === 2
                    ? 'warning'
                    : record.alertSeverity === 3
                    ? 'info'
                    : 'success'"
                  size="mini">
                  {{ record.alertSeverityLabel }}
                </el-tag>
              </template>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="alertDetail" :label="$t('alerts.alertDetail')">
              <el-input v-model="record.alertDetail"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="deviceName" :label="$t('devices.deviceName')">
              <el-input v-model="record.deviceName"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="startTime" :label="$t('alerts.startTime')">
              <el-input v-model="record.startTime"></el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>
    </el-card>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'

export default {
  name: 'current-alert-details',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
  },

  data() {
    return {
      url: '/current_alerts',
    }
  },

  watch: {
    record: {
      handler() {
        this.record.alertDetail = JSON.stringify(this.record.alertDetail)
      },
    },
  },
}
</script>


<style lang="scss">
.current-alert-details {
  @import '../assets/tag.scss';
  .alert-severity-label {
    .el-form-item__content {
      height: 41px;
    }
  }
}
</style>
