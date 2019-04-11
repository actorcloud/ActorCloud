<template>
  <div class="message-rule-details details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/message_rules">{{ $t('rules.messageRule') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <el-card class="message-rules-details-body">
      <edit-toggle-button
        :url="url"
        :disabled="disabled"
        :accessType="accessType"
        @toggleStatus="toggleStatus">
      </edit-toggle-button>
      <el-row :gutter="50" :class="disabled ? 'is-details-form' : ''">
        <el-form
          ref="record"
          label-position="left"
          label-width="120px"
          :disabled="disabled"
          :model="record"
          :rules="disabled ? {} : formRules">
          <el-col :span="12">
            <el-form-item prop="ruleRelateType" :label="$t('rules.ruleRelateType')">
              <el-select v-model="record.ruleRelateType" :placrholder="disabled ? '' : $t('oper.select')">
                <el-option :label="$t('rules.products')" :value="1"></el-option>
                <el-option :label="$t('rules.groups')" :value="2"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col v-if="record.ruleRelateType === 1 && !disabled" :span="12">
            <el-form-item prop="productID" :label="$t('rules.productName')">
              <emq-search-select
                ref="productSelect"
                v-model="record.productID"
                :field="{
                  url: '/emq_select/products',
                  options: [{ value: record.productID, label: record.productName }],
                  searchKey: 'productName',
                }"
                :record="record"
                :placrholder="disabled ? '' : $t('oper.select')"
                :disabled="false">
              </emq-search-select>
            </el-form-item>
          </el-col>
          <el-col v-if="disabled" :span="12">
            <el-form-item :label="$t('rules.productName')">
              <el-input v-model="record.productName"></el-input>
            </el-form-item>
          </el-col>
          <el-col v-if="record.ruleRelateType === 2" :span="12">
            <el-form-item prop="groupID" :label="$t('rules.groupName')">
              <emq-search-select
                ref="groupSelect"
                v-model="record.groupID"
                :field="{
                  url: '/emq_select/groups',
                  options: [{ value: record.groupID, label: record.groupName }],
                  searchKey: 'groupName'
                }"
                :record="record"
                :placrholder="disabled ? '' : $t('oper.select')"
                :disabled="false">
              </emq-search-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="ruleType" :label="$t('rules.ruleType')">
              <el-popover
                placement="top-start"
                width="260"
                trigger="hover">
                <span>
                  {{ $t('rules.read') }}
                  <a href="https://docs.actorcloud.io/rule_engine/message_rules.html" target="_blank">
                    {{ $t('rules.document') }}
                  </a>{{ $t('rules.ruleDifference') }}
                </span>
                <i slot="reference" class="el-icon-question tips-icon" style="cursor: pointer;"></i>
              </el-popover>
              <emq-select
                v-model="record.ruleType"
                :field="{ key: 'ruleType' }"
                :record="record"
                :placrholder="disabled ? '' : $t('oper.select')"
                :disabled="false">
              </emq-select>
            </el-form-item>
          </el-col>
          <!-- Webhook configuration-->
          <div v-if="record.ruleType === 1 && record.config">
            <!-- Webhook type -->
            <el-col v-if="record.ruleType === 1" :span="12">
              <el-form-item prop="config.type" :label="$t('rules.webhookType')">
                <emq-select
                  v-model="record.config.type"
                  :field="{ key: 'webhookType' }"
                  :record="record"
                  :placrholder="disabled ? '' : $t('oper.select')"
                  :disabled="false">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.url" label="URL">
                <el-input
                  v-model="record.config.url"
                  :placrholder="disabled ? '' : $t('rules.url')">
                </el-input>
              </el-form-item>
            </el-col>
            <!-- Webhook private configuration -->
            <div v-if="record.config.type === 1">
              <el-col :span="12">
                <el-form-item prop="config.token" label="Token">
                  <el-input
                    v-model="record.config.token"
                    :placrholder="disabled ? '' : 'token'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
            </div>
            <!-- Webhook special configuration -->
            <div v-if="[2, 3].includes(record.config.type)">
              <el-col :span="12">
                <el-form-item prop="config.appId" :label="$t('rules.appId')">
                  <el-input
                    v-model="record.config.appId"
                    :placrholder="disabled ? '' : $t('rules.appId')"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="config.appKey" :label="$t('rules.appKey')">
                  <el-input
                    v-model="record.config.appKey"
                    :placrholder="disabled ? '' : $t('rules.appKey')"></el-input>
                </el-form-item>
              </el-col>
            </div>
          </div>
          <div v-if="accessType === 'view'" class="message-risk-info">
            <el-col :span="12">
              <el-form-item :label="$t('rules.createUser')">
                <el-input v-model="record.createUser"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('rules.createAt')">
                <el-input v-model="record.createAt"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('rules.updateAt')">
                <el-input v-model="record.updateAt"></el-input>
              </el-form-item>
            </el-col>
          </div>
          <el-col :span="12">
            <el-form-item prop="remark" :label="$t('rules.remark')">
              <el-input v-model="record.remark"></el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>

      <emq-button v-if="!disabled" icon="save" @click="save">
        {{ $t('oper.finish') }}
      </emq-button>
    </el-card>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'message-rule-details',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqSearchSelect,
  },

  data() {
    return {
      url: '/message_rules',
      record: {
        config: {},
      },
      formRules: {
        ruleRelateType: [
          { required: true, message: this.$t('rules.ruleRelateTypeRequired') },
        ],
        productID: [
          { required: true, message: this.$t('rules.productRequired') },
        ],
        groupID: [
          { required: true, message: this.$t('rules.groupRequired') },
        ],
        ruleType: [
          { required: true, message: this.$t('rules.ruleTypeRequired') },
        ],
        config: {
          type: [
            { required: true, message: this.$t('rules.webhookTypeRequired') },
          ],
          url: [
            { required: true, message: this.$t('rules.urlRequired') },
          ],
          token: [
            { required: true, message: this.$t('rules.tokenRequired') },
          ],
          appId: [
            { required: true, message: this.$t('rules.appIdRequired') },
          ],
          appKey: [
            { required: true, message: this.$t('rules.appKeyRequired') },
          ],
        },
      },
    }
  },

  methods: {
    processLoadedData(record) {
      // Associated object, prioritize whether to associate groups
      this.$set(record, 'ruleRelateType', record.groupID ? 2 : 1)
    },
    beforePostData(record) {
      // Determine the type based on this field, empty useless key fields
      const willDeleteKey = record.ruleRelateType === 1 ? 'groupID' : 'productID'
      delete record[willDeleteKey]
    },
  },
}
</script>


<style lang="scss">
.message-rule-details {
  .el-select {
    width: 100%;
  }
  .el-form-item__content {
    position: relative;
    .tips-icon {
      position: absolute;
      z-index: 100;
      top: 13px;
      left: -55px;
    }
  }
}
</style>
