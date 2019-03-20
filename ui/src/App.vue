<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'app',

  created() {
    document.body.removeChild(document.getElementById('full-loading'))
  },
}
</script>

<style lang="scss">
@import "./assets/scss/base";
</style>
