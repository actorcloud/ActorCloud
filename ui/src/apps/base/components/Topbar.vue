<template>
  <div>
    <div class="topbar">

      <div class="site-title">
        <a href="/">
          <img alt="logo" :src="logo"/>
          <!-- <img alt="logo" src="../assets/images/logo-darkTheme.png"> -->
        </a>
      </div>
      <div class="search-bar">
        <el-select
          v-model="searchValue"
          size="medium"
          remote
          filterable
          clearable
          class="el-icon-search"
          placeholder="设备/网关 名称搜索"
          :remote-method="search"
          :loading="selectLoading"
          @focus="search('', reload = true)">
          <el-option
            v-for="option in options"
            :key="option.id"
            :label="option.label"
            :value="option.value">
          </el-option>
        </el-select>
      </div>
      <!--<img v-show="$store.state.base.loading" src="../assets/svg/loading.svg" class="loading" />-->

      <div class="topbar-right">
        <a
          v-if="showProductsMall"
          href="javascript:;"
          :class="['top-link', 'mall-link-visible',
            ($route.path.split('/')[1]) === 'products_mall' ? 'is-select' : '']"
          @click="$router.push({ path: '/products_mall' })">
          产品商城
        </a>
        <a href="http://docs.actorcloud.io"
           target="_blank"
           :class="['top-link', showProductsMall ? '' : 'mall-link-disabled']">
          文 档
        </a>
        <div class="notifications-box">
          <a href="javascript:;" @click="messageVisible = !messageVisible">
            <i class="material-icons" :class="messageVisible ? 'is-noticed' : ''">
              notifications_none
            </i>
          </a>
        </div>
        <el-dropdown trigger="click" :show-timeout="0" @command="handleCommand">
          <span class="el-dropdown-link">
            {{ user.username }}
            <i class="el-icon-caret-bottom el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item v-if="user.tenantType === 2" command="changeCompanyInfo">
              公司信息
            </el-dropdown-item>
            <el-dropdown-item command="changePassword">
              修改密码
            </el-dropdown-item>
            <el-dropdown-item command="toggleTheme">
              切换主题
            </el-dropdown-item>
            <el-dropdown-item command="logout" class="logout">
              登出
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!-- Change password dialog -->
    <emq-dialog
      title="修改密码"
      :saveLoading="btnLoading"
      :visible.sync="passwrodDialogVisible"
      @confirm="changePassword"
      @close="resetFields">
      <el-form
        ref="changePasswordForm"
        :model="changePasswordForm"
        :rules="changePasswordRules">
        <el-form-item prop="oldPassword">
          <el-input
            v-model="changePasswordForm.oldPassword"
            size="medium"
            type="password"
            placeholder="旧密码">
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="changePasswordForm.password"
            size="medium"
            type="password"
            placeholder="新密码">
          </el-input>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="changePasswordForm.confirmPassword"
            size="medium"
            type="password"
            placeholder="密码确认">
          </el-input>
        </el-form-item>
      </el-form>
    </emq-dialog>

    <!-- Company information dialog -->
    <emq-dialog
      title="公司信息"
      class="topbar-dialog"
      width="480"
      :saveLoading="btnLoading"
      :visible.sync="companyInfoDialogVisible"
      @confirm="changeCompanyInfo">
      <el-form
        ref="currentCompany"
        :model="currentCompany"
        :rules="changeCompanyInfoRules">
        <el-form-item label="公司名称" prop="company">
          <el-input
            v-model="currentCompany.company"
            size="medium"
            type="text"
            disabled>
          </el-input>
        </el-form-item>
        <el-form-item label="联系邮箱" prop="contactEmail">
          <el-input
            v-model="currentCompany.contactEmail"
            size="medium"
            type="text">
          </el-input>
        </el-form-item>
        <el-form-item label="联系人" prop="contactPerson">
          <el-input
            v-model="currentCompany.contactPerson"
            size="medium"
            type="text">
          </el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="contactPhone">
          <el-input
            v-model="currentCompany.contactPhone"
            size="medium"
            type="text">
          </el-input>
        </el-form-item>
        <el-form-item label="网站Logo (浅色主题使用，推荐360 * 72)" prop="logo">
          <emq-upload
            ref="fileUpload"
            v-model="currentCompany.logo"
            listType="picture"
            :field="{ type: 'uploadPhoto', url: '/api/v1/upload?fileType=image', limit: 1, }"
            :appendToBody="true">
          </emq-upload>
        </el-form-item>
        <el-form-item label="网站Logo (深色主题使用，推荐360 * 72)" prop="logo">
          <emq-upload
            ref="fileUpload"
            v-model="currentCompany.logoDark"
            listType="picture"
            :field="{ type: 'uploadPhoto', url: '/api/v1/upload?fileType=image', limit: 1, }"
            :appendToBody="true">
          </emq-upload>
        </el-form-item>
      </el-form>
    </emq-dialog>

    <!-- Switch theme dialog -->
    <emq-dialog
      title="切换主题"
      :saveLoading="btnLoading"
      :visible.sync="themeDialogVisible"
      @confirm="toggleTheme"
      @close="resetTheme">
      <el-radio v-model="theme" label="light">浅色主题</el-radio>
      <el-radio v-model="theme" label="dark">深色主题</el-radio>
    </emq-dialog>

    <!-- Message Center -->
    <message-rightbar :messageVisible.sync="messageVisible"></message-rightbar>
  </div>
</template>


<script>
import { SHA256 } from 'crypto-js'
import { mapActions } from 'vuex'

import { httpPut, httpGet } from '@/utils/api'
import EmqDialog from '@/components/EmqDialog'
import EmqUpload from '@/components/EmqUpload'
import MicroApps from '@/assets/micro.apps.json'
import MessageRightbar from './MessageRightbar'

export default {
  name: 'topbar',

  components: {
    EmqDialog,
    MessageRightbar,
    EmqUpload,
  },

  data() {
    return {
      logoSrc: '',
      leftbarWidth: this.$store.state.base.leftbar.width,
      companyInfoDialogVisible: false,
      passwrodDialogVisible: false,
      themeDialogVisible: false,
      theme: this.$store.state.base.currentTheme,
      btnLoading: false,
      messageVisible: false,
      currentCompany: {},
      searchValue: '',
      options: [],
      selectLoading: false,
      changePasswordForm: {
        oldPassword: '',
        password: '',
        confirmPassword: '',
      },
      changePasswordRules: {
        oldPassword: [
          { required: true, message: '请输入旧密码' },
          { min: 6, message: '密码长度必须为6位以上字符' },
        ],
        password: [
          { required: true, message: '请输入新密码' },
          { min: 6, message: '密码长度必须为6位以上字符' },
        ],
        confirmPassword: [
          { required: true, validator: this.validatePassword },
          { min: 6, message: '密码长度必须为6位以上字符' },
        ],
      },
      changeCompanyInfoRules: {
        contactEmail: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur,change' },
        ],
      },
    }
  },

  computed: {
    showProductsMall() {
      return MicroApps.includes('products-mall')
    },
    user() {
      return this.$store.state.accounts.user
    },
    logo() {
      const currentTheme = this.$store.state.base.currentTheme
      const fileName = currentTheme === 'dark' ? 'userLogoDark' : 'userLogo'
      return this.$store.state.base[fileName]
    },
  },

  watch: {
    searchValue: 'jumpPage',
    '$route.path': 'pathChange',
  },

  methods: {
    ...mapActions(['USER_LOGOUT', 'USER_LOGIN', 'CLEAR_BASE', 'LEFTBAR_SWITCH', 'THEME_SWITCH']),
    // Left navigation switch
    leftbarSwitch() {
      this.leftbarWidth = this.leftbarWidth === 'wide' ? 'narrow' : 'wide'
      this.LEFTBAR_SWITCH({ leftbar: { width: this.leftbarWidth } })
    },
    // Top right menu command
    handleCommand(command) {
      if (command === 'changeCompanyInfo') {
        this.getCompanyInfo()
        this.companyInfoDialogVisible = true
      }
      if (command === 'changePassword') {
        this.changePasswordForm = {}
        this.passwrodDialogVisible = true
      }
      if (command === 'toggleTheme') {
        this.themeDialogVisible = true
      }
      if (command === 'logout') {
        this.logout()
      }
    },
    // Change Password
    changePassword() {
      this.$refs.changePasswordForm.validate((valid) => {
        if (!valid) {
          return false
        }
        const data = {
          oldPassword: SHA256(this.changePasswordForm.oldPassword)
            .toString(),
          password: SHA256(this.changePasswordForm.password)
            .toString(),
        }
        this.btnLoading = true
        httpPut('/reset_password', data)
          .then(() => {
            this.$message.success('修改密码成功')
            this.logout()
            this.btnLoading = false
            this.dialogVisible = false
          })
          .catch(() => {
            this.btnLoading = false
            this.dialogVisible = false
          })
      })
    },
    // Verification confirmation password
    validatePassword(rule, value, callback) {
      if (!this.changePasswordForm.confirmPassword) {
        callback(new Error('请输入确认密码'))
        return
      }
      if (this.changePasswordForm.password !== this.changePasswordForm.confirmPassword) {
        callback(new Error('前后密码不一致'))
        return
      }
      callback()
    },
    // Get company information
    getCompanyInfo() {
      const user = JSON.parse(sessionStorage.getItem('user'))
        || JSON.parse(localStorage.getItem('user'))
      this.userCompanyId = user.companyID
      httpGet('/tenant_info')
        .then((response) => {
          this.currentCompany = response.data
        })
    },
    // Modify company information
    changeCompanyInfo() {
      this.$refs.currentCompany.validate((valid) => {
        if (!valid) {
          return false
        }
        const tenantInfo = { ...this.currentCompany }
        delete tenantInfo.company
        this.btnLoading = true
        httpPut('/tenant_info', tenantInfo)
          .then((response) => {
            if (response.status === 200) {
              this.$message.success('修改成功！')
              this.btnLoading = false
              this.companyInfoDialogVisible = false
            }
          })
          .catch(() => {
            this.btnLoading = false
          })
      })
    },
    // Reset verification status
    resetFields() {
      this.$refs.changePasswordForm.resetFields()
    },
    // Sign out
    logout() {
      this.USER_LOGOUT()
      this.CLEAR_BASE()
      this.$router.push({ path: '/login' })
    },
    // Remote search device
    search(query, reload = false) {
      const params = {}
      // Click to load the device when no device is selected
      if (reload && this.searchValue) {
        return
      }
      if (!reload && !query) {
        return
      }
      this.selectLoading = true
      // Search delay
      clearTimeout(this.timer)
      this.timer = setTimeout(() => {
        this.options = []
        params.deviceName_like = query
        httpGet('/emq_select/overview/clients', { params })
          .then((response) => {
            response.data.forEach((record) => {
              const option = {
                label: record.label,
                value: record.value,
                type: record.attr.type,
              }
              const existOption = this.options.filter((row) => {
                return row.value === option.value
              })
              if (existOption.length === 0) {
                this.options.push(option)
              }
            })
            this.selectLoading = false
          })
      }, 200)
    },
    jumpPage(newID) {
      if (newID === '') {
        return
      }
      const device = this.options.find(item => item.value === newID)
      if (device.type === 1) {
        this.$router.push({ path: `/devices/devices/${newID}`, query: { oper: 'view' } })
      } else if (device.type === 2) {
        this.$router.push({ path: `/devices/gateways/${newID}`, query: { oper: 'view' } })
      }
    },
    // Determine if you need to clear the search box when the url changes.
    pathChange(newValue) {
      if (newValue.indexOf('/devices/gateways/') !== -1) {
        return
      }
      if (newValue.indexOf('/devices/devices/') !== -1) {
        return
      }
      this.searchValue = ''
    },
    // Switch theme
    toggleTheme() {
      const currentTheme = this.$store.state.base.currentTheme
      if (this.theme === currentTheme) {
        return
      }
      this.THEME_SWITCH({ currentTheme: this.theme })
      this.$emit('setTheme')

      this.themeDialogVisible = false
    },
    // Cancel switching topic, restore default
    resetTheme() {
      this.theme = this.$store.state.base.currentTheme
    },
    // Load logo
    loadLogo() {
      const currentTheme = this.$store.state.base.currentTheme
      const fileName = currentTheme === 'dark' ? 'userLogoDark' : 'userLogo'
      this.logoSrc = this.$store.state.base[fileName]
    },
  },
}
</script>


<style lang="scss">
@import "~@/assets/scss/variable.scss";

.topbar {
  position: fixed;
  overflow: hidden;
  top: 0;
  left: 0;
  right: 0;
  @media screen and (max-width: 1366px) {
    height: $topbar-height-small;
  }
  height: $topbar-height;

  padding: 0 28px 0 18px;
  background-color: var(--color-topbar-bg);
  z-index: 1003;
  box-shadow: 0 0 20px -1px var(--color-shadow);
  /* flex */
  display: flex;
  align-items: center;
  justify-content: space-between;

  .site-title {
    img {
      width: 160px;
    }
  }

  /*.loading {*/
  /*position: absolute;*/
  /*top: 8px;*/
  /*width: 72px;*/
  /*height: 40px;*/
  /*}*/

  .search-bar {
    width: 32%;
    min-width: 320px;
    .el-select {
      width: 100%;
    }
    .el-icon-search:before {
      position: absolute;
      z-index: 1;
      top: 50%;
      transform: translateY(-50%);
      font-size: 18px;
      left: 14px;
      color: var(--color-topbar-text);
    }
    .el-input {
      .el-input__inner {
        height: 38px;
        line-height: 38px;
        border-radius: 38px;
        padding-left: 40px;
        background-color: var(--color-topbar-input-bg);
        border: none;
        color: var(--color-topbar-text);
        &::-webkit-input-placeholder {
          color: var(--color-topbar-text);
        }
      }
      .el-select__caret {
        color: var(--color-topbar-text);
        &.is-show-close:hover {
          color: var(--color-topbar-text);
        }
      }
      .el-input__icon {
        line-height: 38px;
      }
      .el-input__prefix {
        left: 10px;
      }
    }
    &:hover {
      .el-input {
        .el-input__inner {
          background-color: var(--color-topbar-input-bg);
        }
      }
    }

    @media screen and (max-width: 1366px) {
      .el-input {
        .el-input__inner {
          height: 32px;
          line-height: 32px;
          border-radius: 32px;
        }
        .el-input__icon {
          line-height: 32px;
        }
      }
    }
  }

  .topbar-right {
    font-size: $topbar-font-size;
    @media screen and (max-width: 1366px) {
      font-size: $topbar-font-size-small;
    }
    display: inline-block;
    .material-icons {
      vertical-align: middle;
      color: var(--color-topbar-text);
    }
    .el-dropdown {
      margin-left: 18px;
      font-size: $topbar-font-size;
      @media screen and (max-width: 1366px) {
        font-size: $topbar-font-size-small;
      }
      color: var(--color-topbar-text);
    }
    .el-dropdown-link {
      cursor: pointer;
    }
    .top-link {
      margin-right: 20px;
      color: var(--color-topbar-text);
      &:hover {
        color: var(--color-topbar-text);
      }
    }
    .is-select {
      font-weight: 800;
    }
    .notifications-box {
      display: inline-block;
      .is-noticed {
        font-weight: 800;
      }
    }
  }
}
.el-dropdown-menu {
  background-color: var(--color-bg-card);
  border-color: var(--color-bg-card);
  -webkit-box-shadow: 0 2px 12px 0 var(--color-shadow);
  box-shadow: 0 2px 12px 0 var(--color-shadow);
  .el-dropdown-menu__item {
    color: var(--color-text-light);
    &:not(.is-disabled):hover {
      color: var(--color-main-green);
      background-color: transparent;
    }
  }
  &.el-popper[x-placement^="bottom"] .popper__arrow {
    border-bottom-color: var(--color-bg-card);
    &::after {
      border-bottom-color: var(--color-bg-card);
    }
  }
}
.el-select-dropdown {
  background-color: var(--color-bg-card);
  border-color: var(--color-bg-card);
  -webkit-box-shadow: 0 2px 12px 0 var(--color-shadow);
  box-shadow: 0 2px 12px 0 var(--color-shadow);
  .el-select-dropdown__item {
    color: var(--color-text-light);
    &:not(.is-disabled):hover, &.hover, &.selected {
      color: var(--color-main-green);
      background-color: transparent;
    }
  }
  &.el-popper[x-placement^="bottom"] .popper__arrow {
    border-bottom-color: var(--color-bg-card);
    &::after {
      border-bottom-color: var(--color-bg-card);
    }
  }
}

.topbar-dialog {
  .el-upload-list--picture .el-upload-list__item-thumbnail {
    width: 200px;
  }
  .el-upload-list__item-name {
    padding-left: 20px;
  }
}
.emq-dialog .el-dialog__body {
  padding: 20px;
}
.el-radio {
  .el-radio__label {
    color: var(--color-text-lighter);
  }
  .el-radio__inner {
    background-color: var(--color-checkbox-inner);
  }
}
</style>
