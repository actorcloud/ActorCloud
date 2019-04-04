<template>
  <div class="logo-view details-view">
    <div class="emq-crud">
      <div class="crud-header">
        <el-row type="flex" justify="space-between" align="middle">
          <el-col :span="18">
            <span class="crud-title">{{ $t('logos.logoInfo') }}</span>
          </el-col>
        </el-row>
      </div>
    </div>
    <el-card v-loading="loading">
      <el-row :gutter="20">
        <el-form
          label-width="110px"
          label-position="top"
          :model="record"
          :rules="rules">
          <el-col :span="12">
            <el-form-item prop="icon" :label="$t('logos.webIcon')">
              <emq-upload
                ref="fileUpload"
                v-model="record.icon"
                listType="picture"
                :field="{ type: 'uploadPhoto', url: '/api/v1/upload?fileType=image', limit: 1 }">
              </emq-upload>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="logo" :label="$t('logos.webLogoLight')">
              <emq-upload
                ref="fileUpload"
                v-model="record.logo"
                listType="picture"
                :field="{ type: 'uploadPhoto', url: '/api/v1/upload?fileType=image', limit: 1 }">
              </emq-upload>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="logoDark" :label="$t('logos.webLogoDark')">
              <emq-upload
                ref="fileUpload"
                v-model="record.logoDark"
                listType="picture"
                :field="{ type: 'uploadPhoto', url: '/api/v1/upload?fileType=image', limit: 1 }">
              </emq-upload>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="sign" :label="$t('logos.loginLogo')">
              <emq-upload
                ref="fileUpload"
                v-model="record.sign"
                listType="picture"
                :field="{ type: 'uploadPhoto', url: '/api/v1/upload?fileType=image', limit: 1 }">
              </emq-upload>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>
      <emq-button icon="save" :loading="btnLoading" @click="save">
        {{ $t('oper.save') }}
      </emq-button>
    </el-card>
  </div>
</template>


<script>
import { httpGet, httpPut } from '@/utils/api'
import EmqButton from '@/components/EmqButton'
import EmqUpload from '@/components/EmqUpload'

export default {
  name: 'logo-view',

  components: {
    EmqButton,
    EmqUpload,
  },

  data() {
    return {
      disabled: false,
      loading: false,
      btnLoading: false,
      record: {},
      rules: {},
    }
  },

  methods: {
    loadData() {
      this.loading = true
      httpGet('/logo_info').then((res) => {
        this.record = res.data
        this.loading = false
      })
    },
    save() {
      this.btnLoading = true
      httpPut('/logo_info', this.record).then(() => {
        this.$message.success(this.$t('logos.setSuccess'))
        setTimeout(() => {
          window.location.reload(true) // Force refresh browser
          this.btnLoading = false
        })
      })
    },
  },

  created() {
    this.loadData()
  },
}
</script>


<style lang="scss">
.logo-view {
  .el-col-12 {
    height: 204px;
  }
}
</style>
