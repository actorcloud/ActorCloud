<template>
  <div class="history-alert-details details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/history_alerts">当前告警</el-breadcrumb-item>
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
            <el-form-item prop="alertName" label="告警名称">
              <el-input v-model="record.alertName"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="alertContent" label="告警内容">
              <el-input v-model="record.alertContent"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="alertTimes" label="告警次数">
              <el-input v-model="record.alertTimes"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12" class="alert-severity-label">
            <el-form-item prop="alertSeverityLabel" label="告警等级">
              <template>
                <el-tag v-if="record.alertSeverityLabel==='紧急'" type="danger" size="mini">
                  紧急
                </el-tag>
                <el-tag v-if="record.alertSeverityLabel==='主要'" type="warning" size="mini">
                  主要
                </el-tag>
                <el-tag v-if="record.alertSeverityLabel==='次要'" type="info" size="mini">
                  次要
                </el-tag>
                <el-tag v-if="record.alertSeverityLabel==='警告'" type="success" size="mini">
                  警告
                </el-tag>
              </template>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="alertDetail" label="告警详情">
              <el-input v-model="record.alertDetail"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="deviceName" label="设备名称名称">
              <el-input v-model="record.deviceName"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="startTime" label="开始时间">
              <el-input v-model="record.startTime"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="endTime" label="结束时间">
              <el-input v-model="record.endTime"></el-input>
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
  name: 'history-alert-details',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
  },

  data() {
    return {
      url: '/history_alerts',
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
.history-alert-details {
  @import '../assets/tag.scss';
  .alert-severity-label {
    .el-form-item__content {
      height: 41px;
    }
  }
}
</style>
