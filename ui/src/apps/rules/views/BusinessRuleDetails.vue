<template>
  <div class="details-view business-rule-details-view">
    <!-- Hide copy text -->
    <input
      v-model="clipboardContent"
      type="text"
      id="clipboard">

    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/business_rules/business_rules` }">{{ $t('rules.businessRule') }}</el-breadcrumb-item>
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
          label-position="top"
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
              <span v-if="!disabled && has('POST,/actions')" class="role-button">
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
                  :to="`/business_rules/actions/${action}`">
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
                :placeholder="$t('rules.remarkRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="24" class="split-line"></el-col>

          <!-- Topic and SQL -->
          <el-col :span="12">
            <el-form-item
              class="topic-list"
              prop="fromTopics"
              :label="$t('rules.fromTopic')">
              <emq-button
                class="topic-create__btn"
                size="small"
                icon="create"
                @click="addTopics">
                {{ $t('rules.addTopic') }}
              </emq-button>
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
                v-model="record.sql">
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
      url: '/business_rules',
      record: {
        sql: 'SELECT',
        fromTopics: [{}],
      },
      clipboardContent: '',
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

  methods: {
    addTopics() {
      this.record.fromTopics.push({})
    },
    removeTopics(index) {
      this.record.fromTopics.splice(index, 1)
    },
    copyText(content) {
      this.clipboardContent = content
    },
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
    .role-button {
      position: absolute;
      top: -40px;
      right: 0;
    }

    .split-line {
      margin: 20px -5px;
      height: 2px;
      background: var(--color-line-card);
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
        width: 100px;
        margin-top: -34px;
        margin-bottom: 15px;
        height: 27px;
        padding: 0px;
      }
    }

    .code-sql {
      .el-form-item__content {
        line-height: 18px;
        .code-sql__editor {
          border: 1px solid var(--color-line-card);
          border-radius: 6px;
          .CodeMirror {
            border-radius: 6px;
          }
        }
      }
    }
  }
}
</style>
