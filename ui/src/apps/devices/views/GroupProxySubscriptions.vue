<template>
  <div class="details-view group-proxy-subscriptions">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/devices/groups">分组</el-breadcrumb-item>
        <el-breadcrumb-item>代理订阅</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div class="detail-tabs">
      <emq-button class="custom-button" @click="handleAddTopic">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <group-detail-tabs></group-detail-tabs>
    </div>

    <emq-crud class="emq-crud--details" ref="crud" :url="`/groups/${groupID}/subscriptions`" :tableActions="[]">
      <template slot="tableColumns">
        <el-table-column label="主题" prop="topic"></el-table-column>
        <el-table-column label="Qos" prop="qos"></el-table-column>
        <el-table-column width="60px">
          <template v-slot="props">
            <a
              href="javascript:;"
              @click="deleteRecord(props.row.id)">
              <img src="~@/assets/images/delete.png"/>
            </a>
          </template>
        </el-table-column>
      </template>
    </emq-crud>

    <!-- Add topic subscriptions -->
    <emq-dialog
      :title="$t('devices.addTopic')"
      :visible.sync="dialogVisible"
      @close="handleClose"
      @confirm="addTopic">
      <el-form
        ref="record"
        :model="record"
        :rules="topicRules">
        <el-form-item prop="topic" :label="$t('devices.topic')">
          <el-input v-model="record.topic" :placeholder="$t('devices.topicRequired')"></el-input>
        </el-form-item>
      </el-form>
    </emq-dialog>
  </div>
</template>


<script>
import { httpPost, httpDelete } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqDialog from '@/components/EmqDialog'
import GroupDetailTabs from '../components/GroupDetailTabs'

export default {
  name: 'group-proxy-subscriptions',

  components: {
    GroupDetailTabs,
    EmqDetailsPageHead,
    EmqCrud,
    EmqDialog,
  },

  data() {
    return {
      groupID: this.$route.params.id,
      dialogVisible: false,
      confirmDialogVisible: false,
      record: {
        topic: '',
      },
      topicRules: {
        topic: [
          { required: true, message: this.$t('devices.topicRequired') },
        ],
      },
    }
  },

  methods: {
    addTopic() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return
        }
        httpPost(`/groups/${this.groupID}/subscriptions`, this.record).then(() => {
          this.dialogVisible = false
          this.$message.success(this.$t('devices.addTopicSuccess'))
          this.$refs.crud.loadRecords()
        })
      })
    },
    handleAddTopic() {
      this.record.topic = ''
      this.dialogVisible = true
    },
    handleClose() {
      this.$refs.record.resetFields()
      this.record.topic = ''
    },
    deleteRecord(ids) {
      this.$confirm(this.$t('oper.confirmDelete'), this.$t('oper.warning'), {
        confirmButtonText: this.$t('oper.save'),
        cancelButtonText: this.$t('oper.cancel'),
        cancelButtonClass: 'cancel-button',
        type: 'warning',
      }).then(() => {
        httpDelete(`/groups/${this.groupID}/subscriptions`, { params: { ids } }).then(() => {
          this.$message.success(this.$t('oper.deleteSuccess'))
          this.$refs.crud.loadRecords()
        })
      }).catch(() => {})
    },
  },
}
</script>
