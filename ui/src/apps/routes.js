import MicroApps from '../assets/micro.apps.json'
import PrivateApps from '../assets/micro.private.json'

import Login from './base/views/Login'
import Signup from './base/views/Signup'
import Home from './base/views/Home'
import NotFound from './base/views/404'
import EmptyPage from './base/views/EmptyPage'

const authRoutes = []

MicroApps.forEach((app) => {
  // eslint-disable-next-line
  const router = require(`./${app}/routes`)
  authRoutes.push(...router.default)
})

if (PrivateApps.length) {
  PrivateApps.forEach((app) => {
    // eslint-disable-next-line
    const router = require(`../private_apps/${app}/routes`)
    authRoutes.push(...router.default)
  })
}

export default [
  { path: '/login', component: Login, meta: { requiresAuth: false } },
  { path: '/signup', component: Signup, meta: { requiresAuth: false } },
  { path: '/', component: Home, children: authRoutes },
  { path: '*', meta: { requiresAuth: false }, component: NotFound },
  { path: '/empty_page', component: EmptyPage, meta: { requiresAuth: false } },
]
