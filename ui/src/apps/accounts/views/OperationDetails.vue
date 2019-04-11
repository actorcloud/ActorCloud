<template>
  <div class="details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item
          :to="{ path: `/operate_reporting/operate_detail` }">{{ $t('resource.operate_reporting-operate_detail')}}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('oper.view') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div>
      <el-card class="is-details-form">
        <el-row :gutter="40">
          <el-form
            ref="record"
            label-position="left"
            label-width="120px"
            :model="record">
            <el-col :span="12">
              <el-form-item :label="$t('operations.companyName')" prop="tenantName">
                <el-input
                  type="text"
                  v-model="record.tenantName"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.type')" prop="tenantTypeLabel">
                <el-input
                  type="text"
                  v-model="record.tenantTypeLabel"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('operations.adminEmail')" prop="contactEmail">
                <el-input
                  type="text"
                  v-model="record.contactEmail"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('operations.deviceTotal')" prop="deviceCount">
                <el-input
                  type="text"
                  v-model="record.deviceCount"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.person')" prop="contactPerson">
                <el-input
                  type="text"
                  v-model="record.contactPerson"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.tel')" prop="contactPhone">
                <el-input
                  type="text"
                  v-model="record.contactPhone"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('tenants.companyAddress')" prop="companyAddress">
                <el-input
                  type="text"
                  v-model="record.companyAddress"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col>
              <el-form-item :label="$t('operations.createAt')">
                <el-input
                  v-model="record.createAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
      </el-card>
    </div>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'

export default {
  name: 'product-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
  },

  data() {
    return {
      url: '/operate_detail',
    }
  },
}
</script>
