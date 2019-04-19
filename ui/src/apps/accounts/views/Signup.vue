<template>
  <div class="signup-view">
    <el-row style="height: 100%;">
      <el-col class="signup-form" :xs="20" :sm="20" :md="20" :lg="20">
        <el-col :span="13" style="height: 100%; position: relative">
          <div class="left-part" ref="leftImg">
            <div class="logo-bar">
              <img class="logo-bg" src="../assets/images/bg-circle.png">
              <img class="logo" src="/backend_static/images/sign.png">
            </div>
          </div>
        </el-col>
        <el-col class="information" :span="11">
          <div class="gradient-bg">
            <el-tabs v-model="currentTenantType">
              <el-tab-pane name="1">
                <label
                  v-if="!isInvitation"
                  slot="label"
                  class="el-radio">
                  <span class="el-radio__inner"></span>
                  <span class="el-radio__label">{{ $t('auth.personal') }}</span>
                </label>
                <el-form
                  label-position="left"
                  label-width="60px"
                  ref="ruleForm"
                  :model="ruleForm"
                  :rules="personalRules">
                  <el-form-item :label="$t('auth.email')" prop="email">
                    <el-input v-model="ruleForm.email"></el-input>
                  </el-form-item>
                  <el-form-item :label="$t('auth.username')" prop="username">
                    <el-input v-model="ruleForm.username"></el-input>
                  </el-form-item>
                  <el-form-item :label="$t('auth.password')" prop="password">
                    <el-input type="password" v-model="ruleForm.password"></el-input>
                  </el-form-item>
                  <el-form-item :label="$t('auth.phone')" prop="phone">
                    <el-input v-model="ruleForm.phone"></el-input>
                  </el-form-item>
                </el-form>
                <div class="button-bar">
                  <el-button type="success" :loading="btnLoading" @click="signup">
                    {{ $t('auth.signupNow') }}
                  </el-button>
                </div>
                <div class="button-bar">
                  <p>
                    {{ $t('auth.hasCount') }}
                    <router-link
                      class="login-link"
                      :to="{ path: '/login' }">
                      {{ $t('auth.login') }}
                    </router-link>
                  </p>
                </div>
              </el-tab-pane>
              <el-tab-pane name="2">
                <label
                  v-if="!isInvitation"
                  slot="label"
                  class="el-radio">
                  <span class="el-radio__inner"></span>
                  <span class="el-radio__label">{{ $t('auth.business')}}</span>
                </label>
                <el-form
                  label-position="left"
                  label-width="72px"
                  ref="ruleForm"
                  :model="ruleForm"
                  :rules="personalRules">
                  <div v-if="page === 1">
                    <el-form-item :label="$t('auth.email')" prop="email">
                      <el-input v-model="ruleForm.email"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('auth.username')" prop="username">
                      <el-input v-model="ruleForm.username"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('auth.password')" prop="password">
                      <el-input type="password" v-model="ruleForm.password"></el-input>
                    </el-form-item>
                    <div class="button-bar">
                      <el-button type="success" @click="changePage">
                        {{ $t('auth.nextStep') }}
                      </el-button>
                    </div>
                    <div class="button-bar">
                      <p>
                        {{ $t('auth.hasCount') }}
                        <router-link
                          class="login-link"
                          :to="{ path: '/login' }">
                          {{ $t('auth.login') }}
                        </router-link>
                      </p>
                    </div>
                  </div>
                  <div v-if="page === 2">
                    <el-form-item :label="$t('auth.company')"  prop="company">
                      <el-input v-model="ruleForm.company"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('auth.companySize')"  prop="companySize">
                      <el-input v-model="ruleForm.companySize"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('auth.contactPerson')" prop="contactPerson">
                      <el-input v-model="ruleForm.contactPerson"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('auth.contactPhone')" prop="contactPhone">
                      <el-input v-model="ruleForm.contactPhone"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('auth.companyAddress')" prop="companyAddress">
                      <el-input v-model="ruleForm.companyAddress"></el-input>
                    </el-form-item>
                    <div class="button-bar">
                      <el-button type="success" :loading="btnLoading" @click="signup">
                        {{ $t('auth.signupNow') }}
                      </el-button>
                    </div>
                    <div class="button-bar">
                      <el-button type="text" @click="changePage">
                        &lt;&lt; {{ $t('auth.backStep') }}
                      </el-button>
                    </div>
                  </div>
                </el-form>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-col>
      </el-col>
    </el-row>
  </div>
</template>


<script>
import { SHA256 } from 'crypto-js'
import lottie from 'lottie-web'

import { httpPost } from '@/utils/api'
import bgAnimation from '../static/bg-animation.json'

export default {
  name: 'signup-view',

  data() {
    return {
      btnLoading: false,
      page: 1,
      ruleForm: {
        tenantType: 1,
        email: '',
        username: '',
        password: '',
        phone: '',
        company: '',
        companySize: '',
        companyAddress: '',
        contactPerson: '',
        contactPhone: '',
        contactEmail: '',
      },
      currentTenantType: '1',
      stashForm: {},
      personalRules: {
        email: [
          { required: true, message: this.$t('auth.emailRequired'), trigger: 'blur' },
          { type: 'email', message: this.$t('auth.emailValid'), trigger: 'blur,change' },
        ],
        username: [
          { required: true, message: this.$t('auth.usernameRequired'), trigger: 'blur' },
        ],
        password: [
          { required: true, message: this.$t('auth.passwordRequired'), trigger: 'blur' },
          { min: 6, message: this.$t('auth.passwordLength'), trigger: 'blur,change' },
        ],
        company: [
          { required: true, message: this.$t('auth.companyRequired'), trigger: 'blur' },
        ],
        companySize: [
          { required: true, message: this.$t('auth.companySizeRequired'), trigger: 'blur' },
        ],
        contactEmail: [
          { type: 'email', message: this.$t('auth.emailValid'), trigger: 'change,blur' },
        ],
      },
    }
  },

  computed: {
    // Carry invitation code
    isInvitation() {
      return this.$route.query.i
    },
  },

  watch: {
    currentTenantType: 'refresh',
  },

  methods: {
    signup() {
      this.$refs.ruleForm.validate((valid) => {
        if (!valid) {
          return
        }
        const data = { ...this.ruleForm }
        // Carry the invitation code to the back end
        data.token = this.$route.query.i
        data.password = SHA256(this.ruleForm.password).toString()
        if (data.tenantType === 1) {
          delete data.company
        }
        if (!data.contactEmail) {
          delete data.contactEmail
        }
        this.btnLoading = true
        httpPost('/signup', data).then((response) => {
          this.$message.success(this.$t('auth.signupSuccess'))
          setTimeout(() => this.$router.push({
            path: '/login',
            query: { email: response.data.email },
          }), 1000)
          this.btnLoading = false
        }).catch((error) => {
          if (error.response.status < 500) {
            let errorMessage = ''
            const { errorCode } = error.response.data
            const formError = error.response.data.errors
            if (formError) { // There are error prompt objects in errors
              const errorKey = Object.keys(formError)[0].replace(/ /g, '_')
              Object.keys(formError).forEach((key) => {
                errorMessage = formError[key].replace(/ /g, '_')
              })
              // Stitch key-value in errors
              this.$message.error(`${this.$t(`errors.${errorKey}`)} ${this.$t(`errors.${errorMessage}`)}`)
            } else {
              // No errors output errorCode
              this.$message.error(this.$t(`errors.${errorCode}`))
            }
          } else {
            this.$message.error(this.$t('auth.signupError'))
          }
          this.btnLoading = false
        })
      })
    },
    changePage() {
      // Verify the first page form item
      if (this.page === 1) {
        this.$refs.ruleForm.validate((valid) => {
          if (valid) {
            this.page = 2
            Object.assign(this.ruleForm, this.stashForm)
          }
        })
      } else {
        this.stashForm = {
          company: this.ruleForm.company,
          companyAddress: this.ruleForm.companyAddress,
          companySize: this.ruleForm.companySize,
          contactPerson: this.ruleForm.contactPerson,
          contactPhone: this.ruleForm.contactPhone,
        }
        this.$refs.ruleForm.resetFields()
        this.page = 1
      }
    },
    refresh(newValue) {
      this.page = 1
      this.stashForm = {}
      this.ruleForm = {
        tenantType: parseInt(newValue, 10),
        email: '',
        username: '',
        password: '',
        phone: '',
        company: '',
        companySize: '',
        companyAddress: '',
        contactPerson: '',
        contactPhone: '',
        contactEmail: '',
      }
    },
  },

  mounted() {
    lottie.loadAnimation({
      container: this.$refs.leftImg,
      animationData: bgAnimation, // json file path
      loop: true,
      autoplay: true,
      renderer: 'canvas', // Render mode, there are three kinds of "html", "canvas" and "svg"
    })
  },
}
</script>


<style lang="scss">
.signup-view {
  background-color: #333844;
  height: 100%;

  .signup-form {
    max-width: 1200px;
    height: 70%;
    max-height: 600px;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);

    .left-part {
      height: 100%;

      .logo-bar {
        position: absolute;
        width: 34%;
        left: 49%;
        transform: translateX(-50%);
        top: 32%;

        .logo-bg {
          width: 100%;
          display: block;
        }
        .logo {
          width: 72%;
          position: absolute;
          top: 0;
          bottom: 0;
          left: 0;
          right: 0;
          margin: auto;
        }
      }
      .item-name {
        width: 100%;
        position: absolute;
        top: 50%;
        text-align: center;
        font-size: 24px;
        color: #fff;
      }
    }
    .information {
      position: relative;
      top: 50%;
      transform: translateY(-50%);
      .gradient-bg {
        width: 78%;
        max-width: 500px;
        min-width: 430px;
        position: absolute;
        right: 0;
        transform: translateY(-50%);
        background-image: url(../assets/images/bg-large.png);
        background-size: cover;
        padding: 50px 54px 50px 40px;
      }
      .el-tabs {
        .el-tabs__content {
          overflow: visible;
          margin-left: 10px;
        }
        .el-tabs__item {
          .el-radio {
            color: #a1a1a1;
            font-weight: normal;
            line-height: 40px;

            .el-radio__inner {
              width: 12px;
              height: 12px;
              &::after {
                transition: none;
              }
            }
          }
          &.is-active {
            .el-radio__inner {
              border-color: #23c88e;
              background-color: #23c88e;
              &::after {
                transform: translate(-50%, -50%) scale(1);
                transition: none;
              }
            }
          }
        }
        .el-tabs__nav-wrap::after {
          background-color: transparent;
        }
        .el-tabs__active-bar {
          background-color: transparent;
        }
        .el-form-item__label {
          color: #a8abaf;
          line-height: 36px;
          position: relative;

          &::before {
            position: absolute;
            font-size: 18px;
            color: #E967A6;
            line-height: 42px;
            left: -12px;
          }
        }
        .el-form-item {
          margin-bottom: 20px;
        }
        .el-form-item__content {
          line-height: 36px;

          .el-input {
            height: 36px;
            line-height: 36px;
            border-radius: 50px;
            background-color: rgba($color: #e6e8f1, $alpha: 0.09);
          }
          .el-input__inner {
            height: 36px;
            background-color: transparent;
            border: 0;
            padding: 0 20px;
            color: #b6bac5;
          }
          .el-form-item__error {
            color: #E967A6;
          }
        }
        .button-bar {
          position: relative;
          text-align: center;
          padding: 0 0 0 60px;
          .login-link {
            color: #23c88e;
          }
          .el-button--success {
            margin-top: 16px;
            width: 100%;
            height: 36px;
            background-color: #23c88e;
            border-color: #23c88e;
            border-radius: 50px;
            font-size: 16px;
            box-shadow: 0px 3px 24px -3px #09935F;
            padding: 8px 20px;
          }
          .el-button--text {
            color: #23c88e;
            margin-top: 10px;
          }
        }
      }
    }
  }
}
  @media screen and (min-width: 1400px) {
    .signup-view .signup-form .information .el-tabs .button-bar .el-button--success {
      font-size: 18px;
    }
  }
</style>
