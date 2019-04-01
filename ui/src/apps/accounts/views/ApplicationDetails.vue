<template>
  <div class="application-details-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/applications' }">{{ $t('applications.application') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div class="application-card-details-body">
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
            label-width="100px"
            :model="record"
            :rules="accessType !== 'view' ? formRules : {}">
            <el-col :span="12">
              <el-form-item  v-if="accessType === 'view'" :label="$t('applications.appID')" prop="appID">
                <el-input v-model="record.appID" disabled></el-input>
              </el-form-item>
              <el-form-item :label="$t('applications.appName')" prop="appName">
                <el-input
                  v-model="record.appName"
                  :placeholder="disabled ? '' : $t('applications.appNameRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item :label="$t('applications.products')" prop="products">
                <emq-search-select
                  v-if="!disabled"
                  ref="productsSelect"
                  class="product-select"
                  v-model="record.products"
                  multiple
                  :placeholder="disabled ? '' : $t('oper.productsSearch')"
                  :field="{
                    url: '/emq_select/products',
                    searchKey: 'productName',
                    state: accessType,
                  }"
                  :record="record"
                  :disabled="false">
                </emq-search-select>
                <div v-if="disabled" class="product-link">
                  <router-link
                    style="float: none;"
                    v-for="product in record.productIndex"
                    :key="product.value"
                    :to="`/products/${product.value}`">
                    <el-tag
                      size="small">
                      {{ product.label }}
                    </el-tag>
                  </router-link>
                </div>
              </el-form-item>
              <el-form-item :label="$t('applications.expiredAt')" prop="expiredAt">
                <el-date-picker
                  v-model="record.expiredAt"
                  type="date"
                  value-format="yyyy-MM-dd HH:mm:ss"
                  :placeholder="$t('applications.neverExpires')"
                  :picker-options="pickerOption"
                  :disabled="disabled">
                </el-date-picker>
              </el-form-item>
              <el-form-item v-if="accessType === 'view'" :label="$t('applications.createUser')" prop="username">
                <el-input v-model="record.username" disabled></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item v-if="accessType === 'view'" :label="$t('applications.appToken')" prop="appToken">
                <el-input v-model="record.appToken" disabled></el-input>
              </el-form-item>
              <el-form-item :label="$t('applications.roleIntID')" prop="roleIntID">
                <span v-if="!disabled && has('POST,/app_roles')" class="role-button">
                  {{$t('oper.or')}}&nbsp;
                  <a href="javascript:;" @click="newAnotherPageData">{{ $t('applications.create_roles') }}</a>
                </span>
                <emq-select
                  v-if="['create', 'edit'].includes(accessType)"
                  v-model="record.roleIntID"
                  :field="{ url: '/emq_select/app_roles' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('applications.select')"
                  :disabled="disabled">
                </emq-select>
                <router-link
                  v-else
                  style="float: none;"
                  :to="{ path: `/app_roles/${record.roleIntID}`, query: { oper: 'view', url: '/app_roles' } }">
                  {{ record.roleName }}
                </router-link>
              </el-form-item>
              <el-form-item :label="$t('applications.enable')" prop="appStatus">
                <emq-select
                  v-model="record.appStatus"
                  :field="{ key: 'appStatus'}"
                  :record="record"
                  :placeholder="disabled ? '' : $t('applications.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
              <el-form-item :label="$t('applications.description')" prop="description">
                <el-input
                  v-model="record.description"
                  :placeholder="disabled ? '' : $t('applications.descriptionPlaceholder')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button v-if="!disabled" icon="save" @click="save">
          {{ $t('applications.done') }}
        </emq-button>
      </el-card>
    </div>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'applications-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
    EmqSearchSelect,
  },

  data() {
    return {
      url: '/applications',
      formRules: {
        appName: [{ required: true, message: this.$t('applications.appNameRequired') }],
        appStatus: [{ required: true, message: this.$t('applications.select') }],
        roleIntID: [{ required: true, message: this.$t('applications.roleRequired') }],
        products: [{ required: true, message: this.$t('applications.productRequired') }],
      },
      pickerOption: {
        disabledDate(time) {
          return time.getTime() < Date.now()
        },
      },
      localRecordName: 'applicationRecord',
      toURL: '/app_roles/0?oper=create&url=%2Fapp_roles',
    }
  },

  watch: {
    disabled() {
      this.$nextTick(() => { // DOM updated, reset the value of options
        this.processLoadedData(this.record)
      })
    },
  },

  methods: {
    processLoadedData(record) {
      // Modify the value of the options selected，Displays label when editing
      if (this.$refs.productsSelect
        && record.productIndex.length === record.products.length) {
        this.$refs.productsSelect.options = record.products.map((value, index) => {
          return { value, label: record.productIndex[index].label }
        })
      }
      // After saves the data, go back to the view page
      this.isRenderToList = false
    },
  },
}
</script>


<style lang="scss">
.application-details-view {
  .role-button {
    position: absolute;
    top: 0;
    right: 40px;
    z-index: 1;
  }
  .product-select {
    .el-input {
      height: auto;
    }
  }
  .product-link a {
    .el-tag {
      cursor: pointer;
      margin-right: 4px;
    }
  }
}
</style>
