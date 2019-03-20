<template>
  <div class="empty-view">
    <div class="empty-img">
      <img src="../assets/images/empty-page.png" width="402" height="256" />
    </div>
    <div class="empty-info">
      <h1>{{ emptyInfo.title }}</h1>
      <h2>{{ emptyInfo.subTitle }}</h2>
    </div>
    <el-button
      v-if="emptyInfo.buttonText"
      type="success"
      @click="$router.push({ path: emptyInfo.url })">
      + {{ emptyInfo.buttonText }}
    </el-button>
  </div>
</template>


<script>
export default {
  name: 'empty-view',
  props: {
    // Empty info, Filed: title，subTitle，buttonText
    emptyInfo: {
      type: Object,
      required: true,
    },
  },
}
</script>

<style lang="scss">
.empty-view {
  text-align: center;
  padding-top: 20px;
  .empty-info {
    padding-bottom: 40px;
    h1 {
      padding-bottom: 20px;
      color: var(--color-text-lighter);
    }
    h2 {
      color: var(--color-text-default);
    }
  }
}
</style>
