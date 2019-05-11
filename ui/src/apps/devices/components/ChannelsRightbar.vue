<template>
  <rightbar-pop>
    <el-card v-if="rightbarVisible" class="channels-rightbar-view">
      <div ref="cardHead" slot="header" class="clearfix">
        <span class="header">{{ $t('gateways.channels') }}</span>
        <a href="javascript:;" @click="close" class="close">
          <i class="el-icon-close"></i>
        </a>
      </div>
      <div class="channels-body">
        <el-collapse v-model="activeChannels">
          <el-collapse-item :title="$t('gateways.addChannel')" name="1">
            <el-row :gutter="50">
              <el-form
                ref="record"
                label-width="68px"
                label-position="left"
                :model="record"
                :rules="rules">
                <el-col :span="12">
                  <el-form-item prop="channelType" :label="$t('gateways.channelType')">
                    <el-cascader
                      v-model="channelTypeList"
                      :placeholder="$t('gateways.channelTypeRequired')"
                      :options="channelTypeOptions"
                      @change="channelTypeChanged">
                    </el-cascader>
                  </el-form-item>
                </el-col>
                <template v-if="channelTypeList[0] === 'COM'">
                  <el-col :span="12">
                    <el-form-item prop="COM" label="COM">
                      <el-input
                        type="text"
                        v-model="record.COM"
                        :placeholder="$t('gateways.COMRequired')">
                      </el-input>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item prop="Baud" label="Baud">
                      <emq-select
                        v-model="record.Baud"
                        :field="{ options: BaudOptions }"
                        :record="record"
                        :placeholder="$t('oper.select')">
                      </emq-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item prop="Data" label="Data">
                      <emq-select
                        v-model="record.Data"
                        :field="{ options: DataOptions }"
                        :record="record"
                        :placeholder="$t('oper.select')">
                      </emq-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item prop="Stop" label="Stop">
                      <emq-select
                        v-model="record.Stop"
                        :field="{ options: StopOptions }"
                        :record="record"
                        :placeholder="$t('oper.select')">
                      </emq-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item prop="Parity" label="Parity">
                      <emq-select
                        v-model="record.Parity"
                        :field="{ options: ParityOptions }"
                        :record="record"
                        :placeholder="$t('oper.select')">
                      </emq-select>
                    </el-form-item>
                  </el-col>
                </template>
                <template v-if="channelTypeList[0] === 'TCP'">
                  <el-col :span="12">
                    <el-form-item prop="IP" :label="$t('gateways.IP')">
                      <el-input
                        type="text"
                        v-model="record.IP"
                        :placeholder="$t('gateways.IPRequired')">
                      </el-input>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item prop="Port" :label="$t('gateways.port')">
                      <el-input
                        type="text"
                        v-model="record.Port"
                        :placeholder="$t('gateways.portRequired')">
                      </el-input>
                    </el-form-item>
                  </el-col>
                </template>
              </el-form>
            </el-row>
            <emq-button
              :loading="btnLoading"
              :disabled="!channelTypeList.length"
              @click="save">{{ $t('oper.save') }}</emq-button>
          </el-collapse-item>
        </el-collapse>

        <el-table
          class="device-include-table"
          v-loading="loading"
          lsize="medium"
          :data="records">
          <template v-if="tableChannelType === 'COM'">
            <el-table-column prop="COM" label="COM">
            </el-table-column>
            <el-table-column prop="Baud" label="Baud">
            </el-table-column>
            <el-table-column prop="Data" label="Data">
            </el-table-column>
            <el-table-column prop="Stop" label="Stop">
            </el-table-column>
            <el-table-column prop="Parity" label="Parity">
            </el-table-column>
          </template>
          <template v-if="tableChannelType === 'TCP'">
            <el-table-column prop="IP" :label="$t('gateways.IP')">
            </el-table-column>
            <el-table-column prop="Port" label="Port">
            </el-table-column>
          </template>
          <el-table-column width="45px">
            <template v-slot="props">
              <a
                href="javascript:;"
                class="border-button"
                @click="deleteRecord(props.row.id)">
                <i class="iconfont icon icon-emq-delete"></i>
              </a>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </rightbar-pop>
</template>


<script>
import { httpGet, httpPost, httpDelete } from '@/utils/api'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import RightbarPop from '@/components/RightbarPop'
import { Collapse, CollapseItem } from 'element-ui'

export default {
  name: 'channels-rightbar-view',

  components: {
    EmqButton,
    EmqSelect,
    RightbarPop,
    'el-collapse': Collapse,
    'el-collapse-item': CollapseItem,
  },

  props: {
    rightbarVisible: {
      type: Boolean,
      required: true,
    },
    url: {
      type: String,
      required: true,
    },
    currentGateway: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    return {
      loading: false,
      btnLoading: false,
      activeChannels: [],
      willDeleteId: undefined,
      currentPage: 1,
      pageSize: 10,
      count: 0,
      total: 0,
      tableChannelType: 'COM', // Controls the display of channel types for table
      channelTypeList: [],
      channelTypeOptions: [],
      BaudOptions: [
        { label: 'B0', value: 0 },
        { label: 'B50', value: 50 },
        { label: 'B75', value: 75 },
        { label: 'B110', value: 110 },
        { label: 'B134', value: 134 },
        { label: 'B150', value: 150 },
        { label: 'B200', value: 200 },
        { label: 'B300', value: 300 },
        { label: 'B600', value: 600 },
        { label: 'B1200', value: 1200 },
        { label: 'B1800', value: 1800 },
        { label: 'B2400', value: 2400 },
        { label: 'B4800', value: 4800 },
        { label: 'B9600', value: 9600 },
        { label: 'B19200', value: 19200 },
        { label: 'B38400', value: 38400 },
        { label: 'B57600', value: 57600 },
        { label: 'B115200', value: 115200 },
      ],
      DataOptions: [{ value: 6, label: 6 }, { value: 7, label: 7 }, { value: 8, label: 8 }],
      StopOptions: [{ value: '1', label: '1' }, { value: '1.5', label: '1.5' }, { value: '2', label: '2' }],
      ParityOptions: [{ value: 'N', label: 'N' }, { value: 'O', label: 'O' }, { value: 'E', label: 'E' }],
      records: [],
      record: {},
      rules: {
        channelType: [
          { required: true, message: this.$t('gateways.channelTypeRequired') },
        ],
        COM: [
          { required: true, message: this.$t('gateways.COMRequired') },
        ],
        Baud: [
          { required: true, message: this.$t('gateways.BaudRequired') },
        ],
        Data: [
          { required: true, message: this.$t('gateways.DataRequired') },
        ],
        Stop: [
          { required: true, message: this.$t('gateways.Stop') },
        ],
        Parity: [
          { required: true, message: this.$t('gateways.Parity') },
        ],
        IP: [
          { required: true, message: this.$t('gateways.IPRequired') },
          {
            pattern: /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])(\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])){3}$/,
            message: this.$t('gateways.IPCorrect'),
            trigger: 'blur',
          },
        ],
        Port: [
          { required: true, message: this.$t('gateways.portRequired') },
        ],
      },
    }
  },

  watch: {
    rightbarVisible() {
      if (this.rightbarVisible) {
        this.loadData()
        this.loadChannelType()
      }
    },
  },

  methods: {
    loadData() {
      httpGet(this.url).then((res) => {
        this.records = res.data.items
        if (res.data.channelType) {
          this.tableChannelType = res.data.channelType
        }
      })
    },

    loadChannelType() {
      httpGet('/emq_select/channel_type').then((res) => {
        this.channelTypeOptions = res.data
      })
    },

    channelTypeChanged() {
      this.$refs.record.resetFields()
      this.record = {}
    },

    save() {
      this.record.channelType = this.channelTypeList[0]
      this.record.drive = this.channelTypeList[1]
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        this.btnLoading = true
        const data = this.record
        httpPost(this.url, data).then(() => {
          this.$message.success(this.$t('oper.createSuccess'))
          this.btnLoading = false
          this.$refs.record.resetFields()
          this.loadData()
          this.activeChannels = []
          this.tableChannelType = this.record.channelType
        }).catch((error) => {
          this.btnLoading = false
          if (error.response.status === 403) {
            if (Object.keys(error.response.data.errors)[0] === 'COM') {
              this.$message.error(this.$t('gateways.COMLimit'))
            } else {
              this.$message.error(this.$t('gateways.TCPLimt'))
            }
          }
        })
      })
    },

    close() {
      this.channelTypeList = []
      this.activeChannels = []
      this.records = []
      this.record = {}
      this.$emit('update:rightbarVisible', false)
    },

    deleteRecord(ids) {
      this.$confirm(this.$t('oper.confirmDelete'), this.$t('oper.warning'), {
        confirmButtonText: this.$t('oper.confirm'),
        cancelButtonText: this.$t('oper.cancel'),
        cancelButtonClass: 'cancel-button',
        type: 'warning',
      }).then(() => {
        httpDelete(this.url, { params: { ids } }).then(() => {
          this.$message.success(this.$t('oper.deleteSuccess'))
          this.loadData()
        })
      }).catch(() => {})
    },
  },
}
</script>


<style lang="scss">
.channels-rightbar-view {
  position: fixed;
  top: 56px;
  right: 0;
  z-index: 1001;
  width: 620px;
  height: 100%;
  overflow: scroll;
  background: var(--color-bg-card);
  border-radius: 0;
  box-shadow: -5px 0px 12px rgba(0, 0, 0, 0.1) !important;
  .el-card__header {
    right: 0;
    height: 56px;
    z-index: 999;
    background: var(--color-bg-card);
    padding: 16px 20px;
    border-bottom: 1px solid var(--color-line-card);
    .header {
      font-size: 16px;
      color: var(--color-text-light);
      line-height: 28px;
    }
    .close {
      float: right;
      color: var(--color-text-light);
      padding: 5px 0;
    }
  }
  .el-card__body {
    .el-collapse {
      margin-bottom: 20px;
      border-top: 1px solid var(--color-line-card);
      border-bottom: 1px solid var(--color-line-card);
      .el-collapse-item__header {
        color: var(--color-text-light);
        background: var(--color-bg-card);
        font-size: 14px;
        border-bottom: 1px solid var(--color-line-card);
        transition: border-bottom-color .3s;
        text-align: center;
      }
      .el-collapse-item__header.is-active {
        border-bottom-color: transparent;
      }
      .el-collapse-item__content {
        padding: 0 5px 50px 2px;
        background: var(--color-bg-card);
      }
      .el-collapse-item__wrap {
        border-bottom: 1px solid var(--color-line-card);
      }
    }
    .el-col {
      padding-right: 16px !important;
    }
    .el-form {
      margin: 0 10px;
    }
    .el-table {
      margin-bottom: 60px;
      background-color: var(--color-bg-card);
      tr {
        background-color: var(--color-bg-card);
      }
    }
  }
}
@media screen and (min-width: 1366px) {
  .channels-rightbar-view {
    top: 80px;
  }
}
</style>
