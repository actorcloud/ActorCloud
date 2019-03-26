<template>
  <div class="leftbar-warpper">
    <el-scrollbar>
      <el-menu
        class="leftbar"
        unique-opened
        router
        background-color="var(--color-bg-card)"
        text-color="var(--color-text-light)"
        active-text-color="var(--color-main-green)"
        collapse
        :defaultOpeneds="defaultOpeneds"
        :default-active="defaultActive"
        @select="menuSelected">
        <el-menu-item class="el-submenu" index="/" :route="{ path: '/' }">
          <div class="menu-info">
            <i class="material-icons">home</i>
            <div class="menu-info--name">
              {{ $t('resource.dashboard') }}
            </div>
          </div>
        </el-menu-item>
        <el-submenu v-for="menu in menus" :index="menu.code" :key="menu.id">
          <template slot="title">
            <div class="menu-info">
              <i class="material-icons">{{ menu.icon }}</i>
              <div class="menu-info--name">
                {{ $t(`resource.${menu.code}`) }}
              </div>
            </div>
          </template>
          <el-menu-item
            v-for="subMenu in menu.children"
            v-if="subMenu.id"
            :class="{ 'only-one': menu.children.length === 1 }"
            :index="subMenu.tabs === 1 ? subMenu.children[0].url  : `/${subMenu.code}`"
            :key="subMenu.id">{{ $t(`resource.${subMenu.code}`) }}
          </el-menu-item>
        </el-submenu>
      </el-menu>
    </el-scrollbar>
  </div>
</template>


<script>
import { Scrollbar } from 'element-ui'

export default {
  name: 'leftbar',

  components: { 'el-scrollbar': Scrollbar },

  data() {
    return {
      btnLoading: false,
      defaultOpeneds: [],
      defaultActive: this.$route.path.replace(/\/\d+/g, ''),
    }
  },

  watch: {
    leftbarWidth() {
      this.menuActive()
    },
    // Listen for route changes, change the navigation bar highlighting
    $route() {
      this.menuActive()
    },
  },

  computed: {
    leftbarWidth() {
      return this.$store.state.base.leftbar.width
    },
    menus() {
      return this.$store.state.base.menus
    },
  },

  methods: {
    menuSelected(key) {
      if (key === '/') {
        this.defaultOpeneds = []
      }
    },
    menuActive() {
      // Convert url like '/devices/devices/{number}*' to '/devices/devices'
      const currentPath = this.$route.path.replace(/\/\d+\/*.*/g, '')
      this.defaultActive = currentPath

      // Store secondary menu
      let children = []
      this.menus.forEach((menu) => {
        children = children.concat(menu.children)
      })
      children.forEach((child) => {
        if (!child.children) {
          return
        }
        child.children.forEach((childChild) => {
          // If the menu has tabs, set the active highlight to the url for the first element of tabs.
          if (child.tabs === 1) {
            if (childChild.url === currentPath) {
              this.defaultActive = child.children[0].url
            }
          }
        })
      })
    },
  },

  created() {
    this.menuActive()
  },
}
</script>


<style lang="scss">
@import "~@/assets/scss/variable.scss";

.leftbar-warpper {
  .el-scrollbar__wrap {
    overflow-x: hidden;
    background-color: var(--color-bg-card);
  }
  .el-scrollbar__bar {
    opacity: 0;

    &.is-vertical {
      right: 0;
      width: 2px;
      .el-scrollbar__thumb {
        width: 2px;
      }
    }
    &.is-horizontal {
      display: none;
    }
  }

  &:hover {
    .el-scrollbar__bar {
      transition: opacity .3s;
      opacity: 1;
    }
  }

  position: fixed;
  top: $topbar-height;
  width: $leftbar-width;
  overflow-x: hidden;
  @media screen and (max-width: 1366px) {
    top: $topbar-height-small;
    width: $leftbar-width-small;
  }
  bottom: 0;
  z-index: 1000;
  border-right: 0;
  box-shadow: 0 0 12px -3px var(--color-shadow);
}

.leftbar {
  padding-top: 6px;
  padding-bottom: 6px;
  &.el-menu {
    border-right: none;
    width: 100%;
  }
  .el-menu-item,
  .el-submenu__title {
    height: auto;
    line-height: 20px;
  }
  .menu-info {
    margin: 0 auto;
    text-align: center;
  }
  .material-icons {
    display: block;
    margin: 0 auto;
    height: 44px;
    width: 44px;
    line-height: 44px;
    font-size: 26px;
    transition: all .1s ease-in;
    color: var(--color-text-light);
  }
  .el-submenu {
    height: auto;
    &.el-menu-item, .el-submenu__title {
      padding: 12px 0 16px !important;
    }
    &.is-active, &:hover {
      background-color: var(--color-bg-hover)!important;
      .el-submenu__title {
        background-color: var(--color-bg-hover)!important;
      }
      .material-icons {
        color: var(--color-main-green);
      }
      .menu-info--name {
        color: var(--color-main-green);
      }
    }
    @media screen and (max-width: 1366px) {
      &.el-menu-item, .el-submenu__title {
        padding: 6px 0 10px !important;
      }
      .material-icons {
        height: 40px;
        width: 40px;
      }
    }
  }
}

/* narrow sidebar */
.el-menu--collapse {
  .el-submenu .el-menu-item {
    padding-left: 40px !important;
  }
  .site-title .el-tooltip {
    padding-left: 0 !important;
    img {
      margin-left: 12px;
    }
  }
}

.el-menu--vertical {
  text-align: center;
  border-radius: 6px;
  .el-menu--popup {
    border-radius: 6px;
    min-width: 120px;
    padding: 0;
    -webkit-box-shadow: 0 2px 12px 0 var(--color-shadow);
    box-shadow: 0 2px 12px 0 var(--color-shadow);
  }
  .el-menu-item {
    height: 44px;
    line-height: 44px;
    text-align: left;
    color: var(--color-text-light);
    &:first-of-type {
      border-radius: 6px 6px 0 0;
    }
    &:last-of-type {
      border-radius: 0 0 6px 6px;
    }
    &.only-one {
      border-radius: 6px;
    }
    /*&:first-of-type {*/
      /*border-radius: 6px;*/
      /*&:last-of-type {*/
        /*border-radius: 6px;*/
      /*}*/
    /*}*/
    &:hover, &.is-active {
      background-color: var(--color-main-green)!important;
      color: #fff !important;
    }
  }
}
</style>
