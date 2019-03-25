<template>
  <div class="home-view">
    <topbar @setTheme="setTheme"></topbar>
    <leftbar></leftbar>
    <div class="home-content">
      <router-view></router-view>
    </div>
  </div>
</template>


<script>
import Topbar from '../components/Topbar'
import Leftbar from '../components/Leftbar'

export default {
  name: 'home-view',

  components: { Topbar, Leftbar },

  methods: {
    setTheme() {
      const { classList } = document.getElementsByTagName('body')[0]
      const currentTheme = this.$store.state.base.currentTheme || 'light'
      if (currentTheme === 'light') {
        classList.add('light-theme')
        classList.remove('dark-theme')
      } else if (currentTheme === 'dark') {
        classList.add('dark-theme')
        classList.remove('light-theme')
      }
    },
  },

  created() {
    this.setTheme()
  },
}
</script>


<style lang="scss">
@import "~@/assets/scss/variable.scss";

.home-view {
  min-height: 100%;
  padding: $topbar-height 0;
  background-color: var(--color-bg-gray);
  .home-content {
    transition: margin-left .35s ease-out;
    margin: 8px 20px 0 132px;
  }
  @media screen and (max-width: 1366px) {
    padding: $topbar-height-small 0;
    .home-content {
      margin: 8px 28px 0 108px;
    }
  }
}
</style>
