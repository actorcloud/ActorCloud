import Vue from 'vue'
import { sync } from 'vuex-router-sync'
import VueI18n from 'vue-i18n'
import VueAMap, { lazyAMapApiLoaderInstance } from 'vue-amap'
import ElementLocale from 'element-ui/lib/locale'
import element from '@/utils/element'

import 'element-ui/lib/theme-chalk/index.css'
import '@/assets/scss/element-variables.scss'
import 'material-design-icons/iconfont/material-icons.css'

import App from '@/App'
import store from '@/store'
import router from '@/router'
import lang from '@/lang'
import * as filters from '@/filters'
import installer from '@/utils/installer'

Vue.use(element)
Vue.use(VueI18n)
Vue.use(VueAMap)
Vue.use(installer)

// Register global utility filters.
Object.keys(filters).forEach((key) => {
  Vue.filter(key, filters[key])
})

// Global instance method
Vue.prototype.has = function has(permission) {
  const splited = permission.split(',')
  const method = splited[0]
  // Remove the query parameters from the url
  const url = splited[1].split('?')[0]
  const { permissions } = store.state.accounts
  if (permissions[url] && permissions[url].includes(method)) {
    return true
  }
  return false
}

// Map
VueAMap.initAMapApiLoader({
  key: 'c46bfd7e8adcee87b05cce249fed42a1',
  plugin: [
    'AMap.Autocomplete',
    'AMap.PlaceSearch',
    'AMap.Scale',
    'AMap.OverView',
    'AMap.ToolBar',
    'AMap.MapType',
    'AMap.PolyEditor',
    'AMap.CircleEditor',
    'AMap.Geocoder',
    'AMap.MouseTool',
    'AMap.PolyEditor',
    'AMap.CircleEditor',
  ],
  uiVersion: '1.0',
  v: '1.4.4',
})

lazyAMapApiLoaderInstance.load().then(() => {
})

// Language
const currentLang = store.state.accounts.lang
const i18n = new VueI18n({
  locale: currentLang || 'zh',
  messages: lang,
})
ElementLocale.i18n((key, value) => i18n.t(key, value))

sync(store, router)

window.onload = () => {
  setTimeout(() => {
    document.documentElement.scrollTop = 0
  }, 0)
}

new Vue({
  router,
  store,
  i18n,
  ...App,
}).$mount('#root')
