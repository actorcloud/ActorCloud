<template>
  <tabs-card-head class="crud-title--in-details" :tabs="tabs"></tabs-card-head>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'

export default {
  name: 'group-detail-tabs',

  components: { TabsCardHead },

  computed: {
    tabs() {
      const { id } = this.$route.params
      const data = [
        { code: 'groupInfo', url: `/devices/groups/${id}` },
      ]
      return data
    },
  },
}
</script>
