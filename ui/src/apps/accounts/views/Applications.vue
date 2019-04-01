<template>
  <div class="applications-view">
    <emq-crud
      url="/applications"
      :crudTitle="$t('applications.application')"
      :tableActions="tableActions">
      <template slot="tableColumns">
        <el-table-column prop="appName" :label="$t('applications.appName')">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/applications/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.appName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="appID" :label="$t('applications.appID')"></el-table-column>
        <el-table-column prop="expiredAt" :label="$t('applications.expiredAt')" min-width="100px">
          <template v-slot="scope">
            <span v-if="scope.row.expiredAt">{{ dateFormat('yyyy-mm-dd') }}</span>
            <span v-else>{{ $t('applications.neverExpires') }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="has('PUT,/applications/:id')"
          prop="appStatusLabel"
          :label="$t('applications.enable')">
          <template v-slot="scope">
            <el-tooltip
              :content="scope.row.appStatus === 1 ? $t('applications.enabled') : $t('applications.disabled')"
              placement="left">
              <el-switch
                v-model="scope.row.appStatus"
                active-color="#13ce66"
                inactive-color="#d0d3e0"
                :active-value="1"
                :inactive-value="0"
                @change="updateApplication(scope.row)">
              </el-switch>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column
          v-else
          :label="$t('applications.enable')"
          prop="appStatus">
          <template v-slot="scope">
            {{ scope.row.appStatus === 1 ? $t('applications.isTrue') : $t('applications.isFalse') }}
          </template>
        </el-table-column>
        <el-table-column
          prop="createAt"
          min-width="150px"
          sortable="custom"
          :label="$t('applications.createAt')">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'
import { httpPut } from '@/utils/api'

export default {
  name: 'applications-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['view', 'create', 'edit', 'delete'],
    }
  },

  methods: {
    updateApplication(row) {
      httpPut(`/applications/${row.id}`, row).then(() => {
        this.$message.success(this.$t('applications.editSuccess'))
      }).catch((error) => {
        row.appStatus = row.appStatus ? 0 : 1
        this.$message.error(error.response.data.message)
      })
    },
  },
}
</script>
