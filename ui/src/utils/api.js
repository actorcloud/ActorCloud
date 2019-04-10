import axios from 'axios'
import { Message } from 'element-ui'

import router from '@/router'
import store from '@/store'
import lang from '@/lang'

const baseURL = '/api/v1'

Object.assign(axios.defaults, {
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
  },
  baseURL,
  timeout: 1000000,
})

function handleError(error) {
  const locale = store.state.base.lang
  setTimeout(() => {
    store.dispatch('LOADING_END')
  }, 1500)
  if (error.response.status === 401) {
    if (router.currentRoute.path !== '/login') {
      Message.error(lang[locale].errors.loginExpired)
    }
    // Status of 401, clear login information, redirect to login
    if (store.state.accounts.user.token) {
      store.dispatch('USER_LOGOUT')
      router.replace({
        path: '/login',
        query: { redirect: router.currentRoute.fullPath },
      })
    }
  } else if (error.response.status === 403
    && error.response.data.errorCode === 'PERMISSION_DENIED') {
    router.push({ path: '/forbidden' })
  } else if (error.response.status === 500
    && !error.response.data.errorCode) {
    Message.error(lang[locale].errors.INTERNAL_ERROR) // 500 && has no errorCode to prompt Inveral error
  } else {
    let errorMessage = ''
    const { errorCode } = error.response.data
    const formError = error.response.data.errors
    if (formError) { // errors has error message object
      const errorKey = Object.keys(formError)[0].replace(/ /g, '_')
      Object.keys(formError).forEach((key) => {
        errorMessage = formError[key].replace(/ /g, '_')
      })
      // Determines whether the values of key and value are translated
      if (lang[locale].errors[errorKey] && lang[locale].errors[errorMessage]) {
        // If it did, it spliced the key-value in the errors
        Message.error(`${lang[locale].errors[errorKey]} ${lang[locale].errors[errorMessage]}`)
      } else {
        // If not，the field name and prompt are printed directly
        Message.error(`${errorKey} ${errorMessage}`)
      }
    } else { // With out errors, prompt errorCode
      Message.error(lang[locale].errors[errorCode])
    }
  }
  return Promise.reject(error)
}

axios.interceptors.request.use((config = {}) => {
  const { lang } = store.state.base
  if (!config.disableLoading) {
    store.dispatch('LOADING_START')
  }
  const user = JSON.parse(sessionStorage.getItem('user'))
  || JSON.parse(localStorage.getItem('user')) || {}
  config.headers.Authorization = `Bearer ${user.token}`
  config.headers['Accept-Language'] = lang
  return config
}, () => {
  setTimeout(() => {
    store.dispatch('LOADING_END')
  }, 200)
})

axios.interceptors.response.use((response) => {
  setTimeout(() => {
    store.dispatch('LOADING_END')
  }, 200)
  return response
}, handleError)

const [httpGet, httpPost, httpPut, httpDelete] = [axios.get, axios.post, axios.put, axios.delete]

export { baseURL, httpGet, httpPut, httpPost, httpDelete }
