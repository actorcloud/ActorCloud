
const userCache = JSON.parse(localStorage.getItem('user')) || {}
const state = {
  user: userCache,
}

const USER_LOGIN = 'USER_LOGIN'
const USER_LOGOUT = 'USER_LOGOUT'

const actions = {
  [USER_LOGIN]({ commit }, payload) {
    localStorage.setItem('user', JSON.stringify(payload.user))
    commit(USER_LOGIN, payload.user)
  },
  [USER_LOGOUT]({ commit }) {
    localStorage.removeItem('user')
    commit(USER_LOGOUT)
  },
}

const mutations = {
  [USER_LOGIN](state, user) {
    Object.assign(state.user, user)
  },
  [USER_LOGOUT](state) {
    state.user = {}
  },
}

export default {
  state,
  actions,
  mutations,
}
