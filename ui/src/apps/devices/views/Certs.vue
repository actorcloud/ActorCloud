<template>
  <div class="certs-view">
    <!-- Create Certs -->
    <create-cert
      :dialogVisible.sync="createCertDialogVisible"
      :callbackFunction="updateTableData"></create-cert>

    <emq-crud
      ref="crud"
      url="/certs"
      :crudTitle="$t('certs.cert')"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.accounts.tabs.security"></tabs-card-head>
      </template>
      <emq-button
        slot="createButton"
        v-if="tableActions.includes('create') && has('POST,/certs')"
        class="create-btn"
        @click="createCertDialogVisible = true">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <template slot="tableColumns">
        <el-table-column prop="certName" :label="$t('certs.name')">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/security/certs/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.certName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column v-if="has('PUT,/certs/:id')" :label="$t('certs.enable')" prop="enable">
          <template v-slot="scope">
            <el-tooltip
              :content="scope.row.enable === 1 ? $t('certs.allowed') : $t('certs.notAllowed')"
              placement="left">
              <el-switch
                v-model="scope.row.enable"
                active-color="#13ce66"
                inactive-color="#d0d3e0"
                :active-value="1"
                :inactive-value="0"
                @change="updateCert(scope.row)">
              </el-switch>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column
          v-else
          :label="$t('certs.enable')"
          prop="enable">
          <template v-slot="scope">
            {{ scope.row.enable === 1 ? $t('certs.isTrue') : $t('certs.isFalse') }}
          </template>
        </el-table-column>
        <el-table-column
          prop="createAt"
          :label="$t('certs.createAt')"
          sortable="custom">
        </el-table-column>
      </template>
    </emq-crud>

  </div>
</template>


<script>
import { httpPut } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'
import TabsCardHead from '@/components/TabsCardHead'
import CreateCert from '../components/CreateCert'

export default {
  name: 'certs-view',

  components: {
    EmqCrud,
    TabsCardHead,
    CreateCert,
  },

  data() {
    return {
      createCertDialogVisible: false,
      tableActions: ['view', 'create', 'edit', 'delete', 'search'],
      searchOptions: [
        {
          value: 'certName',
          label: this.$t('devices.certName'),
        },
      ],
    }
  },

  methods: {
    updateCert(row) {
      httpPut(`/certs/${row.id}`, row).then(() => {
        this.$message.success(this.$t('applications.editSuccess'))
      }).catch((error) => {
        row.appStatus = row.appStatus ? 0 : 1
        this.$message.error(error.response.data.message)
      })
    },
    updateTableData() {
      this.$refs.crud.loadData()
    },
  },
}
</script>
