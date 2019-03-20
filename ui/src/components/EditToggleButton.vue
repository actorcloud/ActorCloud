<template>
  <a
    v-if="has(`PUT,${url}/:id`) && accessType !== 'create'"
    :class="['edit-toggle-button', disabled ? '' : 'active']"
    href="javascript:;"
    :title="disabled ? '编辑' : '取消编辑'"
    @click="toggleClick(true)">
    <i class="iconfont edit-icon__details icon-emq-edit"></i>
  </a>
</template>


<script>
export default {
  name: 'edit-toggle-button',

  props: {
    // Used to determine is the url that has permissions to display
    url: {
      type: String,
      required: true,
    },
    // The current state of being edited or not edited
    disabled: {
      type: Boolean,
      required: true,
    },
    // The type of action on the current page
    accessType: {
      type: String,
      default: 'view',
    },
  },

  methods: {
    toggleClick(canceled = false) {
      // Changes the current edit and non-edit state
      this.$emit('toggleStatus', canceled)
    },
  },
}
</script>
