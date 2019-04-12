import Vue from 'vue'
import VueRouter from 'vue-router'

import store from '@/store'
import authRoutes from '@/apps/routes'
import Home from '@/layout/views/Home'
import Login from '@/apps/accounts/views/Login'
import Signup from '@/apps/accounts/views/Signup'
import NotFound from '@/components/404'
import TempPage from '@/components/TempPage'

const routes = [
  { path: '/login', component: Login, meta: { requiresAuth: false } },
  { path: '/signup', component: Signup, meta: { requiresAuth: false } },
  { path: '/', component: Home, children: authRoutes },
  { path: '*', meta: { requiresAuth: false }, component: NotFound },
  { path: '/temp_page', component: TempPage, meta: { requiresAuth: false } },
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
