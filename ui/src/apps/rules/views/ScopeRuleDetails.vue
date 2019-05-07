<template>
  <div class="details-view scope-rule-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/scope_rules` }">{{ $t('scopes.scopesRule') }}</el-breadcrumb-item>
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

          <!-- Topic, Maps and SQL -->
          <el-col :span="12">
            <el-form-item :label="$t('scopes.scopeType')" prop="scopeType">
              <emq-select
                v-model="record.scopeType"
                :field="{ key: 'scopeType' }"
                :record="record"
                :placeholder="disabled ? '' : $t('oper.select')"
                :disabled="disabled">
              </emq-select>
            </el-form-item>
            <el-form-item prop="scope" :label="$t('scopes.scope')">
              <el-input
                v-model="record.scope"
                :placeholder="disabled ? '' : $t('scopes.scopeRequired')"
                @focus="$refs.locationScopeEdit.dialogVisible = true"
                :disabled="disabled">
              </el-input>
            </el-form-item>
            <el-form-item prop="devices" :label="$t('rules.device')">
              <emq-search-select
                ref="deviceSelect"
                v-model="record.devices"
                class="multiple-select"
                multiple
                :placeholder="$t('oper.devicesSearch')"
                :field="{
                  url: `/emq_select/devices`,
                  searchKey: 'deviceName',
                }">
              </emq-search-select>
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

    <location-scope-edit-dialog
      ref="locationScopeEdit"
      :deviceLocation="[116.397477, 39.908692]"
      :locationScope="locationScope"
      :clearLocationScope="clearLocationScope"
      :confirm="locationScopeEditConfirm">
    </location-scope-edit-dialog>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import CodeEditor from '@/components/CodeEditor'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import LocationScopeEditDialog from '../components/LocationScopeEditDialog'

export default {
  name: 'scope-rule-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqSearchSelect,
    CodeEditor,
    LocationScopeEditDialog,
  },

  data() {
    return {
      url: '/rules',
      record: {
        sql: 'SELECT * FROM',
        ruleType: 2,
        scope: '',
      },
      localRecordName: 'scopeRuleRecord',
      toURL: '/actions/0?oper=create',
      center: [116.397477, 39.908692],
      locationScope: [],
      circles: [
        {
          center: [116.397477, 39.908692],
          radius: 0,
        },
      ],
      polygons: [
        {
          draggable: true,
          path: [],
        },
      ],
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
        scopeType: [
          { required: true, message: this.$t('scopes.scopeTypeRequired') },
        ],
        scope: [
          { required: true, message: this.$t('scopes.scopeRequired'), trigger: 'change' },
        ],
        devices: [
          { required: true, message: this.$t('rules.deviceRequired') },
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
    setSelectOptions() {
      if (this.record.actions) {
        this.$refs.actionsSelect.options = this.record.actions.map((value, index) => {
          return { value, label: this.record.actionNames[index] }
        })
      }
    },
    locationScopeEditConfirm() {
      this.$refs.locationScopeEdit.closeEdit()
      this.$refs.locationScopeEdit.dialogVisible = false
      if (this.$refs.locationScopeEdit.scope.length === 0) {
        this.record.scope = ''
      } else {
        this.record.scope = JSON.stringify(this.$refs.locationScopeEdit.scope)
      }
    },
    clearLocationScope() {
      this.locationScope = []
      this.record.scope = null
    },
  },
}
</script>


<style lang="scss">
.scope-rule-details-view {
  .el-card {
    .actions-btn {
      position: absolute;
      top: -40px;
      right: 0;
    }
  }
}
</style>
