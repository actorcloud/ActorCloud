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
          :placeholder="$t('topBar.searchPlaceholder')"
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
      <!--<img v-show="$store.state.accounts.loading" src="../assets/svg/loading.svg" class="loading" />-->

      <div class="topbar-right">
        <a
          v-if="showProductsMall"
          href="javascript:;"
          :class="['top-link', 'mall-link-visible',
            ($route.path.split('/')[1]) === 'products_mall' ? 'is-select' : '']"
          @click="$router.push({ path: '/products_mall' })">
          {{ $t('topBar.productMall') }}
        </a>
        <a :href="`http://docs.actorcloud.io/${language}`"
           target="_blank"
           :class="['top-link', showProductsMall ? '' : 'mall-link-disabled']">
          {{ $t('topBar.document') }}
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
              {{ $t('topBar.companyInfo') }}
            </el-dropdown-item>
            <el-dropdown-item command="changePassword">
              {{ $t('topBar.changePassword') }}
            </el-dropdown-item>
            <el-dropdown-item command="toggleTheme">
              {{ $t('topBar.switchTheme') }}
            </el-dropdown-item>
            <el-dropdown-item command="toggleLanguage">
              {{ $t('topBar.switchLanguage') }}
            </el-dropdown-item>
            <el-dropdown-item command="logout" class="logout">
              {{ $t('topBar.logout') }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!-- Change password dialog -->
    <emq-dialog
      :title="$t('topBar.changePassword')"
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
            :placeholder="$t('topBar.oldPassword')">
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="changePasswordForm.password"
            size="medium"
            type="password"
            :placeholder="$t('topBar.newPassword')">
          </el-input>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="changePasswordForm.confirmPassword"
            size="medium"
            type="password"
            :placeholder="$t('topBar.confirmPassword')">
          </el-input>
        </el-form-item>
      </el-form>
    </emq-dialog>

    <!-- Company information dialog -->
    <emq-dialog
      :title="$t('topBar.companyInfo')"
      class="topbar-dialog"
      width="480"
      :saveLoading="btnLoading"
      :visible.sync="companyInfoDialogVisible"
      @confirm="changeCompanyInfo">
      <el-form
        ref="currentCompany"
        :model="currentCompany"
        :rules="changeCompanyInfoRules">
        <el-form-item
          prop="company"
          :label="$t('topBar.companyName')">
          <el-input
            v-model="currentCompany.company"
            size="medium"
            type="text"
            disabled>
          </el-input>
        </el-form-item>
        <el-form-item
          prop="contactEmail"
          :label="$t('topBar.contactEmail')">
          <el-input
            v-model="currentCompany.contactEmail"
            size="medium"
            type="text">
          </el-input>
        </el-form-item>
        <el-form-item
          prop="contactPerson"
          :label="$t('topBar.contactPerson')">
          <el-input
            v-model="currentCompany.contactPerson"
            size="medium"
            type="text">
          </el-input>
        </el-form-item>
        <el-form-item
          prop="contactPhone"
          :label="$t('topBar.contactPhone')">
          <el-input
            v-model="currentCompany.contactPhone"
            size="medium"
            type="text">
          </el-input>
        </el-form-item>
        <el-form-item
          prop="logo"
          :label="$t('topBar.logoLight')">
          <emq-upload
            ref="fileUpload"
            v-model="currentCompany.logo"
            listType="picture"
            :field="{ type: 'uploadPhoto', url: '/api/v1/upload?fileType=image', limit: 1, }"
            :appendToBody="true">
          </emq-upload>
        </el-form-item>
        <el-form-item
          prop="logo"
          :label="$t('topBar.logoDark')">
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
      :title="$t('topBar.switchTheme')"
      :saveLoading="btnLoading"
      :visible.sync="themeDialogVisible"
      @confirm="toggleTheme"
      @close="resetTheme">
      <el-radio v-model="theme" label="light">{{ $t('topBar.lightTheme') }}</el-radio>
      <el-radio v-model="theme" label="dark">{{ $t('topBar.darkTheme') }}</el-radio>
    </emq-dialog>

    <!-- Switch language dialog -->
    <emq-dialog
      :title="$t('topBar.switchLanguage')"
      :saveLoading="btnLoading"
      :visible.sync="languageDialogVisible"
      @confirm="toggleLanguage"
      @close="resetLanguage">
      <el-radio v-model="language" label="en">English</el-radio>
      <el-radio v-model="language" label="zh">中文</el-radio>
    </emq-dialog>

    <!-- Message Center -->
    <message-rightbar :messageVisible.sync="messageVisible"></message-rightbar>
  </div>
</template>


<script>
import { SHA256 } from 'crypto-js'
import { mapActions } from 'vuex'

import { httpPut, httpGet } from '@/utils/api'
import MessageRightbar from '@/apps/accounts/components/MessageRightbar'
import EmqDialog from '@/components/EmqDialog'
import EmqUpload from '@/components/EmqUpload'
import MicroApps from '@/assets/micro.apps.json'

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
      leftbarWidth: this.$store.state.accounts.leftbar.width,
      companyInfoDialogVisible: false,
      passwrodDialogVisible: false,
      themeDialogVisible: false,
      languageDialogVisible: false,
      theme: this.$store.state.accounts.currentTheme,
      language: this.$store.state.accounts.lang,
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
          { required: true, message: this.$t('topBar.oldPasswordRequired') },
          { min: 6, message: this.$t('topBar.passwordLength') },
        ],
        password: [
          { required: true, message: this.$t('topBar.newPasswordRequired') },
          { min: 6, message: this.$t('topBar.passwordLength') },
        ],
        confirmPassword: [
          { required: true, validator: this.validatePassword },
          { min: 6, message: this.$t('topBar.passwordLength') },
        ],
      },
      changeCompanyInfoRules: {
        contactEmail: [
          { required: true, message: this.$t('topBar.emailRequired'), trigger: 'blur' },
          { type: 'email', message: this.$t('topBar.emailIllegal'), trigger: 'blur,change' },
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
      const currentTheme = this.$store.state.accounts.currentTheme
      const fileName = currentTheme === 'dark' ? 'userLogoDark' : 'userLogo'
      return this.$store.state.accounts[fileName]
    },
  },

  watch: {
    searchValue: 'jumpPage',
    '$route.path': 'pathChange',
  },

  methods: {
    ...mapActions([
      'USER_LOGOUT',
      'USER_LOGIN',
      'CLEAR_BASE',
      'LEFTBAR_SWITCH',
      'THEME_SWITCH',
      'LANG_SWITCH',
      'USER_LOGO',
      'USER_LOGO_DARK',
    ]),
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
      if (command === 'toggleLanguage') {
        this.languageDialogVisible = true
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
            this.$message.success(this.$t('topBar.editSuccess'))
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
        callback(new Error(this.$t('topBar.confirmPasswordRequired')))
        return
      }
      if (this.changePasswordForm.password !== this.changePasswordForm.confirmPassword) {
        callback(new Error(this.$t('topBar.passwordInconsistent')))
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
              this.USER_LOGO({ userLogo: response.data.logo.url })
              this.USER_LOGO_DARK({ userLogoDark: response.data.logoDark.url })
              this.$message.success(this.$t('topBar.editSuccess'))
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
        httpGet('/select_options/devices', { params })
          .then((response) => {
            response.data.forEach((record) => {
              const option = {
                label: record.label,
                value: record.attr.deviceIntID,
                type: record.attr.deviceType,
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
      const currentTheme = this.$store.state.accounts.currentTheme
      if (this.theme === currentTheme) {
        return
      }
      this.THEME_SWITCH({ currentTheme: this.theme })
      this.$emit('setTheme')

      this.themeDialogVisible = false
    },
    // Cancel switching topic, restore default
    resetTheme() {
      this.theme = this.$store.state.accounts.currentTheme
    },
    // Switch language
    toggleLanguage() {
      const currentLanguage = this.$store.state.accounts.lang
      if (currentLanguage === this.language) {
        return
      }
      this.languageDialogVisible = false

      this.LANG_SWITCH({ lang: this.language })
      this.$emit('setLang', this.language)
    },
    resetLanguage() {
      this.language = this.$store.state.accounts.lang
    },
    // Load logo
    loadLogo() {
      const currentTheme = this.$store.state.accounts.currentTheme
      const fileName = currentTheme === 'dark' ? 'userLogoDark' : 'userLogo'
      this.logoSrc = this.$store.state.accounts[fileName]
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
