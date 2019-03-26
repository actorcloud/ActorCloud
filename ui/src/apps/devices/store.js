const currentDevices = JSON.parse(localStorage.getItem('currentDevices')) || []

const state = {
  currentDevices,
}

const STORE_DEVICES = 'STORE_DEVICES'

const actions = {
  [STORE_DEVICES]({ commit }, payload) {
    localStorage.setItem('currentDevices', JSON.stringify(payload.currentDevices))
    commit(STORE_DEVICES, payload.currentDevices)
  },
}

const mutations = {
  [STORE_DEVICES](state, currentDevices) {
    state.currentDevices = currentDevices.slice()
  },
}

export default {
  state,
  actions,
  mutations,
}
