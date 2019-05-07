<template>
  <div class="details-view business-rule-details-view">
    <!-- Hide copy text -->
    <input
      v-model="clipboardContent"
      type="text"
      id="clipboard">

    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/business_rules` }">{{ $t('rules.businessRule') }}</el-breadcrumb-item>
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
      <el-row :gutter="50">
        <el-form
          ref="record"
          :label-position="disabled ? 'left' : 'top'"
          :label-width="disabled ? '100px' : null"
          :model="record"
          :rules="accessType === 'view' ? {} : formRules">

          <!-- Rules base form -->
          <el-col :span="12">
            <el-form-item prop="ruleName" :label="$t('rules.ruleName')">
              <el-input
                v-model="record.ruleName"
                :placeholder="$t('rules.ruleNameRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="enable" :label="$t('rules.enable')">
              <emq-select
                ref="enable"
                v-model="record.enable"
                :field="{ key: 'certEnable' }"
                :record="record"
                :disabled="disabled">
              </emq-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="actions" :label="$t('rules.action')">
              <span v-if="!disabled && has('POST,/actions')" class="actions-btn">
                {{ $t('oper.or') }}&nbsp;
                <a href="javascript:;" @click="newAnotherPageData">{{ $t('rules.addAction') }}</a>
              </span>
              <emq-search-select
                v-if="['create', 'edit'].includes(accessType)"
                ref="actionsSelect"
                v-model="record.actions"
                multiple
                :placeholder="$t('rules.actionRequired')"
                :disabled="disabled"
                :field="{
                  url: '/emq_select/actions',
                  searchKey: 'actionName',
                  state: accessType,
                }"
                :record="record">
              </emq-search-select>
              <div v-else class="action-link">
                <router-link
                  style="float: none;"
                  v-for="(action, actionIndex) in record.actions"
                  :key="actionIndex"
                  :to="`/actions/${action}`">
                  <el-tag
                    size="small">
                    {{ record.actionNames[actionIndex] }}
                  </el-tag>
                </router-link>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="remark" :label="$t('rules.remark')">
              <el-input
                v-model="record.remark"
                :type="disabled ? 'text' : 'textarea'"
                :placeholder="disabled ? '' : $t('rules.remarkRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="24" class="split-line"></el-col>
        </el-form>

        <el-form
          ref="formTopicSql"
          label-position="top"
          :model="record"
          :rules="accessType === 'view' ? {} : formRules">

          <!-- Topic and SQL -->
          <el-col :span="12">
            <el-form-item
              class="topic-list"
              prop="fromTopics"
              :label="$t('rules.fromTopic')">
              <el-button
                round
                class="topic-create__btn"
                type="success"
                size="mini"
                :disabled="disabled"
                @click="addTopics">
                + {{ $t('rules.addTopic') }}
              </el-button>
              <el-scrollbar>
                <topic-form
                  v-for="(item, index) in record.fromTopics"
                  ref="topicForm"
                  class="topic-wrap"
                  :topicRecord="item"
                  :disabled="disabled"
                  :accessType="accessType"
                  :index="index"
                  :key="index"
                  @copy="copyText"
                  @remove="removeTopics">
                </topic-form>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="sql" label="SQL" class="code-sql">
              <code-editor
                class="code-editor__reset code-sql__editor"
                height="480px"
                lang="text/x-sql"
                v-model="record.sql"
                :disabled="disabled">
              </code-editor>
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
import CodeEditor from '@/components/CodeEditor'
import TopicForm from '../components/TopicForm'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'business-rule-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqSearchSelect,
    CodeEditor,
    TopicForm,
  },

  data() {
    return {
      url: '/rules',
      record: {
        sql: 'SELECT * FROM',
        fromTopics: [],
        ruleType: 1,
      },
      clipboardContent: '',
      localRecordName: 'businessRuleRecord',
      toURL: '/actions/0?oper=create',
      formRules: {
        ruleName: [
          { required: true, message: this.$t('rules.ruleNameRequired') },
        ],
        enable: [
          { required: true, message: this.$t('rules.enableRequired') },
        ],
        actions: [
          { required: true, message: this.$t('rules.actionRequired') },
        ],
        fromTopics: [
          { required: true, message: this.$t('rules.fromTopicRequired') },
        ],
        sql: [
          { required: true, message: this.$t('rules.sqlRequired') },
        ],
      },
    }
  },

  watch: {
    disabled() {
      if (!this.disabled) {
        this.$nextTick(() => { // After DOM updated
          this.setSelectOptions()
        })
      }
    },
  },

  methods: {
    processLoadedData() {
      if (this.accessType === 'edit') {
        this.setSelectOptions()
      }
    },
    validateSubForm(record) {
      let isValidatePass = false
      this.$refs.formTopicSql.validate((valid) => {
        if (!valid) {
          return false
        }
        const { fromTopics } = record
        const checkValidate = (val) => {
          isValidatePass = fromTopics.every(item => item[val])
          return isValidatePass
        }
        if (!checkValidate('productID')) {
          this.$message.error(this.$t('rules.productRequired'))
          return false
        }
        if (!checkValidate('deviceID')) {
          this.$message.error(this.$t('rules.deviceRequired'))
          return false
        }
        if (!checkValidate('topic')) {
          this.$message.error(this.$t('rules.lastTopicRequired'))
          return false
        }
        isValidatePass = true
        return true
      })
      return isValidatePass
    },
    addTopics() {
      this.record.fromTopics.push({})
    },
    removeTopics(index) {
      this.record.fromTopics.splice(index, 1)
    },
    copyText(content) {
      this.clipboardContent = content
    },
    setSelectOptions() {
      if (this.record.actions) {
        this.$refs.actionsSelect.options = this.record.actions.map((value, index) => {
          return { value, label: this.record.actionNames[index] }
        })
      }
    },
  },

  created() {
    if (this.accessType === 'create') {
      // If it's a create page, add a topic by default
      this.addTopics()
    }
  },
}
</script>


<style lang="scss">
.business-rule-details-view {
  #clipboard {
    position: absolute;
    z-index: -1;
  }

  .el-card {
    .actions-btn {
      position: absolute;
      top: -40px;
      right: 0;
    }

    .topic-list {
      .el-scrollbar {
        height: 480px;
        width: 102%;
        overflow: hidden;
        padding-right: 0;
      }

      .topic-form.topic-wrap {
        margin-right: 15px;
      }

      .topic-create__btn {
        background-color: var(--color-main-green);
        float: right;
        margin-top: -36px;
        margin-bottom: 10px;
        font-size: 12px;
      }
    }
  }
}
</style>
