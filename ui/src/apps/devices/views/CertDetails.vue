<template>
  <div class="details-view cert-details-view">
   <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/security/certs` }">{{ $t('certs.cert') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div class="certs-card-details-body">
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
            :label-width="lang === 'en' ? '100px' : '82px'"
            :label-position="disabled ? 'left' : 'top'"
            :model="record"
            :rules="accessType !== 'view' ? rules : {}">
            <el-col :span="12">
              <el-form-item :label="$t('certs.name')" prop="certName">
                <el-input
                  type="text"
                  v-model="record.certName"
                  :placeholder="disabled ? '' : $t('certs.nameRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('certs.enable')" prop="enable">
                <emq-select
                  v-model="record.enable"
                  :field="{ key: 'enableStatus'}"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('certs.createUser')">
                <el-input
                  v-model="record.createUser"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('certs.createAt')">
                <el-input
                  v-model="record.createAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button
          v-if="disabled"
          @click="downloadFile"
          style="float:none;margin:10px 0 0 0;">
          {{ $t('certs.downloadCert') }}
        </emq-button>
        <emq-button v-if="!disabled" icon="save" @click="save">
          {{ $t('oper.save') }}
        </emq-button>
      </el-card>

      <add-device
        :url="url"
        :detailsID="parseInt(detailsID, 10)">
      </add-device>
    </div>
  </div>
</template>


<script>
import JSzip from 'jszip'

import detailsPage from '@/mixins/detailsPage'
import EmqButton from '@/components/EmqButton'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import AddDevice from '../components/AddDevice'

export default {
  name: 'cert-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    AddDevice,
  },

  data() {
    return {
      url: '/certs',
      rules: {
        certName: [
          { required: true, message: this.$t('certs.nameRequired'), trigger: 'blur' },
        ],
        enable: [
          { required: true, message: this.$t('certs.enableRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  methods: {
    // Download the cert
    downloadFile() {
      const zip = new JSzip()
      const currDate = new Date()
      const dateWithOffset = new Date(currDate.getTime() - (currDate.getTimezoneOffset() * 60000))
      const certName = this.record.name
      zip.file(`${certName}.crt`, this.record.cert, { binary: true, date: new Date(dateWithOffset) })
      zip.file(`${certName}.key`, this.record.key, { binary: true, date: new Date(dateWithOffset) })
      zip.file('root_ca.crt', this.record.root, { binary: true, date: new Date(dateWithOffset) })
      zip.generateAsync({ type: 'blob' }).then((content) => {
        const aTag = document.createElement('a')
        aTag.download = `${certName}.zip`
        aTag.href = URL.createObjectURL(content)
        aTag.setAttribute('type', 'hidden')
        document.body.appendChild(aTag)
        aTag.click()
        aTag.remove()
        URL.revokeObjectURL(content)
      })
    },
  },

  created() {
    // cert can not be created in the details page, route to 404
    if (this.$route.query.oper === 'create') {
      this.$router.push({ path: '/not_found' })
    }
  },
}
</script>
