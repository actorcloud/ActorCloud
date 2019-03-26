import Vue from 'vue'
import VueRouter from 'vue-router'

import store from '@/store'
import routes from '@/apps/routes'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  routes,
})

router.beforeEach((to, from, next) => {
  const { requiresAuth = true, requiresAdmin = false } = to.meta
  document.body.scrollTop = 0
  document.documentElement.scrollTop = 0
  if (requiresAuth) {
    if (!store.state.accounts.user.token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
    } else if (requiresAdmin && store.state.accounts.user.tenantType !== 0) {
      next('/forbidden')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
