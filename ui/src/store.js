import Vue from 'vue'
import Vuex from 'vuex'
import createMutationsSharer from 'vuex-shared-mutations'

import storeModules from '@/apps/store'

Vue.use(Vuex)

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production',
  modules: storeModules,
  // Sync the state of tabs and windows
  plugins: [createMutationsSharer({ predicate: ['STORE_DEVICES', 'STORE_PRODUCTS'] })],
})
