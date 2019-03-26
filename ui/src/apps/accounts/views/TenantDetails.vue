<template>
  <div class="details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/tenants' }">{{ $t('tenants.tenants') }}
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div class="tenant-card-details-body">
      <el-card :class="disabled ? 'is-details-form' : ''">
        <el-row :gutter="50">
          <el-form
            ref="record"
            label-position="left"
            label-width="100px"
            :model="record"
            :rules="accessType !== 'view' ? formRules : {}">
            <el-col :span="12">
              <el-form-item :label="$t('tenants.name')" prop="tenantName">
                <el-input
                  v-model="record.tenantName"
                  :placeholder="disabled ? '' : $t('tenants.name')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.tenantID')" prop="tenantID">
                <el-input
                  v-model="record.tenantID"
                  :placeholder="disabled ? '' : $t('tenants.tenantID')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.type')" prop="tenantTypeLabel">
                <el-input
                  v-model="record.tenantTypeLabel"
                  :placeholder="disabled ? '' : $t('tenants.type')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="record.tenantType === 2" :span="12">
              <el-form-item :label="$t('tenants.person')" prop="contactPerson">
                <el-input
                  v-model="record.contactPerson"
                  :placeholder="disabled ? '' : $t('tenants.person')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.email')" prop="contactEmail">
                <el-input
                  v-model="record.contactEmail"
                  :placeholder="disabled ? '' : $t('tenants.email')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.tel')" prop="contactPhone">
                <el-input
                  v-model="record.contactPhone"
                  :placeholder="disabled ? '' : $t('tenants.tel')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.enable')" prop="enable">
                <emq-select
                  v-model="record.enable"
                  :field="{ key: 'enable'}"
                  :record="record"
                  :placeholder="disabled ? '' : $t('tenants.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-if="record.tenantType === 2" :span="12">
              <el-form-item :label="$t('tenants.company')" prop="company">
                <el-input
                  v-model="record.company"
                  :placeholder="disabled ? '' : $t('tenants.company')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="record.tenantType === 2" :span="12">
              <el-form-item :label="$t('tenants.companySize')" prop="companySize">
                <el-input
                  v-model="record.companySize"
                  :placeholder="disabled ? '' : $t('tenants.companySize')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="record.tenantType === 2" :span="12">
              <el-form-item :label="$t('tenants.companyAddress')" prop="companyAddress">
                <el-input
                  v-model="record.companyAddress"
                  :placeholder="disabled ? '' : $t('tenants.companyAddress')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('tenants.createAt')" prop="createAt">
                <el-input
                  v-model="record.createAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('tenants.updateAt')" prop="updateAt">
                <el-input
                  v-model="record.updateAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button v-if="!disabled" icon="save" @click="save">
          {{ $t('tenants.done') }}
        </emq-button>
      </el-card>
    </div>

  </div>
</template>


<script>
import { SHA256 } from 'crypto-js'
import { httpPost, httpPut } from '@/utils/api'
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'

export default {
  name: 'tenant-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
  },

  data() {
    return {
      url: '/tenants',
      formRules: {},
    }
  },

  methods: {
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        if (this.accessType === 'create') {
          const data = { ...this.record }
          data.password = SHA256(data.password).toString()
          httpPost(this.url, data).then(() => {
            this.$message.success('新建成功!')
            this.$router.push({ path: this.listPageURL })
          })
        } else if (this.accessType === 'edit') {
          httpPut(`${this.url}/${this.detailsID}`, this.record).then(() => {
            this.$message.success('编辑成功!')
            this.$router.push({ path: this.listPageURL })
          })
        }
      })
    },
  },
}
</script>
