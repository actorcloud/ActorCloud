<template>
  <div class="details-view data-stream-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item
          :to="{ path: `/products/${this.$route.params.id}/definition` }">
          {{ $t('dataStreams.dataStream') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <el-card :class="disabled ? 'is-details-form' : ''">
      <edit-toggle-button
        :url="url"
        :disabled="disabled"
        :accessType="accessType"
        @toggleStatus="toggleStatus">
      </edit-toggle-button>
      <el-row :gutter="40">
        <el-form
          ref="record"
          label-position="left"
          label-width="120px"
          :model="record"
          :rules="disabled ? {} : rules">
          <el-col :span="12">
            <el-form-item :label="$t('dataStreams.streamName')" prop="streamName">
              <el-input
                type="text"
                v-model="record.streamName"
                :placeholder="disabled ? '' : $t('dataStreams.streamNameRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
            <el-form-item :label="$t('dataStreams.streamType')" prop="streamType">
              <emq-select
                v-if="currentProduct.productType === $variable.productType.GATEWAY"
                v-model="record.streamType"
                :field="{ key: 'streamType' }"
                :record="record"
                :placeholder="disabled ? '' : $t('oper.select')"
                :disabled="disabled">
              </emq-select>
              <el-select
                v-else
                v-model="record.streamType"
                 style="width: 100%;"
                :placeholder="disabled ? '' : $t('oper.select')"
                :disabled="disabled">
                <el-option :value="1" :label="$t('dataStreams.dataReport')"></el-option>
                <el-option :value="2" :label="$t('dataStreams.dataPublish')"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item v-if="accessType === 'view'" :label="$t('dataPoints.createAt')">
              <el-input
                v-model="record.createAt"
                :disabled="disabled">
              </el-input>
            </el-form-item>
            <el-form-item :label="$t('dataStreams.description')" prop="description">
              <el-input
                :type="disabled ? 'text' : 'textarea'"
                :placeholder="disabled ? '' : $t('dataStreams.descriptionRequired')"
                v-model="record.description"
                :disabled="disabled">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('dataStreams.topic')" prop="topic">
              <el-input
                type="text"
                v-model="record.topic"
                :disabled="accessType !== 'create'
                  || currentProduct.cloudProtocol === $variable.cloudProtocol.LWM2M">
              </el-input>
            </el-form-item>
            <el-form-item
              prop="streamID"
              :label="$t('dataStreams.streamID')">
              <el-input
                v-model="record.streamID"
                :placeholder="disabled ? '' : $t('dataStreams.streamIDRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>
      <emq-button v-if="!disabled" icon="save" @click="save">
        {{ $t('oper.finish') }}
      </emq-button>
    </el-card>

    <el-dialog
      class="emq-dialog create-success"
      width="420px"
      :visible.sync="createVisable"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false">
      <img src="~@/assets/images/created.png" width="180">
      <h1>{{ $t('dataStreams.streamCreateSuccess') }}</h1>
      <div class="create-success__oper">
        <el-button
          class="add-button"
          @click="$router.push({ path: listPageURL, query: { queryID: detailsID } })">
          {{ $t('dataPoints.addDataPoint') }}
        </el-button>
        <el-button
          class="cancel"
          @click="$router.push({ path: listPageURL })">
          {{ $t('dataStreams.addCancel') }}
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>


<script>
import { currentProductsMixin } from '@/mixins/currentProducts'
import detailsPage from '@/mixins/detailsPage'
import EmqSelect from '@/components/EmqSelect'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'

export default {
  name: 'data-stream-details-view',

  mixins: [detailsPage, currentProductsMixin],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
  },

  data() {
    const validateTopic = (rule, value, callback) => {
      if (!value) {
        callback(new Error(this.$t('dataStreams.topicRequired')))
      } else {
        if (!value.match(/^[a-zA-Z0-9/_/+-/#]*$/g)) {
          callback(new Error(this.$t('dataStreams.topicTips')))
        }
        callback();
      }
    }
    const validateStreamID = (rule, value, callback) => {
      if (!value) {
        callback(new Error(this.$t('dataStreams.streamIDRequired')))
      } else {
        if (!value.match(/^[a-zA-Z]\w*$/g)) {
          callback(new Error(this.$t('dataStreams.streamIDTips')))
        }
        callback()
      }
    }
    return {
      url: '/data_streams',
      createVisable: false,
      record: {},
      rules: {
        streamID: [
          { validator: validateStreamID, required: true },
        ],
        streamName: [
          { required: true, message: this.$t('dataStreams.streamNameRequired'), trigger: 'blur' },
        ],
        streamType: [
          { required: true, message: this.$t('dataStreams.streamTypeRequired'), trigger: 'blur' },
        ],
        topic: [
          { validator: validateTopic, required: true, trigger: 'blur' },
        ],
      },
      localRecordName: 'dataStreams',
    }
  },

  methods: {
    beforePostData(data) {
      data.productID = this.currentProduct.productID
    },
    requestSuccess(response) {
      this.detailsID = response.data.id
      this.createVisable = true
      return true
    },
  },

  created() {
    if (this.currentProduct.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
      this.record.topic = '/ad/19/0/0'
    }
  },
}
</script>
