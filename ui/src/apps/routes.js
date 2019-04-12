import MicroApps from '../assets/micro.apps.json'
import PrivateApps from '../assets/micro.private.json'
import forbidden from '@/components/403'

const authRoutes = [
  { path: 'forbidden', component: forbidden },
]

MicroApps.forEach((app) => {
  // eslint-disable-next-line
  const router = require(`./${app}/routes`)
  authRoutes.push(...router.default)
})

PrivateApps.forEach((app) => {
  // eslint-disable-next-line
  const context = require.context('../', true, /\private_apps/)
  const router = context(`./private_apps/${app}/routes.js`)
  authRoutes.push(...router.default)
})

export default authRoutes
