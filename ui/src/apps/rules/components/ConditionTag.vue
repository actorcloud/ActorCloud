<template>
  <el-tag
    :closable="accessType !== 'view'"
    :close-transition="false"
    @click="editTag(tag)"
    @close="closeTag(tag)">
    <span v-if="tag.relation" class="relation"> {{ tag.relation === 'and' ? 'AND' : 'OR' }} </span>
    <p>
      <span class="float-left">
        <span v-if="record.conditionType === 1">{{ tag.data_point_name }}</span>
        <span v-if="record.conditionType === 2">{{ tag.metricName }}</span>
        <span v-if="record.conditionType === 4">{{ tag.path }}</span>
        <span v-if="tag.difference">与上一次差值</span>
      </span>
      <span class="float-right" v-if="tag.compare_path">&nbsp;{{ tag.compare_path }}</span>
      <span class="float-right" v-if="tag.compare_data_point">&nbsp;{{ tag.compare_data_point_name }}</span>
      <span class="float-right" v-if="tag.threshold || tag.threshold === 0">&nbsp;{{ tag.threshold }}</span>
      <span class="float-right" v-if="tag.difference">&nbsp;{{ tag.difference }}</span>
      <span class="float-right">{{ tag.operator }}</span>
    </p>
  </el-tag>
</template>


<script>
export default {
  name: 'condition-tag-view',

  props: {
    accessType: {
      type: String,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
    tag: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      LWM2M: 3,
    }
  },

  methods: {
    editTag(tag) {
      this.$emit('editConditionItem', tag)
    },
    closeTag(tag) {
      this.$emit('removeConditionItem', tag)
    },
  },
}
</script>
