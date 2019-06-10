import Vue from 'vue'
import VueRouter from 'vue-router'

import store from '@/store'
import authRoutes from '@/apps/routes'

const routes = [
  { path: '/login', component: () => import('@/apps/accounts/views/Login'), meta: { requiresAuth: false } },
  { path: '/signup', component: () => import('@/apps/accounts/views/Signup'), meta: { requiresAuth: false } },
  { path: '/', component: () => import('@/layout/views/Home'), children: authRoutes },
  { path: '*', component: () => import('@/components/404'), meta: { requiresAuth: false } },
  { path: '/temp_page', component: () => import('@/components/TempPage'), meta: { requiresAuth: false } },
]

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
