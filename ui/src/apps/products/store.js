const currentProducts = JSON.parse(localStorage.getItem('currentProducts')) || []

const state = {
  currentProducts,
}

const STORE_PRODUCTS = 'STORE_PRODUCTS'

const actions = {
  [STORE_PRODUCTS]({ commit }, payload) {
    localStorage.setItem('currentProducts', JSON.stringify(payload.currentProducts))
    commit(STORE_PRODUCTS, payload.currentProducts)
  },
}

const mutations = {
  [STORE_PRODUCTS](state, currentProducts) {
    state.currentProducts = currentProducts.slice() // Array assignment to state needs to return a new array assignment using slice
  },
}

export default {
  state,
  actions,
  mutations,
}
