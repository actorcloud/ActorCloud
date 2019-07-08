<template>
  <div class="create-cert-view">
    <el-dialog
      class="emq-dialog"
      :visible.sync="visible"
      :title="!isCreated ? $t('certs.isCreate') : ''"
      :width="!isCreated ? '50%' : '40%'"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false">
      <!-- Create the cert -->
      <el-row v-if="!isCreated" :gutter="20">
        <el-form
          ref="record"
          label-position="top"
          :model="record"
          :rules="formRules">
          <el-col :span="12">
            <el-form-item :label="$t('certs.name')" prop="certName">
              <el-input v-model="record.certName" :placeholder="$t('certs.nameRequired')"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('certs.enable')" prop="enable">
              <emq-select
                v-model="record.enable"
                :field="{ key: 'enableStatus'}"
                :record="record"
                :placeholder="$t('oper.select')"
                :disabled="false">
              </emq-select>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>
      <div v-if="!isCreated" class="form__tips">
        <i class="el-icon-warning" style="color: #ffc741;"></i>
        {{ $t('certs.certTips') }}
      </div>
      <!-- cert created successfully -->
      <div v-if="isCreated" :gutter="20" class="cert-created">
        <img src="~@/assets/images/created.png" width="180">
        <h1>{{ $t('certs.isCreated') }}</h1>
        <div>
          <el-row v-loading="loading" v-if="isCreated" class="create-table">
            <el-col :span="8">
              <div class="cert-download">
                <span>{{ $t('certs.deviceCert') }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="cert-download">
                <span>{{ download.cert.fileName }}</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="cert-download">
                <a
                  href="javaScript:;"
                  @click="downloadFile(download.cert.fileName, download.cert.content)">
                  {{ $t('certs.download') }}
                </a>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="cert-download">
                <span>{{ $t('certs.key') }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="cert-download">
                <span>{{ download.key.fileName }}</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="cert-download">
                <a
                  href="javaScript:;"
                  @click="downloadFile(download.key.fileName, download.key.content)">
                  {{ $t('certs.download') }}
                </a>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="cert-download">
                <span>{{ $t('certs.root') }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="cert-download">
                <span>{{ download.root.fileName }}</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="cert-download">
                <a
                  @click="downloadFile(download.root.fileName, download.root.content)"
                  href="javaScript:;">
                  {{ $t('certs.download') }}
                </a>
              </div>
            </el-col>
          </el-row>
        </div>
        <el-button @click="save">
          {{ $t('oper.finish') }}
        </el-button>
      </div>
      <div v-if="!isCreated" slot="footer" class="dialog-footer">
        <el-button
          type="text"
          size="small"
          @click="visible = false">
          {{ $t('oper.cancel') }}
        </el-button>
        <emq-button
          icon="save"
          :loading="btnLoading"
          @click="save">
          {{ $t('oper.save') }}
        </emq-button>
      </div>
    </el-dialog>
  </div>
</template>


<script>
import EmqButton from '@/components/EmqButton'
import { httpPost } from '@/utils/api'

export default {
  name: 'create-cert-view',

  components: {
    EmqButton,
  },

  props: {
    dialogVisible: {
      type: Boolean,
      default: true,
    },
    callbackFunction: {
      type: Function,
      default: () => {},
    },
  },

  data() {
    return {
      loading: false,
      btnLoading: false,
      isCreated: false,
      record: {},
      download: {},
      formRules: {
        certName: [
          { required: true, message: this.$t('certs.nameRequired') },
        ],
        enable: [
          { required: true, message: this.$t('certs.enableRequired') },
        ],
      },
    }
  },

  computed: {
    visible: {
      get() {
        return this.dialogVisible
      },
      set(val) {
        this.$emit('update:dialogVisible', val)
      },
    },
  },

  methods: {
    save() {
      if (!this.isCreated) {
        this.$refs.record.validate((valid) => {
          if (!valid) {
            return false
          }
          this.btnLoading = true
          this.loading = true
          httpPost('/certs', this.record).then((response) => {
            if (response.status === 201) {
              this.download = response.data
              this.isCreated = true
            }
            this.btnLoading = false
            this.loading = false
          }).catch(() => {
            this.btnLoading = false
          })
        })
      } else {
        this.visible = false
        this.record = {}
        this.isCreated = false
        this.callbackFunction()
      }
    },
    downloadFile(fileName, content) {
      const aTag = document.createElement('a')
      const blob = new Blob([content])
      aTag.download = fileName
      aTag.href = URL.createObjectURL(blob)
      aTag.setAttribute('type', 'hidden')
      document.body.appendChild(aTag)
      aTag.click()
      aTag.remove()
      URL.revokeObjectURL(blob)
    },
  },
}
</script>


<style lang="scss">
.create-cert-view {
  .el-dialog {
    min-width: 610px;
  }
  .form__tips {
    color: var(--color-text-lighter);
    margin-left: 10px;
  }
  .cert-created {
    text-align: center;
    h1 {
      color: var(--color-main-green);
      margin-bottom: 40px;
    }
    .create-table {
      width: 100%;
      border: 1px solid var(--color-line-card);
      text-align: center;
      .cert-download {
        padding: 8px;
        border-top: 1px solid var(--color-line-card);
      }
    }
    .create-table:first-child {
      border-top: 0px;
    }
    .el-button {
      width: 118px;
      border-color: var(--color-main-green);
      background: var(--color-main-green);
      color: #FFFF;
      margin: 40px 0 20px 0;
    }
  }
}
</style>
