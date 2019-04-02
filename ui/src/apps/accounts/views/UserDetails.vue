<template>
  <div class="user-details-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/users/users` }">{{ $t('users.user') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div class="user-card-details-body">
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
            label-position="left"
            label-width="110px"
            :model="record"
            :rules="accessType !== 'view' ? formRules : {}">
            <el-col :span="12">
              <el-form-item prop="username" :label="$t('users.username')">
                <el-input
                  v-model="record.username"
                  :placeholder="disabled ? '' : $t('users.usernameRequired')"
                  :disabled="accessType !== 'create'">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="email" :label="$t('users.email')">
                <el-input
                  v-model="record.email"
                  :placeholder="disabled ? '' : $t('users.emailRequired')"
                  :disabled="accessType !== 'create'">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'create'" :span="12">
              <el-form-item prop="password" :label="$t('users.password')">
                <el-input
                  v-model="record.password"
                  type="password"
                  :placeholder="disabled ? '' : $t('users.passwordRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="roleIntID" :label="$t('users.roleIntID')">
                <span v-if="!disabled && has('POST,/roles')" class="role-button">
                  {{$t('oper.or')}}&nbsp;
                  <a href="javascript:;" @click="newAnotherPageData">
                    {{ $t('applications.createRoles') }}
                  </a>
                </span>
                <emq-select
                  v-if="['create', 'edit'].includes(accessType)"
                  v-model="record.roleIntID"
                  :field="{ url: '/emq_select/roles' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('users.select')"
                  :disabled="disabled">
                </emq-select>
                <router-link
                  v-else
                  style="float: none;"
                  :to="{
                    path: `/roles/${record.roleIntID}`,
                    query: { oper: 'view', url: '/roles' }
                  }">
                  {{ record.roleName }}
                </router-link>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="enable" :label="$t('users.enable')">
                <emq-select
                  v-model="record.enable"
                  :field="{ key: 'enable'}"
                  :record="record"
                  :placeholder="disabled ? '' : $t('users.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="userAuthType" label="可管理标签">
                <emq-select
                  v-model="record.userAuthType"
                  :field="{
                    options: [
                      { label: '所有标签', value: 1 },
                      { label: '部分标签', value: 2 }
                    ]
                  }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('users.select')"
                  :disabled="disabled">
                  </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-show="record.userAuthType === 2" :span="12">
              <el-form-item prop="tags" label="标签权限" style="height: 41px;">
                <emq-search-select
                  v-if="!disabled"
                  ref="tagsSelect"
                  v-model="record.tags"
                  multiple
                  :placeholder="disabled ? '' : '请输入标签名称搜索'"
                  :field="{
                    url: '/emq_select/tags',
                    searchKey: 'tagName',
                    state: accessType,
                  }"
                  :record="record"
                  :disabled="false">
                </emq-search-select>
                <div v-if="disabled" class="link">
                  <router-link
                    style="float: none;"
                    v-for="tag in record.tagIndex"
                    :key="tag.value"
                    to="">
                    <el-tag size="small">
                      {{ tag.label }}
                    </el-tag>
                  </router-link>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="phone" :label="$t('users.phone')">
                <el-input
                  v-model="record.phone"
                  :placeholder="disabled ? '' : $t('users.tel')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="expiresAt" :label="$t('users.expiresAt')">
                <el-date-picker
                  v-model="record.expiresAt"
                  type="datetime"
                  value-format="yyyy-MM-dd HH:mm:ss"
                  :placeholder="$t('users.neverExpire')"
                  :picker-options="pickerOption"
                  :disabled="disabled">
                </el-date-picker>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item prop="createAt" :label="$t('users.createAt')">
                <el-input
                  v-model="record.createAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button v-if="!disabled" icon="save" @click="save">
          {{ $t('users.done') }}
        </emq-button>
      </el-card>
    </div>
  </div>
</template>


<script>
import { SHA256 } from 'crypto-js'
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'user-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
    EmqSearchSelect,
  },

  data() {
    return {
      url: '/users',
      record: {
        userAuthType: 1,
        tags: [],
      },
      formRules: {
        username: [
          { required: true, message: this.$t('users.usernameRequired') },
        ],
        password: [
          { required: true, message: this.$t('users.passwordRequired') },
          { min: 6, message: this.$t('users.passwordLength'), trigger: 'blur,change' },
        ],
        email: [
          { required: true, message: this.$t('users.emailRequired') },
          { type: 'email', message: this.$t('users.emailIllegal') },
        ],
        roleIntID: [
          { required: true, message: this.$t('users.roleRequired') },
        ],
        enable: [
          { required: true, message: this.$t('users.optionRequired') },
        ],
        userAuthType: [
          { required: true, message: '请选择标签管理' },
        ],
      },
      pickerOption: {
        disabledDate(time) {
          return time.getTime() < Date.now()
        },
      },
      localRecordName: 'userRecord',
      toURL: '/roles/0?oper=create&url=%2Froles',
    }
  },

  watch: {
    accessType(newValue) {
      if (newValue === 'edit') {
        setTimeout(() => { this.processLoadedData(this.record) }, 100)
      }
    },
  },

  methods: {
    processLoadedData(record) {
      // Modify the value of the options selected，Displays label when editing
      if (this.$refs.tagsSelect) {
        this.$refs.tagsSelect.options = record.tags.map((value, index) => {
          return { value, label: record.tagIndex[index].label }
        })
      }
      // After saves the data, go back to the view page
      this.isRenderToList = false
    },

    // Encrypt the password before post data
    beforePostData(data) {
      data.password = SHA256(data.password).toString()
    },
  },
}
</script>


<style lang="scss">
.user-details-view {
  .role-button {
    position: absolute;
    top: 0;
    right: 40px;
    z-index: 1;
  }
  .link a {
    .el-tag {
      cursor: pointer;
      margin-right: 4px;
    }
  }
}
</style>
