<template>
  <div class="login-view">
    <el-row style="height: 100%;">
      <el-col class="login-form" :xs="20" :sm="20" :md="20">
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
            <el-form>
              <el-form-item>
                <i class="iconfont icon-email icon"></i>
                <el-input
                  v-model="email"
                  :class="{ error: loginError.email }"
                  :placeholder="loginError.email || placeholder.email"
                  @focus="changeEmailPlaceholder">
                </el-input>
              </el-form-item>
              <el-form-item>
                <i class="iconfont icon-password icon"></i>
                <el-input
                  type="password"
                  v-model="password"
                  :class="{ error: loginError.password }"
                  :placeholder="loginError.password || placeholder.password"
                  @focus="changePasswordPlaceholder"
                  @keyup.enter.native="login">
                </el-input>
              </el-form-item>
            </el-form>
            <div>
              <div class="checkbox">
                <el-checkbox v-model="remember" style="color: inherit;">
                  {{ $t('auth.remember') }}
                </el-checkbox>
              </div>
              <p class="signup" v-if="hasSignup">
                {{ $t('auth.noAccount') }}
                <router-link class="link" :to="{ path: '/signup' }">{{ $t('auth.signup') }}</router-link>
              </p>
              <div style="clear:both;"></div>
            </div>
            <div class="login-footer">
              <el-button type="success" :loading="btnloading" @click="login">
                {{ $t('auth.login') }}
              </el-button>
            </div>
          </div>
        </el-col>
      </el-col>
    </el-row>
  </div>
</template>


<script>
import { mapActions } from 'vuex'
import { SHA256 } from 'crypto-js'
import lottie from 'lottie-web'

// import router from '@/apps/routes'
import { httpPost } from '@/utils/api'
import bgAnimation from '../static/bg-animation.json'

export default {
  name: 'login-view',

  data() {
    return {
      email: '',
      password: '',
      remember: false,
      loginError: {
        email: '',
        password: '',
      },
      placeholder: {
        email: this.$t('auth.email'),
        password: this.$t('auth.password'),
      },
      lang: 'zh',
      hasSignup: true,
      btnloading: false,
    }
  },

  methods: {
    ...mapActions([
      'USER_LOGIN',
      'LEFT_MENUS',
      'NAV_TABS',
      'USER_PERMISSIONS',
      'GET_DICT_CODE',
      'SHOW_PRODUCTS_MALL',
      'USER_LOGO',
      'USER_LOGO_DARK',
    ]),
    login() {
      if (!this.email) {
        this.loginError.email = this.$t('auth.emailRequired')
        return false
      }
      if (!this.password) {
        this.loginError.password = this.$t('auth.passwordRequired')
        return false
      }
      const data = {
        email: this.email,
        password: SHA256(this.password).toString(),
        remember: this.remember,
      }
      this.btnloading = true
      httpPost('/login', data).then((response) => {
        const userInfo = {
          token: response.data.token,
          userIntID: response.data.userIntID,
          username: response.data.username,
          tenantType: response.data.tenantType,
        }
        this.USER_LOGIN({ user: userInfo, remember: this.remember })
        this.LEFT_MENUS({ menus: response.data.menus })
        this.NAV_TABS({ tabs: response.data.tabs })
        this.USER_PERMISSIONS({ permissions: response.data.permissions })
        this.SHOW_PRODUCTS_MALL({ showProductsMall: response.data.show_products_mall })
        this.USER_LOGO({ userLogo: response.data.logo })
        this.USER_LOGO_DARK({ userLogoDark: response.data.logoDark })
        this.GET_DICT_CODE()
        const path = decodeURIComponent(this.$route.query.redirect || '/')
        this.$router.push({ path })
        this.btnloading = false
      }).catch(() => {
        this.btnloading = false
        this.loginError.email = this.$t('auth.error')
        this.email = ''
        this.password = ''
      })
    },
    changeEmailPlaceholder() {
      this.placeholder.email = this.$t('auth.inputEmail')
      this.loginError.email = ''
    },
    changePasswordPlaceholder() {
      this.placeholder.password = this.$t('auth.inputPassword')
      this.loginError.password = ''
    },
  },

  mounted() {
    //  Determine the existence of the registration interface
    // const routePaths = router.map(item => item.path)
    // this.hasSignup = routePaths.includes('/signup')
    // Extract the username from the login page
    this.email = this.$route.query.email

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
@import "~@/assets/scss/variable.scss";

.login-view {
  background-color: #333844;
  height: 100%;
  .login-form {
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
  }
  .el-card {
    border: none;
    background-color: #ffffff;
    border-radius: 0;
  }
  .el-card__body {
    padding: 0;
  }
  .left-img {
    width: 400px;
    height: 524px;
    display: block;
  }
  .information {
    position: relative;
    top: 50%;
    transform: translateY(-50%);

    .gradient-bg {
      width: 66%;
      max-width: 420px;
      min-width: 360px;
      position: absolute;
      right: 0;
      transform: translateY(-50%);
      background-image: url(../assets/images/bg-small.png);
      background-size: cover;
      padding: 60px 40px;
    }
    .el-form-item {
      margin-bottom: 20px;
      .el-input {
        height: 36px;
        line-height: 36px;
        border-radius: 50px;
      }
      .el-input__inner {
        height: 36px;
        background-color: transparent;
        border: 0;
        padding: 0 20px 0 50px;
        color: #b6bac5;
        border-radius: 50px;
      }
      .icon {
        position: absolute;
        left: 20px;
        z-index: 1;
        font-size: 20px;
      }
    }
    .signup {
      float: right;
      margin: 0;
      color: #8e9196;

      .link {
        color: #23c88e;
      }
    }
  }
  .el-input {
    background-color: rgba($color: #e6e8f1, $alpha: 0.09);

    &.error {
      ::-webkit-input-placeholder {
        color: #e0b4b4;
      }
      ::-moz-placeholder {
        color: #e0b4b4;
      }
      .el-input__inner {
        border: 2px solid #e0b4b4;
      }
    }
  }
  .login-footer {
    margin-top: 32px;
    .el-button {
      width: 100%;
      height: 36px;
      background-color: #23c88e;
      border-color: #23c88e;
      border-radius: 50px;
      font-size: 18px;
      box-shadow: 0px 3px 24px -3px #09935F;
      padding: 8px 20px;
    }
  }
  .checkbox {
    float: left;
    display: block;
    margin: 0;

    .el-checkbox__inner {
      background-color: #e1e3e4;
      border: 0;
    }
    .el-checkbox__inner::after {
      left: 5px;
    }
    .el-checkbox__input.is-checked .el-checkbox__inner {
      background-color: #23c88e;
    }
    .el-checkbox__label {
      color: #8e9196;
      font-size: 14px;
      font-weight: normal;
    }
  }
}
</style>
