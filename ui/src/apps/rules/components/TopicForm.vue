<template>
  <div class="topic-form">
    <el-card class="topic-form__card">
      <div slot="header" class="clearfix">
        <el-button
          style="float: right;"
          type="text"
          :disabled="accessType === 'view'"
          @click="closeTopics(index)">
          <i class="el-card__close el-icon-close"></i>
        </el-button>
      </div>
      <el-form
        ref="topicForm"
        label-width="80px"
        label-position="left"
        :model="topicRecord">
        <el-form-item
          prop="productID"
          :label="$t('rules.product')">
          <emq-search-select
            ref="productSelect"
            size="small"
            v-model="topicRecord.productID"
            :placeholder="$t('rules.productRequired')"
            :field="{
              url: '/emq_select/products',
              searchKey: 'productName',
            }"
            :record="topicRecord"
            :disabled="disabled"
            @input="handleProductSelected">
          </emq-search-select>
        </el-form-item>
        <el-form-item prop="deviceID" :label="$t('rules.device')">
          <emq-search-select
            ref="deviceSelect"
            size="small"
            v-model="topicRecord.deviceID"
            clearable
            :placeholder="$t('rules.deviceRequired')"
            :disabled="disabled"
            :field="{
              url: '/emq_select/devices',
              params: { productID: topicRecord.productID },
              rely: 'productID',
              relyName: $t('rules.product'),
              searchKey: 'deviceName',
            }"
            :record="topicRecord"
            @addExtraOptions="addAllDevicesOption"
            @input="handleDeviceSelected">
          </emq-search-select>
        </el-form-item>
        <el-form-item prop="topic" :label="$t('rules.lastTopic')">
          <emq-select
            ref="topicSelect"
            size="small"
            v-model="topicRecord.topic"
            clearable
            :placeholder="$t('rules.lastTopicRequired')"
            :disabled="disabled"
            :field="{
              url: '/emq_select/topics',
              params: { productID: topicRecord.productID },
              rely: 'productID',
              relyName: $t('rules.product'),
            }"
            :record="topicRecord"
            @input="handleTopicSelected">
          </emq-select>
        </el-form-item>
      </el-form>
    </el-card>
    <el-row class="topic-form__result">
      <el-col :span="22">
        <p class="topic-form__text">{{ topicResult }}</p>
      </el-col>
      <el-col :span="2">
        <el-tooltip effect="dark" :content="clipboardStatus" placement="top">
          <el-button type="text" size="small" @click="copyText">
            {{ $t('oper.copy') }}
          </el-button>
        </el-tooltip>
      </el-col>
    </el-row>
  </div>
</template>


<script>
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'topic-form',

  props: {
    topicRecord: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: true,
    },
    accessType: {
      type: String,
      required: true,
    },
    index: {
      type: Number,
      required: true,
    },
  },

  components: {
    EmqSearchSelect,
  },

  data() {
    return {
      topicResult: '',
      clipboardStatus: this.$t('oper.copy'),
      allDeviceDict: {
        value: '+',
        label: this.$t('devices.allDevices'),
      },
    }
  },

  computed: {
    tenantID() {
      return this.$store.state.accounts.user.tenantID
    },
  },

  methods: {
    setTopicResult() {
      const { productID, deviceID, topic } = this.topicRecord
      const productIDStr = productID ? `/${productID}` : ''
      const deviceIDStr = deviceID ? `/${deviceID}` : ''
      const topicStr = topic ? `/${topic}` : ''
      this.topicResult = `/${this.tenantID}${productIDStr}${deviceIDStr}${topicStr}`
    },

    closeTopics(index) {
      this.$emit('remove', index)
    },

    handleProductSelected() {
      this.topicRecord.deviceID = undefined
      this.topicRecord.topic = undefined
      this.setTopicResult()
    },

    handleDeviceSelected() {
      this.setTopicResult()
    },

    handleTopicSelected() {
      this.setTopicResult()
    },

    setSelectOptions() {
      this.$refs.productSelect.options = [
        { value: this.topicRecord.productID, label: this.topicRecord.productName },
      ]
      if (this.topicRecord.deviceID === '+') {
        this.$refs.deviceSelect.options = [
          this.allDeviceDict,
        ]
      } else {
        this.$refs.deviceSelect.options = [
          { value: this.topicRecord.deviceID, label: this.topicRecord.deviceName },
        ]
      }
    },

    copyText() {
      this.$emit('copy', this.topicResult)
      this.clipboardStatus = this.$t('oper.copySuccess')
      setTimeout(() => {
        document.querySelector('#clipboard').select()
        document.execCommand('Copy')
        setTimeout(() => {
          this.clipboardStatus = this.$t('oper.copy')
        }, 500)
      }, 500)
    },

    addAllDevicesOption() {
      this.$refs.deviceSelect.options.splice(0, 0, this.allDeviceDict)
    },
  },

  mounted() {
    this.setTopicResult()
    this.setSelectOptions()
  },
}
</script>


<style lang="scss">
.topic-form {
  .topic-form__card.el-card {
    margin-bottom: 0px;
    border-radius: 6px 6px 0 0;
    box-shadow: none;

    .el-card__header {
      padding: 0;
      height: 20px;
      .el-button--text {
        padding: 5px 2px 0 0;
      }
    }

    .el-card__body {
      padding: 0px 20px 20px 20px;

      .el-form-item {
        margin-bottom: 5px;
        &:last-child {
          margin-bottom: 0px;
        }
        .el-form-item__label {
          float: left;
        }
      }
    }
  }

  .topic-form__result {
    min-height: 45px;
    border-radius: 0 0 6px 6px;
    background-color: var(--color-bg-hover);
    color: var(--color-text-light);
    border: 1px solid var(--color-bg-hover);
    margin-bottom: 30px;

    .topic-form__text {
      margin: 0 20px;
      word-break: break-all;
      white-space: normal;
    }
  }
}
</style>
