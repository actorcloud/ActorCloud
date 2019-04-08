<template>
  <div class="details-view data-stream-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item
          :to="{
            path: currentProduct.cloudProtocol !== $variable.cloudProtocol.LWM2M
              && currentProduct.cloudProtocol !== $variable.cloudProtocol.LORA
              ? `/products/${this.$route.params.id}/data_streams`
              : `/products/${this.$route.params.id}/definition`
          }">{{ $t('dataStreams.dataStream') }}</el-breadcrumb-item>
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
                v-if="currentProduct.productType === 2"
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
            <el-form-item
              v-if="currentProduct.cloudProtocol === $variable.cloudProtocol.LWM2M
              || currentProduct.cloudProtocol === $variable.cloudProtocol.LORA"
              :label="$t('dataStreams.streamID')"
              prop="streamID">
              <el-input
                type="number"
                v-model.number="record.streamID"
                :placeholder="disabled ? '' : $t('dataStreams.streamIDRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
            <el-form-item
              v-if="record.streamDataType === 1
                && dataPointsShow
                && currentProduct.cloudProtocol !== $variable.cloudProtocol.LWM2M
                && currentProduct.cloudProtocol !== $variable.cloudProtocol.LORA"
              :label="$t('dataStreams.dataPointMultiple')" prop="dataPoints">
              <span
                v-if="accessType === 'create'"
                class="data-point__button">
                {{$t('oper.or')}}&nbsp;
                <a href="javascript:;" @click="newAnotherPageData">{{ $t('dataStreams.createDataPoint') }}</a>
              </span>
              <emq-select
                ref="dataPointSelect"
                v-show="!disabled"
                v-model="record.dataPoints"
                class="data-point-input"
                multiple
                :field="{
                  key: 'dataPoints',
                  url: `/emq_select/data_points?productIntID=${this.$route.params.id}&streamDataType=1`,
                  rely: 'streamType',
                  relyName: $t('dataStreams.streamType'),
                }"
                :record="record"
                :placeholder="disabled ? '' : $t('oper.select')"
                :disabled="disabled">
              </emq-select>
              <div v-if="disabled" class="data-point-link">
                <router-link
                  style="float: none;"
                  v-for="(dataPoint, dataPointIndex) in record.dataPoints"
                  :key="dataPointIndex"
                  :to="`/products/${productIntID}/data_points/${dataPoint}`">
                  <el-tag
                    size="small">
                    {{ record.dataPointNames[dataPointIndex] }}
                  </el-tag>
                </router-link>
              </div>
            </el-form-item>
            <el-form-item
              v-if="record.streamDataType === 2 && dataPointsShow"
              :label="$t('dataStreams.dataPoint')"
              prop="dataPoints"
              class="data-points-binary">
              <el-popover
                v-if="!disabled"
                v-model="popoverVisible"
                popper-class="data-point-popover"
                placement="bottom"
                :title="$t('dataPoints.addDataPoint')"
                width="330">
                <el-form label-position="left" label-width="70px">
                  <el-form-item :label="$t('dataPoints.orderNumber')">
                    <el-input
                      v-model.number="orderNumber"
                      type="number"
                      :class="{'error': orderValueExist}"
                      :placeholder="orderValueExist"
                      @focus="orderValueExist=undefined">>
                    </el-input>
                  </el-form-item>
                  <el-form-item :label="$t('dataStreams.dataPoint')">
                    <emq-select
                      ref="dataPointIntId"
                      v-model="dataPointIntId"
                      :disabled="false"
                      :field="{
                        url: `/emq_select/data_points?productIntID=${this.$route.params.id}&streamDataType=2`,
                        rely: 'streamType',
                        relyName: $t('dataStreams.streamType'),
                      }"
                      :record="record">
                    </emq-select>
                  </el-form-item>
                </el-form>
                <div class="btn-bar" style="text-align: right;">
                  <el-button
                    type="text"
                    size="mini"
                    @click="popoverVisible=false">{{ $t('oper.cancel') }}
                  </el-button>
                  <el-button
                    type="success"
                    size="mini"
                    @click="addPointItem">{{ $t('oper.save') }}
                  </el-button>
                </div>
                <el-button
                  style="margin-right: 20px"
                  slot="reference"
                  type="success"
                  size="mini"
                  @click="showPopover">
                  + {{ $t('oper.add') }}
                </el-button>
              </el-popover>
              <template
                v-if="['create', 'edit'].includes(accessType) && record.dataPoints.length !== 0">
                <a
                  v-for="(tag, index) in record.dataPoints"
                  class="condition"
                  v-popover:editPopover
                  @click="editPointPopover(tag,index)"
                  style="float: none; display: inline-block;"
                  :key="index">
                  <el-tag
                    :closable="!disabled"
                    :close-transition="false"
                    @close="removePointItem(tag)"> {{ tag[1]+ ': ' + record.dataPointNames[index] }}
                  </el-tag>
                </a>
              </template>
              <template
                v-if="disabled && record.dataPoints.length !== 0">
                <router-link
                  style="float: none;"
                  v-for="(tag, index) in record.dataPoints"
                  :key="index"
                  :to="`/products/${productIntID}/data_points/${tag[0]}`">
                  <el-tag>
                    {{ tag[1]+ ': ' + record.dataPointNames[index] }}
                  </el-tag>
                </router-link>
              </template>
              <el-popover
                ref="editPopover"
                v-model="editPopoverVisible"
                popper-class="data-point-popover"
                placement="bottom"
                :title="$t('dataPoints.editDataPoint')"
                width="330">
                <el-form label-position="left" label-width="70px">
                  <el-form-item :label="$t('dataPoints.orderNumber')">
                    <el-input
                      v-model.number="orderNumber"
                      type="number"
                      :class="{'error': orderValueExist}"
                      :placeholder="orderValueExist"
                      @focus="orderValueExist=undefined">
                    </el-input>
                  </el-form-item>
                  <el-form-item :label="$t('dataStreams.dataPoint')">
                    <emq-select
                      ref="dataPointIntId"
                      v-model="dataPointIntId"
                      :disabled="false"
                      :field="{
                        url: `/emq_select/data_points?productIntID=${this.$route.params.id}&streamDataType=2`,
                        rely: 'streamType',
                        relyName: $t('dataStreams.streamType'),
                      }"
                      :record="record">
                    </emq-select>
                  </el-form-item>
                </el-form>
                <div class="btn-bar" style="text-align: right;">
                  <el-button
                    type="text"
                    size="mini"
                    @click="editPopoverVisible=false">{{ $t('oper.cancel') }}
                  </el-button>
                  <el-button
                    type="success"
                    size="mini"
                    @click="editPointItem">{{ $t('oper.save') }}
                  </el-button>
                </div>
              </el-popover>
            </el-form-item>
            <el-form-item v-if="accessType === 'view'" :label="$t('dataPoints.createAt')">
              <el-input
                v-model="record.createAt"
                :disabled="disabled">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('dataStreams.streamDataType')" prop="streamDataType">
              <emq-select
                v-model="record.streamDataType"
                :field="{ key: 'streamDataType' }"
                :record="record"
                :placeholder="disabled ? '' : $t('oper.select')"
                :disabled="accessType !== 'create'">
              </emq-select>
            </el-form-item>
            <el-form-item :label="$t('dataStreams.topic')" prop="topic">
              <el-input
                type="text"
                v-model="record.topic"
                :disabled="accessType !== 'create'">
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
        </el-form>
      </el-row>
      <emq-button v-if="!disabled" icon="save" @click="save">
        {{ $t('oper.done') }}
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
import { httpGet } from '@/utils/api'
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
    };
    return {
      url: '/data_streams',
      createVisable: false,
      record: {
        productIntID: this.$route.path.split('/')[2] || undefined,
        dataPoints: [],
        dataPointNames: [],
      },
      rules: {
        streamID: [
          { required: true, message: this.$t('dataStreams.streamIDRequired'), trigger: 'blur' },
        ],
        dataPoints: [
          { required: true, message: this.$t('dataStreams.dataPointRequired'), trigger: 'blur' },
        ],
        streamName: [
          { required: true, message: this.$t('dataStreams.streamNameRequired'), trigger: 'blur' },
        ],
        pointList: [
          { type: 'array', required: true, message: this.$t('dataStreams.dataPointRequired'), trigger: 'blur' },
        ],
        streamDataType: [
          { required: true, message: this.$t('dataStreams.streamDataTypeRequired'), trigger: 'blur' },
        ],
        streamType: [
          { required: true, message: this.$t('dataStreams.streamTypeRequired'), trigger: 'blur' },
        ],
        topic: [
          { validator: validateTopic, required: true, trigger: 'blur' },
        ],
      },
      dataPointsList: [], // Store a list of dataPoints for the current product
      popoverVisible: false,
      editPopoverVisible: false,
      orderNumber: undefined,
      orderValueExist: undefined,
      dataPointIntId: undefined,
      currentDataPoint: undefined,
      editPointIndex: undefined,
      localRecordName: 'dataStreams',
      toURL: `/products/${this.$route.params.id}/data_points/0?oper=create`,
    }
  },

  computed: {
    productIntID() {
      return this.$route.params.id
    },
    dataPointsShow() {
      if (this.currentProduct.productType === 2) {
        return ![1, 2].includes(this.record.streamType)
      }
      if (this.currentProduct.productType === 1) {
        return true
      }
      return false
    },
  },

  watch: {
    dataPointIntId: 'dataPointIntIdChange',
    'record.streamDataType': 'streamDataTypeChange',
  },

  methods: {
    // Load a dataPoints list for getting the dataPoint name
    loadDataPoint() {
      const url = `/data_points?productID=${this.currentProduct.productID}`
      httpGet(url).then((response) => {
        this.dataPointsList = response.data
        // Load data based on valued dependent fields
        if (this.record.streamType) {
          this.$refs.dataPointSelect.loadWithRely()
        }
      })
    },
    // Initialize the relevant value when popover pops up
    showPopover() {
      this.orderNumber = undefined
      this.orderValueExist = undefined
      this.dataPointIntId = undefined
      this.editPointIndex = undefined
    },
    streamDataTypeChange(newValue, oldValue) {
      if (oldValue && this.record.dataPoints && !this.disabled) {
        this.record.dataPoints = []
      }
    },
    dataPointIntIdChange() {
      this.currentDataPoint = this.dataPointsList.items.filter((row) => {
        return row.id === this.dataPointIntId
      })[0]
    },
    addPointItem() {
      if (!this.orderNumber) {
        this.orderValueExist = this.$t('dataStreams.orderNumberNotNull')
        return
      }
      if (this.record.dataPoints && this.record.dataPoints.some((row) => {
        return this.orderNumber === row[1]
      })) {
        this.orderNumber = undefined
        this.orderValueExist = this.$t('dataStreams.orderNumberRepeat')
        return
      }
      this.record.dataPointNames.push(this.currentDataPoint.dataPointName)
      this.record.dataPoints.push([this.dataPointIntId, this.orderNumber])
      this.popoverVisible = false
    },
    removePointItem(item) {
      this.record.dataPoints = this.record.dataPoints.filter((row) => {
        return row !== item
      })
    },
    // Initialize the dialog for editing the datapoint and pop up
    editPointPopover(item, index) {
      this.editPointIndex = index
      this.orderNumber = item[1]
      this.dataPointIntId = item[0]
      this.editPopoverVisible = true
    },
    editPointItem() {
      if (!this.orderNumber) {
        this.orderValueExist = this.$t('dataStreams.orderNumberNotNull')
        return
      }
      // Array updates need to be passed by value
      const dataPoints = [...this.record.dataPoints]
      const dataPointNames = [...this.record.dataPointNames]
      dataPoints[this.editPointIndex] = [this.dataPointIntId, this.orderNumber]
      dataPointNames[this.editPointIndex] = this.currentDataPoint.dataPointName
      this.record.dataPoints = dataPoints
      this.record.dataPointNames = dataPointNames
      this.editPopoverVisible = false
    },
    requestSuccess(response) {
      if (this.currentProduct.cloudProtocol === this.$variable.cloudProtocol.LWM2M
      || this.currentProduct.cloudProtocol === this.$variable.cloudProtocol.LORA) {
        this.detailsID = response.data.id
        this.createVisable = true
        return true
      }
      return false
    },
  },

  mounted() {
    this.loadDataPoint()
  },
}
</script>


<style lang="scss">
@import '~@/assets/scss/detailsPage.scss';

.data-stream-details-view {
  .data-point-input {
    .el-input {
      height: auto;
    }
  }
  .data-point-link a {
    .el-tag {
      cursor: pointer;
      margin-right: 4px;
    }
  }
  .data-points-binary {
    .el-tag {
      margin-right: 8px;
    }
  }
}
.data-point__button {
  position: absolute;
  top: 0;
  right: 40px;
  z-index: 1;
}
.data-point-popover {
  padding: 0;
  .el-popover__title {
    padding: 20px 30px;
    border-bottom: 1px solid #dfe0e4;
    font-size: 16px;
    color: #505050;
    margin-bottom: 20px;
    font-weight: normal;
  }
  .el-form {
    padding: 0 30px;
    .el-form-item {
      margin-bottom: 16px;
    }
  }
  .btn-bar {
    padding: 0 30px 20px;
  }
}
</style>
