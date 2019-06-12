import { httpGet } from '@/utils/api'

// If there is no default language, choose from the browser
const defaultLang = window.navigator.language ? window.navigator.language.substring(0, 2) : 'en'

const userCache = JSON.parse(localStorage.getItem('user')) || {}
const state = {
  user: userCache,
  loading: false,
  leftbar: JSON.parse(localStorage.getItem('leftbar')) || { width: 'wide' },
  menus: JSON.parse(localStorage.getItem('menus')) || [],
  tabs: JSON.parse(localStorage.getItem('tabs')) || {},
  permissions: JSON.parse(localStorage.getItem('permissions')) || {},
  dictCode: JSON.parse(localStorage.getItem('dictCode')) || {},
  showProductsMall: parseInt(localStorage.getItem('showProductsMall'), 10) || 0, // Number type
  userLogo: localStorage.getItem('userLogo') || '',
  userLogoDark: localStorage.getItem('userLogoDark') || '',
  currentTheme: localStorage.getItem('currentTheme') || 'light', // Current theme, light/dark
  lang: localStorage.getItem('lang') || defaultLang, // Current theme, light/dark
}

const USER_LOGIN = 'USER_LOGIN'
const USER_LOGOUT = 'USER_LOGOUT'
const LOADING_START = 'LOADING_START'
const LOADING_END = 'LOADING_END'
const LEFTBAR_SWITCH = 'LEFTBAR_SWITCH'
const LEFT_MENUS = 'LEFT_MENUS'
const NAV_TABS = 'NAV_TABS'
const USER_PERMISSIONS = 'USER_PERMISSIONS'
const CLEAR_BASE = 'CLEAR_BASE'
const GET_DICT_CODE = 'GET_DICT_CODE'
const RECEIVE_DICT_CODE = 'RECEIVE_DICT_CODE'
const SHOW_PRODUCTS_MALL = 'SHOW_PRODUCTS_MALL'
const USER_LOGO = 'USER_LOGO'
const USER_LOGO_DARK = 'USER_LOGO_DARK'
const THEME_SWITCH = 'THEME_SWITCH'
const LANG_SWITCH = 'LANG_SWITCH'

const actions = {
  [USER_LOGIN]({ commit }, payload) {
    localStorage.setItem('user', JSON.stringify(payload.user))
    commit(USER_LOGIN, payload.user)
  },
  [USER_LOGOUT]({ commit }) {
    localStorage.removeItem('user')
    commit(USER_LOGOUT)
  },
  [LOADING_START]({ commit }) {
    commit(LOADING_START)
  },
  [LOADING_END]({ commit }) {
    commit(LOADING_END)
  },
  [LEFTBAR_SWITCH]({ commit }, payload) {
    localStorage.setItem('leftbar', JSON.stringify(payload.leftbar))
    commit(LEFTBAR_SWITCH, payload.leftbar)
  },
  [LEFT_MENUS]({ commit }, payload) {
    localStorage.setItem('menus', JSON.stringify(payload.menus))
    commit(LEFT_MENUS, payload.menus)
  },
  [NAV_TABS]({ commit }, payload) {
    localStorage.setItem('tabs', JSON.stringify(payload.tabs))
    commit(NAV_TABS, payload.tabs)
  },
  [USER_PERMISSIONS]({ commit }, payload) {
    localStorage.setItem('permissions', JSON.stringify(payload.permissions))
    commit(USER_PERMISSIONS, payload.permissions)
  },
  [CLEAR_BASE]({ commit }) {
    localStorage.removeItem('menus')
    localStorage.removeItem('tabs')
    localStorage.removeItem('permissions')
    commit(CLEAR_BASE)
  },
  [GET_DICT_CODE]({ commit }) {
    return new Promise((resolve) => {
      httpGet('/select_options/dict_code').then((response) => {
        commit(RECEIVE_DICT_CODE, response.data)
        localStorage.setItem('dictCode', JSON.stringify(response.data))
        resolve(response.data)
      })
    })
  },
  [SHOW_PRODUCTS_MALL]({ commit }, payload) {
    localStorage.setItem('showProductsMall', payload.showProductsMall)
    commit(SHOW_PRODUCTS_MALL, payload.showProductsMall)
  },
  [USER_LOGO]({ commit }, payload) {
    localStorage.setItem('userLogo', payload.userLogo)
    commit(USER_LOGO, payload.userLogo)
  },
  [USER_LOGO_DARK]({ commit }, payload) {
    localStorage.setItem('userLogoDark', payload.userLogoDark)
    commit(USER_LOGO_DARK, payload.userLogoDark)
  },
  [THEME_SWITCH]({ commit }, payload) {
    localStorage.setItem('currentTheme', payload.currentTheme)
    commit(THEME_SWITCH, payload.currentTheme)
  },
  [LANG_SWITCH]({ commit }, payload) {
    localStorage.setItem('lang', payload.lang)
    commit(LANG_SWITCH, payload.lang)
  },
}

const mutations = {
  [USER_LOGIN](state, user) {
    Object.assign(state.user, user)
  },
  [USER_LOGOUT](state) {
    state.user = {}
  },
  [LOADING_START](state) {
    state.loading = true
  },
  [LOADING_END](state) {
    state.loading = false
  },
  [LEFTBAR_SWITCH](state, leftbar) {
    Object.assign(state.leftbar, leftbar)
  },
  [LEFT_MENUS](state, menus) {
    Object.assign(state.menus, menus)
  },
  [NAV_TABS](state, tabs) {
    Object.assign(state.tabs, tabs)
  },
  [USER_PERMISSIONS](state, permissions) {
    Object.assign(state.permissions, permissions)
  },
  [CLEAR_BASE](state) {
    state.menus = []
    state.tabs = {}
    state.permissions = {}
  },
  [RECEIVE_DICT_CODE](state, dictCode) {
    Object.assign(state.dictCode, dictCode)
  },
  [SHOW_PRODUCTS_MALL](state, showProductsMall) {
    state.showProductsMall = showProductsMall
  },
  [USER_LOGO](state, userLogo) {
    state.userLogo = userLogo
  },
  [USER_LOGO_DARK](state, userLogoDark) {
    state.userLogoDark = userLogoDark
  },
  [THEME_SWITCH](state, currentTheme) {
    state.currentTheme = currentTheme
  },
  [LANG_SWITCH](state, lang) {
    state.lang = lang
  },
}

export default {
  state,
  actions,
  mutations,
}
